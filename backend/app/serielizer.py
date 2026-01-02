from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Perfil

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','password']

class PerfilSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="usuario.username",read_only=True)

    class Meta:
        model = Perfil
        fields = ['id','username','foto_perfil','usuario_id']