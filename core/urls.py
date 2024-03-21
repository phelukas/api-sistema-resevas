from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ReservaViewSet,
    UserRegistrationView,
    PrestadorViewSet,
    ServicoViewSet,
    ClienteCreateView,
)

router = DefaultRouter()
router.register(r"prestadores", PrestadorViewSet, basename="prestadores")
router.register(r"servicos", ServicoViewSet, basename="servicos")
router.register(r"reservas", ReservaViewSet, basename="reservas")

urlpatterns = [
    path("", include(router.urls)),
    path("cadastro/", UserRegistrationView.as_view(), name="cadastro_usuario"),
    path("clientes/", ClienteCreateView.as_view(), name="cliente-create"),
    # Adiciona as URLs do JWT aqui
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
