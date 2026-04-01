"""
PaaS Lab: Enhanced Flask Application (Containerised)
Incorporates 2026 trends: AI-native features, zero-trust security,
sustainability awareness, and container-first deployment.
"""

import os
import json
import logging
from datetime import datetime, timezone

from flask import Flask, request, jsonify, render_template, abort
from markupsafe import escape

# ---------------------------------------------------------------------------
# App Initialisation
# ---------------------------------------------------------------------------
app = Flask(__name__)

# Enforce secure defaults
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants / Configuration
# ---------------------------------------------------------------------------
REGION = os.environ.get("DEPLOY_REGION", "asia-southeast1")
DEPLOYMENT_YEAR = 2026


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
    POST -> analyses input and returns personalised greeting
    """
    if request.method == "POST":
        user_input = request.form.get("name", "").strip()
        if not user_input or len(user_input) > 200:
            abort(400, description="Name must be 1-200 characters.")
        result = analyse_sentiment_and_greet(user_input)
        return render_template("greet.html", result=result, user_input=user_input)
    return render_template("greet_form.html")


@app.route("/health")
def health():
    """Health-check endpoint for load balancers and uptime monitoring."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "region": REGION,
        "containerised": True,
    })


@app.route("/api/analyse", methods=["POST"])
def api_analyse():
    """
    JSON API for sentiment analysis.
    Accepts: {"text": "..."}
    Returns: {"greeting": "...", "sentiment": "...", "ai_powered": bool}
    """
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        abort(400, description="JSON body with 'text' field required.")
    text = data["text"].strip()
    if not text or len(text) > 500:
        abort(400, description="Text must be 1-500 characters.")
    result = analyse_sentiment_and_greet(text)
    return jsonify(result)


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e.description)), 400


@app.errorhandler(404)
def not_found(e):
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
