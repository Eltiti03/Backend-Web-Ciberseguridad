from datetime import timezone
import uuid
from django.db import models
from ..models.usuario import Usuario


class Codigo(models.Model):

    class TipoCodigo(models.TextChoices):
        VERIFICACION = "VERIFICACION"
        RECUPERACION = "RECUPERACION"

    code_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    content = models.CharField(max_length=6)
    used = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    tipo = models.CharField(
        max_length=20,
        choices=TipoCodigo.choices, 
        default=TipoCodigo.VERIFICACION
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="codigos",
    )

    class Meta:
        db_table = "codigo"