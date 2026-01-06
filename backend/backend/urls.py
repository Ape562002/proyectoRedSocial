from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from app import views
from app.views import UserPostListView
from app.views import ToggleLikeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.LoginView.as_view()),
    path('resgister/', views.RegisterView.as_view()),
    path('profile/',views.profile),
    path('subir/',views.simple_uploud),
    path('posts/', UserPostListView.as_view()),
    path('posts/<int:archivo_id>/like/', ToggleLikeView.as_view()),
    path('posts/<int:archivo_id>/comentarios/',views.ComentariosPostView.as_view()),
    path('posts/<int:archivo_id>/comentario/', views.CreateComentarioView.as_view()),
    path('logout/',views.logout)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)