import os
import firebase_admin
from firebase_admin import credentials,firestore
from dotenv import load_dotenv
# Carga las variables de entorno desde el archivo .env
load_dotenv()

def get_firestore_client():
    # Verifica si ya existe una app de Firebase inicializada
    # (evita inicializarla más de una vez)
    if not firebase_admin._apps:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        
        file_name = os.getenv('FIREBASE_KEYS_PATH')
        # Construye la ruta completa al archivo JSON de credenciales
        cert_path = os.path.join(base_dir, file_name)
        
        cred = credentials.Certificate(cert_path)
        # Inicializa la app de Firebase con las credenciales
        firebase_admin.initialize_app(cred)
        
    return firestore.client()