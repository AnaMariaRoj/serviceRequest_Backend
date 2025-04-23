from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.fhirtypes import DateTime
from fhir.resources.fhirabstractmodel import FHIRValidationError
import json

# Función para validar y mostrar un recurso FHIR ServiceRequest
def validate_service_request(json_data):
    try:
        service_request = ServiceRequest.model_validate(json_data)
        print("JSON válido según HL7 FHIR:")
        print(json.dumps(service_request.model_dump(), indent=2, ensure_ascii=False))
    except FHIRValidationError as e:
        print("Error de validación FHIR:")
        print(e)

# Ejemplo de uso
if __name__ == "__main__":
    service_request_json = '''
    {
      "resourceType": "ServiceRequest",
      "status": "active",
      "intent": "order",
      "code": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "386053000",
            "display": "Evaluación médica general"
          }
        ],
        "text": "Consulta general"
      },
      "subject": {
        "reference": "Patient/1020713756",
        "display": "Mario Enrique Duarte"
      },
      "requester": {
        "reference": "Practitioner/12345",
        "display": "Dr. Juan Pérez"
      },
      "authoredOn": "2025-04-04T10:00:00Z"
    }
    '''

    json_data = json.loads(service_request_json)
    validate_service_request(json_data)