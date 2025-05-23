# validateServiceRequest.py del backend (Corregido)

from fhir.resources.servicerequest import ServiceRequest # Modelo FHIR ServiceRequest
from fhir.resources.fhirtypes import DateTime # Para tipos de datos FHIR si se necesitan en validación directa
from fhir.resources.fhirabstractmodel import FHIRValidationError # Para capturar errores específicos de validación FHIR
import json # Para trabajar con JSON
import logging # Para un manejo de logs más profesional

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Función para validar y mostrar un recurso FHIR ServiceRequest
def validate_and_display_service_request(json_data: dict):
    logging.info("Intentando validar el ServiceRequest JSON proporcionado.")
    try:
        # Aquí es donde ocurre la validación FHIR.
        # Recuerda que el campo 'patientIdentifier' que usamos en el frontend
        # y guardamos en MongoDB NO es parte del modelo FHIR ServiceRequest.
        # Si el JSON que pasas aquí contiene ese campo, la validación fallará.
        # Para probar la validación FHIR pura, asegúrate de que el JSON de ejemplo
        # no contenga campos no estándar del modelo ServiceRequest.
        
        # Si estás probando un JSON directamente de tu DB que *sí* tiene patientIdentifier,
        # necesitarías una lógica para removerlo antes de pasar a model_validate,
        # similar a como lo hacemos en WriteServiceRequest.
        
        service_request = ServiceRequest.model_validate(json_data)
        logging.info("JSON válido según el estándar HL7 FHIR ServiceRequest.")
        print("\n--- ServiceRequest FHIR validado (JSON) ---")
        print(json.dumps(service_request.model_dump(by_alias=True, exclude_unset=True), indent=2, ensure_ascii=False))
        
        # También puedes imprimir algunos detalles clave para confirmación
        print("\n--- Detalles resumidos de la validación ---")
        print(f"  resourceType: {service_request.resourceType}")
        print(f"  status: {service_request.status}")
        print(f"  intent: {service_request.intent}")
        if service_request.code and service_request.code.coding:
            print(f"  code (LOINC): {service_request.code.coding[0].code} - {service_request.code.coding[0].display}")
        if service_request.subject:
            print(f"  subject reference: {service_request.subject.reference}")
            print(f"  subject display: {service_request.subject.display}")
        if service_request.requester:
            print(f"  requester display: {service_request.requester.display}")
        print(f"  authoredOn: {service_request.authoredOn}")

    except FHIRValidationError as e:
        logging.error(f"ERROR: Fallo de validación FHIR.")
        print("\n--- Detalles del Error de Validación FHIR ---")
        print(f"Mensaje de error: {e}")
        # Puedes imprimir el JSON original para depurar qué causó el error
        logging.debug(f"JSON que causó el error de validación: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        logging.error(f"ERROR: Ocurrió un error inesperado durante la validación: {e}", exc_info=True)
        print(f"Error inesperado: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    # Este es un ejemplo de ServiceRequest JSON que debería ser válido según FHIR.
    # Es similar a lo que tu frontend enviaría, pero sin el campo 'patientIdentifier' auxiliar,
    # ya que ese campo no es parte del modelo FHIR ServiceRequest.
    # Si quieres probar un JSON de tu DB que sí tiene 'patientIdentifier',
    # tendrías que eliminarlo temporalmente antes de pasar el JSON a esta función.
    
    valid_service_request_json = '''
    {
      "resourceType": "ServiceRequest",
      "status": "active",
      "intent": "order",
      "code": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "57021-8",
            "display": "Hemograma completo (CBC)"
          }
        ],
        "text": "Hemograma completo (CBC)"
      },
      "subject": {
        "reference": "Patient/123456789",
        "display": "Juan Pérez"
      },
      "authoredOn": "2025-05-23T10:30:00Z",
      "note": [
        {
          "text": "Ayuno de 8 horas."
        }
      ],
      "requester": {
        "reference": "Practitioner/MedicoQueSolicita",
        "display": "Dr. Médico Solicitante"
      },
      "identifier": [
        {
          "system": "https://hospital.com/serviceRequest",
          "value": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
        }
      ]
    }
    '''

    # Ejemplo de un JSON con un error intencional (falta resourceType)
    invalid_service_request_json = '''
    {
      "status": "active",
      "intent": "order",
      "code": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "57021-8",
            "display": "Hemograma completo (CBC)"
          }
        ]
      },
      "subject": {
        "reference": "Patient/123",
        "display": "Paciente de Prueba"
      }
    }
    '''

    print("--- Prueba de Validación de ServiceRequest VÁLIDO ---")
    json_data_valid = json.loads(valid_service_request_json)
    validate_and_display_service_request(json_data_valid)

    print("\n" + "="*70 + "\n")

    print("--- Prueba de Validación de ServiceRequest INVÁLIDO (faltando 'resourceType') ---")
    json_data_invalid = json.loads(invalid_service_request_json)
    validate_and_display_service_request(json_data_invalid)