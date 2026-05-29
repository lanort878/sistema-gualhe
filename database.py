import psycopg2
import streamlit as st

def obtener_conexion():
    try:
        # El sistema buscará primero los secretos (en local o en la nube)
        if "postgres" in st.secrets:
            db_config = st.secrets["postgres"]
           def obtener_conexion():
    try:
        # El sistema buscará primero los secretos (en local o en la nube)
        if "postgres" in st.secrets:
            db_config = st.secrets["postgres"]
            conexion = psycopg2.connect(
                host=db_config["host"],
                database=db_config["database"],
                user=db_config["user"],
                password=db_config["password"],
                port=db_config["port"],
                sslmode="require"
            )
        else:
            # Fallback de respaldo por si ejecutas en local de la forma antigua
            conexion = psycopg2.connect(
                host="localhost",
                database="distribuidora_gualhe",
                user="postgres",
                password="tu_contraseña_aqui",  # Pon aquí tu contraseña de pgAdmin local para tus pruebas
                port="5432"
            )
        return conexion
    except Exception as e:
        st.error(f"❌ Error crítico de conexión a la base de datos: {e}")
        return None
