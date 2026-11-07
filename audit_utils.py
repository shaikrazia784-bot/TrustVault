
import hashlib
import json

from extensions import db
from models import AuditLog


def log_audit_event(
    actor_id,
    action,
    outcome,
    details,
    document_id=None
):
    """
    Create an audit event and connect it to the previous
    hashed audit event using SHA-256.

    This function does not commit.
    The calling route must commit the transaction.
    """

    # Get the latest audit event that already has a hash
    previous_event = AuditLog.query.filter(
        AuditLog.event_hash.isnot(None)
    ).order_by(
        AuditLog.id.desc()
    ).first()

    # First hashed event starts with 64 zeroes
    previous_hash = (
        previous_event.event_hash
        if previous_event
        else "0" * 64
    )

    # Create the audit record
    event = AuditLog(
        actor_id=actor_id,
        document_id=document_id,
        action=action,
        outcome=outcome,
        details=details,
        previous_hash=previous_hash
    )

    db.session.add(event)

    # Generate the database ID before calculating the hash
    db.session.flush()

    # Prepare consistent data for hashing
    event_data = {
        "id": event.id,
        "actor_id": event.actor_id,
        "document_id": event.document_id,
        "action": event.action,
        "outcome": event.outcome,
        "details": event.details,
        "previous_hash": event.previous_hash
    }

    event_json = json.dumps(
        event_data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    # Generate SHA-256 hash
    event.event_hash = hashlib.sha256(
        event_json.encode("utf-8")
    ).hexdigest()

    return event
