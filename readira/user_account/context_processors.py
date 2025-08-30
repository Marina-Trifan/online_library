def user_city(request):
    """
    Context processor that injects the authenticated user's city into the template context.
    Args:
        request (HttpRequest): The current HTTP request object.
    Returns:
        dict: A dictionary containing the key 'user_city' with the user's city as value,
              or an empty string if the user is not authenticated or has no city set.
    """
    city = ''
    if request.user.is_authenticated:
        city = getattr(request.user, 'city', '')
    return {'user_city': city}