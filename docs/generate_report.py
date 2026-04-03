#!/usr/bin/env python3
"""Generate the PaaS Lab assignment PDF report."""

from fpdf import FPDF


class Report(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "PaaS Lab Report - Railway Deployment", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 41, 59)
        self.ln(4)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(99, 102, 241)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(4)

    def subsection_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(60, 60, 80)
        self.ln(2)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        x = self.get_x()
        self.cell(6, 5.5, "-")
        self.multi_cell(0, 5.5, text)
        self.ln(1)


def build_report():
    pdf = Report()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ---- Title ----
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 14, "Practical Application of PaaS", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(99, 102, 241)
    pdf.cell(0, 10, "with Railway", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "Cloud Computing & Big Data - PaaS Lab Report", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Date: April 3, 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ---- 1. Deployment Process ----
    pdf.section_title("1. Deployment Process")

    pdf.subsection_title("1.1 Application Overview")
    pdf.body_text(
        "The application is a containerised Flask (Python 3.13) web application that performs keyword-based "
        "sentiment analysis and generates personalised greetings. It features a modern responsive UI, "
        "a RESTful JSON API, and a PostgreSQL-backed persistence layer for full CRUD operations. "
        "The application was originally deployed on Google App Engine and has been migrated to Railway "
        "to demonstrate PaaS portability."
    )

    pdf.subsection_title("1.2 Railway Deployment Steps")
    pdf.bullet("Created a new project on Railway (railway.com) and linked the GitHub repository.")
    pdf.bullet("Provisioned a Railway-managed PostgreSQL database add-on from the Railway dashboard.")
    pdf.bullet("Railway automatically injected DATABASE_URL into the application's environment variables.")
    pdf.bullet("Configured railway.json with Dockerfile builder, health check path (/health), and restart policy.")
    pdf.bullet("Pushed code to GitHub main branch, triggering Railway's automatic deployment pipeline.")
    pdf.bullet("Railway built the Docker image, ran the container, and assigned a public URL.")
    pdf.bullet("Verified the deployment by testing all endpoints: /, /greet, /health, /api/analyse, /logs.")

    pdf.subsection_title("1.3 Environment Configuration")
    pdf.body_text(
        "Sensitive data is managed exclusively through Railway's environment variable management system. "
        "The following variables are configured in Railway's dashboard (never committed to source code):"
    )
    pdf.bullet("DATABASE_URL - Automatically injected by Railway's PostgreSQL plugin. "
               "The app handles the postgres:// to postgresql:// prefix conversion required by SQLAlchemy.")
    pdf.bullet("SECRET_KEY - A cryptographically random key for Flask session signing, set via Railway dashboard.")
    pdf.bullet("DEPLOY_REGION - Set to 'railway-us' to reflect the deployment region.")
    pdf.bullet("PORT - Automatically set by Railway; the app reads it dynamically via os.environ.get('PORT', 7860).")
    pdf.body_text(
        "No .env files or secrets are committed to version control. The .gitignore excludes .env files, "
        "and the application code uses os.environ.get() with safe defaults for local development."
    )

    # ---- 2. Database Integration ----
    pdf.section_title("2. Database Integration")

    pdf.subsection_title("2.1 Schema Design")
    pdf.body_text(
        "A Railway-managed PostgreSQL instance stores sentiment analysis logs. The schema consists of "
        "a single table, sentiment_logs, defined via Flask-SQLAlchemy ORM:"
    )
    pdf.set_font("Courier", "", 9)
    pdf.set_text_color(30, 41, 59)
    schema = (
        "  sentiment_logs\n"
        "  +-------------+---------------+-------------------------------+\n"
        "  | Column      | Type          | Constraints                   |\n"
        "  +-------------+---------------+-------------------------------+\n"
        "  | id          | SERIAL        | PRIMARY KEY, AUTO INCREMENT   |\n"
        "  | input_text  | VARCHAR(500)  | NOT NULL                      |\n"
        "  | sentiment   | VARCHAR(20)   | NOT NULL (pos/neg/neutral)    |\n"
        "  | greeting    | TEXT          | NOT NULL                      |\n"
        "  | created_at  | TIMESTAMP     | DEFAULT NOW() UTC             |\n"
        "  +-------------+---------------+-------------------------------+"
    )
    pdf.multi_cell(0, 4.5, schema)
    pdf.ln(4)

    pdf.subsection_title("2.2 CRUD Operations")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.bullet("CREATE: Every POST to /greet or /api/analyse automatically stores the analysis in the database.")
    pdf.bullet("READ: GET /logs renders an HTML dashboard; GET /api/logs returns JSON for all entries.")
    pdf.bullet("UPDATE: PUT /api/logs/<id> accepts new input text, re-analyses sentiment, and updates the record.")
    pdf.bullet("DELETE: DELETE /api/logs/<id> removes a record. The logs UI provides edit/delete buttons.")

    # ---- 3. Scalability ----
    pdf.section_title("3. Scalability Awareness")

    pdf.subsection_title("3.1 Railway's Pricing & Scaling Model")
    pdf.body_text(
        "Railway uses a usage-based pricing model that charges per vCPU-second and per GB-hour of memory. "
        "The Hobby plan ($5/month) includes $5 of resource credits. For a lightweight Flask app with "
        "Gunicorn (2 workers, 4 threads), baseline costs are minimal ($0.50-2.00/month). "
        "If traffic increases significantly:"
    )
    pdf.bullet("CPU costs scale linearly - a 10x traffic increase might raise compute costs to ~$5-15/month.")
    pdf.bullet("Database costs: Railway PostgreSQL charges for storage and compute separately. "
               "At low volume (<1GB), costs remain under $5/month.")
    pdf.bullet("Bandwidth: Railway includes reasonable egress; heavy API usage could incur additional charges.")

    pdf.subsection_title("3.2 Scaling Plan")
    pdf.bullet("Horizontal scaling: Increase Gunicorn workers from 2 to 4-8 for CPU-bound requests.")
    pdf.bullet("Vertical scaling: Railway allows upgrading instance resources (more vCPU/RAM) via dashboard.")
    pdf.bullet("Database scaling: Enable connection pooling (PgBouncer), add read replicas for heavy read loads.")
    pdf.bullet("Caching: Add Redis (Railway plugin) for frequently accessed data and session storage.")
    pdf.bullet("CDN: Offload static assets to a CDN (Cloudflare) to reduce origin server load.")

    # ---- 4. CI/CD ----
    pdf.section_title("4. CI/CD Workflow")
    pdf.body_text(
        "The repository uses a GitHub Actions workflow (.github/workflows/deploy.yml) that triggers "
        "on every push to the main branch. The pipeline has two stages:"
    )
    pdf.bullet("Test stage: Installs dependencies, runs smoke tests against all endpoints (health check, "
               "landing page, greeting form, sentiment API, logs page, and CRUD API). "
               "Tests verify HTTP status codes and response data correctness.")
    pdf.bullet("Deploy stage: Runs only on main branch pushes (not pull requests). Installs the Railway CLI "
               "and executes 'railway up --detach' using the RAILWAY_TOKEN secret stored in GitHub.")
    pdf.body_text(
        "Additionally, Railway itself monitors the GitHub repository and automatically rebuilds and "
        "redeploys the application on every push to main, providing a second layer of CI/CD. "
        "This dual approach ensures that broken code never reaches production (GitHub Actions gates the tests) "
        "while Railway handles the actual infrastructure deployment."
    )

    # ---- 5. Monitoring & Logging ----
    pdf.section_title("5. Monitoring & Logging")

    pdf.subsection_title("5.1 Structured Logging")
    pdf.body_text(
        "The application uses Python's logging module with structured format "
        "(timestamp, level, module, message). Key events logged include: "
        "database operations (create/update/delete with record IDs), "
        "error conditions (400 bad requests with path info, 404 not-found, 500 internal errors), "
        "and database health check failures."
    )

    pdf.subsection_title("5.2 Debugging Example")
    pdf.body_text(
        "During deployment, Railway logs revealed a critical database connection error: "
        "the DATABASE_URL provided by Railway used the prefix 'postgres://' while SQLAlchemy 2.x "
        "requires 'postgresql://'. The application logs showed:"
    )
    pdf.set_font("Courier", "", 8.5)
    pdf.set_text_color(180, 40, 40)
    pdf.multi_cell(0, 4.5,
        "  sqlalchemy.exc.NoSuchModuleError: Can't load plugin:\n"
        "  sqlalchemy.dialects:postgres"
    )
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.body_text(
        "Resolution: Added a prefix replacement in main.py that converts 'postgres://' to "
        "'postgresql://' before passing the URL to SQLAlchemy. This is a well-known Railway/Heroku "
        "compatibility issue. The fix was verified by checking the /health endpoint's database "
        "status field, which changed from 'error' to 'connected' after redeployment."
    )

    pdf.subsection_title("5.3 Health Check Monitoring")
    pdf.body_text(
        "The /health endpoint returns JSON with application status, timestamp, region, and database "
        "connectivity status. Railway's built-in health check (configured in railway.json) polls this "
        "endpoint every 30 seconds and automatically restarts the container if it fails, providing "
        "zero-downtime monitoring."
    )

    # ---- 6. Comparison ----
    pdf.section_title("6. Railway vs Heroku Comparison")

    pdf.set_font("Courier", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    comparison = (
        "  +---------------------+---------------------------+---------------------------+\n"
        "  | Feature             | Railway                   | Heroku                    |\n"
        "  +---------------------+---------------------------+---------------------------+\n"
        "  | Pricing             | Usage-based ($5/mo hobby) | Plan-based ($5-25/mo)     |\n"
        "  | Free tier           | Trial credits (limited)   | Removed in 2022           |\n"
        "  | Database            | PostgreSQL plugin (1-click)| Heroku Postgres add-on    |\n"
        "  | Docker support      | Native Dockerfile deploy  | Via heroku.yml (limited)  |\n"
        "  | CI/CD               | Auto-deploy from GitHub   | Auto-deploy from GitHub   |\n"
        "  | Cold starts         | Minimal (always running)  | 30s+ on Eco dynos         |\n"
        "  | Dashboard UX        | Modern, real-time logs    | Dated, less intuitive     |\n"
        "  | Env variables       | Dashboard + CLI           | Dashboard + CLI            |\n"
        "  | Scaling             | Vertical + horizontal     | Horizontal (dynos)        |\n"
        "  | Networking          | Private networking free   | Private Spaces ($$$)      |\n"
        "  +---------------------+---------------------------+---------------------------+"
    )
    pdf.multi_cell(0, 4.2, comparison)
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.body_text(
        "Railway offers a more modern developer experience with usage-based pricing, native Docker "
        "support, and a superior dashboard with real-time log streaming. Heroku remains a mature "
        "platform with a larger ecosystem of add-ons but has fallen behind in pricing competitiveness "
        "since removing its free tier in 2022. For this project, Railway was chosen for its seamless "
        "Docker deployment, one-click PostgreSQL provisioning, and transparent usage-based billing "
        "that suits educational and small-scale projects."
    )

    # ---- 7. Reflection ----
    pdf.section_title("7. Reflection")
    pdf.body_text(
        "This project demonstrated the full lifecycle of deploying a containerised application on a "
        "modern PaaS platform. Key takeaways include:"
    )
    pdf.bullet("PaaS platforms like Railway abstract away infrastructure management, allowing developers "
               "to focus on application logic. Provisioning a managed PostgreSQL database took seconds "
               "compared to hours of manual setup on IaaS.")
    pdf.bullet("Environment variable management is critical for security. Railway's dashboard-based "
               "approach ensures secrets never touch version control.")
    pdf.bullet("CI/CD integration provides confidence in deployments. The GitHub Actions pipeline catches "
               "errors before they reach production, while Railway handles zero-downtime deployments.")
    pdf.bullet("Container portability proved valuable - the same Dockerfile that ran on Google App Engine "
               "deployed to Railway with minimal configuration changes (primarily the PORT variable).")
    pdf.bullet("Usage-based pricing aligns costs with actual consumption, making PaaS economically viable "
               "for educational projects and startups that experience variable traffic patterns.")

    # Save
    pdf.output("docs/PaaS_Railway_Report.pdf")
    print("Report generated: docs/PaaS_Railway_Report.pdf")


if __name__ == "__main__":
    build_report()
