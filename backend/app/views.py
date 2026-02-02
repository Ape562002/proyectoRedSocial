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
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser

from django.contrib.auth.models import User
from .models import Comentarios, Perfil
from .models import Archivo
from .models import Like
from django.db.models import Q
from django.db.models import Count, Exists, OuterRef
from .models import SolicitudAmistad
from .serielizer import ArchivoSerializer
from .serielizer import PerfilSerializer
from .serielizer import UserUpdateSerializer
from .serielizer import profileUpdateSerializar
from .serielizer import perfilUsuarioSerializer

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

class PerfilDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        perfil = request.user.perfil
        
        user_data = UserSerializer(user).data
        perfil_data = PerfilSerializer(perfil).data

        return Response({
            'user': user_data,
            'perfil': perfil_data
        }, status=status.HTTP_200_OK)

class PerfilUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self,request):
        user = request.user
        perfil = request.user.perfil

        user_serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        profile_serializer = profileUpdateSerializar(
            perfil,
            data=request.data,
            partial=True
        )

        if user_serializer.is_valid() and profile_serializer.is_valid():
            user_serializer.save()
            profile_serializer.save()
            return Response({
                'user': user_serializer.data,
                'profile': profile_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'user_errors': user_serializer.errors,
            'profile_errors': profile_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

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
    
class perfilUsuarioView(RetrieveAPIView):
    serializer_class = perfilUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Perfil, usuario__id=self.kwargs['user_id'])
    
class PublicacionesUsuarioView(ListAPIView):
    serializer_class = ArchivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']

        return Archivo.objects.filter(
            usuario_id=user_id
        ).annotate(
            likes_count=Count('like'),
            is_liked=Exists(
                Like.objects.filter(
                    usuario=self.request.user,
                    archivo=OuterRef('pk')
                )
            )
        ).order_by('-fecha_subida')
    

class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        from_user = request.user
        to_user = get_object_or_404(User, id=user_id)

        if from_user == to_user:
            return Response(
                {'error': 'No puedes enviarte solicitud a ti mismo'},
                status=400
            )

        # Evitar duplicados
        if SolicitudAmistad.objects.filter(
            remitente=from_user,
            destinatario=to_user
        ).exists():
            return Response(
                {'error': 'Solicitud ya enviada'},
                status=400
            )

        SolicitudAmistad.objects.create(
            remitente=from_user,
            destinatario=to_user
        )

        return Response(
            {'message': 'Solicitud enviada'},
            status=201
        )
    
class FriendshipStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = request.user

        # ¿son amigos?
        if SolicitudAmistad.objects.filter(
            aceptada='aceptada'
        ).filter(
            Q(destinatario=user, remitente=user_id) |
            Q(destinatario=user_id, remitente=user)
        ).exists():
            return Response({'status': 'friends'})

        # ¿solicitud enviada?
        if SolicitudAmistad.objects.filter(
            remitente=user,
            destinatario=user_id,
            aceptada='pendiente'
        ).exists():
            fr = SolicitudAmistad.objects.get(
                remitente=user_id,
                destinatario=user,
                aceptada='pendiente'
            )
            return Response({'status': 'pending_sent', 'request_id': fr.id})

        # ¿solicitud recibida?
        if SolicitudAmistad.objects.filter(
            remitente=user_id,
            destinatario=user,
            aceptada='pendiente'
        ).exists():
            fr = SolicitudAmistad.objects.get(
                remitente=user_id,
                destinatario=user,
                aceptada='pendiente'
            )
            return Response({'status': 'pending_received', 'request_id': fr.id})

        return Response({'status': 'none'})
    
class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        friend_request = get_object_or_404(
            SolicitudAmistad,
            id=request_id,
            destinatario=request.user,
            aceptada='pendiente'
        )

        friend_request.aceptada = 'aceptada'
        friend_request.save()

        return Response({'message': 'Solicitud aceptada'}, status=200)
    
class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        friend_request = get_object_or_404(
            SolicitudAmistad,
            id=request_id,
            destinatario=request.user,
            aceptada='pendiente'
        )

        friend_request.aceptada = 'rechazada'
        friend_request.save()

        return Response({'message': 'Solicitud rechazada'}, status=200)
    

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
