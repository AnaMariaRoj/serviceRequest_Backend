# app.py del backend (Corregido)

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvicorn_run # Renombrado para evitar conflictos

# Importamos las funciones CRUD específicas para ServiceRequest.
# Asumiendo que 'app.controlador' es la ruta correcta a tu ServiceRequestCrud.py
# Si ServiceRequestCrud.py está directamente en la misma carpeta que app.py,
# solo necesitarías: from ServiceRequestCrud import ...
from app.controlador.ServiceRequestCrud import (
    GetServiceRequestById,
    GetServiceRequestByIdentifier,
    WriteServiceRequest,
    GetAllServiceRequests
)
import json # Para pretty-print de JSON en logs
import logging # Para un manejo de logs más profesional

# Configuración básica de logging para FastAPI
# Esto asegura que los mensajes de log de FastAPI y tu código se muestren en la consola.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="HIS Service Request API",
    description="API para gestionar solicitudes de exámenes médicos (ServiceRequest) siguiendo estándares FHIR.",
    version="1.0.0"
)

# Configuración de CORS (Cross-Origin Resource Sharing)
# Esto es crucial para permitir que tu frontend (que corre en un origen diferente)
# pueda comunicarse con tu backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # **ADVERTENCIA**: En producción, reemplaza "*" con el/los dominio(s) de tu frontend
                          # Ejemplo: ["http://localhost:5500", "https://tufrontend.com"]
    allow_credentials=True, # Permitir cookies, cabeceras de autorización, etc.
    allow_methods=["*"],    # Permitir todos los métodos (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],    # Permitir todos los encabezados
)

# --- Rutas de la API para ServiceRequest ---

# Ruta para obtener un ServiceRequest por ID de MongoDB
@app.get("/servicerequest/{sr_id}", response_model=dict, summary="Obtener ServiceRequest por ID de MongoDB")
async def get_service_request_by_id(sr_id: str):
    logging.info(f"GET /servicerequest/{sr_id} recibido.")
    status_code, sr_data = GetServiceRequestById(sr_id) # sr_data es el dict del SR o None
    
    if status_code == 'success':
        return sr_data
    elif status_code == 'notFound':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ServiceRequest no encontrado con el ID proporcionado."
        )
    elif status_code == 'invalidId':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El formato del ID de ServiceRequest proporcionado no es válido."
        )
    else: # Esto capturaría 'error' o cualquier otro estado inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al obtener ServiceRequest por ID: {sr_data}" # sr_data aquí es el mensaje de error
        )

# Ruta para obtener un ServiceRequest por identificador de paciente (ej. número de documento)
@app.get("/servicerequest/by-patient-identifier", response_model=dict, summary="Obtener ServiceRequest por identificador de paciente")
async def get_service_request_by_identifier(system: str, value: str):
    logging.info(f"GET /servicerequest/by-patient-identifier con system='{system}', value='{value}' recibido.")
    status_code, sr_data = GetServiceRequestByIdentifier(system, value)
    
    if status_code == 'success':
        return sr_data
    elif status_code == 'notFound':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ServiceRequest no encontrado para el identificador de paciente proporcionado."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al obtener ServiceRequest por identificador de paciente: {sr_data}"
        )

# Ruta para crear un nuevo ServiceRequest (POST)
@app.post("/servicerequest", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo ServiceRequest")
async def add_service_request(request: Request):
    logging.info("POST /servicerequest recibido.")
    try:
        # FastAPI ya parsea el JSON del cuerpo de la solicitud automáticamente.
        # No necesitas await request.json() si usas Pydantic models directamente,
        # pero para recibir un dict genérico, Request.json() es válido.
        new_sr_dict = await request.json()
        logging.debug(f"Cuerpo de la solicitud JSON recibido: {json.dumps(new_sr_dict, indent=2, ensure_ascii=False)}")

        # Llamar a la función del CRUD para guardar el ServiceRequest
        # `result_data` ahora contendrá el dict completo del SR insertado, incluyendo el _id de MongoDB.
        status_code_crud, result_data = WriteServiceRequest(new_sr_dict)

        if status_code_crud == 'success':
            logging.info(f"Solicitud de servicio guardada con éxito. MongoDB ID: {result_data.get('_id', 'N/A')}")
            # Devolver el dict completo insertado, que incluye el _id de MongoDB.
            return result_data
        elif "errorValidating" in status_code_crud:
            logging.error(f"Fallo en la validación FHIR del ServiceRequest: {status_code_crud}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, # 422 para errores de validación de datos
                detail=f"Error de validación de datos FHIR: {status_code_crud.split(':', 1)[1] if ':' in status_code_crud else status_code_crud}"
            )
        elif "errorInserting" in status_code_crud:
            logging.error(f"Fallo en la inserción de ServiceRequest en MongoDB: {status_code_crud}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error de inserción en la base de datos: {status_code_crud.split(':', 1)[1] if ':' in status_code_crud else status_code_crud}"
            )
        else: # Capturar cualquier otro estado inesperado del CRUD
            logging.error(f"Error interno desconocido al procesar ServiceRequest: {status_code_crud}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {status_code_crud}"
            )
    except Exception as e:
        logging.error(f"Excepción inesperada en la ruta POST /servicerequest: {e}", exc_info=True) # exc_info para traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor al procesar la solicitud: {str(e)}"
        )

# Ruta para obtener todos los ServiceRequest
@app.get("/servicerequest/all", response_model=dict, summary="Obtener todas las solicitudes de examen")
async def get_all_service_requests():
    logging.info("GET /servicerequest/all recibido.")
    status_code, sr_list = GetAllServiceRequests()
    
    if status_code == 'success':
        return {"serviceRequests": sr_list}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al obtener todas las solicitudes de servicio: {sr_list}" # sr_list aquí es el mensaje de error
        )

# Bloque para ejecutar la aplicación con Uvicorn localmente
# Esto se activará cuando ejecutes 'python app.py' directamente.
# En un entorno de producción (como Render), el servidor de aplicaciones (Gunicorn)
# es quien llama a la aplicación FastAPI.
if __name__ == '__main__':
    logging.info("Iniciando servidor Uvicorn localmente en http://0.0.0.0:8000")
    uvicorn_run(app, host="0.0.0.0", port=8000)