# TrustVault – AI Usage and Development Log

## Project Overview
TrustVault is a secure document-sharing application developed using Python Flask and MySQL.

The goal is to ensure that only authorized users can access shared documents and that important activities are recorded in an audit log.

## Technologies Used
- Python
- Flask
- MySQL
- Flask-SQLAlchemy
- Flask-Login
- HTML, CSS and JavaScript
- Git and GitHub

## AI Assistance
AI assistance was used for:
- Understanding Flask application structure.
- Writing and reviewing Python code.
- Implementing authentication and role-based access.
- Debugging errors.
- Understanding database models and relationships.
- Improving the user interface.

## Development Decisions and Corrections
- All newly registered users must receive the VIEWER role by default.
- Admin privileges must depend on the user's actual database role, not merely on selecting Admin during login.
- A non-admin user must be denied admin access even if the correct admin security code is entered.
- Unauthorized admin access attempts should be recorded in the audit log.
- Existing database tables and records must be preserved.
- Private documents must not be stored in the public static folder.

## Current Development Status
- Flask application structure: Implemented.
- Database configuration: Implemented.
- User registration and login: Implemented.
- Role-based dashboards: Implemented.
- Admin access verification: Implemented.
- Document upload backend: Initial implementation completed; integration and testing pending.
- Secure document download: Pending.
- Document sharing and permission revocation: Pending.
- Complete audit trail verification: Pending.
- Deployment: Pending.

## Testing and Learning
I am testing each feature locally and checking the generated code to understand how it works. Any AI-generated mistakes or changes discovered during testing will be recorded here with the correction made.

## Important Note
This project is being developed and tested step by step. Features will only be marked complete after successful testing.