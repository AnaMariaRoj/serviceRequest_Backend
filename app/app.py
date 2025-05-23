from fastapi import FastAPI, HTTPException, Request
import uvicorn
# Importamos las funciones CRUD específicas para ServiceRequest
from app.controlador.ServiceRequestCrud import GetServiceRequestById, GetServiceRequestByIdentifier, WriteServiceRequest
from fastapi.middleware.cors import CORSMiddleware
import json # Importar json para depuración si es necesario

app = FastAPI()

# Configuración de CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # **ADVERTENCIA**: En producción, reemplaza "*" con el/los dominio(s) de tu frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Ruta para obtener un ServiceRequest por ID
@app.get("/servicerequest/{sr_id}", response_model=dict)
async def get_service_request_by_id(sr_id: str):
    print(f"DEBUG: GET /servicerequest/{sr_id} recibido.") # Debug
    status, sr = GetServiceRequestById(sr_id)
    if status == 'success':
        return sr
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="ServiceRequest not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error fetching ServiceRequest by ID: {status}")

# Ruta para obtener un ServiceRequest por identificador de paciente
@app.get("/servicerequest/", response_model=dict)
async def get_service_request_by_identifier(system: str, value: str):
    print(f"DEBUG: GET /servicerequest/ con system={system}, value={value} recibido.") # Debug
    status, sr = GetServiceRequestByIdentifier(system, value)
    if status == 'success':
        return sr
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="ServiceRequest not found for provided identifier")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error fetching ServiceRequest by identifier: {status}")

# Ruta para agregar un nuevo ServiceRequest (POST)
@app.post("/servicerequest", response_model=dict)
async def add_service_request(request: Request):
    print("DEBUG: POST /servicerequest recibido.") # Debug
    try:
        # Obtenemos el cuerpo de la solicitud como un diccionario JSON
        new_sr_dict = dict(await request.json())
        print(f"DEBUG: Cuerpo de la solicitud JSON recibido: {json.dumps(new_sr_dict, indent=2, ensure_ascii=False)}") # Debug

        # Llamamos a la función del CRUD para escribir la solicitud de servicio en la base de datos
        status, sr_id = WriteServiceRequest(new_sr_dict)

        if status == 'success':
            print(f"DEBUG: Solicitud de servicio guardada con éxito. ID: {sr_id}") # Debug
            return {"_id": sr_id}
        elif "errorValidating" in status:
            print(f"ERROR: Fallo en la validación de ServiceRequest: {status}") # Debug
            raise HTTPException(status_code=422, detail=f"Validation Error: {status}")
        elif "errorInserting" in status:
            print(f"ERROR: Fallo en la inserción de ServiceRequest en DB: {status}") # Debug
            raise HTTPException(status_code=500, detail=f"Database Insertion Error: {status}")
        else:
            print(f"ERROR: Error interno desconocido al procesar ServiceRequest: {status}") # Debug
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {status}")
    
    except Exception as e:
        print(f"ERROR: Excepción inesperada en add_service_request: {e}") # Debug
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Bloque para ejecutar la aplicación con Uvicorn si se ejecuta directamente este archivo
# En un entorno de producción (como Render), esto es gestionado por el servidor de aplicaciones
# (Gunicorn, por ejemplo), por lo que normalmente estaría comentado o ajustado.
# if __name__ == '__main__':
#     print("DEBUG: Iniciando servidor Uvicorn localmente (si se ejecuta directamente este archivo).") # Debug
#     uvicorn.run(app, host="0.0.0.0", port=8000)