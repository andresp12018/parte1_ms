"""
Microservicio básico en Python usando FastAPI.

Provee 3 endpoints:
- /health : comprobación de salud
- /get    : obtiene todos los empleados desde Postgres
- /post   : inserta un empleado en la tabla `empleados`

El servicio crea la tabla `empleados` al arrancar si no existe.
Todas las credenciales de la BD se leen desde variables de entorno (para integrarse con Kubernetes Secrets).
Comentado en español como pidió el usuario.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# --------------------------------------------------
# Configuración: variables de entorno (esperadas en k8s Secret)
# --------------------------------------------------
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "mydb")
DB_USER = os.getenv("POSTGRES_USER", "myuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mypassword")


def get_conn():
    """Obtiene una conexión nueva a Postgres.

    Usamos una conexión simple por cada operación para mantener el ejemplo claro.
    En producción conviene usar un pool (psycopg2.pool o SQLAlchemy).
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        return conn
    except Exception as e:
        # Exponer excepciones claras para debugging
        raise


# Modelo Pydantic para la entrada de /post
class EmpleadoIn(BaseModel):
    nombres: str
    telefono: str


# Modelo de salida opcional
class EmpleadoOut(BaseModel):
    id: int
    nombres: str
    telefono: str


app = FastAPI()


@app.on_event("startup")
def startup():
    """Evento de arranque: crea la tabla `empleados` si no existe.

    Esto garantiza que la tabla esté disponible cuando lleguen peticiones.
    """
    # Crear la tabla si no existe
    create_table_sql = (
        """
        CREATE TABLE IF NOT EXISTS empleados (
            id SERIAL PRIMARY KEY,
            nombres TEXT NOT NULL,
            telefono TEXT
        );
        """
    )

    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(create_table_sql)
        conn.commit()
        cur.close()
    except Exception as e:
        # Si no podemos crear la tabla, el servicio seguirá arrancando,
        # pero las llamadas a DB fallarán con mensajes claros.
        print("Error creando tabla empleados:", e)
    finally:
        if conn:
            conn.close()


@app.get("/health")
def health():
    """Endpoint de salud simple.

    Retorna un JSON sencillo indicando que la app está viva.
    """
    return {"status": "ok"}


@app.get("/get", response_model=list[EmpleadoOut])
def get_empleados():
    """Devuelve la lista de empleados de la tabla `empleados`.

    Realiza una consulta simple y devuelve todos los registros.
    """
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, nombres, telefono FROM empleados ORDER BY id;")
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error DB: {e}")
    finally:
        if conn:
            conn.close()


@app.post("/post", response_model=EmpleadoOut)
def create_empleado(payload: EmpleadoIn):
    """Inserta un nuevo empleado en la tabla `empleados`.

    Espera un body JSON con `nombres` y `telefono`. Devuelve el registro insertado.
    """
    insert_sql = (
        "INSERT INTO empleados (nombres, telefono) VALUES (%s, %s) RETURNING id, nombres, telefono;"
    )
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(insert_sql, (payload.nombres, payload.telefono))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        return row
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error insertando: {e}")
    finally:
        if conn:
            conn.close()
