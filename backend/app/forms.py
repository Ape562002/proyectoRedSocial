from django import forms
from .models import Archivo

class subir(forms.ModelForm):
    class Meta:
        model = Archivo
        fields = ['comentario', 'archivo']