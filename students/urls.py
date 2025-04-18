from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet

# Создаём роутер
router = DefaultRouter()
# Регистрируем ViewSet с префиксом 'students'
router.register(r'students', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),  # Подключаем все маршруты роутера
]