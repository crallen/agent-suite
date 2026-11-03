# Permissions are roles, not profile fields

We removed `can_approve_refunds` from the profile response and granted it as a
role instead. A permission stored on the profile bypasses the role model: it is
not granted, audited, or revoked in one place. New permissions are roles.
