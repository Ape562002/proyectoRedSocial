from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serielizer import UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_list_or_404

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.contrib.auth.models import User
from .models import Perfil
from .serielizer import PerfilSerializer

from django.contrib.auth import authenticate

from .forms import subir

@api_view(['POST'])
def login(request):
    user = get_list_or_404(User, username = request.data['username'])
    
    user = authenticate(username = request.data['username'],password = request.data['password'])

    if not user:
        return Response({"error":"Invalid password"},status=status.HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)

    return Response({"token": token.key, "user":serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def resgister(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        user = User.objects.get(username = serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()

        token = Token.objects.create(user=user)
        return Response({'token':token.key,"user":serializer.data},status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    #serializer = UserSerializer(instance=request.user)
    perfil = Perfil.objects.get(usuario=request.user)
    serializer = PerfilSerializer(instance=perfil)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def simple_uploud(request):
    if request.method == 'POST':
        form = subir(request.POST, request.FILES)
        print(request.user)
        if form.is_valid():
            form.instance.usuario = request.user
            form.save()
            return Response({'mensaje':'archivo subido'},status=200)
        return Response({'error': 'No se envió ningún archivo'}, status=400)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"message":"Logout exitoso"}, status=status.HTTP_200_OK)
    except:
        return Response({"error":"No se encontro un token activo"}, status=status.HTTP_400_BAD_REQUEST)
