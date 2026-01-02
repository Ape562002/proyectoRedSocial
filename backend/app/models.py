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
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200, null=True,blank=True)
    privado = models.BooleanField(default=False, null=True,blank=True)
    foto_perfil = models.ImageField(
        upload_to='perfil_fotos/',
        default='perfil_fotos/default.webp',
        null=True,
        blank=True
    )

    def __str__(self):
        return super.usuario.username
    
class Archivo(models.Model):
    comentario = models.CharField(max_length=200, null=True, blank=True)
    archivo = models.FileField(upload_to=profile_picture_path)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    formato = models.CharField(max_length=20,blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        _, ext = os.path.splitext(self.archivo.name)
        ext = ext.lower().lstrip('.')

        if ext in ['jpg', 'jpeg', 'png', 'gif']:
            img = Image.open(self.archivo)

            max_width = 1280
            if img.width > max_width:
                ratio = max_width / float(img.width)
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)

            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=75)
            img_io.seek(0)

            self.archivo = ContentFile(img_io.read(), name=self.archivo.name)

        self.formato = ext
        super().save(*args, **kwargs)


    def __str__(self):
        return self.file.name
    
