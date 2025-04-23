import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.fhirabstractmodel import FHIRValidationError

# Función para conectar con MongoDB
def connect_to_mongodb():
    uri = "mongodb+srv://mardugo:clave@sampleinformationservic.t2yog.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["HIS"]
    return db["serviceRequest"]

# Función que valida y guarda el ServiceRequest
def save_service_request_to_mongodb(service_request_data, collection):
    try:
        if isinstance(service_request_data, str):
            service_request_data = json.loads(service_request_data)

        # Validar con el modelo FHIR
        sr = ServiceRequest.model_validate(service_request_data)
        validated_data = sr.model_dump()

        # Insertar en la colección
        result = collection.insert_one(validated_data)
        return "success", str(result.inserted_id)

    except FHIRValidationError as ve:
        print(f"Error de validación FHIR: {ve}")
        return "errorValidating", None

    except Exception as e:
        print(f"Error general al guardar en MongoDB: {e}")
        return "error", None

# Función que puede llamarse desde el backend
def WriteServiceRequest(service_request_json):
    collection = connect_to_mongodb()
    return save_service_request_to_mongodb(service_request_json, collection)