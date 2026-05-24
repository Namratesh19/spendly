# Spec: Registration

## Overview
This feature implements the user registration process, allowing new users to create an account. It transforms the existing static registration page into a functional form that validates input, hashes passwords, and stores user data in the SQLite database. This is the primary entry point for new users to join the platform.

## Depends on
- 01-database-setup

## Routes
- `GET /register` — Renders the registration form — public
- `POST /register` — Handles form submission, validates input, creates user account, and redirects to login — public

## Database changes
No database changes. Uses existing `users` table.

## Templates
- **Modify:** `templates/register.html` — Add a `<form>` with fields for name, email, and password. Include CSRF protection (if applicable, though not currently in requirements) and error messaging.

## Files to change
- `app.py` — Add `POST /register` route and logic for user creation.
- `database/db.py` — Add a helper function `create_user(name, email, password_hash)` to handle user insertion.
- `templates/register.html` — Update the UI to a functional form.

## Files to create
- None.

## New dependencies
No new dependencies. Uses `werkzeug.security` for password hashing.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate that the email is not already registered; if it is, show a user-friendly error message.
- Ensure input fields are trimmed and basic validation (e.g., non-empty fields, password confirmation check) is performed.

## Definition of done
- [ ] `GET /register` renders the registration form.
- [ ] Submitting the form with valid data creates a new user in the `users` table.
- [ ] Passwords are stored as hashes, not plain text.
- [ ] Attempting to register with an existing email shows an error message and does not create a duplicate.
- [ ] The user is redirected to the login page upon successful registration.
- [ ] Basic validation prevents empty submissions and ensures passwords match.
