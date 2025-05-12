from rest_framework_simplejwt.tokens import RefreshToken

def generate_tokens_for_user(user):
    """
    Generate custom tokens with additional claims for the given user.
    """
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role  # Add custom claims
    refresh['permissions'] = user.get_permissions()  # Include dynamic permissions

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
