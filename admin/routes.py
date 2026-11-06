
from flask import Blueprint, render_template, abort, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import AuditLog, User

admin = Blueprint("admin", __name__, url_prefix="/admin")


# Check whether the logged-in user is ADMIN
def is_admin():

    return (current_user.role or "").strip().lower() == "admin"


# Admin Dashboard
@admin.route("/")
@login_required
def dashboard():

    # Only ADMIN can access Admin Dashboard
    if not is_admin():

        event = AuditLog(
            actor_id=current_user.id,
            document_id=None,
            action="UNAUTHORIZED_ADMIN_ACCESS",
            outcome="DENIED",
            details=(
                f"User {current_user.email} with role "
                f"{current_user.role} attempted to open Admin dashboard."
            )
        )

        db.session.add(event)
        db.session.commit()

        abort(403)

    # Fetch security alerts
    security_alerts = AuditLog.query.filter(
        AuditLog.outcome == "DENIED"
    ).order_by(
        AuditLog.id.desc()
    ).limit(100).all()

    # Fetch registered users
    users = User.query.order_by(User.id.desc()).all()

    # Count all users
    total_users = User.query.count()

    # Count ADMIN users
    total_admins = User.query.filter(
        db.func.lower(User.role) == "admin"
    ).count()

    # Count OWNER users
    total_owners = User.query.filter(
        db.func.lower(User.role) == "owner"
    ).count()

    # Count VIEWER users
    total_viewers = User.query.filter(
        db.func.lower(User.role) == "viewer"
    ).count()

    return render_template(
        "admin.html",
        security_alerts=security_alerts,
        users=users,
        total_users=total_users,
        total_admins=total_admins,
        total_owners=total_owners,
        total_viewers=total_viewers
    )


# Promote VIEWER to OWNER
@admin.route("/promote/<int:user_id>", methods=["POST"])
@login_required
def promote_owner(user_id):

    # Only ADMIN can promote users
    if not is_admin():

        event = AuditLog(
            actor_id=current_user.id,
            document_id=None,
            action="UNAUTHORIZED_OWNER_PROMOTION",
            outcome="DENIED",
            details=(
                f"User {current_user.email} attempted to promote "
                f"user ID {user_id} without ADMIN permission."
            )
        )

        db.session.add(event)
        db.session.commit()

        abort(403)

    # Find selected user
    user = db.session.get(User, user_id)

    if not user:

        flash("User not found.", "error")
        return redirect(url_for("admin.dashboard"))

    # Only VIEWER can be promoted
    user_role = (user.role or "").strip().lower()

    if user_role != "viewer":

        flash("Only VIEWER accounts can be promoted to OWNER.", "error")
        return redirect(url_for("admin.dashboard"))

    # Change role to OWNER
    user.role = "OWNER"

    # Record promotion in audit logs
    event = AuditLog(
        actor_id=current_user.id,
        document_id=None,
        action="OWNER_PROMOTION",
        outcome="SUCCESS",
        details=(
            f"Admin {current_user.email} promoted "
            f"{user.email} from VIEWER to OWNER."
        )
    )

    db.session.add(event)
    db.session.commit()

    flash(f"{user.name} has been promoted to OWNER successfully!", "success")

    return redirect(url_for("admin.dashboard"))
