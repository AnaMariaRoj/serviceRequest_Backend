from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Función para conectar a la base de datos MongoDB
def connect_to_mongodb(uri, db_name, collection_name):
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[db_name]
    collection = db[collection_name]
    return collection

# Función para leer todas las solicitudes de servicio
def read_service_requests_from_mongodb(collection):
    try:
        service_requests = collection.find()
        return list(service_requests)
    except Exception as e:
        print(f"Error al leer desde MongoDB: {e}")
        return None

# Función para mostrar las solicitudes de servicio
def display_service_requests(service_request_list):
    if service_request_list:
        for sr in service_request_list:
            print("Solicitud de Servicio:")
            print(f"  ID: {sr.get('_id')}")
            print(f"  Estado: {sr.get('status', 'No especificado')}")
            print(f"  Intención: {sr.get('intent', 'No especificado')}")
            print(f"  Tipo de servicio: {sr.get('code', {}).get('text', 'No especificado')}")
            print(f"  Solicitado por: {sr.get('requester', {}).get('display', 'No especificado')}")
            print(f"  Paciente: {sr.get('subject', {}).get('display', 'No especificado')}")
            print(f"  Fecha: {sr.get('authoredOn', 'No especificado')}")
            print("-" * 40)
    else:
        print("No se encontraron solicitudes de servicio en la base de datos.")

# Ejemplo de uso
if __name__ == "__main__":
    uri = "mongodb+srv://mardugo:clave@sampleinformationservic.t2yog.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
    db_name = "HIS"
    collection_name = "serviceRequest"

    collection = connect_to_mongodb(uri, db_name, collection_name)
    
    service_requests = read_service_requests_from_mongodb(collection)
    
    display_service_requests(service_requests)
