# TrustVault – Security Threat Model

## 1. Introduction

TrustVault is a secure document-sharing application designed to protect confidential documents such as salary letters, contracts, drawings and audit papers.

The main security objective is to ensure that only authorized users can access shared documents and that important activities are recorded in an audit trail.

This document identifies potential security threats, their impact and the security controls implemented or considered in TrustVault.

## 2. Assets to Protect

The important assets in TrustVault are:

- User account credentials.
- User roles and permissions.
- Uploaded documents and document versions.
- Document ownership information.
- Sharing and access-control records.
- Audit logs and hash-chain information.
- Database credentials and application secrets.

## 3. Potential Threats and Mitigations

### Threat 1 – Unauthorized Document Access

**Threat:** An unauthorized user may try to access another user's private document by guessing or changing a document ID.

**Impact:** Confidential documents could be exposed.

**Mitigation:**

- Require authentication before accessing protected routes.
- Check document ownership or active sharing permission before allowing access.
- Restrict VIEWER users to documents shared with them.
- Do not rely only on hidden buttons or frontend restrictions.

**Verification:** Tested owner upload, shared viewer download and permission revocation workflows.

### Threat 2 – Privilege Escalation

**Threat:** A VIEWER may try to obtain OWNER or ADMIN privileges by changing login selections or submitting manipulated requests.

**Impact:** An ordinary user could gain unauthorized administrative or document-management capabilities.

**Mitigation:**

- New registrations default to VIEWER.
- Only ADMIN users can promote selected users to OWNER.
- Admin authorization checks the authenticated user's actual database role.
- A correct admin security code alone does not grant ADMIN access.

**Verification:** Tested VIEWER registration, ADMIN promotion and unauthorized Admin login attempts.

### Threat 3 – Unauthorized Document Modification

**Threat:** A user with READ permission may attempt to modify or upload a new version of a document.

**Impact:** Confidential documents could be modified without owner authorization.

**Mitigation:**

- READ permission allows downloading only.
- EDIT permission must be explicitly granted by the document owner.
- Server-side permission checks must protect document update routes.
- Document updates are handled through separate document versions.

**Verification:** Tested READ and EDIT permission workflows and new-version upload.

### Threat 4 – Permission Revocation Bypass

**Threat:** A user may attempt to access a document even after the owner revokes sharing permission.

**Impact:** A previously authorized user could continue accessing confidential information.

**Mitigation:**

- Maintain active/inactive permission records.
- Check the current permission status during protected document requests.
- Reject access when permission is revoked.

**Verification:** Tested permission revocation and subsequent access restrictions.

### Threat 5 – Audit Log Tampering

**Threat:** An attacker or unauthorized database user may attempt to modify historical audit records.

**Impact:** Evidence of unauthorized access or document activity could be altered.

**Mitigation:**

- Record important activities in the audit log.
- Use SHA-256 hash chaining with previous and current event hashes.
- Verify the hash chain to detect changes to recorded events.

**Verification:**

Executed:

`python -m pytest -v test_audit_tampering.py`

Result: `1 passed in 4.85s`

**Limitation:** Hash chaining helps detect modifications during verification but does not prevent every possible privileged database-level attack.

### Threat 6 – Unauthorized File Download

**Threat:** An attacker may attempt to download files directly using a guessed URL or document identifier.

**Impact:** Sensitive documents may be exposed.

**Mitigation:**

- Protect download routes with authentication.
- Validate ownership or sharing permission on the server.
- Verify the requested document exists before sending its contents.
- Deny requests from users without valid access.

**Verification:** Tested owner and authorized VIEWER download workflows.

### Threat 7 – Data Loss During Deployment

**Threat:** Uploaded documents stored only on an ephemeral hosting filesystem may disappear after application restarts or deployments.

**Impact:** Users may lose access to previously uploaded documents.

**Mitigation:**

- Store document contents in database binary columns.
- Store document-version contents persistently in the database.
- Retrieve document contents from the database during downloads.

**Verification:** Tested database-backed PDF, DOCX, JPG and PNG upload/download workflows.

### Threat 8 – Credential and Secret Exposure

**Threat:** Database passwords, application secret keys or other credentials may be exposed through source-code commits or public repository access.

**Impact:** Attackers may gain access to application sessions or the database.

**Mitigation:**

- Keep credentials in environment variables.
- Avoid committing `.env` files and private key files.
- Use protected deployment environment settings.
- Review repository contents before making the repository public.

**Verification:** Review secret and configuration files before final submission.

## 4. Security Testing Summary

| Security Check | Status |
|---|---|
| Default VIEWER registration | Tested |
| ADMIN authorization | Tested |
| ADMIN promotion to OWNER | Tested |
| Unauthorized Admin access denial | Tested |
| READ permission download | Tested |
| EDIT permission version upload | Tested |
| Permission revocation | Tested |
| Audit event visibility | Checked |
| Audit tampering simulation | Passed |
| PDF upload and download | Tested |
| DOCX upload and download | Tested |
| JPG upload and download | Tested |
| PNG upload and download | Tested |

## 5. Security Limitations and Future Improvements

The following areas require additional hardening or independent verification:

- Add rate limiting and account lockout protections for repeated failed login attempts.
- Review password hashing configuration and password-reset security.
- Add stronger protection for administrator accounts, such as multi-factor authentication.
- Verify CSRF protection on all state-changing forms.
- Review file-size limits and content validation for uploads.
- Consider storing audit-chain checkpoints outside the application database.
- Conduct independent security testing before production use with highly sensitive documents.
- Review database backup and recovery procedures.

## 6. Conclusion

TrustVault applies authentication, role-based authorization, document-level permissions and audit logging to reduce the risk of unauthorized document access.

The application was tested with different user roles and document permissions. A SHA-256 audit tampering simulation test also passed.

Security is an ongoing process. The threats and mitigations documented here describe implemented controls, observed test results and areas identified for further improvement.