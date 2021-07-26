from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb import settings

from .models import User
from .permissions import IsAdmin
from .serializers import (ConfirmationCodeSerializer, EmailSerializer,
                          UserSerializer)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirmation_code_sender(request):
    serializer = EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    username = serializer.data['username']
    user = User.objects.get_or_create(email=email, username=username)[0]
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Ваш персональный код',
        from_email=settings.DEFAULT_FROM_EMAIL,
        message=f'Ваш код: {confirmation_code}.',
        recipient_list=[email],
        fail_silently=False,
    )
    return Response(
        {'message': f'Код отправлен на почту: {email}'},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_code = request.POST.get('confirmation_code')
    email = request.POST.get('email')
    if confirmation_code is None:
        return Response("Введите confirmation_code")
    if email is None:
        return Response("Введите email")
    token_check = default_token_generator.check_token(email, confirmation_code)
    if token_check is True:
        user = get_object_or_404(User, email=email)
        refresh = RefreshToken.for_user(user)
        return Response(f'Ваш токен:{refresh.access_token}')
    return Response('Неправильный confirmation_code')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        url_path='me',
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
