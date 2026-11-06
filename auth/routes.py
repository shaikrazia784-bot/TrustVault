
import os
import hmac

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User, AuditLog

auth = Blueprint("auth", __name__)


# Save security activity in audit_logs
def log_security_event(user, action, outcome, details):

    event = AuditLog(
        actor_id=user.id if user else None,
        document_id=None,
        action=action,
        outcome=outcome,
        details=details
    )

    db.session.add(event)
    db.session.commit()


# Registration Route
@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("Please fill all fields.", "error")

        elif password != confirm_password:
            flash("Passwords do not match.", "error")

        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")

        elif User.query.filter_by(email=email).first():
            flash("Email already exists. Please use another email.", "error")

        else:

            new_user = User(
                name=name,
                email=email,
                role="VIEWER"
            )

            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! Please login.", "success")

            return redirect(url_for("auth.login"))

    return render_template("register.html")


# Login Route
@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        login_type = request.form.get("login_type", "viewer").strip().lower()
        admin_code = request.form.get("admin_code", "")

        user = User.query.filter_by(email=email).first()

        # Normalize database role
        user_role = (user.role or "").strip().lower() if user else ""

        # Check credentials
        if not user or not user.is_active or not user.check_password(password):

            if login_type == "admin":

                log_security_event(
                    user,
                    "ADMIN_LOGIN_ATTEMPT",
                    "DENIED",
                    "Admin login attempt failed because credentials were invalid."
                )

            flash("Invalid email or password.", "error")

            return render_template("login.html")

        # ADMIN LOGIN
        if login_type == "admin":

            saved_code = os.getenv("ADMIN_SECURITY_CODE", "")

            code_correct = (
                bool(saved_code)
                and hmac.compare_digest(admin_code, saved_code)
            )

            # Only actual ADMIN accounts can access Admin Dashboard
            if user_role != "admin":

                log_security_event(
                    user,
                    "UNAUTHORIZED_ADMIN_ACCESS",
                    "DENIED",
                    f"User {user.email} with role {user.role} "
                    f"attempted Admin access. "
                    f"Security code correct: {code_correct}."
                )

                flash(
                    "Unauthorized! Your account does not have Admin permission.",
                    "error"
                )

                return render_template("login.html")

            # Verify Admin security code
            if not code_correct:

                log_security_event(
                    user,
                    "ADMIN_LOGIN_ATTEMPT",
                    "DENIED",
                    "Admin account entered an incorrect security code."
                )

                flash("Incorrect Admin Security Code.", "error")

                return render_template("login.html")

            # Successful Admin login
            log_security_event(
                user,
                "ADMIN_LOGIN",
                "SUCCESS",
                "Admin logged in successfully."
            )

            login_user(user)

            flash("Admin login successful!", "success")

            return redirect(url_for("dashboard"))

        # VIEWER LOGIN
        elif login_type == "viewer":

            # Admin account cannot use Viewer login
            if user_role == "admin":

                flash(
                    "Please select Admin login for this account.",
                    "error"
                )

                return render_template("login.html")

            log_security_event(
                user,
                "VIEWER_LOGIN",
                "SUCCESS",
                "User logged in successfully."
            )

            login_user(user)

            flash("Login successful!", "success")

            return redirect(url_for("dashboard"))

        else:

            flash("Invalid login selection.", "error")

            return render_template("login.html")

    return render_template("login.html")


# Logout Route
@auth.route("/logout")
@login_required
def logout():

    log_security_event(
        current_user,
        "LOGOUT",
        "SUCCESS",
        "User logged out successfully."
    )

    logout_user()

    flash("You have logged out successfully.", "success")

    return redirect(url_for("auth.login"))
