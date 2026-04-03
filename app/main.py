"""
PaaS Lab: Enhanced Flask Application (Containerised) — Railway Edition
Incorporates 2026 trends: AI-native features, zero-trust security,
sustainability awareness, container-first deployment, and managed database.
"""

import os
import json
import logging
from datetime import datetime, timezone

from flask import Flask, request, jsonify, render_template, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape

# ---------------------------------------------------------------------------
# App Initialisation
# ---------------------------------------------------------------------------
app = Flask(__name__)

# Database configuration — Railway injects DATABASE_URL automatically
database_url = os.environ.get("DATABASE_URL", "sqlite:////tmp/local.db")
# Railway Postgres URLs use 'postgres://' but SQLAlchemy requires 'postgresql://'
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# Enforce secure defaults
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

db = SQLAlchemy(app)

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants / Configuration
# ---------------------------------------------------------------------------
REGION = os.environ.get("DEPLOY_REGION", "railway-us")
DEPLOYMENT_YEAR = 2026


# ---------------------------------------------------------------------------
# Database Model
# ---------------------------------------------------------------------------
class SentimentLog(db.Model):
    """Stores each sentiment analysis request for CRUD demonstration."""
    __tablename__ = "sentiment_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    input_text = db.Column(db.String(500), nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    greeting = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "input_text": self.input_text,
            "sentiment": self.sentiment,
            "greeting": self.greeting,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Create tables on first request
with app.app_context():
    db.create_all()
    logger.info("Database tables created/verified — URI: %s", "***" if "postgresql" in database_url else "sqlite (local)")


# ---------------------------------------------------------------------------
# Helper: Sentiment Analysis & Greeting Generation
# ---------------------------------------------------------------------------
def analyse_sentiment_and_greet(user_input: str) -> dict:
    """
    Analyse sentiment and generate a personalised greeting.
    Uses a simple keyword-based approach. Swap in any AI/ML service
    (OpenAI, Hugging Face, Ollama, etc.) for production use.
    """
    text_lower = user_input.lower()

    positive_words = {"happy", "excited", "great", "love", "amazing", "wonderful",
                      "thrilled", "awesome", "fantastic", "good", "joy", "glad"}
    negative_words = {"sad", "angry", "upset", "hate", "terrible", "awful",
                      "frustrated", "disappointed", "annoyed", "bad", "worse"}

    pos_count = sum(1 for w in text_lower.split() if w in positive_words)
    neg_count = sum(1 for w in text_lower.split() if w in negative_words)

    if pos_count > neg_count:
        sentiment = "positive"
        greeting = f"Hello, {escape(user_input)}! Your enthusiasm is wonderful — welcome to our PaaS Lab!"
    elif neg_count > pos_count:
        sentiment = "negative"
        greeting = f"Hello, {escape(user_input)}. We hope this experience brightens your day. Welcome to our PaaS Lab."
    else:
        sentiment = "neutral"
        greeting = f"Hello, {escape(user_input)}! Welcome to our PaaS Lab."

    return {
        "greeting": greeting,
        "sentiment": sentiment,
        "ai_powered": False,
    }


# ---------------------------------------------------------------------------
# Security: Request-level guards (Zero-Trust mindset)
# ---------------------------------------------------------------------------
@app.after_request
def set_security_headers(response):
    """Apply defence-in-depth HTTP security headers."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "ALLOWALL"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    response.headers["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains; preload"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https://images.unsplash.com; "
        "connect-src 'self'; "
        "frame-ancestors 'self' https://*.hf.space https://huggingface.co;"
    )
    return response


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Landing page with project information."""
    return render_template("index.html", region=REGION, year=DEPLOYMENT_YEAR)


@app.route("/greet", methods=["GET", "POST"])
def greet():
    """
    Greeting endpoint.
    GET  -> renders input form
    POST -> analyses input, stores in DB, and returns personalised greeting
    """
    if request.method == "POST":
        user_input = request.form.get("name", "").strip()
        if not user_input or len(user_input) > 200:
            abort(400, description="Name must be 1-200 characters.")
        result = analyse_sentiment_and_greet(user_input)

        # Store in database (CREATE operation)
        log_entry = SentimentLog(
            input_text=user_input,
            sentiment=result["sentiment"],
            greeting=result["greeting"],
        )
        db.session.add(log_entry)
        db.session.commit()
        logger.info("Sentiment logged: id=%d sentiment=%s", log_entry.id, log_entry.sentiment)

        return render_template("greet.html", result=result, user_input=user_input)
    return render_template("greet_form.html")


@app.route("/health")
def health():
    """Health-check endpoint for load balancers and uptime monitoring."""
    db_status = "connected"
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {e}"
        logger.error("Database health check failed: %s", e)

    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "region": REGION,
        "containerised": True,
        "database": db_status,
    })


@app.route("/api/analyse", methods=["GET", "POST"])
def api_analyse():
    """
    JSON API for sentiment analysis.
    GET  -> returns API usage documentation
    POST -> Accepts: {"text": "..."}, Returns: {"greeting": "...", "sentiment": "...", "ai_powered": bool}
    """
    if request.method == "GET":
        return jsonify({
            "endpoint": "/api/analyse",
            "method": "POST",
            "description": "Sentiment analysis and greeting generation API",
            "request_body": {"text": "string (1-500 characters)"},
            "response": {
                "greeting": "string",
                "sentiment": "positive | negative | neutral",
                "ai_powered": "boolean",
            },
            "example": {
                "curl": 'curl -X POST /api/analyse -H "Content-Type: application/json" -d \'{"text": "I love cloud computing!"}\''
            },
        })
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        abort(400, description="JSON body with 'text' field required.")
    text = data["text"].strip()
    if not text or len(text) > 500:
        abort(400, description="Text must be 1-500 characters.")
    result = analyse_sentiment_and_greet(text)

    # Store in database
    log_entry = SentimentLog(
        input_text=text,
        sentiment=result["sentiment"],
        greeting=result["greeting"],
    )
    db.session.add(log_entry)
    db.session.commit()
    logger.info("API sentiment logged: id=%d sentiment=%s", log_entry.id, log_entry.sentiment)

    return jsonify(result)


# ---------------------------------------------------------------------------
# CRUD Routes for Sentiment Logs
# ---------------------------------------------------------------------------
@app.route("/logs")
def list_logs():
    """READ — List all sentiment analysis logs."""
    logs = SentimentLog.query.order_by(SentimentLog.created_at.desc()).all()
    logger.info("Listing %d sentiment logs", len(logs))
    return render_template("logs.html", logs=logs)


@app.route("/api/logs")
def api_list_logs():
    """READ — JSON API to list all logs."""
    logs = SentimentLog.query.order_by(SentimentLog.created_at.desc()).all()
    return jsonify([log.to_dict() for log in logs])


@app.route("/api/logs/<int:log_id>", methods=["PUT"])
def api_update_log(log_id):
    """UPDATE — Edit a sentiment log entry."""
    log_entry = SentimentLog.query.get_or_404(log_id)
    data = request.get_json(silent=True)
    if not data or "input_text" not in data:
        abort(400, description="JSON body with 'input_text' field required.")
    new_text = data["input_text"].strip()
    if not new_text or len(new_text) > 500:
        abort(400, description="Text must be 1-500 characters.")

    # Re-analyse sentiment with updated text
    result = analyse_sentiment_and_greet(new_text)
    log_entry.input_text = new_text
    log_entry.sentiment = result["sentiment"]
    log_entry.greeting = result["greeting"]
    db.session.commit()
    logger.info("Updated log id=%d", log_id)
    return jsonify(log_entry.to_dict())


@app.route("/api/logs/<int:log_id>", methods=["DELETE"])
def api_delete_log(log_id):
    """DELETE — Remove a sentiment log entry."""
    log_entry = SentimentLog.query.get_or_404(log_id)
    db.session.delete(log_entry)
    db.session.commit()
    logger.info("Deleted log id=%d", log_id)
    return jsonify({"message": f"Log {log_id} deleted"}), 200


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(400)
def bad_request(e):
    logger.warning("Bad request: %s — path=%s", e.description, request.path)
    return jsonify(error=str(e.description)), 400


@app.errorhandler(404)
def not_found(e):
    logger.warning("Not found: %s", request.path)
    return jsonify(error="Resource not found"), 404


@app.errorhandler(500)
def server_error(e):
    logger.error("Internal error: %s", e)
    return jsonify(error="Internal server error"), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)), debug=True)
