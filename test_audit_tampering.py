
from app import app
from models import AuditLog
from verify_audit_chain import calculate_hash


def test_tampering():

    with app.app_context():

        event = (
            AuditLog.query
            .filter(AuditLog.event_hash.isnot(None))
            .order_by(AuditLog.id.asc())
            .first()
        )

        if event is None:
            print("No hashed audit record found.")
            return

        original_details = event.details
        original_hash = event.event_hash

        print("\nTRUSTVAULT TAMPERING DETECTION TEST")
        print("-----------------------------------")

        print("Testing Audit ID:", event.id)

        # Temporarily change details in memory only
        event.details = (original_details or "") + " TAMPERED"

        tampered_hash = calculate_hash(event)

        # Restore the original value in memory
        event.details = original_details

        if tampered_hash != original_hash:
            print("Original Hash: ", original_hash)
            print("Modified Hash: ", tampered_hash)
            print("\nRESULT: TAMPERING DETECTED!")
        else:
            print("\nRESULT: TAMPERING NOT DETECTED!")


if __name__ == "__main__":
    test_tampering()
