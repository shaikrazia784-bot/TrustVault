
from flask import Blueprint, render_template, abort, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import AuditLog, User
from audit_utils import log_audit_event

admin = Blueprint("admin", __name__, url_prefix="/admin")


def is_admin():
    return (current_user.role or "").strip().lower() == "admin"


@admin.route("/")
@login_required
def dashboard():

    if not is_admin():

        log_audit_event(
            actor_id=current_user.id,
            document_id=None,
            action="UNAUTHORIZED_ADMIN_ACCESS",
            outcome="DENIED",
            details=(
                f"User {current_user.email} with role "
                f"{current_user.role} attempted to open Admin dashboard."
            )
        )

        db.session.commit()
        abort(403)

    security_alerts = AuditLog.query.filter(
        AuditLog.outcome == "DENIED"
    ).order_by(
        AuditLog.id.desc()
    ).limit(100).all()

    audit_logs = AuditLog.query.order_by(
        AuditLog.id.desc()
    ).limit(200).all()

    users = User.query.order_by(User.id.desc()).all()

    total_users = User.query.count()

    total_admins = User.query.filter(
        db.func.lower(User.role) == "admin"
    ).count()

    total_owners = User.query.filter(
        db.func.lower(User.role) == "owner"
    ).count()

    total_viewers = User.query.filter(
        db.func.lower(User.role) == "viewer"
    ).count()

    return render_template(
        "admin.html",
        security_alerts=security_alerts,
        audit_logs=audit_logs,
        users=users,
        total_users=total_users,
        total_admins=total_admins,
        total_owners=total_owners,
        total_viewers=total_viewers
    )


@admin.route("/promote/<int:user_id>", methods=["POST"])
@login_required
def promote_owner(user_id):

    if not is_admin():

        log_audit_event(
            actor_id=current_user.id,
            document_id=None,
            action="UNAUTHORIZED_OWNER_PROMOTION",
            outcome="DENIED",
            details=(
                f"User {current_user.email} attempted to promote "
                f"user ID {user_id} without ADMIN permission."
            )
        )

        db.session.commit()
        abort(403)

    user = db.session.get(User, user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin.dashboard"))

    user_role = (user.role or "").strip().lower()

    if user_role != "viewer":
        flash(
            "Only VIEWER accounts can be promoted to OWNER.",
            "error"
        )
        return redirect(url_for("admin.dashboard"))

    user.role = "OWNER"

    log_audit_event(
        actor_id=current_user.id,
        document_id=None,
        action="OWNER_PROMOTION",
        outcome="SUCCESS",
        details=(
            f"Admin {current_user.email} promoted "
            f"{user.email} from VIEWER to OWNER."
        )
    )

    db.session.commit()

    flash(
        f"{user.name} has been promoted to OWNER successfully!",
        "success"
    )

    return redirect(url_for("admin.dashboard"))
