from django.db import models

class CategoriaPublicacion(models.TextChoices):
    GENERAL      = 'general',      'General'
    CIBERATAQUES = 'ciberataques', 'Ciberataques'
    CONTRASENAS  = 'contrasenas',  'Contraseñas'
    PROTECCION   = 'proteccion',   'Protección'
    AYUDA        = 'ayuda',        'Ayuda Técnica'