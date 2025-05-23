# readServiceRequest.py del backend (Corregido)

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId # Importar ObjectId para manejar _id de MongoDB
import logging # Para un manejo de logs más profesional
import json # Para imprimir el JSON completo si es necesario

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
        logging.info("Reutilizando conexión existente a MongoDB en readServiceRequest.py.")
        return _db_collection_sr

    try:
        _db_client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        _db_client.admin.command('ping') # Probar la conexión
        
        db = _db_client[DB_NAME]
        _db_collection_sr = db[SERVICE_REQUEST_COLLECTION]
        logging.info(f"Conectado a la colección '{SERVICE_REQUEST_COLLECTION}' en la base de datos '{DB_NAME}'.")
        return _db_collection_sr
    except Exception as e:
        logging.critical(f"ERROR CRÍTICO: No se pudo conectar a MongoDB en readServiceRequest.py. Detalles: {e}")
        raise # Levanta la excepción para que el script falle si no puede conectar

# --- Función para leer todas las solicitudes de servicio ---
def read_all_service_requests_from_mongodb(collection):
    logging.info("Leyendo todas las solicitudes de servicio de MongoDB.")
    try:
        service_requests = collection.find({}) # Vacío para obtener todos los documentos
        # Convertir ObjectId a string para cada documento antes de devolver la lista
        result_list = []
        for sr in service_requests:
            if '_id' in sr:
                sr['_id'] = str(sr['_id'])
            result_list.append(sr)
        
        logging.info(f"Se leyeron {len(result_list)} solicitudes de servicio.")
        return result_list
    except Exception as e:
        logging.error(f"Error al leer desde MongoDB: {e}")
        return None

# --- Función para mostrar las solicitudes de servicio (estructura FHIR) ---
def display_service_requests(service_request_list):
    if service_request_list:
        print("\n--- Listado de Solicitudes de Servicio ---")
        for i, sr in enumerate(service_request_list):
            print(f"\n--- Solicitud de Servicio #{i+1} ---")
            
            # Imprime el JSON completo para una visión detallada
            print("JSON completo del ServiceRequest:")
            print(json.dumps(sr, indent=2, ensure_ascii=False))
            
            # Luego, imprime un resumen más legible
            print("\nDetalles resumidos:")
            print(f"  ID de MongoDB: {sr.get('_id', 'No especificado')}")
            print(f"  ID FHIR (si aplica): {sr.get('id', 'No especificado')}") # El 'id' de FHIR no es el '_id' de Mongo
            print(f"  Estado: {sr.get('status', 'No especificado')}")
            print(f"  Intención: {sr.get('intent', 'No especificado')}")

            code = sr.get('code', {})
            coding_list = code.get('coding', [])
            if coding_list:
                print("  Tipo de Servicio:")
                for coding in coding_list:
                    print(f"    - Sistema: {coding.get('system', 'No especificado')}")
                    print(f"      Código: {coding.get('code', 'No especificado')}")
                    print(f"      Descripción: {coding.get('display', 'No especificado')}")
            else:
                print("  Tipo de servicio: No especificado")

            # Mostrar información del sujeto (paciente)
            subject = sr.get('subject', {})
            print(f"  Paciente (Referencia): {subject.get('reference', 'No especificado')}")
            print(f"  Paciente (Display): {subject.get('display', 'No especificado')}")
            
            # Mostrar el identificador auxiliar del paciente si existe
            patient_id_data = sr.get('patientIdentifier', {})
            if patient_id_data:
                print(f"  Identificador de Paciente (Auxiliar) - Sistema: {patient_id_data.get('system', 'No especificado')}")
                print(f"                                   Valor: {patient_id_data.get('value', 'No especificado')}")

            print(f"  Solicitado por: {sr.get('requester', {}).get('display', 'No especificado')}")
            print(f"  Fecha de Solicitud: {sr.get('authoredOn', 'No especificado')}")
            
            notes = sr.get('note', [])
            if notes and notes[0].get('text'):
                print(f"  Notas: {notes[0].get('text')}")
            else:
                print("  Notas: No hay notas.")
            
            print("-" * 50) # Separador entre solicitudes
    else:
        logging.info("No se encontraron solicitudes de servicio en la base de datos.")

# --- Ejemplo de uso ---
if __name__ == "__main__":
    # Intenta conectar a la base de datos al inicio
    try:
        service_request_collection = connect_to_mongodb()
    except Exception:
        logging.critical("No se pudo iniciar el script debido a un error de conexión a la base de datos.")
        exit(1) # Sale si la conexión falla
    
    service_requests_list = read_all_service_requests_from_mongodb(service_request_collection)
    
    if service_requests_list:
        display_service_requests(service_requests_list)
    else:
        logging.info("No hay solicitudes de servicio para mostrar.")