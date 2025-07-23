def user_city(request):
  city = None
  if request.user.is_authenticated and hasattr(request.user, 'profile'):
    city = request.user.profile.city
  return {'user_city': city}