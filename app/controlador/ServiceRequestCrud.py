from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from fhir.resources.servicerequest import ServiceRequest
import json # Importar json para poder imprimir el dict si es necesario

# Función para conectar a la base de datos MongoDB
# NOTA: En un entorno de producción, la URI de conexión (incluyendo usuario y contraseña)
# debería cargarse desde variables de entorno para mayor seguridad y flexibilidad.
def connect_to_mongodb(db_name, collection_name):
    uri = "mongodb+srv://mardugo:clave@sampleinformationservic.t2yog.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[db_name]
    collection = db[collection_name]
    print(f"DEBUG: Conectado a la colección '{collection_name}' en la base de datos '{db_name}'.") # Debug
    return collection

# La colección se inicializa cuando el módulo es importado
collection = connect_to_mongodb("HIS", "serviceRequest")

def GetServiceRequestById(sr_id: str):
    try:
        service_request = collection.find_one({"_id": ObjectId(sr_id)})
        if service_request:
            service_request["_id"] = str(service_request["_id"])
            return "success", service_request
        return "notFound", None
    except Exception as e:
        print(f"ERROR: Fallo al obtener ServiceRequest por ID '{sr_id}': {e}") # Debug
        return "notFound", None

def GetServiceRequestByIdentifier(patientSystem, patientValue):
    try:
        service_request = collection.find_one({
            "subject.identifier.system": patientSystem, 
            "subject.identifier.value": patientValue
        })
        if service_request:
            service_request["_id"] = str(service_request["_id"])
            return "success", service_request
        return "notFound", None
    except Exception as e:
        print(f"ERROR: Fallo al obtener ServiceRequest por identificador '{patientSystem}|{patientValue}': {e}") # Debug
        return "notFound", None        

def WriteServiceRequest(sr_dict: dict):
    print("DEBUG: Iniciando WriteServiceRequest...") # Debug
    print(f"DEBUG: Datos recibidos para ServiceRequest: {json.dumps(sr_dict, indent=2, ensure_ascii=False)}") # Debug

    try:
        sr = ServiceRequest.model_validate(sr_dict)
        print("DEBUG: ServiceRequest validado correctamente por el modelo FHIR.") # Debug
    except Exception as e:
        print(f"ERROR: Error de validación en ServiceRequest: {e}") # Debug
        # Puedes imprimir el dict recibido si quieres ver la causa exacta de la validación fallida
        # print(f"DEBUG: Datos que causaron el error de validación: {json.dumps(sr_dict, indent=2, ensure_ascii=False)}")
        return f"errorValidating: {str(e)}", None

    validated_sr_json = sr.model_dump()
    print(f"DEBUG: Datos validados y listos para insertar en MongoDB: {json.dumps(validated_sr_json, indent=2, ensure_ascii=False)}") # Debug

    try:
        result = collection.insert_one(validated_sr_json)
        if result.inserted_id:
            inserted_id = str(result.inserted_id)
            print(f"DEBUG: ServiceRequest insertado con éxito. ID: {inserted_id}") # Debug
            return "success", inserted_id
        else:
            print("ERROR: Fallo en la inserción de ServiceRequest: inserted_id no encontrado.") # Debug
            return "errorInserting", None
    except Exception as e:
        print(f"ERROR: Excepción durante la inserción en MongoDB: {e}") # Debug
        return "errorInserting: {str(e)}", None

def GetAllServiceRequests():
    try:
        collection = connect_to_mongodb()
        all_docs = list(collection.find({}))
        for doc in all_docs:
            doc["_id"] = str(doc["_id"])  # Convertir ObjectId a string
        return "success", all_docs
    except Exception as e:
        print(f"Error al obtener todos los ServiceRequest: {e}")
        return "error", []