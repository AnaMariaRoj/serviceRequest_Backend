# writeServiceRequest.py del backend (Corregido)

import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId # Para trabajar con IDs de MongoDB
from fhir.resources.servicerequest import ServiceRequest # Modelo FHIR ServiceRequest
from fhir.resources.fhirabstractmodel import FHIRValidationError # Para capturar errores específicos de validación FHIR
import logging # Para un manejo de logs más profesional
import datetime # Para generar marcas de tiempo si se necesita

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuración de la base de datos ---
MONGODB_URI = "mongodb+srv://mardugo:clave@sampleinformationservic.t2yog.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
DB_NAME = "HIS"
SERVICE_REQUEST_COLLECTION = "serviceRequest"

# --- Funciones de conexión ---
_db_client = None
_db_collection_sr = None

def connect_to_mongodb():
    global _db_client, _db_collection_sr

    if _db_client and _db_client.server_info():
        logging.info("Reutilizando conexión existente a MongoDB en writeServiceRequest.py.")
        return _db_collection_sr

    try:
        _db_client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        _db_client.admin.command('ping') # Probar la conexión
        
        db = _db_client[DB_NAME]
        _db_collection_sr = db[SERVICE_REQUEST_COLLECTION]
        logging.info(f"Conectado a la colección '{SERVICE_REQUEST_COLLECTION}' en la base de datos '{DB_NAME}'.")
        return _db_collection_sr
    except Exception as e:
        logging.critical(f"ERROR CRÍTICO: No se pudo conectar a MongoDB en writeServiceRequest.py. Detalles: {e}")
        raise # Levanta la excepción para que el script falle si no puede conectar

# Función que valida y guarda el ServiceRequest
def save_service_request_to_mongodb(service_request_data: dict, collection):
    logging.info("Intentando guardar ServiceRequest en MongoDB.")
    
    # 1. Asegúrate de que los datos sean un diccionario Python, no una cadena JSON
    if isinstance(service_request_data, str):
        try:
            service_request_data = json.loads(service_request_data)
        except json.JSONDecodeError as jde:
            logging.error(f"Error al decodificar JSON de la solicitud: {jde}")
            return "errorInvalidJson", None

    # 2. Extraer el campo auxiliar 'patientIdentifier' antes de la validación FHIR.
    # Es crucial porque 'patientIdentifier' no es un campo estándar en el modelo FHIR ServiceRequest.
    patient_identifier_data = service_request_data.pop("patientIdentifier", None)
    
    try:
        # 3. Validar el ServiceRequest con el modelo FHIR oficial.
        # El service_request_data en este punto ya no debe contener 'patientIdentifier' para la validación.
        sr_resource = ServiceRequest.model_validate(service_request_data)
        logging.info("ServiceRequest validado correctamente por el modelo FHIR.")
        
        # 4. Convertir el modelo FHIR validado a un diccionario para MongoDB.
        validated_data_for_mongo = sr_resource.model_dump(by_alias=True, exclude_unset=True)

        # 5. Re-añadir el campo 'patientIdentifier' al diccionario que se guardará en MongoDB.
        if patient_identifier_data:
            validated_data_for_mongo["patientIdentifier"] = patient_identifier_data

    except FHIRValidationError as ve:
        logging.error(f"Error de validación FHIR para ServiceRequest: {ve}")
        logging.debug(f"Datos originales que causaron el error de validación: {json.dumps(service_request_data, indent=2, ensure_ascii=False)}")
        return f"errorValidating: {str(ve)}", None
    
    except Exception as e: # Captura cualquier otro error durante la validación o procesamiento previo
        logging.error(f"Error inesperado durante la validación o procesamiento de ServiceRequest: {e}", exc_info=True)
        return f"errorProcessing: {str(e)}", None

    try:
        # 6. Insertar el ServiceRequest validado y enriquecido en la colección de MongoDB.
        result = collection.insert_one(validated_data_for_mongo)
        
        if result.inserted_id:
            inserted_id = str(result.inserted_id)
            logging.info(f"ServiceRequest insertado con éxito. MongoDB ID: {inserted_id}")
            # Devuelve el documento completo con el _id generado por MongoDB
            validated_data_for_mongo["_id"] = inserted_id
            return "success", validated_data_for_mongo
        else:
            logging.error("Fallo en la inserción de ServiceRequest: inserted_id no encontrado.")
            return "errorInserting", None
    except Exception as e:
        logging.error(f"Excepción durante la inserción en MongoDB: {e}", exc_info=True)
        return f"errorInserting: {str(e)}", None

# Función que puede llamarse desde el backend (para ser usada por app.py, por ejemplo)
def WriteServiceRequest(service_request_json: dict):
    # La colección se obtiene al inicio del módulo y se reutiliza
    return save_service_request_to_mongodb(service_request_json, _db_collection_sr)

# --- Ejemplo de uso si se ejecuta el script directamente ---
if __name__ == "__main__":
    # Intenta conectar a la base de datos al inicio
    try:
        service_request_collection = connect_to_mongodb()
    except Exception:
        logging.critical("No se pudo iniciar el script debido a un error de conexión a la base de datos.")
        exit(1) # Sale si la conexión falla

    # Ejemplo de un ServiceRequest JSON para insertar
    # Asegúrate de cambiar los valores (ej. identifierValue) para que sean únicos
    # o para probar diferentes escenarios.
    sample_sr_data = {
      "resourceType": "ServiceRequest",
      "status": "active",
      "intent": "order",
      "" \
      "code": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "24331-1", # Perfil lipídico
            "display": "Perfil lipídico"
          }
        ],
        "text": "Solicitud de Perfil lipídico"
      },
      "subject": {
        "reference": "Patient/1020713756", # Usa el identificador del paciente aquí
        "display": "Juan Carlos Perez (via script)" # Nombre del paciente
      },
      "patientIdentifier": { # Campo auxiliar para el identificador de paciente
          "system": "http://hospital.com/patient-identifiers",
          "value": "1020713756" # El número de documento real
      },
      "authoredOn": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds') + 'Z', # Fecha y hora actual UTC
      "note": [
        {
          "text": "Paciente en ayunas de 12 horas. Historial de hiperlipidemia."
        }
      ],
      "requester": {
        "reference": "Practitioner/ScriptUser",
        "display": "Dr. Script Tester"
      },
      "identifier": [ # Un identificador único para esta solicitud de servicio
        {
          "system": "https://hospital.com/serviceRequest",
          "value": "req-" + ObjectId().__str__() # Genera un ID único basado en ObjectId
        }
      ]
    }

    logging.info("\n--- Intentando insertar un ServiceRequest de ejemplo ---")
    status_crud, result_data = save_service_request_to_mongodb(sample_sr_data, service_request_collection)

    if status_crud == "success":
        logging.info(f"¡ServiceRequest de ejemplo insertado con éxito! ID de MongoDB: {result_data['_id']}")
        logging.debug(f"Datos insertados: {json.dumps(result_data, indent=2, ensure_ascii=False)}")
    else:
        logging.error(f"Fallo al insertar ServiceRequest de ejemplo. Estado: {status_crud}, Detalles: {result_data}")

    # Ejemplo de un ServiceRequest inválido para probar la validación
    invalid_sample_sr_data = {
        "status": "active", # Falta resourceType
        "intent": "order"
    }
    logging.info("\n--- Intentando insertar un ServiceRequest INVÁLIDO de ejemplo ---")
    status_crud_invalid, result_data_invalid = save_service_request_to_mongodb(invalid_sample_sr_data, service_request_collection)
    if status_crud_invalid == "success":
        logging.warning("¡Advertencia! Se insertó un ServiceRequest inválido. Esto no debería pasar.")
    else:
        logging.info(f"Correcto: Fallo al insertar ServiceRequest inválido. Estado: {status_crud_invalid}")