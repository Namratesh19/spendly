---
# Spec: Login and Logout

## Overview
This feature implements user authentication, allowing registered users to sign in to their accounts and securely sign out. It transforms the static login page into a functional form that verifies credentials against the database and manages the user's session using Flask's session object.

## Depends on
- 02-registration

## Routes
- `GET /login` — Renders the login form — public
- `POST /login` — Validates credentials, starts session, and redirects to landing/profile — public
- `GET /logout` — Clears the user session and redirects to landing — logged-in

## Database changes
No database changes. Uses existing `users` table.

## Templates
- **Modify:** `templates/login.html` — Add a `<form>` with fields for email and password.
- **Modify:** `templates/base.html` — Add a "Logout" link if the user is logged in, and a "Login/Register" link if they are not.

## Files to change
- `app.py` — Implement `POST /login` and `GET /logout` logic. Use `flask.session`.
- `database/db.py` — Add a helper function `get_user_by_email(email)` to retrieve user data.
- `templates/login.html` — Update the UI to a functional form.
- `templates/base.html` — Add conditional navigation links based on session state.

## Files to create
- None.

## New dependencies
No new dependencies. Uses `werkzeug.security.check_password_hash`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords verified with `werkzeug.security.check_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `flask.session` for session management.
- Ensure a user is redirected to the login page if they try to access a protected route.

## Definition of done
- [ ] `GET /login` renders the login form.
- [ ] Submitting valid credentials logs the user in and redirects them.
- [ ] Submitting invalid credentials shows an error message on the login page.
- [ ] `GET /logout` successfully clears the session and redirects the user to the landing page.
- [ ] The navigation bar in `base.html` correctly toggles between "Login/Register" and "Logout" based on the user's authentication state.
- [ ] Users cannot access the `/logout` route (or it behaves gracefully) if they are not logged in.
---
