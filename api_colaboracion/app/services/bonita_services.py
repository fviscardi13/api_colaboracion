import requests
from flask import current_app

def iniciar_proceso_bonita(nombre_proceso):
    base = current_app.config["BONITA_BASE_URL"]
    url = f"{base}/API/bpm/process?p=0&c=10&o=displayName ASC&f=displayName={nombre_proceso}"
    try:
        resp = requests.get(url, auth=(
            current_app.config["BONITA_USER"],
            current_app.config["BONITA_PASS"]
        ))
        return resp.json()
    except Exception as e:
        return {"error": str(e)}