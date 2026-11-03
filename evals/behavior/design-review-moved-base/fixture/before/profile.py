def profile_response(user):
    return {
        "name": user.name,
        "email": user.email,
        "team": user.team,
    }
