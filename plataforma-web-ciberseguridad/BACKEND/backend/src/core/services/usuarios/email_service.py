import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings

def enviar_codigo_verificacion(destinatario, codigo, tipo='verificacion'):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    if tipo == 'recuperacion':
        subject     = "Recuperación de contraseña — CyberGuard"
        etiqueta    = "Recuperación de contraseña"
        titulo      = "Código para restablecer tu contraseña"
        descripcion = "Recibimos una solicitud para restablecer la contraseña de tu cuenta."
        icono       = "🔐"
    else:
        subject     = "Código de verificación — CyberGuard"
        etiqueta    = "Verificación de identidad"
        titulo      = "Tu código de verificación"
        descripcion = "Usa el siguiente código para completar tu verificación."
        icono       = "🛡️"

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>{subject}</title>
    </head>
    <body style="margin:0; padding:0; background-color:#0f172a; font-family:'Segoe UI', Arial, sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f172a; padding: 40px 0;">
        <tr>
          <td align="center">
            <table width="520" cellpadding="0" cellspacing="0" style="background-color:#1e293b; border-radius:16px; overflow:hidden; border: 1px solid #334155;">
              <tr>
                <td style="background: linear-gradient(135deg, #1d4ed8, #0ea5e9); padding: 36px 40px; text-align:center;">
                  <p style="margin:0 0 8px 0; font-size:28px;">{icono}</p>
                  <h1 style="margin:0; color:#ffffff; font-size:22px; font-weight:700;">CyberGuard</h1>
                  <p style="margin:6px 0 0 0; color:#bfdbfe; font-size:13px;">Plataforma de Ciberseguridad</p>
                </td>
              </tr>
              <tr>
                <td style="padding: 36px 40px;">
                  <p style="margin:0 0 12px 0; color:#94a3b8; font-size:13px; text-transform:uppercase; letter-spacing:1px; font-weight:600;">{etiqueta}</p>
                  <h2 style="margin:0 0 16px 0; color:#f1f5f9; font-size:20px; font-weight:600;">{titulo}</h2>
                  <p style="margin:0 0 28px 0; color:#94a3b8; font-size:14px; line-height:1.6;">
                    {descripcion} Este código expira en <strong style="color:#f1f5f9;">10 minutos</strong>.
                  </p>
                  <div style="background-color:#0f172a; border: 1px solid #334155; border-radius:12px; padding: 28px; text-align:center; margin-bottom:28px;">
                    <p style="margin:0 0 8px 0; color:#64748b; font-size:12px; letter-spacing:1px; text-transform:uppercase;">Código de acceso</p>
                    <p style="margin:0; font-size:42px; font-weight:800; letter-spacing:12px; color:#38bdf8; font-family:'Courier New', monospace;">{codigo}</p>
                  </div>
                  <div style="background-color:#1e3a5f; border-left: 4px solid #3b82f6; border-radius:8px; padding:14px 16px; margin-bottom:24px;">
                    <p style="margin:0; color:#93c5fd; font-size:13px; line-height:1.5;">
                      ⚠️ <strong>Nunca compartas este código</strong> con nadie. CyberGuard jamás te lo pedirá por otro medio.
                    </p>
                  </div>
                  <p style="margin:0; color:#64748b; font-size:13px; line-height:1.6;">
                    Si no solicitaste este código, puedes ignorar este mensaje. Tu cuenta permanece segura.
                  </p>
                </td>
              </tr>
              <tr>
                <td style="background-color:#0f172a; padding: 20px 40px; text-align:center; border-top: 1px solid #1e293b;">
                  <p style="margin:0; color:#475569; font-size:12px;">© 2026 CyberGuard · Todos los derechos reservados</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": destinatario}],
        sender={"email": settings.BREVO_SENDER_EMAIL, "name": "CyberGuard"},
        subject=subject,
        html_content=html
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        print("CORREO ENVIADO CON BREVO")
    except ApiException as e:
        print("ERROR BREVO:", str(e))
        raise