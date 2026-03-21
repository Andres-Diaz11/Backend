from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import TareasSerializer
from .authentication import FirebaseAuthentication
from backend.firebase_config import get_firestore_client
from firebase_admin import firestore

db = get_firestore_client()


class TareaAPIView(APIView):

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]

    # =========================
    # GET - Traer tareas del usuario
    # =========================
    def get(self, request, tarea_id=None):

        uid_usuario = request.user.uid
        rol_usuario = request.user.rol
        
        #parametros de la consulta
        
        limit = int(request.query_params.get('limit', 10))
        last_doc_id = request.query_params.get('last_doc_id')
        
        #definir la consulta del rol
        if rol_usuario == 'instructor':
            # no tiene nungun filtro 
            query = db.collection('api_tareas')
            mensaje = "listar como rol del instructor"
            
        else:
            #se filtra por si uid
            query = db.collection('api_tareas').where('usuario_id','==', uid_usuario)
            mensaje = "listado como aprendiz"
            
            
        #ordenar
        query = query.order_by('fecha_creacion')
        
        #logica de la paginacion
        if last_doc_id:
            last_doc = db.collection('api_tareas').document(last_doc_id).get()
            if last_doc.exists:
                query = query.start_after(last_doc)
                
                
        #aplica el limite
        docs = query.limit(limit).stream()
        

        # try:
        #     # Si es instructor → ver todas
        #     if rol_usuario == 'instructor':
        #         docs = db.collection('api_tareas').stream()

        #     # Si NO es instructor → solo sus tareas
        #     else:
        #         docs = db.collection('api_tareas') \
        #             .where('usuario_id', "==", uid_usuario) \
        #             .stream()

        tareas = []

        for doc in docs:
            tarea_data = doc.to_dict()
            tarea_data['id'] = doc.id
            tareas.append(tarea_data)

        return Response(
            {"mensaje": mensaje,#mensaje es listando como rol de instructor
             "total en pagina": len(tareas), #el len es para contar el numero de tareas y haci traerlas en orden y con cantidades exactas
             "datos":tareas, # trae todas las tareas con sus atributos de las propias
             "next_page_token": tareas [-1]['id']if tareas else None
             },status=status.HTTP_200_OK)

    #esto de codigo anterior para traer los datos de la ultima y se vea en diferentes paginar como un libro pj 1 aparte colocamos 10 y las separa pj 1 10 pj2 10 
    
        # except Exception as e:
        #     return Response(
        #         {"error": str(e)},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
    # =========================
    # POST - Crear tarea
    # =========================
    def post(self, request):

        serializer = TareasSerializer(data=request.data)

        if serializer.is_valid():

            datos_validados = serializer.validated_data
            datos_validados['usuario_id'] = request.user.uid
            datos_validados['fecha_creacion'] = firestore.SERVER_TIMESTAMP

            try:
                nuevo_doc = db.collection('api_tareas').add(datos_validados)
                id_generado = nuevo_doc[1].id

                return Response(
                    {
                        "mensaje": "Tarea creada correctamente",
                        "id": id_generado
                    },
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # =========================
    # PUT - Actualizar tarea
    # =========================
    def put(self, request, tarea_id=None):

        if not tarea_id:
            return Response(
                {"error": "El ID es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tarea_ref = db.collection('api_tareas').document(tarea_id)
            doc = tarea_ref.get()

            if not doc.exists:
                return Response(
                    {"error": "No encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )

            tarea_data = doc.to_dict()

            if tarea_data.get('usuario_id') != request.user.uid:
                return Response(
                    {"error": "No tienes acceso a esta tarea"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = TareasSerializer(
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                tarea_ref.update(serializer.validated_data)

                return Response(
                    {
                        "mensaje": f"Tarea {tarea_id} actualizada",
                        "datos": serializer.validated_data
                    },
                    status=status.HTTP_200_OK
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # =========================
    # DELETE - Eliminar tarea
    # =========================
    def delete(self, request, tarea_id=None):

        if not tarea_id:
            return Response(
                {"error": "El ID es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tarea_ref = db.collection('api_tareas').document(tarea_id)
            doc = tarea_ref.get()

            if not doc.exists:
                return Response(
                    {"error": "No encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )

            tarea_data = doc.to_dict()

            
            # Permitir eliminar si:
            # - Es instructor
            # - O es el dueño de la tarea
            if request.user.rol != "instructor" and \
            tarea_data.get("usuario_id") != request.user.uid:

                return Response(
                    {"error": "No tienes permiso para eliminar esta tarea"},
                    status=status.HTTP_403_FORBIDDEN
                )

            tarea_ref.delete()

            return Response(
                {"mensaje": f"Tarea {tarea_id} eliminada"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )