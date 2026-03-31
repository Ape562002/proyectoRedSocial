from django.contrib import admin
from django.urls import path
from django.db.models import Count,Q
from .models import Archivo, Categoria, Perfil, Comentarios, Like, HistorialVisto
from . import views

class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'categorias_favoritas', 'total_likes', 'total_comentarios', 'actividad']
    search_fields = ['usuario__username']

    def categorias_favoritas(self, obj):
        categorias = Categoria.objects.filter(
            archivo__like__usuario=obj.usuario
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:3]
        return ', '.join([c.nombre for c in categorias])
    categorias_favoritas.short_description = 'Categorias favoritas'

    def total_likes(self, obj):
        return Like.objects.filter(usuario=obj.usuario).count()
    total_likes.short_description = 'Likes Dados'

    def total_comentarios(self, obj):
        return Comentarios.objects.filter(usuario=obj.usuario).count()
    total_comentarios.short_description = 'Comentarios'

    def actividad(self, obj):
        total = self.total_likes(obj) + self.total_comentarios(obj)
        if total > 50:
            return '🔥 Alta'
        elif total > 20:
            return '✅ Media'
        else:
            return '💤 Baja'
    actividad.short_description = 'Actividad'

class MiAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('tendencias/', views.panel_tendencias, name='tendencias'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tendencias_url'] = '/admin/tendencias/'
        return super().index(request, extra_context)

admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Categoria)
admin.site.register(Archivo)
admin.site.register(Comentarios)
