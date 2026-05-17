import json
import os
from datetime import datetime

LEADS_FILE = "leads_sinergia.json"

def registrar_lead(nombre, mensaje, interes="Bajo"):
    """
    Registra o actualiza un prospecto en el archivo local.
    """
    leads = []
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, "r", encoding="utf-8") as f:
                leads = json.load(f)
        except:
            leads = []

    # Buscar si ya existe
    existe = False
    for lead in leads:
        if lead["nombre"] == nombre:
            lead["ultimo_mensaje"] = mensaje
            lead["fecha_actualizacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lead["interes"] = interes
            lead["conteo_mensajes"] = lead.get("conteo_mensajes", 0) + 1
            existe = True
            break
    
    if not existe:
        nuevo_lead = {
            "nombre": nombre,
            "ultimo_mensaje": mensaje,
            "interes": interes,
            "conteo_mensajes": 1,
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        leads.append(nuevo_lead)

    # Guardar
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=4, ensure_ascii=False)
    
    return True

def obtener_leads():
    if not os.path.exists(LEADS_FILE):
        return []
    with open(LEADS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    # Prueba rápida
    registrar_lead("Prueba Jorge", "Me interesa el ESP3", "Alto")
    print("Lead registrado con éxito.")
