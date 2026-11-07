
import hashlib
import json

from app import app
from models import AuditLog


def calculate_hash(event):
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

    return hashlib.sha256(
        event_json.encode("utf-8")
    ).hexdigest()


def verify_audit_chain():

    with app.app_context():

        events = (
            AuditLog.query
            .filter(AuditLog.event_hash.isnot(None))
            .order_by(AuditLog.id.asc())
            .all()
        )

        if not events:
            print("No hashed audit records found.")
            return

        expected_previous_hash = "0" * 64
        valid_count = 0

        print("\nTRUSTVAULT AUDIT CHAIN VERIFICATION")
        print("-----------------------------------")

        for event in events:

            calculated_hash = calculate_hash(event)

            previous_hash_valid = (
                event.previous_hash == expected_previous_hash
            )

            event_hash_valid = (
                event.event_hash == calculated_hash
            )

            if previous_hash_valid and event_hash_valid:

                print(
                    f"ID: {event.id} | "
                    f"{event.action} | VALID"
                )

                valid_count += 1

            else:

                print(
                    f"ID: {event.id} | "
                    f"{event.action} | INVALID"
                )

                if not previous_hash_valid:
                    print("  Previous hash mismatch!")

                if not event_hash_valid:
                    print("  Event hash mismatch!")

            expected_previous_hash = event.event_hash

        print("-----------------------------------")
        print(f"Total records: {len(events)}")
        print(f"Valid records: {valid_count}")
        print(f"Invalid records: {len(events) - valid_count}")

        if valid_count == len(events):
            print("\nRESULT: AUDIT CHAIN VERIFIED SUCCESSFULLY!")
        else:
            print("\nRESULT: AUDIT CHAIN VERIFICATION FAILED!")


if __name__ == "__main__":
    verify_audit_chain()
