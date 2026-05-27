import sqlite3
import os

DB_FILE = "sinergia_cloud.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS afiliados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            whatsapp TEXT UNIQUE NOT NULL,
            cta_bcp TEXT,
            cta_interbank TEXT,
            tipo_cambio REAL DEFAULT 3.85,
            activo INTEGER DEFAULT 1
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordenes_bot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            afiliado_id INTEGER NOT NULL,
            destinatario TEXT NOT NULL,
            instruccion TEXT NOT NULL,
            estado TEXT DEFAULT 'PENDIENTE',
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferencias_contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            afiliado_id INTEGER NOT NULL,
            nombre_contacto TEXT NOT NULL,
            accion TEXT NOT NULL,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(afiliado_id, nombre_contacto)
        )
    ''')
    conn.commit()
    conn.close()
    print(f"[DB] Base de datos {DB_FILE} inicializada correctamente.")

def registrar_o_actualizar_afiliado(nombre, whatsapp, cta_bcp=None, cta_interbank=None, tipo_cambio=3.85):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT id FROM afiliados WHERE whatsapp = ?", (whatsapp,))
    row = cursor.fetchone()
    
    if row:
        # Update
        cursor.execute('''
            UPDATE afiliados 
            SET nombre = ?, cta_bcp = ?, cta_interbank = ?, tipo_cambio = ?
            WHERE whatsapp = ?
        ''', (nombre, cta_bcp, cta_interbank, tipo_cambio, whatsapp))
        afiliado_id = row[0]
    else:
        # Insert
        cursor.execute('''
            INSERT INTO afiliados (nombre, whatsapp, cta_bcp, cta_interbank, tipo_cambio)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, whatsapp, cta_bcp, cta_interbank, tipo_cambio))
        afiliado_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    
    # Crear carpeta de usuario para QRs
    user_dir = f"c:\\GanoiTouch\\qrs\\user_{afiliado_id}"
    os.makedirs(user_dir, exist_ok=True)
    
    return afiliado_id

def obtener_afiliado(whatsapp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, nombre, whatsapp, cta_bcp, cta_interbank, tipo_cambio, activo 
        FROM afiliados WHERE whatsapp = ?
    ''', (whatsapp,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "nombre": row[1],
            "whatsapp": row[2],
            "cta_bcp": row[3],
            "cta_interbank": row[4],
            "tipo_cambio": row[5],
            "activo": bool(row[6])
        }
    return None

def obtener_todos_activos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, nombre, whatsapp, cta_bcp, cta_interbank, tipo_cambio 
        FROM afiliados WHERE activo = 1
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    afiliados = []
    for row in rows:
        afiliados.append({
            "id": row[0],
            "nombre": row[1],
            "whatsapp": row[2],
            "cta_bcp": row[3],
            "cta_interbank": row[4],
            "tipo_cambio": row[5]
        })
    return afiliados

def insertar_orden(afiliado_id, destinatario, instruccion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ordenes_bot (afiliado_id, destinatario, instruccion)
        VALUES (?, ?, ?)
    ''', (afiliado_id, destinatario, instruccion))
    conn.commit()
    conn.close()

def obtener_ordenes_pendientes(afiliado_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, destinatario, instruccion 
        FROM ordenes_bot 
        WHERE afiliado_id = ? AND estado = 'PENDIENTE'
    ''', (afiliado_id,))
    rows = cursor.fetchall()
    conn.close()
    
    ordenes = []
    for row in rows:
        ordenes.append({
            "id": row[0],
            "destinatario": row[1],
            "instruccion": row[2]
        })
    return ordenes

def marcar_orden_completada(orden_id, estado='COMPLETADO'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE ordenes_bot SET estado = ? WHERE id = ?
    ''', (estado, orden_id))
    conn.commit()
    conn.close()

def obtener_preferencia_contacto(afiliado_id, nombre_contacto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT accion FROM preferencias_contactos 
        WHERE afiliado_id = ? AND nombre_contacto = ?
    ''', (afiliado_id, nombre_contacto))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def actualizar_preferencia_contacto(afiliado_id, nombre_contacto, accion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO preferencias_contactos (afiliado_id, nombre_contacto, accion)
        VALUES (?, ?, ?)
        ON CONFLICT(afiliado_id, nombre_contacto) 
        DO UPDATE SET accion=excluded.accion, actualizado_en=CURRENT_TIMESTAMP
    ''', (afiliado_id, nombre_contacto, accion))
    conn.commit()
    conn.close()

def obtener_contactos_pendientes(afiliado_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT nombre_contacto FROM preferencias_contactos 
        WHERE afiliado_id = ? AND accion = 'PENDIENTE'
    ''', (afiliado_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

if __name__ == "__main__":
    init_db()
    # Crear el usuario administrador por defecto (Tú)
    registrar_o_actualizar_afiliado(
        nombre=os.getenv("FACEBOOK_PAGE_NAME", "Jorge Rodríguez"),
        whatsapp=os.getenv("WHATSAPP_PHONE", "51947347666").replace(" ", "").replace("-", ""),
        cta_bcp=os.getenv("CTA_BCP", "Solicitar por interno"),
        cta_interbank=os.getenv("CTA_INTERBANK", "Solicitar por interno"),
        tipo_cambio=float(os.getenv("TIPO_CAMBIO", 3.85))
    )
    print("[DB] Matriz lista y administrador registrado.")
