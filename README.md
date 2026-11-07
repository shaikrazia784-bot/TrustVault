# TrustVault – Secure Document Sharing with Audit Trail

## Project Overview

TrustVault is a secure document-sharing web application built using Python Flask and MySQL-compatible database technology (MySQL/TiDB).

It helps users securely upload, share, download and manage documents with role-based access control. Important user activities are recorded in an audit trail to provide accountability and traceability.

**Live Application:** https://trustvault-df6q.onrender.com

## Key Features

### 1. User Authentication
- User registration and login.
- Secure password hashing.
- Role-based access control.
- New registrations receive the VIEWER role by default.

### 2. Role-Based Access

| Role | Responsibilities |
|---|---|
| ADMIN | Manage users and promote selected users to OWNER. |
| OWNER | Upload documents and manage sharing permissions. |
| VIEWER | Access documents shared with them. |

### 3. Document Management
- Upload PDF, DOCX, JPG, JPEG and PNG files.
- Secure document downloads.
- Document and version management.
- Store document contents in database binary storage instead of relying on ephemeral hosting storage.

### 4. Document Sharing
- Share documents with authorized users.
- Grant READ or EDIT permissions.
- Revoke previously granted permissions.
- Prevent unauthorized document access through server-side permission checks.

### 5. Document Version Management
- Users with EDIT permission can upload edited versions.
- New versions are stored separately.
- Version information is maintained in the database.

### 6. Audit Trail and Security
- Record important document activities.
- Record successful and denied access attempts.
- Maintain a SHA-256 hash-chain for audit events.
- Verify audit-chain integrity and detect tampering through a test.

## Technology Stack

- Backend: Python, Flask
- Database: MySQL / TiDB
- ORM: Flask-SQLAlchemy
- Authentication: Flask-Login
- Frontend: HTML, CSS, JavaScript
- Version Control: Git and GitHub
- Production Hosting: Render
- Production Server: Gunicorn

## Installation and Setup

### Prerequisites

- Python 3
- MySQL Server or compatible database
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/shaikrazia784-bot/TrustVault.git
cd TrustVault
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure the Database

Create the database:

```sql
CREATE DATABASE trustvault_db;
```

Configure the database connection and SECRET_KEY using the environment variables expected by `config.py`.

Use your own database credentials. Never upload `.env`, passwords, private keys or other secrets to GitHub.

Make sure the required database tables and columns are initialized before running the application.

### Step 5: Run the Application

```bash
python app.py
```

Open the application in your browser:

http://127.0.0.1:5000/

## Production Deployment

TrustVault is deployed on Render.

Live URL:

https://trustvault-df6q.onrender.com

The production application uses Gunicorn and a persistent database connection. Uploaded document contents are stored in database binary columns to avoid dependence on Render's ephemeral local filesystem.

## Audit Verification

Run the audit-chain verification script:

```bash
python verify_audit_chain.py
```

This checks the integrity of the stored hash-linked audit events.

The tampering simulation test can be executed using:

```bash
python -m pytest -v test_audit_tampering.py
```

## Testing

The following functionality was tested during development:

- User registration and authentication.
- Default VIEWER role assignment.
- Admin authorization and OWNER promotion.
- Unauthorized admin access denial.
- Document upload and download.
- PDF, DOCX, JPG and PNG upload/download.
- READ and EDIT permission management.
- Permission revocation.
- Edited document version uploads.
- Audit event recording.
- Audit-chain tampering simulation.

## Project Documentation

- [PROMPTS.md](PROMPTS.md) – AI assistance, development decisions, corrections and testing history.
- [THREATS.md](THREATS.md) – Security threats, mitigations, verification and future improvements.

## Security Considerations

- Private uploaded documents should not be stored in public static folders.
- Environment secrets must remain outside source control.
- Server-side authorization checks are required for protected document operations.
- Audit hash chaining helps detect modifications but does not prevent every possible privileged database-level attack.
- Additional security hardening and independent testing are recommended before handling highly sensitive production documents.

## Project Status

Core TrustVault application features have been implemented and tested.

The application is deployed and accessible through Render. PDF, DOCX, JPG and PNG upload/download workflows have been tested.

The GitHub repository is maintained as a private repository during the submission period, pending clarification of the submission instructions regarding repository visibility.

---

**TrustVault – Secure Documents. Controlled Access. Trusted Audit Trail.**