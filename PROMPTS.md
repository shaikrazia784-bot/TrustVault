# TrustVault – AI Usage and Development Log

## 1. Project Overview

TrustVault is a secure document-sharing application developed using Python Flask and MySQL/TiDB.

The main objective is to ensure that documents are accessible only to authorized users while maintaining a reliable audit trail of important activities.

The application supports role-based access control, document ownership, permission-based sharing, document version management, database-backed file storage and audit logging.

This document describes how AI assistance was used during development, the issues identified, the corrections made and the testing performed.

## 2. Technologies Used

- Python 3.12
- Flask
- Flask-SQLAlchemy
- Flask-Login
- MySQL / TiDB
- HTML, CSS and JavaScript
- Git and GitHub
- Render

## 3. AI-Assisted Development Log

### Entry 1 – Authentication and Admin Authorization

**Date:** 2026-11-07

**What I asked AI:**

Help implement secure login and role-based authorization. Selecting Admin during login or entering an admin security code must not grant administrator access unless the authenticated account actually has the ADMIN role in the database.

**What AI produced:**

Authentication and role-checking logic, admin route restrictions and unauthorized access logging.

**Issue identified:**

A login selection or correct security code alone must not be treated as proof of administrator authorization.

**My correction and verification:**

I required administrator access to depend on the authenticated user's actual database role. I tested a VIEWER account attempting Admin login with the correct security code. Access was denied and the attempt was recorded in the audit log.

**Result:** Unauthorized admin access test passed.

**Related commit:**

https://github.com/shaikrazia784-bot/TrustVault/commit/ba50e4f

### Entry 2 – Default Roles and Owner Promotion

**Date:** 2026-11-07

**What I asked AI:**

Implement a role model in which new registrations receive VIEWER by default and only an ADMIN can promote selected users to OWNER.

**What AI produced:**

Registration role handling and administrator-controlled role promotion logic.

**Issue identified:**

Ordinary users must not be able to assign themselves privileged roles during registration.

**My correction and verification:**

I retained VIEWER as the default registration role and restricted OWNER promotion to administrators. I tested new registration and ADMIN promotion of a user to OWNER.

**Result:** Default VIEWER registration and ADMIN promotion tests passed.

**Related commit:**

https://github.com/shaikrazia784-bot/TrustVault/commit/ba50e4f

### Entry 3 – Document Permissions and Version Management

**Date:** 2026-11-07

**What I asked AI:**

Implement document sharing where owners can grant READ or EDIT permissions. VIEWER users with READ access should be able to download but not edit. New edited documents must be stored as separate versions.

**What AI produced:**

Document-sharing routes, permission checks, revocation and version-management functionality.

**Issue identified:**

READ users must not be allowed to edit documents, and revoked permissions must no longer grant access.

**My correction and verification:**

I tested owner upload, sharing with a VIEWER, viewer download, permission revocation and an EDIT user's new-version upload. The new version appeared as Version 1.

**Result:** Upload, sharing, download, revocation and edited-version upload tests passed. Original-document preservation should be independently checked before claiming that specific behavior as verified.

**Related commit:**

https://github.com/shaikrazia784-bot/TrustVault/commit/ba50e4f

### Entry 4 – Audit Trail and Tampering Detection

**Date:** 2026-11-07

**What I asked AI:**

Implement audit logging for important document activities and use SHA-256 hash chaining to help detect modifications to historical audit records.

**What AI produced:**

Audit-event logging, hash-chain verification logic and a tampering simulation test.

**Issue identified:**

Recording events alone is insufficient. The audit verification process must also detect changes to recorded events.

**My correction and verification:**

I reviewed the verification approach and executed the tampering test using:

`python -m pytest -v test_audit_tampering.py`

**Test result:**

`1 passed in 4.85s`

**Result:** Audit tampering simulation test passed.

**Related commit:**

https://github.com/shaikrazia784-bot/TrustVault/commit/ba50e4f

### Entry 5 – Persistent Document Storage

**Date:** 2026-11-07

**What I asked AI:**

Fix document downloads on the deployed Render application. Files stored only on the hosting server's local filesystem were not persistent across restarts or deployments.

**What AI produced:**

A database-backed storage approach using binary columns for document and document-version contents, together with database-based download handling.

**Issue identified:**

The Render filesystem is ephemeral, so previously uploaded documents could become unavailable after a restart or deployment.

**My correction and verification:**

I updated the document models and upload/download routes to store file contents in database binary columns. I also restored existing document records and tested downloads.

**Result:** PDF, DOCX, JPG and PNG upload/download workflows were successfully tested.

**Related commit:**

https://github.com/shaikrazia784-bot/TrustVault/commit/6513bca

### Entry 6 – Production Deployment and Debugging

**Date:** 2026-11-07

**What I asked AI:**

Help deploy TrustVault on Render using Gunicorn and troubleshoot production issues related to application startup, database connectivity and document downloads.

**What AI produced:**

Deployment configuration guidance, Gunicorn setup, diagnostic logging and debugging suggestions for production errors.

**Issue identified:**

The application worked locally, but production deployment introduced additional challenges, including startup configuration, database connection errors and document download failures.

**My correction and verification:**

I configured Gunicorn for production, reviewed Render deployment logs, investigated download errors and corrected the document storage approach to use database-backed binary storage.

I verified that the deployed application opened and that document upload and download workflows worked after the storage correction.

**Result:** Render deployment is live and the tested document workflows are working.

**Related commits:**

- https://github.com/shaikrazia784-bot/TrustVault/commit/ec70e53
- https://github.com/shaikrazia784-bot/TrustVault/commit/ac9a4ea
- https://github.com/shaikrazia784-bot/TrustVault/commit/6513bca

## 4. Important Security Decisions

- New registrations receive the VIEWER role by default.
- Only ADMIN users can promote users to OWNER.
- Admin authorization depends on the authenticated user's database role.
- A correct admin security code alone cannot grant administrator access.
- VIEWER users can access only documents shared with them.
- READ permission allows downloading but not editing.
- EDIT permission is granted by the document owner.
- Owners can revoke previously granted permissions.
- Document updates are stored as separate versions.
- Unauthorized access attempts are recorded in the audit trail.
- Existing database tables and records were preserved during file-storage changes.

## 5. Implemented Features and Testing

| Feature | Test Status |
|---|---|
| User registration and login | Tested |
| Default VIEWER registration | Tested |
| Admin authorization | Tested |
| ADMIN promotion to OWNER | Tested |
| OWNER document upload | Tested |
| Document download | Tested |
| READ and EDIT permissions | Tested |
| Permission revocation | Tested |
| Edited-version upload | Tested |
| Audit event visibility | Checked |
| SHA-256 tampering simulation | Passed |
| PDF upload and download | Tested |
| DOCX upload and download | Tested |
| JPG upload and download | Tested |
| PNG upload and download | Tested |
| Database-backed file storage | Tested |

## 6. Audit Trail Design

TrustVault records important activities, including:

- Document uploads and downloads.
- Document updates and version uploads.
- Document sharing and permission changes.
- Permission revocation.
- Unauthorized access attempts.

A SHA-256 hash-chain mechanism links audit events using previous and current event hashes. The tampering simulation test was executed successfully.

This mechanism helps detect modifications during verification. It should not be considered protection against every possible privileged database-level attack.

## 7. Development Approach and Lessons Learned

The project was developed incrementally rather than as a single generated solution.

My development approach included:

1. Understanding user roles and security requirements.
2. Implementing authentication and authorization.
3. Testing authorized and unauthorized access scenarios.
4. Implementing document sharing and version management.
5. Reviewing audit events and hash verification.
6. Debugging deployment-specific storage issues.
7. Retesting affected functionality after corrections.

An important lesson was that a feature appearing to work is not sufficient. Authorization must be tested using different user roles, and document access must be verified after permission changes.

AI assistance helped accelerate implementation and debugging, but its suggestions were reviewed and tested rather than accepted blindly.

## 8. Deployment and Submission Status

- Live application: https://trustvault-df6q.onrender.com
- GitHub repository: https://github.com/shaikrazia784-bot/TrustVault
- Render deployment: Live.
- Database-backed document storage: Implemented and tested.
- Final repository visibility, secret-file review, README, THREATS.md and submission-form checks: Pending.

## 9. Transparency Statement

AI tools were used during development for code assistance, debugging, implementation suggestions and documentation.

This log summarizes the development discussions and actual testing evidence available. It does not claim that AI independently built or verified the entire application. Features that have not been tested are identified as pending rather than described as completed.