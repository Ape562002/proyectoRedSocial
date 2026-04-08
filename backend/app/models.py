from django.db import models
import uuid
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth.models import User

def profile_picture_path(instance, filename):
    random_filename = str(uuid.uuid4())
    extension = os.path.splitext(filename)[1]
    return 'archivos/{}{}'.format(random_filename, extension)

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    descripcion = models.CharField(max_length=200, null=True,blank=True)
    privado = models.BooleanField(default=False, null=True,blank=True)
    foto_perfil = models.ImageField(
        upload_to='perfil_fotos/',
        default='perfil_fotos/default.webp',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.usuario.username
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    es_predefinida = models.BooleanField(default=False)
    creada_por = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class Archivo(models.Model):
    comentario = models.CharField(max_length=200, null=True, blank=True)
    archivo = models.FileField(upload_to=profile_picture_path, null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    formato = models.CharField(max_length=20,blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categorias = models.ManyToManyField(Categoria, blank=True)
    score_base = models.FloatField(default=3)
    bloqueado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.archivo:
            self.formato = "NaN"
            
            super().save(*args, **kwargs)
            return

        _, ext = os.path.splitext(self.archivo.name)
        ext = ext.lower().lstrip('.')

        if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
            img = Image.open(self.archivo)

            if img.mode in ('RGBA', 'LA','P'):
                img = img.convert('RGB')

            max_width = 1280
            if img.width > max_width:
                ratio = max_width / float(img.width)
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)

            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=75)
            img_io.seek(0)

            nombre_sin_ext = os.path.splitext(self.archivo.name)[0]
            self.archivo = ContentFile(img_io.read(), name=f"{nombre_sin_ext}.jpg")
            self.formato = 'jpg'
        else:
            self.formato = ext

        super().save(*args, **kwargs)


    def __str__(self):
        return self.archivo.name if self.archivo else f"Publicacion #{self.id}"
    
class ContenidoBloqueado(models.Model):

    ESTADO_CHOICES = [
        ('bloqueado', 'Bloqueado - pendiente de revision'),
        ('confirmaso', 'Confirmado - contenido bloqueado'),
        ('apelado', 'Apelado - el usuario soicita revision'),
        ('restaurado', 'Restaurado - falso positivo'),
    ]

    archivo = models.OneToOneField(Archivo, on_delete=models.CASCADE, related_name='contenido_bloqueado')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contenido_bloqueado')
    categoria_modelo = models.CharField(max_length=100)
    confianza = models.FloatField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='bloqueado')
    fecha_bloqueo = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    revisado_por = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='revisiones_moderacion'
    )
    motivo_revision = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_bloqueo']
        verbose_name = 'Contenido Bloqueado'
        verbose_name_plural = 'Contenidos Bloqueados'

    def __str__(self):
        return f"Bloqueado: {self.archivo} | {self.categoria_modelo} ({self.confianza:.1f})"

    
class Like(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    archivo = models.ForeignKey(Archivo, on_delete=models.CASCADE)
    fecha_like = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'archivo')


class Comentarios(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    archivo = models.ForeignKey(Archivo, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)
    sentimiento = models.CharField(max_length=20, default='neutral')

class HistorialVisto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    archivo = models.ForeignKey(Archivo, on_delete=models.CASCADE)
    fecha_visto = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'archivo')
        ordering = ['-fecha_visto']

class SolicitudAmistad(models.Model):
    remitente = models.ForeignKey(User, related_name='solicitudes_enviadas', on_delete=models.CASCADE)
    destinatario = models.ForeignKey(User, related_name='solicitudes_recibidas', on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    aceptada = models.CharField(max_length=10, choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')], default='pendiente')

    class Meta:
        unique_together = ('remitente', 'destinatario')

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversaciones')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversación {self.id}"
    
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"