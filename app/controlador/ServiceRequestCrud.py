from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.servicerequest import ServiceRequest

collection = connect_to_mongodb("HIS", "serviceRequest")

def GetServiceRequestById(sr_id: str):
    try:
        service_request = collection.find_one({"_id": ObjectId(sr_id)})
        if service_request:
            service_request["_id"] = str(service_request["_id"])
            return "success", service_request
        return "notFound", None
    except Exception as e:
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
        return "notFound", None        

def WriteServiceRequest(sr_dict: dict):
    try:
        sr = ServiceRequest.model_validate(sr_dict)
    except Exception as e:
        print("Error de validación en ServiceRequest:", e)
        return f"errorValidating: {str(e)}", None

    validated_sr_json = sr.model_dump()
    result = collection.insert_one(validated_sr_json)
    if result:
        inserted_id = str(result.inserted_id)
        return "success", inserted_id
    else:
        return "errorInserting", None
