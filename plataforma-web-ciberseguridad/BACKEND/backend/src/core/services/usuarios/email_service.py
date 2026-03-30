from django.core.mail import send_mail
from django.conf import settings

def enviar_codigo_verificacion(destinatario, codigo):
    send_mail(
        subject="Código de verificación",
        message=f"Tu código de verificación es: {codigo}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[destinatario],
        fail_silently=False
    )