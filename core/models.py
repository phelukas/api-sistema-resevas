from django.db import models
from django.contrib.auth.models import User


class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.usuario


class Servico(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    duracao = models.DurationField()

    def __str__(self):
        return self.nome


class Prestador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    servicos = models.ManyToManyField(Servico)
    foto = models.ImageField(upload_to="fotos_prestadores/", blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)
    quantidade_servicos_prestados = models.PositiveIntegerField(default=0)
    rank_avaliacao = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    def __str__(self):
        return self.usuario.username


class HorarioTrabalho(models.Model):
    prestador = models.ForeignKey(Prestador, on_delete=models.CASCADE)
    dia_semana = models.IntegerField()
    inicio = models.TimeField()
    fim = models.TimeField()


class Reserva(models.Model):
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="reservas_cliente"
    )
    prestador = models.ForeignKey(
        Prestador, on_delete=models.CASCADE, related_name="reservas_prestador"
    )
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    data_hora = models.DateTimeField()
    status = models.CharField(
        max_length=50,
        choices=[
            ("confirmado", "Confirmado"),
            ("cancelado", "Cancelado"),
            ("concluido", "Concluído"),
        ],
    )
    notas = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self._state.adding and self.status == "confirmado":
            self.prestador.quantidade_servicos_prestados += 1
            self.prestador.save()
        super(Reserva, self).save(*args, **kwargs)
