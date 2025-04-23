from fastapi import FastAPI, HTTPException, Request
import uvicorn
from ServiceRequestCrud import GetServiceRequestById, GetServiceRequestByIdentifier, WriteServiceRequest
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

@app.get("/servicerequest/{sr_id}", response_model=dict)
async def get_service_request_by_id(sr_id: str):
    status, sr = GetServiceRequestById(sr_id)
    if status == 'success':
        return sr
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="ServiceRequest not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

@app.get("/servicerequest/", response_model=dict)
async def get_service_request_by_identifier(system: str, value: str):
    status, sr = GetServiceRequestByIdentifier(system, value)
    if status == 'success':
        return sr
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="ServiceRequest not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

@app.post("/servicerequest", response_model=dict)
async def add_service_request(request: Request):
    new_sr_dict = dict(await request.json())
    status, sr_id = WriteServiceRequest(new_sr_dict)

    if status == 'success':
        return {"_id": sr_id}
    elif "errorValidating" in status:
        raise HTTPException(status_code=422, detail=f"Validation Error: {status}")
    else:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {status}")