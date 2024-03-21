from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from core.models import Prestador, Servico, HorarioTrabalho, Reserva, Cliente
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.urls import reverse
from django.utils import timezone


class ClienteCreateTestCase(APITestCase):
    def setUp(self):
        # Define a URL para o endpoint. Substitua 'cliente-create' pelo nome real da sua URL, se for diferente.
        self.url = reverse("cliente-create")

    def test_create_cliente(self):
        """
        Garante que podemos criar um novo cliente e usuário associado.
        """
        data = {
            "usuario": {
                "username": "testuser",
                "password": "testpassword",
                "email": "test@example.com",
            },
            "telefone": "123456789",
            "endereco": "Rua Exemplo, 123",
        }

        response = self.client.post(self.url, data, format="json")

        # Verifica se o cliente foi criado com sucesso
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifica se o usuário associado foi criado
        self.assertTrue(
            User.objects.filter(username=data["usuario"]["username"]).exists()
        )

        # Verifica se o objeto Cliente foi criado e está associado ao usuário correto
        user = User.objects.get(username=data["usuario"]["username"])
        self.assertTrue(Cliente.objects.filter(usuario=user).exists())

        cliente = Cliente.objects.get(usuario=user)
        # Verifica se os campos do Cliente foram salvos corretamente
        self.assertEqual(cliente.telefone, data["telefone"])
        self.assertEqual(cliente.endereco, data["endereco"])

    def test_create_cliente_invalid_data(self):
        """
        Garante que a API retorna erro ao tentar criar um cliente com dados inválidos.
        """
        # Dados inválidos: 'username' está faltando
        data = {
            "usuario": {"password": "testpassword", "email": "test@example.com"},
            "telefone": "123456789",
            "endereco": "Rua Exemplo, 123",
        }

        response = self.client.post(self.url, data, format="json")

        # Verifica se a API retorna um erro devido aos dados inválidos
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verifica se nenhum Cliente foi criado
        self.assertEqual(Cliente.objects.count(), 0)

        # Verifica se nenhum Usuário foi criado
        self.assertEqual(User.objects.count(), 0)


class ServicoAPITest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.servico_data = {
            "nome": "Corte de Cabelo",
            "descricao": "Corte básico",
            "duracao": "00:30:00",
        }
        self.response = self.client.post(
            "/api/servicos/", self.servico_data, format="json"
        )

    def test_create_servico(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Servico.objects.count(), 1)
        self.assertEqual(Servico.objects.get().nome, "Corte de Cabelo")

    def test_update_servico(self):
        servico = Servico.objects.get()
        updated_servico_data = {
            "nome": "Corte de Cabelo Deluxe",
            "descricao": "Corte de cabelo com lavagem e secagem",
            "duracao": "01:00:00",
        }
        response = self.client.put(
            f"/api/servicos/{servico.id}/", updated_servico_data, format="json"
        )
        servico.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(servico.nome, "Corte de Cabelo Deluxe")
        self.assertEqual(servico.descricao, "Corte de cabelo com lavagem e secagem")
        self.assertEqual(str(servico.duracao), "1:00:00")

    def test_patch_update_servico(self):
        servico = Servico.objects.get()
        patch_data = {"descricao": "Corte básico incluindo lavagem"}
        response = self.client.patch(
            f"/api/servicos/{servico.id}/", patch_data, format="json"
        )
        servico.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(servico.descricao, "Corte básico incluindo lavagem")

    def test_delete_servico(self):
        servico = Servico.objects.get()
        response = self.client.delete(f"/api/servicos/{servico.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Servico.objects.count(), 0)

    def test_get_servico(self):
        servico = Servico.objects.get()
        response = self.client.get(f"/api/servicos/{servico.id}/")

        duracao_formatada = f"{servico.duracao}".rjust(8, "0")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], servico.nome)
        self.assertEqual(response.data["descricao"], servico.descricao)
        self.assertEqual(response.data["duracao"], duracao_formatada)


class ReservaAPITest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.cliente_user = User.objects.create_user(
            username="cliente_user", password="testpass123", email="cliente@example.com"
        )
        self.cliente = Cliente.objects.create(
            usuario=self.cliente_user,
        )

        self.prestador_user = User.objects.create_user(
            username="prestador_user",
            password="testpass123",
            email="prestador@example.com",
        )
        self.prestador = Prestador.objects.create(
            usuario=self.prestador_user, biografia="Prestador de serviços"
        )
        self.horario = HorarioTrabalho.objects.create(
            prestador=self.prestador,
            dia_semana=0,
            inicio=datetime.now().time(),
            fim=(datetime.now() + timedelta(hours=1)).time(),
        )

        self.servico = Servico.objects.create(
            nome="Serviço Teste",
            descricao="Descrição do serviço teste",
            duracao=timedelta(minutes=30),
        )
        self.client.force_authenticate(user=self.cliente_user)

    def test_create_reserva(self):
        data_reserva = datetime.now() + timedelta(days=10)
        reserva_data = {
            "cliente": self.cliente.id,
            "prestador": self.prestador.id,
            "servico": self.servico.id,
            "data_hora": data_reserva.isoformat(),
            "status": "confirmado",
            "notas": "Alguma nota aqui",
        }
        response = self.client.post("/api/reservas/", reserva_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reserva.objects.count(), 1)
        reserva = Reserva.objects.first()
        self.assertEqual(reserva.status, "confirmado")

    def test_update_reserva(self):
        data_reserva = datetime.now() + timedelta(days=1)
        data_reserva_up = datetime.now() + timedelta(days=2)
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            prestador=self.prestador,
            servico=self.servico,
            data_hora=data_reserva,
            status="confirmado",
        )

        updated_data = {
            "prestador": self.prestador.id,
            "status": "cancelado",
            "notas": "Atualização de notas",
            "data_hora": data_reserva_up,
        }
        response = self.client.patch(
            f"/api/reservas/{reserva.id}/", updated_data, format="json"
        )
        reserva.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reserva.status, "cancelado")
        self.assertEqual(reserva.notas, "Atualização de notas")

    def test_update_reserva_no_mesmo_horario(self):
        data_reserva = datetime.now() + timedelta(days=1)
        data_reserva_up = datetime.now() + timedelta(days=2)
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            prestador=self.prestador,
            servico=self.servico,
            data_hora=data_reserva,
            status="confirmado",
        )

        updated_data = {
            "prestador": self.prestador.id,
            "status": "cancelado",
            "notas": "Atualização de notas",
            "data_hora": data_reserva_up,
        }
        response = self.client.patch(
            f"/api/reservas/{reserva.id}/", updated_data, format="json"
        )
        reserva.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reserva.status, "cancelado")
        self.assertEqual(reserva.notas, "Atualização de notas")

    def test_get_reserva(self):
        data_hora = timezone.make_aware(datetime(2024, 3, 15, 10, 0, 0))

        reserva = Reserva.objects.create(
            cliente=self.cliente,
            prestador=self.prestador,
            servico=self.servico,
            data_hora=data_hora,
            status="confirmado",
        )
        response = self.client.get(f"/api/reservas/{reserva.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "confirmado")


class PrestadorAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="prestador_user",
            password="testpass123",
            email="prestador@example.com",
        )
        cls.servico = Servico.objects.create(
            nome="Corte de Cabelo",
            descricao="Corte básico",
            duracao=timedelta(minutes=30),
        )

    def create_prestador(self, **kwargs):
        defaults = {
            "usuario": self.user,
            "biografia": "Uma breve biografia do prestador.",
        }
        defaults.update(kwargs)
        prestador = Prestador.objects.create(**defaults)
        prestador.servicos.add(self.servico)
        return prestador

    def test_create_prestador(self):
        prestador_data = {
            "usuario": self.user.id,
            "servicos": [self.servico.id],
            "biografia": "Uma breve biografia do prestador.",
        }
        url = reverse("prestadores-list")
        response = self.client.post(url, prestador_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Prestador.objects.count(), 1)
        self.assertEqual(
            Prestador.objects.first().biografia, prestador_data["biografia"]
        )

    def test_get_prestador(self):
        prestador = self.create_prestador()
        url = reverse("prestadores-detail", args=[prestador.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["biografia"], prestador.biografia)

    def test_update_prestador(self):
        prestador = self.create_prestador(biografia="Biografia original")
        updated_data = {
            "usuario": self.user.id,
            "servicos": [self.servico.id],
            "biografia": "Biografia completa atualizada",
        }
        url = reverse("prestadores-detail", args=[prestador.id])
        response = self.client.put(url, updated_data, format="json")
        prestador.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(prestador.biografia, "Biografia completa atualizada")

    def test_patch_update_prestador(self):
        prestador = self.create_prestador(biografia="Biografia original do Prestador")
        updated_data = {
            "biografia": "Biografia atualizada do Prestador",
            "servicos": [self.servico.id],
        }
        url = reverse("prestadores-detail", args=[prestador.id])
        response = self.client.patch(url, updated_data, format="json")
        prestador.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(prestador.biografia, "Biografia atualizada do Prestador")

    def test_delete_prestador(self):
        prestador = self.create_prestador(
            biografia="Biografia do Prestador para deletar"
        )
        url = reverse("prestadores-detail", args=[prestador.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Prestador.objects.count(), 0)

    def test_confirmar_reserva_incrementa_servicos_prestados(self):
        prestador = self.create_prestador(
            quantidade_servicos_prestados=0, rank_avaliacao=0
        )
        cliente_user = User.objects.create_user(
            username="cliente_user", password="testpass123"
        )
        cliente = Cliente.objects.create(
            usuario=cliente_user,
        )

        reserva_data = {
            "cliente": cliente.id,
            "prestador": prestador.id,
            "servico": self.servico.id,
            "data_hora": timezone.now().isoformat(),
            "status": "confirmado",
            "notas": "Por favor, chegar 10 minutos antes.",
        }
        url = reverse("reservas-list")
        response = self.client.post(url, reserva_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        prestador.refresh_from_db()
        self.assertEqual(prestador.quantidade_servicos_prestados, 1)
