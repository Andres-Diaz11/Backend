from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
from backend.firebase_config import get_firestore_client

db = get_firestore_client()


class FirebaseAuthentication(BaseAuthentication):
    """
    Lee el token JWT del encabezado, lo valida y extrae el UID del usuario
    """

    def authenticate(self, request):

        auth_header = request.META.get('HTTP_AUTHORIZATION') or request.headers.get('Authorization')

        if not auth_header:
            return None

        partes = auth_header.split()

        if len(partes) != 2 or partes[0].lower() != 'bearer':
            return None

        token = partes[1]

        try:
            # Validar token con Firebase
            decoded_token = auth.verify_id_token(token)

            uid = decoded_token.get('uid')
            email = decoded_token.get('email')

            # Obtener perfil desde Firestore
            user_profile = db.collection('perfiles').document(uid).get()

            if user_profile.exists:
                rol = user_profile.to_dict().get('rol', 'aprendiz')
            else:
                rol = 'aprendiz'

            # Usuario personalizado compatible con Django
            class FirebaseUser:
                def __init__(self, uid, rol, email):
                    self.uid = uid
                    self.rol = rol
                    self.email = email
                    self.is_authenticated = True

            return (FirebaseUser(uid, rol, email), None)

        except Exception as e:
            raise AuthenticationFailed(
                f"Token no es válido o está expirado: {str(e)}"
            )