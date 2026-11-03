def profile_response(user):
    return {
        "name": user.name,
        "email": user.email,
        "team": user.team,
        # Regions the user can approve refunds in, comma separated.
        "approval_regions": user.approval_regions,
    }
