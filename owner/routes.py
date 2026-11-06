
import os
import uuid

from flask import (
    Blueprint, request, redirect, url_for,
    flash, current_app
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from extensions import db
from models import Document, AuditLog


owner = Blueprint("owner", __name__, url_prefix="/owner")

ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}


def is_owner():
    return (current_user.role or "").strip().lower() == "owner"


@owner.route("/upload", methods=["POST"])
@login_required
def upload_document():

    # Only OWNER can upload documents
    if not is_owner():
        event = AuditLog(
            actor_id=current_user.id,
            action="UNAUTHORIZED_UPLOAD",
            outcome="DENIED",
            details="A non-OWNER user attempted to upload a document."
        )

        db.session.add(event)
        db.session.commit()

        return "Access Denied: Only OWNER can upload documents.", 403

    uploaded_file = request.files.get("document")

    if not uploaded_file or uploaded_file.filename == "":
        flash("Please select a document.", "error")
        return redirect(url_for("dashboard"))

    original_name = secure_filename(uploaded_file.filename)

    if "." not in original_name:
        flash("Invalid file name.", "error")
        return redirect(url_for("dashboard"))

    extension = original_name.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        flash("Only PDF, DOCX, JPG, JPEG and PNG files are allowed.", "error")
        return redirect(url_for("dashboard"))

    # Create private storage folder
    storage_folder = os.path.join(
        current_app.instance_path,
        "private_documents"
    )

    os.makedirs(storage_folder, exist_ok=True)

    # Generate a unique storage name
    storage_key = f"{uuid.uuid4().hex}.{extension}"

    file_path = os.path.join(storage_folder, storage_key)

    try:
        uploaded_file.save(file_path)

        file_size = os.path.getsize(file_path)

        new_document = Document(
            owner_id=current_user.id,
            title=original_name,
            storage_key=storage_key,
            mime_type=uploaded_file.mimetype,
            file_size=file_size
        )

        db.session.add(new_document)

        event = AuditLog(
            actor_id=current_user.id,
            action="DOCUMENT_UPLOAD",
            outcome="SUCCESS",
            details=f"Document '{original_name}' uploaded successfully."
        )

        db.session.add(event)
        db.session.commit()

        flash("Document uploaded successfully!", "success")

    except Exception:
        db.session.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        current_app.logger.exception("Document upload failed")
        flash("Document upload failed. Please try again.", "error")

    return redirect(url_for("dashboard"))
