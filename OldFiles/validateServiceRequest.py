from fhir.resources.servicerequest import ServiceRequest
import json

# Ejemplo de uso
if __name__ == "__main__":
    # JSON string correspondiente al artefacto ServiceRequest de HL7 FHIR
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

    # Validar el recurso ServiceRequest
    service_request = ServiceRequest.model_validate(json.loads(service_request_json))
    print("JSON validado:", service_request.model_dump())
