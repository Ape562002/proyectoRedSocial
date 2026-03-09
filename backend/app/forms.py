from django import forms
from .models import Archivo

class subir(forms.ModelForm):
    class Meta:
        model = Archivo
        fields = ['comentario', 'archivo','categorias']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivo'].required = False