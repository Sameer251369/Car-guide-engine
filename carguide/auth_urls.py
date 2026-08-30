from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active or not user.is_staff:
        return Response({'detail': 'Invalid admin credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    login(request, user)
    return Response({
        'message': 'Login successful.',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
        },
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_logout(request):
    logout(request)
    return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_token(request):
    # Return the token in JSON so a Vercel (cross-origin) client can send X-CSRFToken.
    return Response({'csrfToken': get_token(request)})


@api_view(['GET'])
def admin_me(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'is_staff': request.user.is_staff,
        }
    }, status=status.HTTP_200_OK)


urlpatterns = [
    path('csrf/', csrf_token, name='csrf-token'),
    path('login/', admin_login, name='admin-login'),
    path('logout/', admin_logout, name='admin-logout'),
    path('me/', admin_me, name='admin-me'),
]
