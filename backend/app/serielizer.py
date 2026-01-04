from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Perfil
from .models import Archivo

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','username','email','password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class PerfilSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="usuario.username",read_only=True)

    class Meta:
        model = Perfil
        fields = ['id','username','foto_perfil','usuario_id']

class ArchivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archivo
        fields = ['id','comentario','archivo','fecha_subida','formato','usuario_id']