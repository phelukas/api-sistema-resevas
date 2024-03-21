from rest_framework import viewsets
from .models import Reserva, Prestador, Servico, Cliente
from .serializers import ReservaSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import (
    UserRegistrationSerializer,
    PrestadorSerializer,
    ServicoSerializer,
    ClienteSerializer,
)
from django.contrib.auth import get_user_model
from rest_framework.views import APIView


class ClienteCreateView(APIView):
    def post(self, request, format=None):
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    def get_queryset(self):
        user = self.request.user
        cliente = Cliente.objects.get(usuario=user)
        return Reserva.objects.filter(cliente=cliente)


class UserRegistrationView(generics.CreateAPIView):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserRegistrationSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "message": "Usuário cadastrado com sucesso.",
            },
            status=status.HTTP_201_CREATED,
        )


class PrestadorViewSet(viewsets.ModelViewSet):
    queryset = Prestador.objects.all()
    serializer_class = PrestadorSerializer


class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
