
import os
import uuid

from flask import (
    Blueprint, request, redirect, url_for,
    flash, current_app, send_from_directory, abort
)

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from extensions import db
from models import (
    User, Document, DocumentPermission,
    DocumentVersion
)
from audit_utils import log_audit_event


owner = Blueprint("owner", __name__, url_prefix="/owner")

ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}


def is_owner():
    return (current_user.role or "").strip().upper() == "OWNER"


def is_viewer():
    return (current_user.role or "").strip().upper() == "VIEWER"


def log_event(document_id, action, outcome, details):
    return log_audit_event(
        actor_id=current_user.id,
        document_id=document_id,
        action=action,
        outcome=outcome,
        details=details
    )


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def private_folder():
    folder = os.path.join(
        current_app.instance_path,
        "private_documents"
    )
    os.makedirs(folder, exist_ok=True)
    return folder


def save_uploaded_file(file):
    original_name = secure_filename(file.filename)

    if not original_name or not allowed_file(original_name):
        return None, None

    extension = original_name.rsplit(".", 1)[1].lower()
    storage_key = f"{uuid.uuid4().hex}.{extension}"

    folder = private_folder()
    file_path = os.path.join(folder, storage_key)

    file.save(file_path)

    return storage_key, original_name


# DASHBOARD DATA
def inject_dashboard_data():

    my_documents = []
    viewers = []
    shared_permissions = []
    shared_documents = []

    if is_owner():

        my_documents = Document.query.filter_by(
            owner_id=current_user.id
        ).order_by(Document.created_at.desc()).all()

        viewers = User.query.filter_by(
            role="VIEWER",
            is_active=True
        ).order_by(User.name.asc()).all()

        shared_permissions = (
            DocumentPermission.query
            .join(Document)
            .filter(
                Document.owner_id == current_user.id,
                DocumentPermission.is_active.is_(True)
            )
            .all()
        )

    elif is_viewer():

        shared_permissions = DocumentPermission.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).all()

        shared_documents = [
            permission
            for permission in shared_permissions
            if permission.document is not None
        ]

    return (
        my_documents,
        viewers,
        shared_permissions,
        shared_documents
    )


# OWNER UPLOAD DOCUMENT
@owner.route("/upload", methods=["POST"])
@login_required
def upload_document():

    if not is_owner():
        abort(403)

    file = request.files.get("document")

    if not file or not file.filename:
        flash("Please select a document.", "error")
        return redirect(url_for("dashboard"))

    storage_key, original_name = save_uploaded_file(file)

    if not storage_key:
        flash("Invalid file type.", "error")
        return redirect(url_for("dashboard"))

    file_path = os.path.join(private_folder(), storage_key)

    try:
        document = Document(
            owner_id=current_user.id,
            title=original_name,
            storage_key=storage_key,
            mime_type=file.mimetype,
            file_size=os.path.getsize(file_path)
        )

        db.session.add(document)
        db.session.flush()

        log_event(
            document.id,
            "DOCUMENT_UPLOAD",
            "SUCCESS",
            f"Document uploaded: {original_name}"
        )

        db.session.commit()

        flash("Document uploaded successfully!", "success")

    except Exception:
        db.session.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        current_app.logger.exception("Document upload failed")
        flash("Document upload failed.", "error")

    return redirect(url_for("dashboard"))


# OWNER REPLACE DOCUMENT
@owner.route("/replace/<int:document_id>", methods=["POST"])
@login_required
def replace_document(document_id):

    if not is_owner():
        abort(403)

    document = Document.query.filter_by(
        id=document_id,
        owner_id=current_user.id
    ).first_or_404()

    file = request.files.get("document")

    if not file or not file.filename:
        flash("Please select a replacement file.", "error")
        return redirect(url_for("dashboard"))

    new_key, original_name = save_uploaded_file(file)

    if not new_key:
        flash("Invalid file type.", "error")
        return redirect(url_for("dashboard"))

    new_path = os.path.join(private_folder(), new_key)
    old_key = document.storage_key
    old_path = os.path.join(private_folder(), old_key)

    try:
        document.title = original_name
        document.storage_key = new_key
        document.mime_type = file.mimetype
        document.file_size = os.path.getsize(new_path)

        log_event(
            document.id,
            "DOCUMENT_UPDATED",
            "SUCCESS",
            f"Document replaced with '{original_name}'."
        )

        db.session.commit()

        if os.path.exists(old_path):
            os.remove(old_path)

        flash("Document replaced successfully!", "success")

    except Exception:
        db.session.rollback()

        if os.path.exists(new_path):
            os.remove(new_path)

        current_app.logger.exception("Document replacement failed")
        flash("Document replacement failed.", "error")

    return redirect(url_for("dashboard"))


# OWNER SHARE DOCUMENT
@owner.route("/share", methods=["POST"])
@login_required
def share_document():

    if not is_owner():
        abort(403)

    document_id = request.form.get("document_id", type=int)
    user_id = request.form.get("user_id", type=int)
    access_level = (
        request.form.get("access_level", "READ")
        .strip()
        .upper()
    )

    if access_level not in {"READ", "EDIT"}:
        flash("Invalid permission type.", "error")
        return redirect(url_for("dashboard"))

    document = Document.query.filter_by(
        id=document_id,
        owner_id=current_user.id
    ).first()

    viewer = User.query.filter_by(
        id=user_id,
        role="VIEWER",
        is_active=True
    ).first()

    if not document or not viewer:
        flash("Invalid document or viewer.", "error")
        return redirect(url_for("dashboard"))

    permission = DocumentPermission.query.filter_by(
        document_id=document_id,
        user_id=user_id
    ).first()

    try:
        if permission:
            old_level = permission.access_level
            permission.access_level = access_level
            permission.is_active = True

            action = (
                "DOCUMENT_SHARED"
                if not old_level
                else "DOCUMENT_ACCESS_UPDATED"
            )
        else:
            permission = DocumentPermission(
                document_id=document_id,
                user_id=user_id,
                access_level=access_level,
                granted_by=current_user.id,
                is_active=True
            )

            db.session.add(permission)
            action = "DOCUMENT_SHARED"

        log_event(
            document.id,
            action,
            "SUCCESS",
            f"Access {access_level} granted to {viewer.email}."
        )

        db.session.commit()

        flash(
            f"{access_level} permission granted successfully!",
            "success"
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Sharing failed")
        flash("Unable to share document.", "error")

    return redirect(url_for("dashboard"))


# OWNER REVOKE ACCESS
@owner.route("/revoke/<int:permission_id>", methods=["POST"])
@login_required
def revoke_access(permission_id):

    if not is_owner():
        abort(403)

    permission = (
        DocumentPermission.query
        .join(Document)
        .filter(
            DocumentPermission.id == permission_id,
            Document.owner_id == current_user.id,
            DocumentPermission.is_active.is_(True)
        )
        .first_or_404()
    )

    try:
        permission.is_active = False

        log_event(
            permission.document_id,
            "DOCUMENT_ACCESS_REVOKED",
            "SUCCESS",
            f"Access revoked for user ID {permission.user_id}."
        )

        db.session.commit()

        flash("Document access revoked.", "success")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Revoke failed")
        flash("Unable to revoke access.", "error")

    return redirect(url_for("dashboard"))


# DOWNLOAD DOCUMENT
@owner.route("/download/<int:document_id>")
@login_required
def download_document(document_id):

    document = Document.query.get_or_404(document_id)

    if is_owner():

        if document.owner_id != current_user.id:
            log_event(
                document.id,
                "UNAUTHORIZED_DOWNLOAD",
                "DENIED",
                "OWNER attempted to download another owner's document."
            )
            db.session.commit()
            abort(403)

    elif is_viewer():

        permission = DocumentPermission.query.filter_by(
            document_id=document.id,
            user_id=current_user.id,
            is_active=True
        ).first()

        if not permission or permission.access_level not in {"READ", "EDIT"}:
            log_event(
                document.id,
                "UNAUTHORIZED_DOWNLOAD",
                "DENIED",
                "VIEWER attempted download without active permission."
            )
            db.session.commit()
            abort(403)

    else:
        abort(403)

    file_path = os.path.join(
        private_folder(),
        document.storage_key
    )

    # DIAGNOSTIC LOG: Check whether uploaded file exists
    if not os.path.isfile(file_path):
        current_app.logger.error(
            "DOWNLOAD FILE MISSING: document_id=%s",
            document.id
        )
        abort(404)

    log_event(
        document.id,
        "DOCUMENT_DOWNLOAD",
        "SUCCESS",
        f"Document downloaded: {document.title}"
    )

    db.session.commit()

    return send_from_directory(
        private_folder(),
        document.storage_key,
        as_attachment=True,
        download_name=document.title
    )


# VIEWER UPLOAD EDITED DOCUMENT
@owner.route("/edit-upload/<int:document_id>", methods=["POST"])
@login_required
def upload_edited_version(document_id):

    if not is_viewer():
        abort(403)

    document = Document.query.get_or_404(document_id)

    permission = DocumentPermission.query.filter_by(
        document_id=document.id,
        user_id=current_user.id,
        access_level="EDIT",
        is_active=True
    ).first()

    if not permission:
        log_event(
            document.id,
            "UNAUTHORIZED_EDIT",
            "DENIED",
            "VIEWER attempted edit upload without active EDIT permission."
        )

        db.session.commit()
        abort(403)

    file = request.files.get("document")

    if not file or not file.filename:
        flash("Please select your edited document.", "error")
        return redirect(url_for("dashboard"))

    storage_key, original_name = save_uploaded_file(file)

    if not storage_key:
        flash("Invalid file type.", "error")
        return redirect(url_for("dashboard"))

    file_path = os.path.join(private_folder(), storage_key)

    try:
        latest_version = (
            db.session.query(db.func.max(DocumentVersion.version_number))
            .filter_by(document_id=document.id)
            .scalar()
        )

        next_version = (latest_version or 0) + 1

        version = DocumentVersion(
            document_id=document.id,
            editor_id=current_user.id,
            version_number=next_version,
            title=original_name,
            storage_key=storage_key,
            mime_type=file.mimetype,
            file_size=os.path.getsize(file_path)
        )

        db.session.add(version)

        log_event(
            document.id,
            "DOCUMENT_EDITED",
            "SUCCESS",
            f"Version {next_version} uploaded by {current_user.email}: {original_name}"
        )

        db.session.commit()

        flash(
            f"Edited document uploaded successfully! Version {next_version}.",
            "success"
        )

    except Exception:
        db.session.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        current_app.logger.exception("Edited version upload failed")
        flash("Unable to upload edited document.", "error")

    return redirect(url_for("dashboard"))


# DOWNLOAD A PARTICULAR EDITED VERSION
@owner.route("/version-download/<int:version_id>")
@login_required
def download_version(version_id):

    version = DocumentVersion.query.get_or_404(version_id)

    document = Document.query.get_or_404(version.document_id)

    if is_owner():

        if document.owner_id != current_user.id:
            abort(403)

    elif is_viewer():

        permission = DocumentPermission.query.filter_by(
            document_id=document.id,
            user_id=current_user.id,
            is_active=True
        ).first()

        if not permission or permission.access_level not in {"READ", "EDIT"}:
            abort(403)

    else:
        abort(403)

    file_path = os.path.join(
        private_folder(),
        version.storage_key
    )

    if not os.path.isfile(file_path):
        abort(404)

    log_event(
        document.id,
        "DOCUMENT_VERSION_DOWNLOAD",
        "SUCCESS",
        f"Version {version.version_number} downloaded."
    )

    db.session.commit()

    return send_from_directory(
        private_folder(),
        version.storage_key,
        as_attachment=True,
        download_name=version.title
    )
