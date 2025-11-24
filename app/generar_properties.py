import os

def generar_properties_env():
    variables = [
        "URL_APP",
        "DESPLIEGUE_LOCAL",

        # GEMINI
        "GEMINI_API_KEY_IGNA",
        "GEMINI",
        "GEMINI_API_KEY_MARCOS",
        "GEMINI_API_KEY_MARCOS_BACKUP",

        # GOOGLE AUTH
        "GOOGLE_AUTH_SECRET",
        "GOOGLE_AUTH_CLIENT",

        # TWILIO
        "TWILIO_ACCOUNT_SID_IGNA",
        "TWILIO_AUTH_TOKEN_IGNA",
        "NRO_REMITENTE",
        "TWILIO_TEST_SID",
        "TWILIO_TEST_TOKEN",
        "TWILIO_ACCOUNT_SID_MORA",
        "TWILIO_AUTH_TOKEN_MORA",

        # ELEVEN LABS
        "ELEVEN_LABS_IGNA",
        "API_KEY_CLONACION_VOZ",

        # SENDGRID
        "SENDGRID_TOKEN_IGNA",
        "SENDGRID_EMAILS_PHISHINTEL",
        "SENDGRID_EMAILS_PGCONTROL",

        # SMTP MEDIO
        "SMTP_MEDIO_HOST",
        "SMTP_MEDIO_PORT",
        "SMTP_MEDIO_USER",
        "SMTP_MEDIO_PASSWORD",

        # SMTP DIFICIL
        "SMTP_DIFICIL_HOST",
        "SMTP_DIFICIL_PORT",
        "SMTP_DIFICIL_USER",
        "SMTP_DIFICIL_PASSWORD",
        "SMTP_DIFICIL_MARCOS_USER",
        "SMTP_DIFICIL_MARCOS_PASSWORD",
        "SMTP_DIFICIL_MORA_USER",
        "SMTP_DIFICIL_MORA_PASSWORD",

        # TELEGRAM
        "TELEGRAM_TOKEN",
        "TELEGRAM_APP_ID",
        "TELEGRAM_API_HASH",

        # WHATSAPP
        "WHAPI_CLOUD_TOKEN",

        # SMS
        "TEXTBEE_TOKEN",
        "TEXTBEE_DEVICE_ID",
        "TEXTBEE_TOKEN_BACKUP",

        # WEB SCRAPING
        "API_KEY_WEB_SCRAPPING_IGNA",
        "CX_WEB_SCRAPPING_IGNA",

        # SEGURIDAD BASICA
        "LLAMAR_PASSWORD",

        # LINKEDIN
        "LINKEDIN_EMAIL",
        "LINKEDIN_PASSWORD",
    ]

    lines = []
    for var in variables:
        value = os.getenv(var, "")
        lines.append(f"{var}={value}")

    filepath = os.path.join("phishintel", "app", "properties.env")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w") as f:
        f.write("\n".join(lines))

    print("Archivo properties.env generado correctamente.")
