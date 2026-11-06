
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


# USER MODEL
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.Enum("ADMIN", "OWNER", "VIEWER"),
        nullable=False,
        default="VIEWER"
    )

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# CATEGORY MODEL
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


# DOCUMENT MODEL
class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=True
    )

    title = db.Column(db.String(200), nullable=False)
    storage_key = db.Column(db.String(255), unique=True, nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.BigInteger, nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    owner = db.relationship("User", foreign_keys=[owner_id])
    category = db.relationship("Category")


# PERMISSION MODEL
class DocumentPermission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    access_level = db.Column(
        db.Enum("READ", "EDIT"),
        nullable=False
    )

    granted_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    document = db.relationship("Document")
    user = db.relationship("User", foreign_keys=[user_id])
    grantor = db.relationship("User", foreign_keys=[granted_by])


# AUDIT LOG MODEL
class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    actor_id = db.Column(db.Integer, nullable=True)
    document_id = db.Column(db.Integer, nullable=True)

    action = db.Column(db.String(50), nullable=False)
    outcome = db.Column(db.String(30), nullable=False)
    details = db.Column(db.Text, nullable=True)

    previous_hash = db.Column(db.String(64), nullable=True)
    event_hash = db.Column(db.String(64), nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )
