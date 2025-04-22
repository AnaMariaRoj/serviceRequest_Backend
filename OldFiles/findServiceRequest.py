from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Función para conectar a la base de datos MongoDB
def connect_to_mongodb(uri, db_name, collection_name):
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[db_name]
    collection = db[collection_name]
    return collection

# Función para buscar solicitudes de servicio por identifier de paciente
def find_service_request_by_identifier(collection, identifier_value):
    try:
        query = {"subject.identifier.value": identifier_value}
        service_request = collection.find_one(query)
        return service_request
    except Exception as e:
        print(f"Error al buscar en MongoDB: {e}")
        return None

# Función para mostrar los datos de una solicitud de servicio
def display_service_request(service_request):
    if service_request:
        print("Solicitud de servicio encontrada:")
        print(f"  ID: {service_request.get('_id')}")
        print(f"  Estado: {service_request.get('status', 'Desconocido')}")
        print(f"  Intención: {service_request.get('intent', 'Desconocida')}")
        print(f"  Tipo de servicio: {service_request.get('code', {}).get('text', 'Desconocido')}")
        print(f"  Fecha: {service_request.get('authoredOn', 'Desconocida')}")
        print(f"  Solicitado por: {service_request.get('requester', {}).get('display', 'Desconocido')}")
        print(f"  Paciente: {service_request.get('subject', {}).get('display', 'Desconocido')}")
    else:
        print("No se encontró ninguna solicitud con el identifier especificado.")

# Ejemplo de uso
if __name__ == "__main__":
    uri = "mongodb+srv://mardugo:clave@sampleinformationservic.t2yog.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
    db_name = "HIS"
    collection_name = "serviceRequest"

    collection = connect_to_mongodb(uri, db_name, collection_name)
    
    identifier_value = "1020713756"
    
    service_request = find_service_request_by_identifier(collection, identifier_value)
    
    display_service_request(service_request)
