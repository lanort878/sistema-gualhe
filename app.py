import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
from database import obtener_conexion
from fpdf import FPDF

# Configuración inicial de la página
st.set_page_config(page_title="Distribuidora Gualhe", page_icon="🐔", layout="centered")

# 🛒 INICIALIZAR VARIABLES DE SESIÓN
if "carrito_ventas" not in st.session_state:
    st.session_state.carrito_ventas = []
if "carrito_procesado" not in st.session_state:
    st.session_state.carrito_procesado = []
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol" not in st.session_state:
    st.session_state.rol = None

# --- 📁 CONFIGURACIÓN DE RUTA DEL LOGO LOCAL ---
carpeta_actual = Path(__file__).parent
ruta_logo = carpeta_actual / "logo.png"
if not ruta_logo.exists():
    ruta_logo = carpeta_actual / "logo.png.png"

# --- 📄 FUNCIÓN PARA GENERAR EL PDF DE LA NOTA DE VENTA ---
def generar_pdf_nota(id_nota, nombre_cliente, fecha, items, estado="Pagado"):
    pdf = FPDF(format='letter')
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 8, "DISTRIBUIDORA GUALHE", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "Procesamiento y Distribución de Pollo de Alta Calidad", ln=True, align="C")
    pdf.cell(0, 5, f"Mérida, Yucatán, México", ln=True, align="C")
    pdf.ln(5)
    
    pdf.line(15, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(100, 6, f"Cliente: {nombre_cliente}")
    pdf.cell(0, 6, f"Nota de Remisión: #{id_nota}", ln=True, align="R")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(100, 6, f"Fecha de Emisión: {fecha}")
    pdf.cell(0, 6, f"Condición: {estado.upper()}", ln=True, align="R")
    pdf.ln(10)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(20, 8, "Lote", border=1, fill=True, align="C")
    pdf.cell(85, 8, "Descripción del Producto", border=1, fill=True)
    pdf.cell(25, 8, "Cant. Kilos", border=1, fill=True, align="C")
    pdf.cell(25, 8, "Precio/Kg", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Subtotal", border=1, fill=True, align="C")
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 10)
    gran_total = 0.0
    for item in items:
        pdf.cell(20, 7, f"#{item['id_lote']}", border=1, align="C")
        pdf.cell(85, 7, f" {item['producto_nombre']}", border=1)
        pdf.cell(25, 7, f"{float(item['kg']):.2f}", border=1, align="C")
        pdf.cell(25, 7, f"${float(item['precio']):.2f}", border=1, align="C")
        pdf.cell(30, 7, f"${float(item['total']):.2f}", border=1, align="C")
        pdf.ln()
        gran_total += float(item['total'])
        
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(155, 8, "TOTAL A PAGAR: ", align="R")
    pdf.set_fill_color(255, 240, 240)
    pdf.cell(30, 8, f"${gran_total:,.2f}", border=1, ln=True, fill=True, align="C")
    
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, "* Esta nota constituye un comprobante de entrega de producto en andén/reparto.", ln=True, align="C")
    pdf.cell(0, 5, "¡Gracias por su preferencia!", ln=True, align="C")
    
    # Solución aplicada para FPDF en Streamlit Cloud
    return pdf.output(dest='S').encode('latin-1')

# --- 📄 FUNCIÓN PARA GENERAR EL PDF DE LA NOTA DE ENTRADA ---
def generar_pdf_proveedor(id_lote, nombre_proveedor, producto, kg, cajas, costo, fecha):
    pdf = FPDF(format='letter')
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 8, "DISTRIBUIDORA GUALHE", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "Recepción y Control de Materia Prima en Andén", ln=True, align="C")
    pdf.cell(0, 5, f"Mérida, Yucatán, México", ln=True, align="C")
    pdf.ln(5)
    
    pdf.line(15, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(100, 6, f"Proveedor / Origen: {nombre_proveedor}")
    pdf.cell(0, 6, f"ID Lote Generado: #{id_lote}", ln=True, align="R")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(100, 6, f"Fecha de Ingreso: {fecha}")
    pdf.ln(10)
    
    pdf.set_fill_color(220, 235, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(75, 8, "Producto Entregado", border=1, fill=True)
    pdf.cell(30, 8, "Kilos Recibidos", border=1, fill=True, align="C")
    pdf.cell(25, 8, "Cajas", border=1, fill=True, align="C")
    pdf.cell(25, 8, "Costo/Kg", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Total Lote", border=1, fill=True, align="C")
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 10)
    total_compra = float(kg) * float(costo)
    pdf.cell(75, 7, f" {producto}", border=1)
    pdf.cell(30, 7, f"{float(kg):.2f} Kg", border=1, align="C")
    pdf.cell(25, 7, f"{cajas}", border=1, align="C")
    pdf.cell(25, 7, f"${float(costo):.2f}", border=1, align="C")
    pdf.cell(30, 7, f"${total_compra:,.2f}", border=1, align="C")
    pdf.ln()
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(155, 8, "VALOR TOTAL DE ENTRADA: ", align="R")
    pdf.set_fill_color(240, 248, 255)
    pdf.cell(30, 8, f"${total_compra:,.2f}", border=1, ln=True, fill=True, align="C")
    
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, "* Esta nota valida los pesos y costos capturados en el sistema para control interno.", ln=True, align="C")
    
    # Solución aplicada para FPDF en Streamlit Cloud
    return pdf.output(dest='S').encode('latin-1')
# --- FUNCION PARA GENERAR PDF CONSOLIDADO DE ENTRADAS POR PROVEEDOR ---
def generar_pdf_proveedor_resumen(nombre_proveedor, fecha_inicio, fecha_fin, items):
    pdf = FPDF(format='letter')
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 8, "DISTRIBUIDORA GUALHE", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "Recepcion y Control de Materia Prima en Anden", ln=True, align="C")
    pdf.cell(0, 5, "Merida, Yucatan, Mexico", ln=True, align="C")
    pdf.ln(5)

    pdf.line(15, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(100, 6, f"Proveedor / Origen: {nombre_proveedor}")
    pdf.cell(0, 6, "Nota consolidada por proveedor", ln=True, align="R")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(100, 6, f"Periodo: {fecha_inicio} a {fecha_fin}")
    pdf.cell(0, 6, f"Lotes incluidos: {len(items)}", ln=True, align="R")
    pdf.ln(10)

    pdf.set_fill_color(220, 235, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(18, 8, "Lote", border=1, fill=True, align="C")
    pdf.cell(25, 8, "Fecha", border=1, fill=True, align="C")
    pdf.cell(55, 8, "Producto", border=1, fill=True)
    pdf.cell(25, 8, "Kilos", border=1, fill=True, align="C")
    pdf.cell(18, 8, "Cajas", border=1, fill=True, align="C")
    pdf.cell(22, 8, "Costo/Kg", border=1, fill=True, align="C")
    pdf.cell(22, 8, "Total", border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    total_kg = 0.0
    total_cajas = 0
    total_compra = 0.0

    for item in items:
        if pdf.get_y() > 250:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(18, 8, "Lote", border=1, fill=True, align="C")
            pdf.cell(25, 8, "Fecha", border=1, fill=True, align="C")
            pdf.cell(55, 8, "Producto", border=1, fill=True)
            pdf.cell(25, 8, "Kilos", border=1, fill=True, align="C")
            pdf.cell(18, 8, "Cajas", border=1, fill=True, align="C")
            pdf.cell(22, 8, "Costo/Kg", border=1, fill=True, align="C")
            pdf.cell(22, 8, "Total", border=1, fill=True, align="C")
            pdf.ln()
            pdf.set_font("Helvetica", "", 8)

        kg = float(item["kg"])
        cajas = int(item["cajas"] or 0)
        costo = float(item["costo"])
        total = float(item["total"])
        producto = str(item["producto"])[:32]

        pdf.cell(18, 7, f"#{item['id_lote']}", border=1, align="C")
        pdf.cell(25, 7, str(item["fecha"]), border=1, align="C")
        pdf.cell(55, 7, f" {producto}", border=1)
        pdf.cell(25, 7, f"{kg:.2f}", border=1, align="C")
        pdf.cell(18, 7, f"{cajas}", border=1, align="C")
        pdf.cell(22, 7, f"${costo:.2f}", border=1, align="C")
        pdf.cell(22, 7, f"${total:,.2f}", border=1, align="C")
        pdf.ln()

        total_kg += kg
        total_cajas += cajas
        total_compra += total

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(98, 8, "TOTALES DEL PROVEEDOR:", align="R")
    pdf.set_fill_color(240, 248, 255)
    pdf.cell(25, 8, f"{total_kg:,.2f}", border=1, fill=True, align="C")
    pdf.cell(18, 8, f"{total_cajas}", border=1, fill=True, align="C")
    pdf.cell(22, 8, "", border=1, fill=True, align="C")
    pdf.cell(22, 8, f"${total_compra:,.2f}", border=1, fill=True, align="C")
    pdf.ln(15)

    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, "* Esta nota consolida las entradas del proveedor dentro del periodo seleccionado.", ln=True, align="C")

    return pdf.output(dest='S').encode('latin-1')

# --- 🔐 CONTROL DE ACCESO ---
if not st.session_state.autenticado:
    if ruta_logo.exists():
        col_izq, col_centro, col_der = st.columns([1, 2, 1])
        with col_centro: st.image(str(ruta_logo), use_container_width=True)
            
    st.markdown("<h2 style='text-align: center;'>🔑 Ingreso al Sistema</h2>", unsafe_allow_html=True)
    with st.form("form_login"):
        usuario = st.text_input("Usuario:")
        password = st.text_input("Contraseña:", type="password")
        btn_ingresar = st.form_submit_button("Ingresar al Sistema")
        
    if btn_ingresar:
        if usuario == "admin" and password == "gualhe2026":
            st.session_state.autenticado = True
            st.session_state.rol = "admin"
            st.rerun()
        elif usuario == "operador" and password == "ventasgualhe":
            st.session_state.autenticado = True
            st.session_state.rol = "operador"
            st.rerun()
        else: st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

# --- MENÚ LATERAL DE NAVEGACIÓN ---
if ruta_logo.exists(): st.sidebar.image(str(ruta_logo), use_container_width=True)
else: st.sidebar.title("🍗 Distribuidora Gualhe")

st.sidebar.write(f"👤 **Usuario:** {st.session_state.rol.upper()}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.carrito_ventas = []
    st.session_state.carrito_procesado = []
    st.rerun()

# MENÚ DE MÓDULOS
if st.session_state.rol == "admin":
    modulos_disponibles = ["📋 Proveedores", "📦 Catálogo de Productos", "⚖️ Entradas de Lotes", "🔪 Procesamiento", "👥 Clientes y Ventas", "❄️ Almacén y Ajustes", "💵 Control de Cobranza", "📑 Historial de Notas", "📈 Dashboard y Métricas"]
else:
    modulos_disponibles = ["⚖️ Entradas de Lotes", "🔪 Procesamiento", "👥 Clientes y Ventas", "❄️ Almacén y Ajustes", "💵 Control de Cobranza", "📑 Historial de Notas"]

opcion = st.sidebar.radio("Selecciona un módulo:", modulos_disponibles)
st.title("🐔 Sistema de Control - Distribuidora Gualhe")
st.write("---")

# ==========================================
# MÓDULO 1: PROVEEDORES (SOLO ADMIN)
# ==========================================
if opcion == "📋 Proveedores":
    st.subheader("Registro de Proveedores")
    with st.form("formulario_proveedor", clear_on_submit=True):
        nombre = st.text_input("Nombre de la Empresa / Proveedor *")
        telefono = st.text_input("Teléfono de Contacto")
        direccion = st.text_area("Dirección")
        boton_guardar = st.form_submit_button("Guardar Proveedor")

    if boton_guardar:
        if not nombre: st.error("⚠️ El nombre del proveedor es obligatorio.")
        else:
            conn = obtener_conexion()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO proveedores (nombre_empresa, telefono, direccion) VALUES (%s, %s, %s);", (nombre, telefono, direccion))
                    conn.commit()
                    st.success(f"🎉 ¡Proveedor '{nombre}' registrado!")
                except Exception as e: st.error(f"❌ Error: {e}")
                finally: cursor.close(); conn.close()

    st.write("---")
    st.subheader("📋 Lista de Proveedores Actuales")
    conn = obtener_conexion()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_proveedor, nombre_empresa, telefono, direccion FROM proveedores ORDER BY id_proveedor DESC;")
            datos = cursor.fetchall()
            if datos: st.table([{"ID": fila[0], "Proveedor": fila[1], "Teléfono": fila[2], "Dirección": fila[3]} for fila in datos])
        except Exception as e: st.error(f"Error: {e}")
        finally: cursor.close(); conn.close()

# ==========================================
# MÓDULO 2: CATÁLOGO DE PRODUCTOS (SOLO ADMIN)
# ==========================================
elif opcion == "📦 Catálogo de Productos":
    st.subheader("Catálogo Maestro de Productos")
    with st.form("formulario_producto", clear_on_submit=True):
        nombre_prod = st.text_input("Nombre del Producto *")
        tipo_prod = st.selectbox("Tipo de Producto *", ["Materia Prima", "Procesado"])
        boton_guardar_prod = st.form_submit_button("Registrar Producto")

    if boton_guardar_prod:
        if not nombre_prod: st.error("⚠️ Nombre obligatorio.")
        else:
            conn = obtener_conexion()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO productos (nombre_producto, tipo_producto) VALUES (%s, %s);", (nombre_prod, tipo_prod))
                    conn.commit()
                    st.success(f"📦 ¡'{nombre_prod}' añadido!")
                except Exception as e: st.error(f"❌ Error: {e}")
                finally: cursor.close(); conn.close()

    st.write("---")
    st.subheader("📋 Productos en Catálogo")
    todos_productos_dict = {}
    conn = obtener_conexion()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_producto, nombre_producto, tipo_producto FROM productos ORDER BY id_producto ASC;")
            datos = cursor.fetchall()
            if datos:
                st.table([{"ID": f[0], "Producto": f[1], "Tipo": f[2]} for f in datos])
                for f in datos: todos_productos_dict[f"{f[1]} (ID: {f[0]})"] = {"id": f[0], "nombre": f[1], "tipo": f[2]}
        except Exception as e: st.error(f"Error: {e}")
        finally: cursor.close(); conn.close()

    if todos_productos_dict:
        st.write("---")
        st.markdown("#### 🛠️ Formulario para Corregir Errores")
        prod_a_editar_label = st.selectbox("Selecciona el producto que deseas corregir:", list(todos_productos_dict.keys()))
        prod_seleccionado_info = todos_productos_dict[prod_a_editar_label]
        index_defecto = 0 if prod_seleccionado_info["tipo"] == "Materia Prima" else 1
        
        with st.form("formulario_edicion_producto", clear_on_submit=False):
            nuevo_nombre = st.text_input("Corregir Nombre:", value=prod_seleccionado_info["nombre"])
            nuevo_tipo = st.selectbox("Corregir Tipo:", ["Materia Prima", "Procesado"], index=index_defecto)
            boton_actualizar_prod = st.form_submit_button("💾 Guardar Cambios")
            
        if boton_actualizar_prod:
            if not nuevo_nombre: st.error("⚠️ No puede estar vacío.")
            else:
                conn = obtener_conexion()
                if conn is not None:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE productos SET nombre_producto = %s, tipo_producto = %s WHERE id_producto = %s;", (nuevo_nombre, nuevo_tipo, prod_seleccionado_info["id"]))
                        conn.commit()
                        st.success("🎉 ¡Cambios guardados!")
                        st.rerun()
                    except Exception as e: st.error(f"❌ Error al actualizar: {e}")
                    finally: cursor.close(); conn.close()

# ==========================================
# MÓDULO 3: ENTRADAS DE LOTES (CON PESTAÑAS DE CORRECCIÓN)
# ==========================================
elif opcion == "⚖️ Entradas de Lotes":
    st.subheader("⚖️ Gestión de Lotes (Materia Prima)")
    
    tab_registro, tab_edicion = st.tabs(["⚖️ Registrar Lote de Entrada", "🛠️ Corregir / Eliminar Lote"])
    
    with tab_registro:
        proveedores_dict = {}
        productos_dict = {}
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id_proveedor, nombre_empresa FROM proveedores;")
                for p in cursor.fetchall(): proveedores_dict[p[1]] = p[0]
                cursor.execute("SELECT id_producto, nombre_producto FROM productos WHERE tipo_producto = 'Materia Prima';")
                for prod in cursor.fetchall(): productos_dict[prod[1]] = prod[0]
            except Exception as e: st.error(f"Error: {e}")
            finally: cursor.close(); conn.close()

        if not proveedores_dict or not productos_dict:
            st.warning("⚠️ Catálogos vacíos. Contacte al administrador.")
        else:
            with st.form("formulario_lote", clear_on_submit=True):
                prov_seleccionado = st.selectbox("Selecciona el Proveedor:", list(proveedores_dict.keys()))
                prod_seleccionado = st.selectbox("Selecciona el Producto Recibido:", list(productos_dict.keys()))
                kg = st.number_input("Kilogramos Recibidos *", min_value=0.0, step=0.1, format="%.2f")
                cajas = st.number_input("Cantidad de Cajas (Opcional)", min_value=0, step=1)
                costo = st.number_input("Costo por Kilogramo ($) *", min_value=0.0, step=0.1, format="%.2f")
                fecha_manual = st.date_input("Fecha de Entrada del Producto *")
                boton_guardar_lote = st.form_submit_button("Registrar Entrada y Generar Lote")

            if boton_guardar_lote:
                if kg <= 0 or costo <= 0: st.error("⚠️ Deben ser mayores a cero.")
                else:
                    id_prov_real = proveedores_dict[prov_seleccionado]
                    id_prod_real = productos_dict[prod_seleccionado]
                    conn = obtener_conexion()
                    if conn is not None:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("""
                                INSERT INTO lotes_entrada (id_proveedor, id_producto, kg_recibidos, cantidad_cajas, costo_por_kg, fecha_entrada) 
                                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_lote;
                            """, (id_prov_real, id_prod_real, kg, cajas, costo, fecha_manual))
                            id_lote_generado = cursor.fetchone()[0]
                            conn.commit()
                            
                            pdf_prov_data = generar_pdf_proveedor(id_lote_generado, prov_seleccionado, prod_seleccionado, kg, cajas, costo, str(fecha_manual))
                            st.session_state["ultimo_pdf_prov"] = pdf_prov_data
                            st.session_state["ultimo_pdf_prov_name"] = f"Entrada_Lote_{id_lote_generado}_{prov_seleccionado}.pdf"
                            
                            st.success(f"🎉 ¡Lote registrado con éxito! **ID DE LOTE: {id_lote_generado}**")
                            st.rerun()
                        except Exception as e: st.error(f"❌ Error al guardar el lote: {e}")
                        finally: cursor.close(); conn.close()

            if "ultimo_pdf_prov" in st.session_state and st.session_state["ultimo_pdf_prov"] is not None:
                st.write("---")
                st.download_button(
                    label="🖨️ DESCARGAR NOTA DE ENTRADA DEL PROVEEDOR (PDF)",
                    data=st.session_state["ultimo_pdf_prov"],
                    file_name=st.session_state["ultimo_pdf_prov_name"],
                    mime="application/pdf"
                )

        st.write("---")
        st.subheader("📋 Inventario de Lotes Recibidos")
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT l.id_lote, p.nombre_empresa, pr.nombre_producto, l.kg_recibidos, l.cantidad_cajas, l.costo_por_kg, l.fecha_entrada
                    FROM lotes_entrada l JOIN proveedores p ON l.id_proveedor = p.id_proveedor
                    JOIN productos pr ON l.id_producto = pr.id_producto ORDER BY l.id_lote DESC;
                """)
                datos_lotes = cursor.fetchall()
                if datos_lotes:
                    st.table([{
                        "ID Lote": f[0], "Proveedor": f[1], "Producto": f[2], "Kg Recibidos": float(f[3]), 
                        "Cajas": f[4], "Costo/Kg": f"${float(f[5]):.2f}" if st.session_state.rol == "admin" else "RESTRINGIDO", "Fecha": str(f[6])
                    } for f in datos_lotes])
            except Exception as e: st.error(f"Error: {e}")
            finally: cursor.close(); conn.close()

    with tab_edicion:
        st.markdown("### 🛠️ Corrección de Lotes Ingresados")
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT l.id_lote, p.nombre_empresa, pr.nombre_producto, l.kg_recibidos, l.cantidad_cajas, l.costo_por_kg, l.fecha_entrada
                    FROM lotes_entrada l 
                    JOIN proveedores p ON l.id_proveedor = p.id_proveedor
                    JOIN productos pr ON l.id_producto = pr.id_producto 
                    ORDER BY l.id_lote DESC LIMIT 50;
                """)
                lotes_guardados = cursor.fetchall()
                
                if not lotes_guardados:
                    st.info("No hay lotes registrados para corregir.")
                else:
                    dict_lotes = {}
                    for lt in lotes_guardados:
                        id_l, prov, prod, kg, cajas, costo, fecha = lt
                        label = f"Lote #{id_l} - {prov} ({prod}) - {float(kg):.2f} Kg"
                        dict_lotes[label] = {"id": id_l, "kg": float(kg), "cajas": cajas, "costo": float(costo), "fecha": fecha}
                    
                    lote_a_corregir = st.selectbox("Selecciona el lote que deseas modificar o eliminar:", list(dict_lotes.keys()))
                    meta_lote = dict_lotes[lote_a_corregir]
                    
                    st.write("---")
                    with st.form("form_corregir_lote"):
                        st.markdown(f"**Modificando valores del Lote #{meta_lote['id']}**")
                        col_k, col_c, col_co = st.columns(3)
                        with col_k: nuevo_kg = st.number_input("Corregir Kilos:", min_value=0.01, value=meta_lote["kg"], step=0.1, format="%.2f")
                        with col_c: nuevo_cajas = st.number_input("Corregir Cajas:", min_value=0, value=meta_lote["cajas"], step=1)
                        with col_co: nuevo_costo = st.number_input("Corregir Costo ($):", min_value=0.01, value=meta_lote["costo"], step=0.1, format="%.2f")
                        
                        nueva_fecha = st.date_input("Corregir Fecha de Entrada:", value=meta_lote["fecha"])
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            btn_actualizar_lote = st.form_submit_button("💾 Actualizar Valores del Lote", type="primary")
                        with col_btn2:
                            btn_eliminar_lote = st.form_submit_button("🗑️ Eliminar Lote por Completo")
                    
                    if btn_actualizar_lote:
                        cursor.execute("""
                            UPDATE lotes_entrada 
                            SET kg_recibidos = %s, cantidad_cajas = %s, costo_por_kg = %s, fecha_entrada = %s
                            WHERE id_lote = %s;
                        """, (nuevo_kg, nuevo_cajas, nuevo_costo, nueva_fecha, meta_lote["id"]))
                        conn.commit()
                        st.success(f"🎉 Valores del Lote #{meta_lote['id']} actualizados correctamente en el sistema.")
                        st.rerun()
                        
                    if btn_eliminar_lote:
                        try:
                            cursor.execute("DELETE FROM lotes_entrada WHERE id_lote = %s;", (meta_lote["id"],))
                            conn.commit()
                            st.success(f"🗑️ Lote #{meta_lote['id']} eliminado completamente del andén.")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            error_str = str(e).lower()
                            if "foreign key constraint" in error_str or "violates foreign key" in error_str or "llave foránea" in error_str:
                                st.error("⚠️ ERROR: No puedes eliminar este lote porque ya tiene movimientos asociados (se registró deshuese, se vendió producto o se aplicaron mermas). Debes eliminar o corregir primero esos movimientos en los otros módulos.")
                            else:
                                st.error(f"Error al eliminar el lote: {e}")
                            
            except Exception as e: st.error(f"Error en panel de corrección de lotes: {e}")
            finally: cursor.close(); conn.close()

# ==========================================
# MÓDULO 4: 🔪 PROCESAMIENTO
# ==========================================
elif opcion == "🔪 Procesamiento":
    st.subheader("🔪 Departamento de Procesamiento y Deshuese Multi-Producto")
    lotes_lista = []
    productos_procesados_dict = {}
    conn = obtener_conexion()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT l.id_lote, p.nombre_producto, l.kg_recibidos, l.fecha_entrada FROM lotes_entrada l JOIN productos p ON l.id_producto = p.id_producto ORDER BY l.id_lote DESC;")
            for row in cursor.fetchall():
                lotes_lista.append((f"Lote {row[0]} - {row[1]} ({float(row[2])} Kg) - {row[3]}", row[0]))
            cursor.execute("SELECT id_producto, nombre_producto FROM productos WHERE tipo_producto = 'Procesado';")
            for prod in cursor.fetchall(): productos_procesados_dict[prod[1]] = prod[0]
        except Exception as e: st.error(f"Error: {e}")
        finally: cursor.close(); conn.close()

    if not lotes_lista or not productos_procesados_dict:
        st.warning("⚠️ No hay lotes o productos procesados disponibles.")
    else:
        col_lote, col_fecha = st.columns(2)
        with col_lote:
            lote_seleccionado_texto = st.selectbox("Selecciona el Lote de Pollo Entero a Procesar *", [lbl for lbl, _ in lotes_lista])
            id_lote_real = [id_num for lbl, id_num in lotes_lista if lbl == lote_seleccionado_texto][0]
        with col_fecha:
            fecha_proceso = st.date_input("Fecha de Procesamiento *")
            
        kg_materia_prima_a_cortar = st.number_input("Kilogramos totales de Pollo Entero que entran a la mesa *", min_value=0.0, step=0.1, format="%.2f")
        st.write("---")
        
        st.markdown("#### 📦 Registrar Subproductos Obtenidos")
        with st.form("form_agregar_subproducto", clear_on_submit=True):
            col_sub, col_kgs = st.columns([2, 1])
            with col_sub:
                prod_procesado_seleccionado = st.selectbox("Subproducto Obtenido de la Mesa:", list(productos_procesados_dict.keys()))
            with col_kgs:
                kg_pros = st.number_input("Kilos de Carne Limpia Obtenidos *", min_value=0.0, step=0.1, format="%.2f")
            btn_add_sub = st.form_submit_button("➕ Añadir Subproducto a la Lista")
            
        if btn_add_sub:
            if kg_pros <= 0: st.error("⚠️ Los kilogramos obtenidos deben ser mayores a cero.")
            else:
                st.session_state.carrito_procesado.append({
                    "producto_nombre": prod_procesado_seleccionado,
                    "id_producto": productos_procesados_dict[prod_procesado_seleccionado],
                    "kg_obtenidos": kg_pros
                })
                st.toast(f"✅ Añadido al rendimiento: {prod_procesado_seleccionado}")
                st.rerun()

        if st.session_state.carrito_procesado:
            st.write("### 📝 Rendimiento Total del Deshuese")
            st.table([{"Subproducto": item["producto_nombre"], "Kilogramos Logrados": f"{item['kg_obtenidos']:.2f} Kg"} for item in st.session_state.carrito_procesado])
            
            sumatoria_obtenida = sum(i["kg_obtenidos"] for i in st.session_state.carrito_procesado)
            st.info(f"**Resumen de pesos:** Entraron {kg_materia_prima_a_cortar:.2f} Kg a mesa | Se obtuvieron {sumatoria_obtenida:.2f} Kg limpios.")
            
            col_save, col_clear = st.columns(2)
            with col_save:
                if st.button("💾 CONFIRMAR Y GUARDAR PROCESAMIENTO EN LOTE", type="primary"):
                    if kg_materia_prima_a_cortar <= 0: st.error("⚠️ Debes capturar los kilos de pollo entero de origen.")
                    elif sumatoria_obtenida > kg_materia_prima_a_cortar: st.error("⚠️ Alerta: Los kilos obtenidos no pueden ser mayores a la materia prima.")
                    else:
                        conn = obtener_conexion()
                        if conn is not None:
                            try:
                                cursor = conn.cursor()
                                for item in st.session_state.carrito_procesado:
                                    cursor.execute("""
                                        INSERT INTO salidas_procesado (id_lote, id_producto, kg_materia_prima, kg_procesados, fecha_proceso) 
                                        VALUES (%s, %s, %s, %s, %s);
                                    """, (id_lote_real, item["id_producto"], kg_materia_prima_a_cortar, item["kg_obtenidos"], fecha_proceso))
                                conn.commit()
                                st.session_state.carrito_procesado = []
                                st.success("🎉 ¡Rendimiento multi-producto guardado con éxito!")
                                st.rerun()
                            except Exception as e: st.error(f"❌ Error al guardar en lote: {e}")
                            finally: cursor.close(); conn.close()
            with col_clear:
                if st.button("🗑️ Limpiar Tabla de Rendimiento"):
                    st.session_state.carrito_procesado = []
                    st.rerun()

    st.write("---")
    st.subheader("📋 Historial de Pollo Procesado")
    conn = obtener_conexion()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id_procesado, s.id_lote, p.nombre_producto, COALESCE(s.kg_materia_prima, 0), COALESCE(s.kg_procesados, 0), s.fecha_proceso 
                FROM salidas_procesado s JOIN productos p ON s.id_producto = p.id_producto ORDER BY s.id_procesado DESC;
            """)
            datos_proceso = cursor.fetchall()
            if datos_proceso:
                st.table([{"ID": f[0], "Lote Origen": f[1], "Corte Obtenido": f[2], "Kg MP (Entrada)": float(f[3]), "Kg Obtenidos (Limpio)": float(f[4]), "Fecha": str(f[5])} for f in datos_proceso])
        except Exception as e: st.error(f"Error en Historial: {e}")
        finally: cursor.close(); conn.close()

# ==========================================
# MÓDULO 5: CLIENTES Y VENTAS
# ==========================================
elif opcion == "👥 Clientes y Ventas":
    tab1, tab2 = st.tabs(["👥 Registrar Clientes", "💵 Capturar Ventas (Notas de Remisión)"])
    with tab1:
        st.subheader("Alta de Nuevos Clientes")
        with st.form("form_cliente", clear_on_submit=True):
            n_cliente = st.text_input("Nombre Completo del Cliente *")
            t_cliente = st.text_input("Teléfono")
            d_cliente = st.text_area("Dirección")
            btn_cliente = st.form_submit_button("Guardar Cliente")
        if btn_cliente:
            if not n_cliente: st.error("⚠️ Nombre obligatorio.")
            else:
                conn = obtener_conexion()
                if conn is not None:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO clientes (nombre_cliente, telefono, direccion) VALUES (%s, %s, %s);", (n_cliente, t_cliente, d_cliente))
                        conn.commit()
                        st.success(f"👥 Cliente '{n_cliente}' registrado.")
                    except Exception as e: st.error(f"Error: {e}")
                    finally: cursor.close(); conn.close()

    with tab2:
        st.subheader("Nueva Nota de Venta")
        clientes_dict, lotes_lista = {}, []
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id_cliente, nombre_cliente FROM clientes;")
                for cl in cursor.fetchall(): clientes_dict[cl[1]] = cl[0]
                
                cursor.execute("""
                    WITH existencias_calculadas AS (
                        SELECT 
                            u.id_lote,
                            le.fecha_entrada,
                            (
                                COALESCE(le.kg_recibidos, 0) 
                                - COALESCE(po.kg_a_corte, 0) 
                                + COALESCE(pd.kg_obtenidos, 0) 
                                - COALESCE(v.kg_vendidos, 0) 
                                - COALESCE(a.kg_ajustados, 0)
                            ) as stock_real
                        FROM (
                            SELECT id_lote FROM lotes_entrada
                            UNION
                            SELECT id_lote FROM salidas_procesado
                        ) u
                        LEFT JOIN lotes_entrada le ON u.id_lote = le.id_lote
                        LEFT JOIN (SELECT id_lote, SUM(kg_materia_prima) as kg_a_corte FROM salidas_procesado GROUP BY id_lote) po ON u.id_lote = po.id_lote
                        LEFT JOIN (SELECT id_lote, SUM(kg_procesados) as kg_obtenidos FROM salidas_procesado GROUP BY id_lote) pd ON u.id_lote = pd.id_lote
                        LEFT JOIN (SELECT id_lote, SUM(kg_vendidos) as kg_vendidos FROM ventas GROUP BY id_lote) v ON u.id_lote = v.id_lote
                        LEFT JOIN (SELECT id_lote, SUM(kg_ajustados) as kg_ajustados FROM ajustes_inventario GROUP BY id_lote) a ON u.id_lote = a.id_lote
                    )
                    SELECT id_lote, fecha_entrada, stock_real 
                    FROM existencias_calculadas 
                    WHERE stock_real > 0.01
                    ORDER BY id_lote DESC;
                """)
                for lt in cursor.fetchall(): 
                    fecha_str = lt[1] if lt[1] else "Procesado"
                    lotes_lista.append((f"Lote #{lt[0]} (Disponible: {float(lt[2]):.2f} Kg) - [{fecha_str}]", lt[0], float(lt[2])))
            except Exception as e: st.error(f"Error cargando catálogo base: {e}")
            finally: cursor.close(); conn.close()

        if clientes_dict and not lotes_lista:
            st.info("❄️ No hay lotes con existencias disponibles en el Cuarto Frío en este momento.")
        elif clientes_dict and lotes_lista:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1: c_sel = st.selectbox("Selecciona el Cliente:", list(clientes_dict.keys()))
            with col2: fecha_v = st.date_input("Fecha de la Nota *")
            with col3: estado_cobro_inicial = st.selectbox("Condición de Pago *:", ["Pagado", "En Transcurso", "Pendiente"])
            st.write("---")
            
            st.markdown("#### 🛒 Agregar Productos")
            l_sel_text = st.selectbox("Lote de Origen (Solo lotes con existencias real) *:", [lbl for lbl, _, _ in lotes_lista])
            
            id_lote_seleccionado = [id_num for lbl, id_num, _ in lotes_lista if lbl == l_sel_text][0]
            max_disponible_lote = [stock for lbl, _, stock in lotes_lista if lbl == l_sel_text][0]
            
            productos_filtrados_dict = {}
            conn = obtener_conexion()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT DISTINCT p.id_producto, p.nombre_producto, p.tipo_producto
                        FROM productos p JOIN lotes_entrada le ON le.id_producto = p.id_producto WHERE le.id_lote = %s
                        UNION
                        SELECT DISTINCT p.id_producto, p.nombre_producto, p.tipo_producto
                        FROM productos p JOIN salidas_procesado sp ON sp.id_producto = p.id_producto WHERE sp.id_lote = %s
                        ORDER BY tipo_producto ASC, nombre_producto ASC;
                    """, (id_lote_seleccionado, id_lote_seleccionado))
                    for pr in cursor.fetchall(): productos_filtrados_dict[f"{pr[1]} [{pr[2]}]"] = pr[0]
                except Exception as e: st.error(f"Error al filtrar productos: {e}")
                finally: cursor.close(); conn.close()
            
            if not productos_filtrados_dict:
                st.warning("⚠️ Este lote no cuenta con existencias vinculadas.")
            else:
                with st.form("form_renglon_venta", clear_on_submit=True):
                    col_p, col_k, col_pr = st.columns([2, 1, 1])
                    with col_p: p_sel = st.selectbox("Producto disponible de este lote *:", list(productos_filtrados_dict.keys()))
                    with col_k: kg_v = st.number_input(f"Kilos (Máx: {max_disponible_lote:.2f} Kg) *", min_value=0.0, max_value=max_disponible_lote, step=0.1, format="%.2f")
                    with col_pr: precio_v = st.number_input("Precio/Kg *", min_value=0.0, step=0.5, format="%.2f")
                    btn_agregar_carrito = st.form_submit_button("➕ Agregar Producto")

                if btn_agregar_carrito:
                    if p_sel not in productos_filtrados_dict:
                        st.error("⚠️ Error de sincronización. Selecciona nuevamente el producto.")
                        st.stop()
                        
                    if kg_v <= 0 or precio_v <= 0: st.error("⚠️ Los valores deben ser mayores a cero.")
                    else:
                        st.session_state.carrito_ventas.append({
                            "id_lote": id_lote_seleccionado, "producto_nombre": p_sel, 
                            "id_producto": productos_filtrados_dict[p_sel], "kg": kg_v, "precio": precio_v, "total": kg_v * precio_v
                        })
                        st.toast(f"✅ Añadido: {p_sel}")
                        st.rerun()

            if st.session_state.carrito_ventas:
                st.write("### 📝 Vista Previa de la Nota")
                st.table([{"Lote": i["id_lote"], "Producto": i["producto_nombre"], "Kg": f"{i['kg']:.2f}", "Precio": f"${i['precio']:.2f}", "Subtotal": f"${i['total']:.2f}"} for i in st.session_state.carrito_ventas])
                
                b_save, b_del = st.columns(2)
                with b_save:
                    if st.button("💾 CONFIRMAR Y GUARDAR NOTA", type="primary"):
                        id_c = clientes_dict[c_sel]
                        conn = obtener_conexion()
                        if conn is not None:
                            try:
                                cursor = conn.cursor()
                                for item in st.session_state.carrito_ventas:
                                    cursor.execute("""
                                        INSERT INTO ventas (fecha_venta, id_cliente, id_lote, id_producto, kg_vendidos, precio_por_kg, estado_pago) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_venta;
                                    """, (fecha_v, id_c, item["id_lote"], item["id_producto"], item["kg"], item["precio"], estado_cobro_inicial))
                                id_nota_final = cursor.fetchone()[0]
                                conn.commit()
                                
                                pdf_data = generar_pdf_nota(id_nota_final, c_sel, str(fecha_v), st.session_state.carrito_ventas, estado_cobro_inicial)
                                st.session_state["ultimo_pdf"] = pdf_data
                                st.session_state["ultimo_pdf_name"] = f"Nota_{id_nota_final}_{c_sel}.pdf"
                                st.session_state.carrito_ventas = []
                                st.success("🎉 ¡Venta guardada!")
                                st.rerun()
                            except Exception as e: st.error(f"Error al insertar venta: {e}")
                            finally: cursor.close(); conn.close()
                with b_del:
                    if st.button("🗑️ Vaciar Nota"):
                        st.session_state.carrito_ventas = []
                        st.rerun()
                        
            if "ultimo_pdf" in st.session_state and st.session_state["ultimo_pdf"] is not None:
                st.write("---")
                st.download_button(
                    label="🖨️ DESCARGAR E IMPRIMIR ÚLTIMA NOTA EN PDF",
                    data=st.session_state["ultimo_pdf"],
                    file_name=st.session_state["ultimo_pdf_name"],
                    mime="application/pdf"
                )

# ==========================================
# MÓDULO 6: ❄️ ALMACÉN Y RESGUARDO
# ==========================================
elif opcion == "❄️ Almacén y Ajustes":
    st.subheader("❄️ Inventario Real en Resguardo (Cuarto Frío)")
    
    conn = obtener_conexion()
    inventario_neto = []
    lotes_opciones_ajuste = {}
    
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                WITH entradas AS (
                    SELECT id_lote, id_producto, kg_recibidos as kg FROM lotes_entrada
                ),
                procesamientos_origen AS (
                    SELECT id_lote, SUM(kg_materia_prima) as kg FROM salidas_procesado GROUP BY id_lote
                ),
                procesamientos_destino AS (
                    SELECT id_lote, id_producto, SUM(kg_procesados) as kg FROM salidas_procesado GROUP BY id_lote, id_producto
                ),
                ventas_totales AS (
                    SELECT id_lote, id_producto, SUM(kg_vendidos) as kg_vendidos FROM ventas GROUP BY id_lote, id_producto
                ),
                ajustes_totales AS (
                    SELECT id_lote, id_producto, SUM(kg_ajustados) as kg_ajustados FROM ajustes_inventario GROUP BY id_lote, id_producto
                ),
                universo_lote_prod AS (
                    SELECT id_lote, id_producto FROM entradas
                    UNION
                    SELECT id_lote, id_producto FROM procesamientos_destino
                )
                SELECT 
                    u.id_lote,
                    p.nombre_producto,
                    p.tipo_producto,
                    COALESCE(e.kg, 0) as kg_inicial_mp,
                    COALESCE(po.kg, 0) as kg_enviado_a_corte,
                    COALESCE(pd.kg, 0) as kg_obtenido_proceso,
                    COALESCE(v.kg_vendidos, 0) as kg_vendidos,
                    COALESCE(a.kg_ajustados, 0) as kg_ajustados,
                    u.id_producto
                FROM universo_lote_prod u
                JOIN productos p ON u.id_producto = p.id_producto
                LEFT JOIN entradas e ON u.id_lote = e.id_lote AND u.id_producto = e.id_producto
                LEFT JOIN procesamientos_origen po ON u.id_lote = po.id_lote AND p.tipo_producto = 'Materia Prima'
                LEFT JOIN procesamientos_destino pd ON u.id_lote = pd.id_lote AND u.id_producto = pd.id_producto
                LEFT JOIN ventas_totales v ON u.id_lote = v.id_lote AND u.id_producto = v.id_producto
                LEFT JOIN ajustes_totales a ON u.id_lote = a.id_lote AND u.id_producto = a.id_producto
                ORDER BY u.id_lote DESC, p.tipo_producto ASC;
            """)
            
            for r in cursor.fetchall():
                id_lote, nombre_p, tipo_p, init_mp, a_corte, obt_pr, vendidos, ajustados, id_prod_real = r
                
                if tipo_p == "Materia Prima":
                    stock_fisico = float(init_mp) - float(a_corte) - float(vendidos) - float(ajustados)
                else:
                    stock_fisico = float(obt_pr) - float(vendidos) - float(ajustados)
                
                if stock_fisico > 0.01:
                    inventario_neto.append({
                        "Lote": id_lote, "Producto": nombre_p, "Tipo": tipo_p, "Inventario Físico": f"{stock_fisico:.2f} Kg"
                    })
                    label_combo = f"Lote #{id_lote} - {nombre_p} (Disp: {stock_fisico:.2f} Kg)"
                    lotes_opciones_ajuste[label_combo] = {
                        "id_lote": int(id_lote), "id_producto": int(id_prod_real), "max": float(stock_fisico)
                    }
                    
        except Exception as e: st.error(f"Error cargando almacén: {e}")
        finally: cursor.close(); conn.close()

    if not inventario_neto:
        st.info("❄️ El Cuarto Frío está vacío. Registre entradas o procesamientos.")
    else:
        st.table(inventario_neto)
        
    st.write("---")
    st.subheader("⚠️ Registrar Salida Extraordinaria (Ajuste de Almacén)")
    
    if lotes_opciones_ajuste:
        with st.form("form_ajuste_almacen", clear_on_submit=True):
            item_sel_text = st.selectbox("Selecciona el Lote and Producto a ajustar *:", list(lotes_opciones_ajuste.keys()))
            tipo_ajuste = st.selectbox("Tipo de Movimiento *:", ["Merma Almacén", "Cortesía"])
            kg_ajuste = st.number_input("Kilogramos a descontar *", min_value=0.0, step=0.1, format="%.2f")
            motivo = st.text_input("Detalle / Motivo *")
            fecha_ajuste = st.date_input("Fecha del Ajuste *")
            btn_guardar_ajuste = st.form_submit_button("💾 Aplicar Ajuste de Almacén")
            
        if btn_guardar_ajuste:
            meta = lotes_opciones_ajuste[item_sel_text]
            if kg_ajuste <= 0: st.error("⚠️ La cantidad debe ser mayor a cero.")
            elif kg_ajuste > meta["max"]: st.error(f"⚠️ Cantidad excede el disponible de {meta['max']} Kg.")
            elif not motivo: st.error("⚠️ El motivo del ajuste es obligatorio.")
            else:
                conn = obtener_conexion()
                if conn is not None:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO ajustes_inventario (fecha_ajuste, id_lote, id_producto, tipo_ajuste, kg_ajustados, motivo)
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """, (fecha_ajuste, meta["id_lote"], meta["id_producto"], tipo_ajuste, kg_ajuste, motivo))
                        conn.commit()
                        st.success(f"🎉 Ajuste registrado con éxito.")
                        st.rerun()
                    except Exception as e: st.error(f"Error al guardar ajuste: {e}")
                    finally: cursor.close(); conn.close()

# ==========================================
# MÓDULO 7: 💵 CONTROL DE COBRANZA
# ==========================================
elif opcion == "💵 Control de Cobranza":
    st.subheader("💵 Panel de Cobranza y Liquidación en Vivo")
    
    tab_captura, tab_correccion = st.tabs(["🖋️ Registrar Cobros", "🛠️ Corregir Errores de Captura"])
    f_hoy = datetime.now().date()
    
    with tab_captura:
        rango_cobro = st.selectbox("Selecciona el periodo de consulta de cobros:", ["Hoy", "📅 Día Específico", "Esta Semana", "Este Mes"])
        
        if rango_cobro == "Hoy":
            f_inicio = f_hoy
            f_fin = f_hoy
        elif rango_cobro == "📅 Día Específico":
            fecha_seleccionada = st.date_input("🎯 Elige el día que deseas auditar:", f_hoy)
            f_inicio = fecha_seleccionada
            f_fin = fecha_seleccionada
        elif rango_cobro == "Esta Semana":
            f_inicio = f_hoy - timedelta(days=f_hoy.weekday())
            f_fin = f_hoy
        else:
            f_inicio = f_hoy.replace(day=1)
            f_fin = f_hoy
        
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        v.id_venta,
                        v.fecha_venta,
                        c.nombre_cliente,
                        SUM(v.kg_vendidos * v.precio_por_kg) as total_nota,
                        v.estado_pago
                    FROM ventas v
                    JOIN clientes c ON v.id_cliente = c.id_cliente
                    WHERE v.fecha_venta BETWEEN %s AND %s
                    GROUP BY v.id_venta, v.fecha_venta, c.nombre_cliente, v.estado_pago
                    ORDER BY v.id_venta DESC;
                """, (f_inicio, f_fin))
                notas_cobranza = cursor.fetchall()
                
                if not notas_cobranza:
                    st.info(f"No hay movimientos de venta registrados en el periodo seleccionado.")
                else:
                    total_pagado = sum(float(n[3]) for n in notas_cobranza if n[4] == 'Pagado')
                    total_transcurso = sum(float(n[3]) for n in notas_cobranza if n[4] == 'En Transcurso')
                    total_pendiente = sum(float(n[3]) for n in notas_cobranza if n[4] == 'Pendiente')
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("✅ Ya Pagado", f"${total_pagado:,.2f}")
                    c2.metric("⏳ En Transcurso", f"${total_transcurso:,.2f}")
                    c3.metric("🚨 Pendiente", f"${total_pendiente:,.2f}", delta=f"{len([n for n in notas_cobranza if n[4]=='Pendiente'])} Notas")
                    
                    st.write("---")
                    st.markdown("#### 📂 Desglose Detallado de Saldos")
                    
                    tabla_cobros = []
                    dict_recaudacion = {}
                    for n in notas_cobranza:
                        tabla_cobros.append({
                            "Nota Ref": n[0], "Fecha": str(n[1]), "Cliente": n[2], "Importe Total": f"${float(n[3]):.2f}", "Estado Actual": n[4].upper()
                        })
                        if n[4] in ['En Transcurso', 'Pendiente']:
                            dict_recaudacion[f"Nota #{n[0]} - {n[2]} (${float(n[3]):.2f})"] = {"id": n[0], "total": float(n[3])}
                    
                    st.table(tabla_cobros)
                    
                    if dict_recaudacion:
                        st.write("---")
                        st.markdown("### 🖋️ Registrar Liquidación / Abono de Cliente")
                        nota_a_liquidar = st.selectbox("Selecciona la nota que va a liquidar o abonar:", list(dict_recaudacion.keys()))
                        meta_nota = dict_recaudacion[nota_a_liquidar]
                        
                        cursor.execute("SELECT COALESCE(SUM(monto_pagado), 0) FROM control_cobranza WHERE id_venta = %s;", (meta_nota["id"],))
                        total_abonado_previo = float(cursor.fetchone()[0] or 0.0)
                        
                        saldo_pendiente_actual = max(0.0, meta_nota["total"] - total_abonado_previo)
                        
                        if saldo_pendiente_actual <= 0:
                            st.warning("Nota sin saldo pendiente real. Verifique si ya fue liquidada.")
                        else:
                            monto_abono = st.number_input("Monto que está abonando el cliente ahora ($) *:", min_value=0.01, max_value=saldo_pendiente_actual, value=saldo_pendiente_actual, step=50.0, format="%.2f")
                            nuevo_saldo_restante = max(0.0, saldo_pendiente_actual - monto_abono)
                            
                            st.markdown("##### 📊 Previsualización del Movimiento en Caja")
                            cm1, cm2, cm3 = st.columns(3)
                            cm1.metric("Importe Total Nota", f"${meta_nota['total']:,.2f}")
                            cm2.metric("Abono a Registrar", f"${monto_abono:,.2f}", delta=f"-${monto_abono:,.2f}", delta_color="inverse")
                            cm3.metric("Saldo Quedante", f"${nuevo_saldo_restante:,.2f}", delta="¡Liquidado!" if nuevo_saldo_restante == 0 else "Resta por cobrar", delta_color="normal" if nuevo_saldo_restante == 0 else "off")
                            
                            with st.form("form_liquidar_nota"):
                                sugerencia_estado = ["Pagado", "En Transcurso", "Pendiente"] if nuevo_saldo_restante == 0 else ["En Transcurso", "Pendiente", "Pagado"]
                                nuevo_estado = st.selectbox("Cambiar condición de cobranza a:", sugerencia_estado)
                                metodo = st.selectbox("Método de Ingreso:", ["Efectivo", "Transferencia Bancaria"])
                                btn_actualizar_cobro = st.form_submit_button("💾 Registrar Pago en Caja")
                                
                            if btn_actualizar_cobro:
                                cursor.execute("UPDATE ventas SET estado_pago = %s WHERE id_venta = %s;", (nuevo_estado, meta_nota["id"]))
                                cursor.execute("""
                                    INSERT INTO control_cobranza (id_venta, fecha_pago, monto_pagado, metodo_pago) 
                                    VALUES (%s, %s, %s, %s);
                                """, (meta_nota["id"], f_hoy, monto_abono, metodo))
                                conn.commit()
                                st.success(f"🎉 ¡Abono de ${monto_abono:,.2f} registrado con éxito en caja!")
                                st.rerun()
            except Exception as e: st.error(f"Error en panel de cobranza: {e}")
            finally: cursor.close(); conn.close()

    with tab_correccion:
        st.markdown("### 🛠️ Corrección Dinámica de Dinero en Caja")
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        cc.id_cobro, 
                        cc.id_venta, 
                        c.nombre_cliente, 
                        cc.monto_pagado, 
                        cc.metodo_pago, 
                        cc.fecha_pago
                    FROM control_cobranza cc
                    JOIN ventas v ON cc.id_venta = v.id_venta
                    JOIN clientes c ON v.id_cliente = c.id_cliente
                    ORDER BY cc.id_cobro DESC LIMIT 50;
                """)
                abonos_guardados = cursor.fetchall()
                
                if not abonos_guardados:
                    st.info("No se han registrado abonos todavía en la tabla `control_cobranza`.")
                else:
                    dict_abonos = {}
                    for ab in abonos_guardados:
                        id_cobro, id_venta, cliente, monto, metodo_p, fecha = ab
                        label = f"Pago ID: {id_cobro} | Nota #{id_venta} - {cliente} por ${float(monto):.2f} ({metodo_p})"
                        dict_abonos[label] = {"id_cobro": id_cobro, "monto_actual": float(monto), "metodo_actual": metodo_p, "id_venta": id_venta}
                    
                    abono_a_corregir = st.selectbox("Selecciona el abono capturado erróneamente:", list(dict_abonos.keys()))
                    meta_abono = dict_abonos[abono_a_corregir]
                    
                    st.write("---")
                    st.markdown("#### 🖋️ Datos Modificables")
                    
                    with st.form("form_corregir_abono"):
                        nuevo_monto_caja = st.number_input("Corregir cantidad real pagada ($):", min_value=0.01, value=meta_abono["monto_actual"], step=50.0, format="%.2f")
                        nuevo_metodo_caja = st.selectbox("Corregir Método:", ["Efectivo", "Transferencia Bancaria"], index=0 if meta_abono["metodo_actual"] == "Efectivo" else 1)
                        correccion_estado_nota = st.selectbox("Re-ajustar Estado de la Nota de Remisión a:", ["Pagado", "En Transcurso", "Pendiente"])
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            btn_guardar_correccion = st.form_submit_button("💾 Actualizar Valores en Sistema", type="primary")
                        with col_btn2:
                            btn_eliminar_abono = st.form_submit_button("🗑️ Eliminar este abono por completo")
                    
                    if btn_guardar_correccion:
                        cursor.execute("""
                            UPDATE control_cobranza 
                            SET monto_pagado = %s, metodo_pago = %s 
                            WHERE id_cobro = %s;
                        """, (nuevo_monto_caja, nuevo_metodo_caja, meta_abono["id_cobro"]))
                        
                        cursor.execute("UPDATE ventas SET estado_pago = %s WHERE id_venta = %s;", (correccion_estado_nota, meta_abono["id_venta"]))
                        conn.commit()
                        st.success("🎉 ¡El registro en caja y la nota fueron corregidos exitosamente!")
                        st.rerun()
                        
                    if btn_eliminar_abono:
                        cursor.execute("DELETE FROM control_cobranza WHERE id_cobro = %s;", (meta_abono["id_cobro"],))
                        cursor.execute("UPDATE ventas SET estado_pago = %s WHERE id_venta = %s;", (correccion_estado_nota, meta_abono["id_venta"]))
                        conn.commit()
                        st.success("🗑️ ¡El abono seleccionado ha sido eliminado del historial financiero!")
                        st.rerun()
            except Exception as e: st.error(f"Error procesando la corrección: {e}")
            finally: cursor.close(); conn.close()

# ==========================================
# MÓDULO 8: HISTORIAL DE NOTAS
# ==========================================
elif opcion == "📑 Historial de Notas":
    st.subheader("📑 Auditoría y Consulta de Notas de Remisión")
    tab_clientes, tab_proveedores, tab_ajustes = st.tabs(["👥 Notas de Clientes (Ventas)", "📋 Notas de Proveedores (Entradas)", "⚠️ Historial de Ajustes (Almacén)"])
    fecha_hoy = datetime.now().date()
    
    with tab_clientes:
        filtro_tiempo = st.selectbox("Rango Clientes:", ["Hoy", "Esta Semana", "Este Mes"], key="t_cli")
        f_inicio = fecha_hoy if filtro_tiempo == "Hoy" else (fecha_hoy - timedelta(days=fecha_hoy.weekday()) if filtro_tiempo == "Esta Semana" else fecha_hoy.replace(day=1))
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT v.id_venta, v.fecha_venta, c.nombre_cliente, pr.nombre_producto, v.id_lote, v.kg_vendidos, v.precio_por_kg, (v.kg_vendidos * v.precio_por_kg) as total
                    FROM ventas v JOIN clientes c ON v.id_cliente = c.id_cliente JOIN productos pr ON v.id_producto = pr.id_producto
                    WHERE v.fecha_venta BETWEEN %s AND %s ORDER BY v.id_venta DESC;
                """, (f_inicio, fecha_hoy))
                records = cursor.fetchall()
                if not records: st.info("No hay ventas en este periodo.")
                else:
                    st.metric("Monto Total Recaudado", f"${sum(float(r[7]) for r in records):,.2f}")
                    st.table([{"Ref Nota": r[0], "Fecha": str(r[1]), "Cliente": r[2], "Producto": r[3], "Lote": r[4], "Kilos": float(r[5]), "Precio/Kg": f"${float(r[6]):.2f}", "Total": f"${float(r[7]):.2f}"} for r in records])
                    
                    st.markdown("#### 🔄 Reimpresión de Notas de Venta")
                    nota_a_reimprimir = st.selectbox("Selecciona Nota:", [f"Nota #{r[0]} - {r[2]}" for r in records], key="sel_v")
                    id_nota_reimp = int(nota_a_reimprimir.split(" ")[1].replace("#", ""))
                    if st.button("⚙️ Re-generar PDF Venta"):
                        datos_nota = [r for r in records if r[0] == id_nota_reimp]
                        items_pdf = [{"id_lote": d[4], "producto_nombre": d[3], "kg": d[5], "precio": d[6], "total": d[7]} for d in datos_nota]
                        pdf_reimp = bytes(generar_pdf_nota(id_nota_reimp, datos_nota[0][2], str(datos_nota[0][1]), items_pdf))
                        st.download_button("📥 Descargar Copia PDF Venta", data=pdf_reimp, file_name=f"Copia_Nota_{id_nota_reimp}.pdf", mime="application/pdf")
            except Exception as e: st.error(f"Error: {e}")
            finally: cursor.close(); conn.close()

    with tab_proveedores:
        filtro_tiempo_p = st.selectbox("Rango Proveedores:", ["Hoy", "Esta Semana", "Este Mes"], key="t_prov")
        f_inicio_p = fecha_hoy if filtro_tiempo_p == "Hoy" else (fecha_hoy - timedelta(days=fecha_hoy.weekday()) if filtro_tiempo_p == "Esta Semana" else fecha_hoy.replace(day=1))
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT l.id_lote, l.fecha_entrada, p.nombre_empresa, pr.nombre_producto, l.kg_recibidos, l.cantidad_cajas, l.costo_por_kg, (l.kg_recibidos * l.costo_por_kg) as total
                    FROM lotes_entrada l JOIN proveedores p ON l.id_proveedor = p.id_proveedor JOIN productos pr ON l.id_producto = pr.id_producto
                    WHERE l.fecha_entrada BETWEEN %s AND %s ORDER BY l.id_lote DESC;
                """, (f_inicio_p, fecha_hoy))
                records_p = cursor.fetchall()
                if not records_p: st.info("No hay entradas registradas en este periodo.")
                else:
                    st.metric("Total Kilos Suministrados", f"{sum(float(r[4]) for r in records_p):,.2f} Kg")
                    st.table([{"Lote": r[0], "Fecha": str(r[1]), "Proveedor": r[2], "Producto": r[3], "Kilos": float(r[4]), "Cajas": r[5], "Costo/Kg": f"${float(r[6]):.2f}" if st.session_state.rol == "admin" else "RESTRINGIDO", "Total Lote": f"${float(r[7]):.2f}" if st.session_state.rol == "admin" else "RESTRINGIDO"} for r in records_p])
                    
                    st.markdown("#### Reimpresion de Notas de Entrada")
                    modo_reimpresion_p = st.radio("Tipo de reimpresion:", ["Por lote", "Por proveedor"], horizontal=True, key="modo_reimp_p")

                    if modo_reimpresion_p == "Por lote":
                        lote_a_reimprimir = st.selectbox("Selecciona Lote a Re-imprimir:", [f"Lote #{r[0]} - {r[2]}" for r in records_p], key="sel_p")
                        id_lote_reimp = int(lote_a_reimprimir.split(" ")[1].replace("#", ""))
                        if st.button("Re-generar PDF Entrada", key="btn_reimp_lote_p"):
                            d_l = [r for r in records_p if r[0] == id_lote_reimp][0]
                            pdf_prov_reimp = bytes(generar_pdf_proveedor(d_l[0], d_l[2], d_l[3], d_l[4], d_l[5], d_l[6], str(d_l[1])))
                            st.download_button("Descargar Copia PDF Entrada", data=pdf_prov_reimp, file_name=f"Copia_Entrada_Lote_{id_lote_reimp}.pdf", mime="application/pdf")
                    else:
                        proveedores_periodo = sorted({r[2] for r in records_p})
                        proveedor_a_reimprimir = st.selectbox("Selecciona Proveedor a Re-imprimir:", proveedores_periodo, key="sel_proveedor_pdf")
                        registros_proveedor = [r for r in records_p if r[2] == proveedor_a_reimprimir]
                        st.caption(f"Se incluiran {len(registros_proveedor)} lote(s) del periodo seleccionado.")

                        if st.button("Re-generar PDF por Proveedor", key="btn_reimp_proveedor_p"):
                            items_proveedor = [{
                                "id_lote": r[0],
                                "fecha": str(r[1]),
                                "producto": r[3],
                                "kg": r[4],
                                "cajas": r[5],
                                "costo": r[6],
                                "total": r[7]
                            } for r in registros_proveedor]
                            pdf_proveedor = bytes(generar_pdf_proveedor_resumen(proveedor_a_reimprimir, str(f_inicio_p), str(fecha_hoy), items_proveedor))
                            nombre_archivo_proveedor = proveedor_a_reimprimir.replace(" ", "_").replace("/", "-")
                            st.download_button(
                                "Descargar Copia PDF Proveedor",
                                data=pdf_proveedor,
                                file_name=f"Copia_Entradas_{nombre_archivo_proveedor}_{f_inicio_p}_a_{fecha_hoy}.pdf",
                                mime="application/pdf"
                            )
            except Exception as e: st.error(f"Error: {e}")
            finally: cursor.close(); conn.close()

    with tab_ajustes:
        filtro_tiempo_a = st.selectbox("Rango Ajustes Almacén:", ["Hoy", "Esta Semana", "Este Mes"], key="t_ajuste")
        f_inicio_a = fecha_hoy if filtro_tiempo_a == "Hoy" else (fecha_hoy - timedelta(days=fecha_hoy.weekday()) if filtro_tiempo_a == "Esta Semana" else fecha_hoy.replace(day=1))
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.id_ajuste, a.fecha_ajuste, a.id_lote, p.nombre_producto, a.tipo_ajuste, a.kg_ajustados, a.motivo
                    FROM ajustes_inventario a JOIN productos p ON a.id_producto = p.id_producto
                    WHERE a.fecha_ajuste BETWEEN %s AND %s ORDER BY a.id_ajuste DESC;
                """, (f_inicio_a, fecha_hoy))
                records_a = cursor.fetchall()
                if not records_a: st.info("No hay mermas ni cortesías en este periodo.")
                else:
                    st.table([{"ID": r[0], "Fecha": str(r[1]), "Lote": r[2], "Producto": r[3], "Tipo Ajuste": r[4], "Kilos": float(r[5]), "Motivo": r[6]} for r in records_a])
            except Exception as e: st.error(f"Error: {e}")
            finally: cursor.close(); conn.close()

# ==========================================
# MÓDULO 9: DASHBOARD Y MÉTRICAS
# ==========================================
elif opcion == "📈 Dashboard y Métricas":
    st.subheader("📈 Ingeniería de Procesos y Métricas")
    lotes_opciones = {}
    conn = obtener_conexion()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT l.id_lote, p.nombre_producto, l.kg_recibidos, l.fecha_entrada FROM lotes_entrada l JOIN productos p ON l.id_producto = p.id_producto ORDER BY l.id_lote DESC;")
            for r in cursor.fetchall(): lotes_opciones[f"Lote #{r[0]} - {r[1]} ({float(r[2])} Kg)"] = r[0]
        except Exception as e: st.error(f"Error: {e}")
        finally: cursor.close(); conn.close()

    if lotes_opciones:
        lote_sel = st.selectbox("🎯 Selecciona un Lote:", list(lotes_opciones.keys()))
        id_l = lotes_opciones[lote_sel]
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT kg_recibidos, costo_por_kg, id_producto FROM lotes_entrada WHERE id_lote = %s;", (id_l,))
                dc = cursor.fetchone()
                kg_init = float(dc[0]); inv = kg_init * float(dc[1]); id_producto_lote = dc[2]
                
                cursor.execute("SELECT SUM(kg_materia_prima), SUM(kg_procesados) FROM salidas_procesado WHERE id_lote = %s;", (id_l,))
                rp = cursor.fetchone()
                kg_corte = float(rp[0]) if rp[0] else 0.0; kg_limpio = float(rp[1]) if rp[1] else 0.0
                
                cursor.execute("SELECT SUM(v.kg_vendidos) FROM ventas v JOIN productos p ON v.id_producto = p.id_producto WHERE v.id_lote = %s AND p.tipo_producto = 'Materia Prima';", (id_l,))
                kg_v_mp = float(cursor.fetchone()[0] or 0.0)
                
                cursor.execute("SELECT SUM(kg_vendidos * precio_por_kg) FROM ventas WHERE id_lote = %s;", (id_l,))
                ing = float(cursor.fetchone()[0] or 0.0)
                
                cursor.execute("SELECT SUM(kg_ajustados) FROM ajustes_inventario WHERE id_lote = %s AND id_producto = %s;", (id_l, id_producto_lote))
                aj_mp = float(cursor.fetchone()[0] or 0.0)
                
                resg = max(0.0, kg_init - kg_v_mp - kg_corte - aj_mp)
                merma = max(0.0, kg_corte - kg_limpio)
                
                st.markdown("### 💰 Balance Financiero")
                c1, c2, c3 = st.columns(3)
                c1.metric("Inversión", f"${inv:,.2f}")
                c2.metric("Ingresos", f"${ing:,.2f}")
                c3.metric("Utilidad", f"${ing-inv:,.2f}", delta=f"${ing-inv:,.2f}")
                
                st.write("---")
                st.markdown("### 📦 Cuarto Frío e Inventario")
                st.columns(3)[0].metric("Inicial", f"{kg_init:,.2f} Kg")
                st.columns(3)[1].metric("Vendido MP", f"{kg_v_mp:,.2f} Kg")
                st.columns(3)[2].metric("Resguardo", f"{resg:,.2f} Kg")
                
                st.write("---")
                st.markdown("### ⚖️ Rendimiento Técnico de Deshuese")
                st.columns(3)[0].metric("A Mesa", f"{kg_corte:,.2f} Kg")
                st.columns(3)[1].metric("Limpio", f"{kg_limpio:,.2f} Kg", f"{(kg_limpio/kg_corte*100) if kg_corte>0 else 0:.1f}%")
                st.columns(3)[2].metric("Merma", f"{merma:,.2f} Kg", f"{(merma/kg_corte*100) if kg_corte>0 else 0:.1f}% Merma", delta_color="inverse")
            except Exception as e: st.error(f"Error: {e}")
            finally: cursor.close(); conn.close()
