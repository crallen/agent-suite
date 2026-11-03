# Accounts

The accounts service owns identity, sessions, and role policy. Other services
decide what a user may do by checking that user's roles, never a profile field.

## Language

- **Profile**: descriptive facts about a user: name, email, team.
- **Role**: a named permission, optionally scoped to one resource.
