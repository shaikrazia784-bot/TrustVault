# TrustVault - Secure Document Sharing with Audit Trail
## Project Overview
TrustVault is a secure document-sharing web application built using Python Flask and MySQL.
It helps users securely upload, share, download and manage documents with role-based access control. Important user activities are recorded in an audit trail to provide accountability and traceability.
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
- Replace existing documents.
- Store private documents outside the public static directory.
### 4. Document Sharing
- Share documents with authorized VIEWER users.
- Grant READ or EDIT permissions.
- Revoke previously granted permissions.
- Prevent unauthorized document access.
### 5. Document Version Management
- VIEWER users with EDIT permission can upload edited versions.
- New versions are stored separately.
- Original documents are preserved during version uploads.
- Version information is stored in MySQL.
### 6. Audit Trail and Security
- Record important document activities.
- Record successful and denied access attempts.
- Maintain a SHA-256 hash-chain for audit events.
- Verify audit-chain integrity using a Python script.
## Technology Stack
- Backend: Python, Flask
- Database: MySQL
- ORM: Flask-SQLAlchemy
- Authentication: Flask-Login
- Frontend: HTML, CSS, JavaScript
- Version Control: Git and GitHub
## Project Structure
```text
TrustVault/
│
├── app.py
├── config.py
├── models.py
├── extensions.py
├── audit_utils.py
├── verify_audit_chain.py
├── requirements.txt
├── PROMPTS.md
├── README.md
├── .gitignore
│
├── auth/
├── admin/
├── owner/
│
├── templates/
├── static/
└── instance/
    └── private_documents/
```
## Installation and Setup

### Prerequisites

- Python 3
- MySQL Server
- MySQL Workbench
- Git

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd TrustVault
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```
### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
### Step 4: Configure MySQL
Create the database in MySQL Workbench:
```sql
CREATE DATABASE trustvault_db;
```
Configure the database connection and SECRET_KEY in your local `.env` file according to `config.py`.
Never upload `.env` or database credentials to GitHub.
### Step 5: Run the Application

python app.py
Open the application in your browser:
http://127.0.0.1:5000/
## Audit Verification
Run the audit-chain verification script:
python verify_audit_chain.py
This checks the integrity of the stored hash-linked audit events.
## Testing
The following functionality was tested locally during development:

- User registration and authentication.
- Role-based access restrictions.
- Document upload, download and replacement.
- READ and EDIT permission management.
- Permission revocation.
- Edited document version uploads.
- Audit event recording.
- Audit-chain verification and tampering simulation.
## Project Documentation
See [PROMPTS.md](PROMPTS.md) for information about AI assistance, development decisions and corrections.
## Security Note
- Private uploaded documents should not be stored in public static folders.
- Environment secrets must remain outside source control.
- Production deployment requires appropriate security configuration, validation and testing.
- The local testing results do not represent production security certification.
## Project Status
Core application features have been implemented and tested locally. Public repository preparation and production deployment are separate remaining submission tasks.
---
TrustVault – Secure Documents. Controlled Access. Trusted Audit Trail.