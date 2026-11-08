
from flask import Flask, render_template, redirect, url_for
from sqlalchemy import text
from config import Config
from extensions import db, login_manager
from flask_login import login_required, current_user


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Import models
    from models import User, DocumentVersion

    # Import Blueprints
    from auth.routes import auth
    from admin.routes import admin
    from owner.routes import owner, inject_dashboard_data

    # Load logged-in user
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            app.logger.exception("Failed to load user from database")
            db.session.rollback()
            return None

    # Register Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(owner)

    # Home page
    @app.route("/")
    def home():
        return render_template("index.html")

    # Health Check - Does not depend on database
    @app.route("/health", methods=["GET"])
    def health_check():
        return "TrustVault is Healthy!", 200

    # Role Based Dashboard
    @app.route("/dashboard")
    @login_required
    def dashboard():

        user_role = (current_user.role or "").strip().upper()

        if user_role == "ADMIN":
            return redirect(url_for("admin.dashboard"))

        (
            my_documents,
            viewers,
            shared_permissions,
            shared_documents
        ) = inject_dashboard_data()

        return render_template(
            "dashboard.html",
            user=current_user,
            my_documents=my_documents,
            viewers=viewers,
            shared_permissions=shared_permissions,
            shared_documents=shared_documents
        )

    # Database Connection Check
    @app.route("/db-check", methods=["GET"])
    def database_check():

        try:
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            return "TrustVault Database Connected Successfully!", 200

        except Exception:
            app.logger.exception("Database connection failed")
            db.session.rollback()
            return "Database connection failed!", 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
