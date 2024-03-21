from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Reserva, Prestador, Servico, Cliente

User = get_user_model()


class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = "__all__"

    def validate(self, data):
        prestador = data.get("prestador")
        data_hora = data.get("data_hora")

        if prestador and data_hora:
            if Prestador.objects.filter(
                id=prestador.id,
                horariotrabalho__dia_semana=data_hora.weekday(),
                horariotrabalho__inicio__lte=data_hora.time(),
                horariotrabalho__fim__gte=data_hora.time(),
            ).exists():
                raise serializers.ValidationError(
                    {"prestador": "O prestador não está disponível neste horário."}
                )

            if Reserva.objects.filter(
                prestador=prestador, data_hora=data_hora
            ).exists():
                raise serializers.ValidationError(
                    {
                        "data_hora": "Já existe uma reserva neste horário para o prestador selecionado."
                    }
                )
        else:
            raise serializers.ValidationError("Prestador e data/hora são obrigatórios.")

        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "A confirmação de senha não coincide."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        user = User.objects.create_user(**validated_data)
        return user


class PrestadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestador
        fields = [
            "usuario",
            "servicos",
            "foto",
            "biografia",
            "quantidade_servicos_prestados",
            "rank_avaliacao",
        ]
        extra_kwargs = {
            "quantidade_servicos_prestados": {"read_only": True},
            "rank_avaliacao": {"read_only": True},
        }

    def create(self, validated_data):
        servicos_data = validated_data.pop("servicos")
        prestador = Prestador.objects.create(**validated_data)
        prestador.servicos.set(servicos_data)
        return prestador

    def update(self, instance, validated_data):
        instance.biografia = validated_data.get("biografia", instance.biografia)
        if "servicos" in validated_data:
            servicos_data = validated_data.pop("servicos")
            instance.servicos.set(servicos_data)
        instance.save()
        return instance


class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "email"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ClienteSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()

    class Meta:
        model = Cliente
        fields = ["usuario", "telefone", "endereco"]

    def create(self, validated_data):
        user_data = validated_data.pop("usuario")
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        cliente = Cliente.objects.create(usuario=user, **validated_data)
        return cliente
