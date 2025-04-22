import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from fhir.resources.servicerequest import ServiceRequest

def connect_to_mongodb():
    """ Conecta a la base de datos MongoDB """
    uri = "mongodb+srv://mardugo:clave@sampleinformationservic.t2yog.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["HIS"]
    return db["serviceRequest"]  # <--- usamos la colección correcta

def save_service_request_to_mongodb(service_request_data, collection):
    try:
        # Si el input es string, convertir a dict
        if isinstance(service_request_data, str):
            service_request_data = json.loads(service_request_data)

        # Validar el recurso FHIR ServiceRequest
        sr = ServiceRequest.model_validate(service_request_data)
        validated_data = sr.model_dump()

        # Insertar en MongoDB
        result = collection.insert_one(validated_data)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error al guardar ServiceRequest en MongoDB: {e}")
        return None

def WriteServiceRequest(service_request_json):
    """ Guarda una solicitud médica en MongoDB """
    collection = connect_to_mongodb()
    inserted_id = save_service_request_to_mongodb(service_request_json, collection)
    
    if inserted_id:
        return "success", inserted_id
    else:
        return "error", None
