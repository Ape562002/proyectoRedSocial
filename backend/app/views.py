from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serielizer import ComentariosSerializer, UserSearchSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_list_or_404, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
import json

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
from .models import Categoria
from .models import HistorialVisto
from .models import ContenidoBloqueado
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

from .ml import analizar_comentario
from .clasificador_imagen import clasificar_imagen
from .clasificador_imagen import clasificar_video
from django.core.cache import cache
import pandas as pd

@staff_member_required
def panel_tendencias(request):
    hoy = timezone.now().date()

    total_publicaciones = Archivo.objects.count()
    total_likes = Like.objects.count()
    total_comentarios = Comentarios.objects.count()
    total_usuarios = User.objects.count()

    labels_dias = []
    datos_publicaciones = []
    datos_likes = []
    datos_comentarios = []

    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        labels_dias.append(dia.strftime('%d/%m'))
        datos_publicaciones.append(
            Archivo.objects.filter(fecha_subida__date=dia).count()
        )
        datos_likes.append(
            Like.objects.filter(fecha_like__date=dia).count()
        )
        datos_comentarios.append(
            Comentarios.objects.filter(fecha_comentario__date=dia).count()
        )

    categorias = Categoria.objects.annotate(
        total_interacciones=Count('archivo__like') + Count('archivo__comentarios')
    ).order_by('-total_interacciones')[:7]

    labels_categorias = [c.nombre for c in categorias]
    datos_categorias = [c.total_interacciones for c in categorias]

    labels_semanas = []
    datos_semanales = []

    for i in range(7, -1, -1):
        inicio_semana = hoy - timedelta(weeks=i)
        fin_semana = inicio_semana + timedelta(days=7)
        labels_semanas.append(inicio_semana.strftime('%d/%m'))
        datos_semanales.append(
            Archivo.objects.filter(
                fecha_subida__date__gte=inicio_semana,
                fecha_subida__date__lt=fin_semana
            ).count()
        )

    context = {
        'total_publicaciones': total_publicaciones,
        'total_likes': total_likes,
        'total_comentarios': total_comentarios,
        'total_usuarios': total_usuarios,
        'labels_dias': json.dumps(labels_dias),
        'datos_publicaciones': json.dumps(datos_publicaciones),
        'datos_likes': json.dumps(datos_likes),
        'datos_comentarios': json.dumps(datos_comentarios),
        'labels_categorias': json.dumps(labels_categorias),
        'datos_categorias': json.dumps(datos_categorias),
        'labels_semanas': json.dumps(labels_semanas),
        'datos_semanales': json.dumps(datos_semanales),
    }

    return render(request, 'admin/tendencias.html', context)

@staff_member_required
def panel_moderacion(request):
    estado_activo = request.GET.get('estado', '')

    bloques = ContenidoBloqueado.objects.select_related('archivo', 'usuario', 'revisado_por')

    if estado_activo:
        bloques = bloques.filter(estado=estado_activo)

    bloqueos = bloques.order_by('-fecha_bloqueo')

    context = {
        'bloqueos':           bloqueos,
        'estado_activo':      estado_activo,
        'total_bloqueados':   ContenidoBloqueado.objects.filter(estado='bloqueado').count(),
        'total_apelados':     ContenidoBloqueado.objects.filter(estado='apelado').count(),
        'total_restaurados':  ContenidoBloqueado.objects.filter(estado='restaurado').count(),
        'total_confirmados':  ContenidoBloqueado.objects.filter(estado='confirmado').count(),
    }

    return render(request, 'admin/moderacion.html', context)

@staff_member_required
def revisar_bloqueo(request, bloqueo_id):
    bloqueo = get_object_or_404(ContenidoBloqueado, id=bloqueo_id)
    accion = request.POST.get('accion')

    if accion == 'restaurar':
        bloqueo.estado = 'restaurado'
        bloqueo.archivo.bloqueado = False
        bloqueo.archivo.save(update_fields=['bloqueado'])
    elif accion == 'confirmar':
        bloqueo.estado = 'confirmado'

    bloqueo.revisado_por = request.user
    bloqueo.fecha_revision = timezone.now()
    bloqueo.save()

    estado_previo = request.POST.get('estado_previo', '')
    return redirect(f'/admin/moderacion/?estado={estado_previo}')

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

            tiene_archivo = bool(request.FILES.get('archivo'))
            tiene_comentario = bool(request.POST.get('comentario','').strip())

            if not tiene_archivo and not tiene_comentario:
                return Response({'error': 'Debes proporcionar un archivo o un comentario'}, status=400)
            
            categoria_detectada = None
            confianza_detectada = None
            es_imagen = False

            if tiene_archivo:
                tipo = request.FILES.get('archivo') and request.FILES['archivo'].content_type or ''
                es_imagen = tipo.startswith('image/')
                es_video = tipo.startswith('video/')

            form.instance.usuario = request.user
            publicacion = form.save(commit=False)

            if es_video:
                publicacion.save()
                resultado = clasificar_video(publicacion.archivo.path)
            elif es_imagen:
                resultado = clasificar_imagen(request.FILES['archivo'])
            else:
                resultado = None

            if resultado and resultado['confianza_suficiente']:
                categoria_detectada = resultado['categoria']
                confianza_detectada = resultado['confianza']

                if resultado and resultado['es_moderada']:
                    form.instance.usuario = request.user
                    form.instance.bloqueado = True
                    publicacion.save()

                    ContenidoBloqueado.objects.create(
                        archivo=publicacion,
                        usuario = request.user,
                        categoria_modelo = categoria_detectada,
                        confianza = confianza_detectada,
                        estado = 'bloqueado',
                    )

                    return Response({
                        'bloqueado': True,
                        'mensaje': ('Tu publicación ha sido bloqueada por contener contenido inapropiado','Puedes apelar esta decisión contactando con soporte.'),
                        'categoria_detectada': categoria_detectada,
                        'confianza': confianza_detectada,
                    },status=200)
            
            if not es_video:
                publicacion.bloqueado = False
                publicacion.save()
        
            if categoria_detectada:
                try:
                    cat_obj = Categoria.objects.get(nombre__iexact=categoria_detectada)
                    publicacion.categorias.add(cat_obj)
                except Categoria.DoesNotExist:
                    pass

            serializer = ArchivoSerializer(publicacion, context={'request': request})
            return Response({
                **serializer.data,
                'categoria_auto': categoria_detectada,
                'confianza_auto': confianza_detectada,
                'bloqueado': False,
            },status=200)
        
        return Response({'error': form.errors}, status=400)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def apelar_bloqueo(request, archivo_id):
    try:
        bloquear = ContenidoBloqueado.objects.get(
            archivo_id=archivo_id,
            usuario=request.user,
            estado='bloqueado'
        )
    except ContenidoBloqueado.DoesNotExist:
        return Response({'error': 'No se encontró una publicación bloqueada para apelar'}, status=404)
    
    bloquear.estado = 'apelada'
    bloquear.save()

    return Response({'message': 'Tu apelación ha sido enviada. Nuestro equipo revisará tu caso.'}, status=200)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def crear_categoria(request):
    nombre = request.data.get('nombre', '').strip()
    if not nombre:
        return Response({'error':'El nombre es requerido'}, status=400)
    
    categoria, _ = Categoria.objects.get_or_create(
        nombre=nombre,
        defaults={'creada_por_id': request.user.id, 'es_predefinida': False}
    )
    return Response({'id': categoria.id, 'nombre': categoria.nombre}, status=201)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getCategorias(request):
    categorias = Categoria.objects.all().values('id', 'nombre')
    return Response(list(categorias))

def obtener_datos_recomendacion(usuario):
    historial = HistorialVisto.objects.filter(
        usuario=usuario
    ).select_related('archivo').order_by('-fecha_visto')[:5]

    if historial.exists():
        usuario_en = [
            {
                'id': h.archivo.id,
                'rating': h.archivo.score_base
            }
            for h in historial
        ]
    else:
        historial_default = Archivo.objects.order_by('-score_base')[:5]
        usuario_en = [
            {
                'id': int(pub.id),
                'rating': float(pub.score_base)
            }
            for pub in historial_default
        ]

    publicaciones_lista = []
    for pub in Archivo.objects.prefetch_related('categorias').all():
        publicaciones_lista.append({
            'id': pub.id,
            'score_base': pub.score_base,
            'categorias': " ".join([c.nombre for c in pub.categorias.all()])
        })

    df_publicaciones = pd.DataFrame(publicaciones_lista)
    df_historial = pd.DataFrame(usuario_en)

    return df_publicaciones, df_historial

def calcular_recomendaciones(usuario):
    df_publicaciones, df_historial = obtener_datos_recomendacion(usuario)

    if df_historial.empty:
        return list(
            Archivo.objects.order_by('-score_base')
            .values('id')[:10]
        )
    
    peliculas_co = df_publicaciones.copy()

    for index, row in df_publicaciones.iterrows():
        if not row['categorias']:
            continue
        categorias = row['categorias'].split()
        for categoria in categorias:
            peliculas_co.at[index, categoria] = 1

    peliculas_co = peliculas_co.fillna(0)

    entrada = df_publicaciones[df_publicaciones['id'].isin(df_historial['id'].tolist())]
    entrada = pd.merge(entrada, df_historial, on='id')

    if entrada.empty:
        return list(
            Archivo.objects.order_by('-score_base')
            .values('id',flat=True)[:20]
        )

    pubs_usuario = peliculas_co[peliculas_co['id'].isin(entrada['id'].tolist())]
    pubs_usuario = pubs_usuario.drop_duplicates(subset=['id'])
    pubs_usuario = pubs_usuario.reset_index(drop=True)
    entrada = entrada.drop_duplicates(subset=['id'])
    entrada = entrada.reset_index(drop=True)

    columnas_categorias = [
        col for col in peliculas_co.columns 
        if col not in ['id', 'score_base', 'categorias']
    ]

    tabla_categorias = pubs_usuario[columnas_categorias]

    perfil_usuario = tabla_categorias.transpose().dot(entrada['rating'])

    generos = peliculas_co.set_index(peliculas_co['id'])
    generos = generos.drop(columns=['id','score_base', 'categorias'])

    recom = ((generos *perfil_usuario).sum(axis=1)) / (perfil_usuario.sum())
    recom = recom.sort_values(ascending=False)

    ids_vistos = df_historial['id'].tolist()
    recom = recom[~recom.index.isin(ids_vistos)]
    
    return recom.index.tolist()

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def feed_recomendado(request):
    pagina = int(request.GET.get('pagina',1))
    por_pagina = 20
    usuario = request.user

    cache_key = f'recomendaciones_{usuario.id}'
    ids_recomendados = cache.get(cache_key)

    if not ids_recomendados:
        ids_recomendados = calcular_recomendaciones(usuario)
        cache.set(cache_key, ids_recomendados, timeout=3600)

    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    ids_pagina = ids_recomendados[inicio:fin]

    publicaciones = Archivo.objects.filter(
        id__in=ids_pagina
    ).prefetch_related('categorias').annotate(
        likes_count=Count('like'),
        is_liked=Exists(
            Like.objects.filter(
                usuario=request.user,
                archivo=OuterRef('pk')
            )
        )
    )

    publicaciones_dict = {pub.id: pub for pub in publicaciones}
    publicaciones_ordenadas = [
        publicaciones_dict[id] for id in ids_pagina if id in publicaciones_dict
    ]

    serializer = ArchivoSerializer(publicaciones_ordenadas, many=True, context={'request': request})

    return Response({
        'recomendaciones': serializer.data,
        'hay mas': fin < len(ids_recomendados),
        'pagina_actual': pagina
    })


class UserPostListView(ListAPIView):
    serializer_class = ArchivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Archivo.objects.filter(usuario=user).annotate(
            likes_count=Count('like'),
            is_liked=Exists(
                Like.objects.filter(
                    usuario=self.request.user,
                    archivo=OuterRef('pk')
                )
            )
        ).order_by('-fecha_subida')
    
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
            registrar_visto(request.user, archivo)

        actualizar_score_base(archivo)

        likes_count = Like.objects.filter(archivo=archivo).count()

        return Response({
            'liked': liked,
            'likes_count': likes_count
        }, status=status.HTTP_200_OK)
    
def actualizar_score_base(archivo, sentimiento=None):
    tiene_likes = Like.objects.filter(archivo=archivo).exists()

    score = archivo.score_base

    if tiene_likes:
        score = min(5, score + 1)

    if sentimiento == 'positive':
        score = min(5, score + 1)
    elif sentimiento == 'negative' or sentimiento == 'neutral':
        score = max(0, score - 1)

    archivo.score_base = score
    archivo.save(update_fields=['score_base'])

class CreateComentarioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, archivo_id):
        serializer = ComentariosSerializer(data=request.data)
        archivo = get_object_or_404(Archivo, id=archivo_id)

        if serializer.is_valid():
            contenido = request.data.get('contenido', '')
            sentimiento, _ = analizar_comentario(contenido)

            serializer.save(
                usuario=request.user,
                archivo_id=archivo_id,
                sentimiento=sentimiento
            )

            registrar_visto(request.user, archivo)
            actualizar_score_base(archivo, sentimiento=sentimiento)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def registrar_visto(usuario, archivo):
    HistorialVisto.objects.update_or_create(
        usuario=usuario,
        archivo=archivo
    )

    ids_mantener = list(
        HistorialVisto.objects.filter(usuario=usuario)
        .order_by('-fecha_visto')
        .values_list('id', flat=True)[:5]
    )

    if ids_mantener:
        HistorialVisto.objects.filter(
            usuario=usuario
        ).exclude(id__in=ids_mantener).delete()

    cache.delete(f'recomendaciones_{usuario.id}')

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

        return Archivo.objects.filter(usuario_id=user_id).annotate(
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
