# findServiceRequest.py del backend (Corregido)

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId # Importar ObjectId para validación si se busca por _id
import logging # Para un manejo de logs más profesional

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuración de la base de datos ---
MONGODB_URI = "mongodb+srv://mardugo:clave@sampleinformationservic.t2yog.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
DB_NAME = "HIS"
SERVICE_REQUEST_COLLECTION = "serviceRequest"
PATIENT_COLLECTION = "patient" # Referencia por si lo usas

# --- Funciones de conexión ---
_db_client = None
_db_collection_sr = None

def connect_to_mongodb():
    global _db_client, _db_collection_sr

    if _db_client and _db_client.server_info():
        logging.info("Reutilizando conexión existente a MongoDB en findServiceRequest.py.")
        return _db_collection_sr

    try:
        _db_client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        _db_client.admin.command('ping') # Probar la conexión
        
        db = _db_client[DB_NAME]
        _db_collection_sr = db[SERVICE_REQUEST_COLLECTION]
        logging.info(f"Conectado a la colección '{SERVICE_REQUEST_COLLECTION}' en la base de datos '{DB_NAME}'.")
        return _db_collection_sr
    except Exception as e:
        logging.critical(f"ERROR CRÍTICO: No se pudo conectar a MongoDB en findServiceRequest.py. Detalles: {e}")
        raise # Levanta la excepción para que el script falle si no puede conectar

# --- Funciones de búsqueda ---

# Función para buscar solicitudes de servicio por el 'value' del identificador de paciente
def find_service_request_by_patient_identifier_value(collection, identifier_value: str):
    logging.info(f"Buscando ServiceRequest por identificador de paciente (value): {identifier_value}")
    try:
        # La búsqueda ahora utiliza el campo 'patientIdentifier.value' que añadimos
        # como auxiliar en el ServiceRequestCrud.py para almacenar este dato.
        query = {
            "patientIdentifier.value": identifier_value
        }
        service_request = collection.find_one(query)
        return service_request
    except Exception as e:
        logging.error(f"Error al buscar en MongoDB por identificador de paciente: {e}")
        return None

# Función para buscar solicitudes de servicio por ID de MongoDB (_id)
def find_service_request_by_mongo_id(collection, sr_id: str):
    logging.info(f"Buscando ServiceRequest por ID de MongoDB (_id): {sr_id}")
    try:
        if not ObjectId.is_valid(sr_id):
            logging.warning(f"ID proporcionado '{sr_id}' no es un ObjectId válido.")
            return None
        
        service_request = collection.find_one({"_id": ObjectId(sr_id)})
        return service_request
    except Exception as e:
        logging.error(f"Error al buscar en MongoDB por _id: {e}")
        return None

# --- Función para mostrar los datos ---
def display_service_request(service_request):
    if service_request:
        logging.info("Solicitud de servicio encontrada (formato HL7 FHIR aproximado):")
        # Asegúrate de que el _id sea un string para mostrarlo
        if "_id" in service_request and not isinstance(service_request["_id"], str):
            service_request["_id"] = str(service_request["_id"])
            
        print(json.dumps(service_request, indent=2, ensure_ascii=False))
        print("\n--- Detalles resumidos ---")
        print(f"  ID de MongoDB: {service_request.get('_id', 'Sin ID')}")
        print(f"  ID FHIR (si aplica): {service_request.get('id', 'No especificado')}")
        print(f"  Estado: {service_request.get('status', 'Desconocido')}")
        print(f"  Intención: {service_request.get('intent', 'Desconocida')}")

        # Mostrar información del código del servicio
        code = service_request.get('code', {})
        coding_list = code.get('coding', [])
        if coding_list:
            for coding in coding_list:
                print(f"  Servicio - Sistema: {coding.get('system', '')}")
                print(f"            Código: {coding.get('code', '')}")
                print(f"            Nombre: {coding.get('display', '')}")
        else:
            print("  Tipo de servicio: No especificado")

        # Mostrar información del sujeto (paciente)
        subject = service_request.get('subject', {})
        print(f"  Paciente (Referencia): {subject.get('reference', 'No especificado')}")
        print(f"  Paciente (Display): {subject.get('display', 'No especificado')}")
        
        # Mostrar el identificador auxiliar del paciente si existe
        patient_id_data = service_request.get('patientIdentifier', {})
        if patient_id_data:
            print(f"  Identificador de Paciente (Auxiliar) - Sistema: {patient_id_data.get('system', 'No especificado')}")
            print(f"                                   Valor: {patient_id_data.get('value', 'No especificado')}")

        # Mostrar información del solicitante (requester)
        requester = service_request.get('requester', {})
        print(f"  Solicitado por (Referencia): {requester.get('reference', 'No especificado')}")
        print(f"                (Display): {requester.get('display', 'No especificado')}")
        
        print(f"  Fecha de Solicitud: {service_request.get('authoredOn', 'No especificado')}")
        
        # Mostrar notas
        notes = service_request.get('note', [])
        if notes:
            print(f"  Notas: {notes[0].get('text', 'N/A')}")
        else:
            print("  Notas: No hay notas.")
        
    else:
        logging.info("No se encontró ninguna solicitud de servicio con los criterios especificados.")

# --- Ejemplo de uso ---
if __name__ == "__main__":
    # Intenta conectar a la base de datos al inicio
    try:
        service_request_collection = connect_to_mongodb()
    except Exception:
        logging.critical("No se pudo iniciar el script debido a un error de conexión a la base de datos.")
        exit(1) # Sale si la conexión falla

    # --- Ejemplo de búsqueda por identificador de paciente ---
    # Reemplaza '1020713756' con un número de documento que esperes encontrar.
    # Puedes usar el que usaste al llenar el formulario en el frontend.
    identifier_to_find = "1020713756" 
    logging.info(f"\n--- Buscando ServiceRequest por identificador de paciente: {identifier_to_find} ---")
    found_sr_by_identifier = find_service_request_by_patient_identifier_value(service_request_collection, identifier_to_find)
    display_service_request(found_sr_by_identifier)

    # --- Ejemplo de búsqueda por ID de MongoDB (_id) ---
    # Después de ejecutar el frontend y guardar un ServiceRequest,
    # copia el 'ID de solicitud en DB' que te muestra el mensaje de éxito.
    # Pégalo aquí para buscar ese registro específico.
    # Si no tienes un ID aún, puedes dejarlo comentado o poner un ID de ejemplo (que no funcionará si no existe).
    # mongo_id_to_find = "66504a37e1b9b1d9d1e4e6c7" # Reemplaza con un ID real de tu DB
    # logging.info(f"\n--- Buscando ServiceRequest por ID de MongoDB (_id): {mongo_id_to_find} ---")
    # found_sr_by_mongo_id = find_service_request_by_mongo_id(service_request_collection, mongo_id_to_find)
    # display_service_request(found_sr_by_mongo_id)