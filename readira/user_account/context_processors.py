def user_city(request):
    city = ''
    if request.user.is_authenticated:
        city = getattr(request.user, 'city', '')
    return {'user_city': city}