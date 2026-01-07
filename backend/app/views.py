from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serielizer import ComentariosSerializer, UserSearchSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_list_or_404, get_object_or_404

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView

from django.contrib.auth.models import User
from .models import Comentarios, Perfil
from .models import Archivo
from .models import Like
from django.db.models import Q
from .models import SolicitudAmistad
from .serielizer import ArchivoSerializer
from .serielizer import PerfilSerializer

from django.contrib.auth import authenticate

from .forms import subir
from rest_framework.generics import ListAPIView

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'token': token.key
        }, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': token.key
            }, status=status.HTTP_201_CREATED)

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
        if form.is_valid():
            form.instance.usuario = request.user
            form.save()
            return Response({'mensaje':'archivo subido'},status=200)
        return Response({'error': 'No se envió ningún archivo'}, status=400)

class UserPostListView(ListAPIView):
    serializer_class = ArchivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Archivo.objects.filter(usuario=user).order_by('-fecha_subida')
    
class ToggleLikeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, archivo_id):
        archivo = get_object_or_404(Archivo, id=archivo_id)

        like, created = Like.objects.get_or_create(
            usuario=request.user,
            archivo=archivo
        )

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        likes_count = Like.objects.filter(archivo=archivo).count()

        return Response({
            'liked': liked,
            'likes_count': likes_count
        }, status=status.HTTP_200_OK)
    

class CreateComentarioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, archivo_id):
        serializer = ComentariosSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                usuario=request.user,
                archivo_id=archivo_id
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ComentariosPostView(ListAPIView):
    serializer_class = ComentariosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        archivo_id = self.kwargs['archivo_id']
        return Comentarios.objects.filter(archivo_id=archivo_id).order_by('-fecha_comentario')
    
class UserSearchView(ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')

        if not query:
            return User.objects.none()

        return User.objects.filter(
            username__icontains=query
        ).exclude(id=self.request.user.id)[:10]
    
class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        to_user = get_object_or_404(User, id=user_id)

        if to_user == request.user:
            return Response(
                {'error': 'No puedes enviarte solicitud a ti mismo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if SolicitudAmistad.objects.filter(
            remitente=request.user,
            destinatario=to_user,
            aceptada='pendiente'
        ).exists():
            return Response(
                {'error': 'Ya enviaste una solicitud'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if SolicitudAmistad.objects.filter(
            aceptada='aceptada'
        ).filter(
            Q(remitente=request.user, destinatario=to_user) |
            Q(remitente=to_user, destinatario=request.user)
        ).exists():
            return Response(
                {'error': 'Ya son amigos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        SolicitudAmistad.objects.create(
            remitente=request.user,
            destinatario=to_user,
            aceptada='pendiente'
        )

        return Response(
            {'message': 'Solicitud enviada'},
            status=status.HTTP_201_CREATED
        )
    

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
