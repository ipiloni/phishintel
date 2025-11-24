import os
import shutil

def generar_properties_env():
    # Render coloca los archivos secretos en esta carpeta
    secret_dir = os.environ.get("RENDER_SERVICE_SECRETS_DIR")

    if not secret_dir:
        print("No se encontró la variable RENDER_SERVICE_SECRETS_DIR.")
        return

    origen = os.path.join(secret_dir, "properties.env")

    if not os.path.exists(origen):
        print(f"No se encontró el archivo secreto en: {origen}")
        return

    destino = os.path.join("phishintel", "app", "properties.env")

    # Crear carpeta destino si no existe
    os.makedirs(os.path.dirname(destino), exist_ok=True)

    shutil.copy(origen, destino)

    print("✔ properties.env copiado correctamente a phishintel/app/")
