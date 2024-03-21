from django.test import TestCase
from core.models import Prestador, Servico, HorarioTrabalho, Reserva, Cliente
from datetime import timedelta
from django.contrib.auth.models import User


class ServicoModelTest(TestCase):

    def setUp(self):
        Servico.objects.create(
            nome="Corte de Cabelo",
            descricao="Corte básico",
            duracao=timedelta(minutes=30),
        )

    def test_servico_creation(self):
        servico = Servico.objects.get(nome="Corte de Cabelo")
        self.assertTrue(isinstance(servico, Servico))
        self.assertEqual(servico.__str__(), servico.nome)


class PrestadorModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.servico = Servico.objects.create(
            nome="Corte de Cabelo",
            descricao="Um corte de cabelo básico para homens.",
            duracao=timedelta(minutes=30),
        )

        self.prestador = Prestador.objects.create(
            usuario=self.user,
            biografia="Uma breve biografia do prestador.",
            quantidade_servicos_prestados=10,
            rank_avaliacao=4.5,
        )
        self.prestador.servicos.add(self.servico)

    def test_prestador_creation(self):
        self.assertTrue(isinstance(self.prestador, Prestador))

    def test_prestador_str(self):
        self.assertEqual(str(self.prestador), self.user.username)

    def test_quantidade_servicos_prestados(self):
        self.assertEqual(self.prestador.quantidade_servicos_prestados, 10)

    def test_rank_avaliacao(self):
        self.assertEqual(self.prestador.rank_avaliacao, 4.5)


class HorarioTrabalhoModelTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username="prestador_user", password="testpass123"
        )
        prestador = Prestador.objects.create(usuario=user)

        self.horario_trabalho = HorarioTrabalho.objects.create(
            prestador=prestador,
            dia_semana=1,
            inicio="09:00",
            fim="17:00",
        )

    def test_horario_trabalho_creation(self):
        self.assertTrue(isinstance(self.horario_trabalho, HorarioTrabalho))


class ReservaModelTest(TestCase):

    def setUp(self):
        cliente_user = User.objects.create_user(
            username="cliente_user", password="testpass123"
        )
        cliente = Cliente.objects.create(
            usuario=cliente_user, nome_completo="Cliente de Teste"
        )

        prestador_user = User.objects.create_user(
            username="prestador_user", password="testpass123"
        )
        prestador = Prestador.objects.create(
            usuario=prestador_user,
            biografia="Uma breve biografia do prestador.",
            quantidade_servicos_prestados=10,
            rank_avaliacao=4.5,
        )
        
        servico = Servico.objects.create(
            nome="Corte de Cabelo",
            descricao="Um corte de cabelo básico para homens.",
            duracao=timedelta(minutes=30),
        )
        
        self.reserva = Reserva.objects.create(
            cliente=cliente,
            prestador=prestador,
            servico=servico,
            data_hora="2024-03-15T10:00:00Z",
            status="confirmado",
            notas="Por favor, chegar 10 minutos antes.",
        )

    def test_reserva_creation(self):
        self.assertTrue(isinstance(self.reserva, Reserva))
        self.assertEqual(self.reserva.status, "confirmado")
