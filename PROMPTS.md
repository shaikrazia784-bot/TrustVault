# TrustVault – AI Usage and Development Log

## 1. Project Overview

TrustVault is a secure document-sharing application developed using Python Flask and MySQL.

The main objective is to ensure that only authorized users can access shared documents and that important document activities are recorded in an audit trail.

The application supports role-based access control, secure document storage, document sharing, version management and audit logging.

## 2. Technologies Used

- Python
- Flask
- MySQL
- Flask-SQLAlchemy
- Flask-Login
- HTML, CSS and JavaScript
- Git and GitHub

## 3. AI Assistance

AI assistance was used during development for:

- Understanding Flask application structure and routing.
- Writing and reviewing Python code.
- Implementing authentication and role-based access control.
- Designing database models and relationships.
- Debugging application errors.
- Implementing document upload, download and sharing functionality.
- Implementing document version management.
- Developing audit logging and hash verification.
- Improving the user interface.
- Preparing project documentation.

All generated code was reviewed and tested during development.

## 4. Development Decisions and Corrections

- All newly registered users receive the VIEWER role by default.
- Only ADMIN users can promote selected users to OWNER.
- Admin privileges depend on the actual database role, not merely on selecting Admin during login.
- A non-admin user must be denied admin access even if the correct admin security code is entered.
- Unauthorized admin access attempts are recorded in the audit log.
- Existing database tables and records must be preserved.
- Private documents must not be stored in the public static folder.
- VIEWER users can access only documents shared with them.
- OWNER users can grant and revoke READ or EDIT permissions.
- Edited documents are stored as separate versions without replacing the original document.

## 5. Implemented Features and Testing

- Flask application structure: Implemented.
- Database configuration: Implemented and connection tested.
- User registration and login: Implemented and tested.
- Default VIEWER registration: Tested.
- Role-based dashboards: Implemented.
- Admin access verification: Implemented and tested.
- OWNER document upload: Tested.
- Secure document download: Tested.
- Document replacement: Implemented and tested.
- Document sharing with READ and EDIT permissions: Tested.
- Permission revocation: Tested.
- Unauthorized document download prevention: Tested.
- VIEWER edited-version upload: Tested successfully.
- Document version database storage: Verified.
- Audit logging for document activities: Tested.
- SHA-256 audit hash-chain verification: Tested.
- Audit tampering detection simulation: Tested.

## 6. Audit Trail

The application records important activities, including:

- Document upload and download.
- Document updates.
- Document sharing and permission changes.
- Permission revocation.
- Edited document version uploads.
- Unauthorized access attempts.

A SHA-256 hash-chain mechanism is implemented to help detect changes to recorded audit events.

The audit-chain verification script and a tampering simulation were executed successfully during local testing.

## 7. Development and Testing Approach

The project was developed step by step.

Each major feature was implemented, reviewed and tested locally. Database records and audit logs were checked to verify important operations.

Errors discovered during development were corrected and the affected functionality was tested again.

## 8. Remaining Submission Tasks

- Review and finalize project documentation.
- Prepare the public GitHub repository.
- Verify that private files and credentials are excluded from GitHub.
- Deploy the application to a suitable hosting platform.
- Configure production database and environment variables.
- Perform final testing on the deployed application.

## 9. Important Note

This document reflects the development and testing progress at the time of submission preparation. Local testing results do not by themselves establish production deployment or production security readiness.