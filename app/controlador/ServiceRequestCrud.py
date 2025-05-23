# ServiceRequestCrud.py del backend (Corregido)

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId # Para trabajar con IDs de MongoDB
from fhir.resources.servicerequest import ServiceRequest # Modelo FHIR ServiceRequest
from fhir.resources.bundle import Bundle # Podría ser útil si manejas bundles de recursos
from fhir.resources.patient import Patient # Importar el recurso Patient si lo vas a usar
from fhir.resources.practitioner import Practitioner # Importar el recurso Practitioner si lo vas a usar
import json # Para pretty-print de JSON en logs
import logging # Para un manejo de logs más profesional

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Conexión a la base de datos ---
# NOTA: En un entorno de producción, la URI de conexión (incluyendo usuario y contraseña)
# debería cargarse desde variables de entorno para mayor seguridad y flexibilidad.
MONGODB_URI = "mongodb+srv://mardugo:clave@sampleinformationservic.t2yog.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
DB_NAME = "HIS"
SERVICE_REQUEST_COLLECTION = "serviceRequest"
PATIENT_COLLECTION = "patient" # Nombre de la colección para pacientes, si la creas
PRACTITIONER_COLLECTION = "practitioner" # Nombre de la colección para médicos, si la creas

_db_client = None # Para almacenar el cliente de MongoDB
_db_collection_sr = None # Para la colección de ServiceRequest
_db_collection_patient = None # Para la colección de Patient (opcional, para futura expansión)

def connect_to_mongodb():
    global _db_client, _db_collection_sr, _db_collection_patient

    if _db_client and _db_client.server_info(): # Reutilizar la conexión si ya existe y es válida
        logging.info("Reutilizando conexión existente a MongoDB.")
        return _db_collection_sr, _db_collection_patient

    try:
        _db_client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        _db_client.admin.command('ping') # Probar la conexión

        db = _db_client[DB_NAME]
        _db_collection_sr = db[SERVICE_REQUEST_COLLECTION]
        _db_collection_patient = db[PATIENT_COLLECTION] # Puedes inicializar esta colección también
        logging.info(f"Conectado a las colecciones '{SERVICE_REQUEST_COLLECTION}' y '{PATIENT_COLLECTION}' en la base de datos '{DB_NAME}'.")
        return _db_collection_sr, _db_collection_patient
    except Exception as e:
        logging.critical(f"ERROR CRÍTICO: No se pudo conectar a MongoDB. La aplicación no puede continuar. Detalles: {e}")
        # En una aplicación real, aquí podrías manejar un reintento o un mecanismo de alerta.
        raise # Vuelve a lanzar la excepción para que el servidor falle si no hay conexión

# Inicializar la conexión al cargar el módulo
try:
    service_request_collection, patient_collection = connect_to_mongodb()
except Exception:
    # Asegura que si la conexión falla al inicio, el programa se detenga.
    logging.critical("Error al inicializar la conexión a la base de datos. Saliendo.")
    exit(1)


# --- Funciones CRUD para ServiceRequest ---

def GetServiceRequestById(sr_id: str):
    logging.info(f"Intentando obtener ServiceRequest por ID: {sr_id}")
    try:
        if not ObjectId.is_valid(sr_id):
            logging.warning(f"ID proporcionado '{sr_id}' no es un ObjectId válido.")
            return "invalidId", None

        service_request = service_request_collection.find_one({"_id": ObjectId(sr_id)})
        if service_request:
            service_request["_id"] = str(service_request["_id"]) # Convertir ObjectId a string para JSON
            logging.info(f"ServiceRequest encontrado para ID: {sr_id}")
            return "success", service_request
        logging.info(f"ServiceRequest no encontrado para ID: {sr_id}")
        return "notFound", None
    except Exception as e:
        logging.error(f"Fallo al obtener ServiceRequest por ID '{sr_id}': {e}")
        return "error", str(e)


def GetServiceRequestByIdentifier(patient_system: str, patient_value: str):
    logging.info(f"Intentando obtener ServiceRequest por identificador de paciente: system='{patient_system}', value='{patient_value}'")
    try:
        # **Importante:** Tu frontend envía 'patientIdentifier' como un campo auxiliar.
        # Aquí buscamos ese campo. Si en el futuro tienes un recurso Patient y quieres buscar
        # ServiceRequests por el ID real del Patient referenciado, la lógica sería diferente.
        query = {
            "patientIdentifier.system": patient_system,
            "patientIdentifier.value": patient_value
        }
        
        service_request = service_request_collection.find_one(query)

        if service_request:
            service_request["_id"] = str(service_request["_id"])
            logging.info(f"ServiceRequest encontrado por identificador de paciente: {patient_value}")
            return "success", service_request
        logging.info(f"ServiceRequest no encontrado por identificador de paciente: {patient_value}")
        return "notFound", None
    except Exception as e:
        logging.error(f"Fallo al obtener ServiceRequest por identificador '{patient_system}|{patient_value}': {e}")
        return "error", str(e)


def WriteServiceRequest(sr_dict: dict):
    logging.info("Iniciando WriteServiceRequest...")
    logging.debug(f"Datos recibidos para ServiceRequest: {json.dumps(sr_dict, indent=2, ensure_ascii=False)}")

    # 1. Extraer el campo auxiliar 'patientIdentifier' antes de la validación FHIR.
    # Esto es crucial porque 'patientIdentifier' no es un campo estándar en el modelo FHIR ServiceRequest,
    # y si lo dejas, la validación de fhir.resources fallará.
    patient_identifier_data = sr_dict.pop("patientIdentifier", None)
    
    # 2. (Opcional, pero recomendado para un HIS real): Manejar el recurso Patient.
    # En un sistema real, aquí buscarías si el paciente ya existe en tu colección 'patient'.
    # Si no existe, lo crearías. Luego, actualizarías sr_dict['subject']['reference']
    # para apuntar al ID del Patient real en tu base de datos.
    # Por ahora, simplemente lo extraemos y lo re-añadimos al final.
    
    try:
        # 3. Validar el ServiceRequest con el modelo FHIR oficial.
        # El sr_dict en este punto ya no debe contener 'patientIdentifier' para la validación.
        sr_resource = ServiceRequest.model_validate(sr_dict)
        logging.info("ServiceRequest validado correctamente por el modelo FHIR.")
        
        # 4. Convertir el modelo FHIR validado a un diccionario para MongoDB.
        # by_alias=True asegura que los nombres de los campos sigan el estándar FHIR (ej. resourceType en lugar de resource_type).
        # exclude_unset=True evita incluir campos que no fueron explícitamente seteados.
        validated_data_for_mongo = sr_resource.model_dump(by_alias=True, exclude_unset=True)

        # 5. Re-añadir el campo 'patientIdentifier' al diccionario que se guardará en MongoDB.
        # Hacemos esto para que la información del identificador del paciente quede registrada en la base de datos
        # junto con el ServiceRequest, incluso si no es parte del modelo FHIR estricto.
        if patient_identifier_data:
            validated_data_for_mongo["patientIdentifier"] = patient_identifier_data

    except Exception as e: # Captura cualquier error durante la validación FHIR
        logging.error(f"Error de validación FHIR para ServiceRequest: {e}")
        logging.debug(f"Datos originales que causaron el error de validación: {json.dumps(sr_dict, indent=2, ensure_ascii=False)}")
        return f"errorValidating: {str(e)}", None

    try:
        # 6. Insertar el ServiceRequest validado y enriquecido en la colección de MongoDB.
        result = service_request_collection.insert_one(validated_data_for_mongo)
        
        if result.inserted_id:
            inserted_id = str(result.inserted_id)
            logging.info(f"ServiceRequest insertado con éxito. MongoDB ID: {inserted_id}")
            
            # Devuelve el documento completo con el _id generado por MongoDB
            # Esto es muy útil para que el frontend pueda mostrar el ID real de la DB.
            validated_data_for_mongo["_id"] = inserted_id 
            return "success", validated_data_for_mongo
        else:
            logging.error("Fallo en la inserción de ServiceRequest: inserted_id no encontrado.")
            return "errorInserting", None
    except Exception as e:
        logging.error(f"Excepción durante la inserción en MongoDB: {e}")
        return f"errorInserting: {str(e)}", None


def GetAllServiceRequests():
    logging.info("Intentando obtener todos los ServiceRequest.")
    try:
        # Usamos la colección inicializada al cargar el módulo
        all_docs = list(service_request_collection.find({}))
        
        for doc in all_docs:
            doc["_id"] = str(doc["_id"]) # Asegurar que _id sea string para JSON
        
        logging.info(f"Se encontraron {len(all_docs)} ServiceRequests.")
        return "success", all_docs
    except Exception as e:
        logging.error(f"Error al obtener todos los ServiceRequest: {e}")
        return "error", str(e)