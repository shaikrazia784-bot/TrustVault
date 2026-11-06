
from flask import Flask, render_template, redirect, url_for
from sqlalchemy import text
from config import Config
from extensions import db, login_manager
from flask_login import login_required, current_user


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from models import User
    from auth.routes import auth
    from admin.routes import admin
    from owner.routes import owner

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(owner)

    @app.route("/")
    def home():
        return render_template("index.html")

    # Role Based Dashboard
    @app.route("/dashboard")
    @login_required
    def dashboard():

        user_role = (current_user.role or "").strip().lower()

        if user_role == "admin":
            return redirect(url_for("admin.dashboard"))

        return render_template("dashboard.html", user=current_user)

    # Database Connection Check
    @app.route("/db-check")
    def database_check():

        try:
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            return "TrustVault Database Connected Successfully!"

        except Exception:
            app.logger.exception("Database connection failed")
            return "Database connection failed!", 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
