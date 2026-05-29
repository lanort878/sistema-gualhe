import psycopg2
import streamlit as st

def obtener_conexion():
    try:
        # El sistema buscará primero los secretos (en local o en la nube)
        if "postgres" in st.secrets:
            db_config = st.secrets["postgres"]
            return psycopg2.connect(
                host=db_config["host"],
                database=db_config["database"],
                user=db_config["user"],
                password=db_config["password"],
                port=db_config["port"],
                sslmode="require"
            )
        else:
            # Fallback de respaldo por si ejecutas en local de la forma antigua
            return psycopg2.connect(
                host="localhost",
                database="distribuidora_gualhe",
                user="postgres",
                password="tu_contraseña_aquí",
                port="5432"
            )
    except Exception as e:
        st.error(f"❌ Error crítico de conexión a la base de datos: {e}")
        return None

def ejecutar_consulta(sql, params=None, retornar_datos=False):
    conexion = obtener_conexion()
    if not conexion:
        return None
    
    cursor = conexion.cursor()
    resultado = None
    try:
        cursor.execute(sql, params or ())
        if retornar_datos:
            resultado = cursor.fetchall()
        else:
            conexion.commit()
            resultado = True
    except Exception as e:
        st.error(f"❌ Error al ejecutar consulta SQL: {e}")
        conexion.rollback()
    finally:
        cursor.close()
        conexion.close()
        
    return resultado
