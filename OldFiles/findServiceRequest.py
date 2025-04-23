from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Función para conectar a la base de datos MongoDB
def connect_to_mongodb(db_name, collection_name):
    uri = "mongodb+srv://mardugo:clave@sampleinformationservic.t2yog.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[db_name]
    collection = db[collection_name]
    return collection

# Función para buscar solicitudes de servicio por identifier (FHIR: subject.identifier.value)
def find_service_request_by_identifier(collection, identifier_value):
    try:
        query = {
            "subject.identifier.value": identifier_value
        }
        service_request = collection.find_one(query)
        return service_request
    except Exception as e:
        print(f"Error al buscar en MongoDB: {e}")
        return None

# Función para mostrar los datos de una solicitud de servicio con estructura HL7 FHIR
def display_service_request(service_request):
    if service_request:
        print("Solicitud de servicio encontrada:")
        print(f"  ID: {service_request.get('id', 'Sin ID')}")
        print(f"  Estado: {service_request.get('status', 'Desconocido')}")
        print(f"  Intención: {service_request.get('intent', 'Desconocida')}")

        # Mostrar codificación del código del servicio
        code = service_request.get('code', {})
        coding_list = code.get('coding', [])
        if coding_list:
            for coding in coding_list:
                print(f"  Servicio - Sistema: {coding.get('system', '')}")
                print(f"             Código: {coding.get('code', '')}")
                print(f"             Nombre: {coding.get
::contentReference[oaicite:0]{index=0}