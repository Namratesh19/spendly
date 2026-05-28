---
# Spec: Date Filter for Profile Page

## Overview
Allow users to filter their spending data on the profile page by a specific date range. This allows users to see how much they spent in a particular month, week, or custom period.

## Depends on
- 05-profile-backend

## Routes
- `GET /profile` — Modified to accept `start_date` and `end_date` query parameters — logged-in

## Database changes
No database changes.

## Templates
- **Modify:** `templates/profile.html` — Add a date filter form (two date inputs and a filter button).

## Files to change
- `app.py`
- `database/queries.py`
- `templates/profile.html`

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Date filtering should apply to:
    - Total spent
    - Transaction count
    - Top category
    - Category breakdown
    - Transaction list
- If no dates are provided, default to all-time data.
- Handle invalid date formats gracefully.

## Definition of done
- [ ] Profile page has a date filter section with "Start Date" and "End Date" inputs.
- [ ] Clicking "Filter" updates the summary stats to reflect only expenses within the selected range.
- [ ] Category breakdown only includes expenses within the selected range.
- [ ] Transaction list only shows expenses within the selected range.
- [ ] Clearing dates or submitting an empty filter resets the view to all-time data.
- [ ] The filter state is preserved in the URL as query parameters.
---
