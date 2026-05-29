import streamlit as st
from pathlib import Path
from database import obtener_conexion

# Configuración inicial de la página
st.set_page_config(page_title="Distribuidora Gualhe", page_icon="🐔", layout="centered")

# 🛒 INICIALIZAR VARIABLES DE SESIÓN (Carrito y Control de Usuarios)
if "carrito_ventas" not in st.session_state:
    st.session_state.carrito_ventas = []
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol" not in st.session_state:
    st.session_state.rol = None

# --- 📁 CONFIGURACIÓN DE RUTA DEL LOGO LOCAL ---
carpeta_actual = Path(__file__).parent
ruta_logo = carpeta_actual / "logo.png"

# Si por alguna razón se quedó guardado como logo.png.png lo detecta igual
if not ruta_logo.exists():
    ruta_logo = carpeta_actual / "logo.png.png"

# --- 🔐 CONTROL DE ACCESO (LOGIN CON LOGO INTEGRADO) ---
if not st.session_state.autenticado:
    # 🎨 AGREGAR LOGO EN LA PANTALLA DE INICIO DE SESIÓN
    if ruta_logo.exists():
        col_izq, col_centro, col_der = st.columns([1, 2, 1])
        with col_centro:
            st.image(str(ruta_logo), use_container_width=True)
            
    # 🛠️ CORRECCIÓN DE SINTAXIS: Cambiamos unsafe_html por unsafe_allow_html
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
        else:
            st.error("❌ Usuario o contraseña incorrectos.")
    st.stop() # Detiene la app aquí si no se han firmado

# --- MENÚ LATERAL DE NAVEGACIÓN ---
if ruta_logo.exists():
    st.sidebar.image(str(ruta_logo), use_container_width=True)
else:
    st.sidebar.title("🍗 Distribuidora Gualhe")

st.sidebar.write(f"👤 **Usuario:** {st.session_state.rol.upper()}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.carrito_ventas = []
    st.rerun()

# 🚀 FILTRADO DE MENÚ SEGÚN EL ROL
if st.session_state.rol == "admin":
    modulos_disponibles = ["📋 Proveedores", "📦 Catálogo de Productos", "⚖️ Entradas de Lotes", "🔪 Procesamiento", "👥 Clientes y Ventas", "📈 Dashboard y Métricas"]
else:
    modulos_disponibles = ["⚖️ Entradas de Lotes", "🔪 Procesamiento", "👥 Clientes y Ventas"]

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
# MÓDULO 3: ENTRADAS DE LOTES
# ==========================================
elif opcion == "⚖️ Entradas de Lotes":
    st.subheader("Registro de Entradas de Lotes (Materia Prima)")
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
                        st.success(f"🎉 ¡Lote registrado con éxito! **ID DE LOTE: {id_lote_generado}**")
                    except Exception as e: st.error(f"❌ Error al guardar el lote: {e}")
                    finally: cursor.close(); conn.close()

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

# ==========================================
# MÓDULO 4: PROCESAMIENTO (ADMIN Y OPERADOR)
# ==========================================
elif opcion == "🔪 Procesamiento":
    st.subheader("🔪 Departamento de Procesamiento y Deshuese")
    lotes_lista = []
    productos_procesados_dict = {}
    conn = obtener_conexion()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT l.id_lote, p.nombre_producto, l.kg_recibidos, l.fecha_entrada FROM lotes_entrada l JOIN productos p ON l.id_producto = p.id_producto;")
            for row in cursor.fetchall():
                lotes_lista.append((f"Lote {row[0]} - {row[1]} ({float(row[2])} Kg) - {row[3]}", row[0]))
            cursor.execute("SELECT id_producto, nombre_producto FROM productos WHERE tipo_producto = 'Procesado';")
            for prod in cursor.fetchall(): productos_procesados_dict[prod[1]] = prod[0]
        except Exception as e: st.error(f"Error: {e}")
        finally: cursor.close(); conn.close()

    if not lotes_lista or not productos_procesados_dict:
        st.warning("⚠️ No hay lotes o productos procesados disponibles.")
    else:
        with st.form("formulario_proceso", clear_on_submit=True):
            lote_seleccionado_texto = st.selectbox("Selecciona el Lote de Origen a Procesar *", [lbl for lbl, _ in lotes_lista])
            kg_materia_prima_a_cortar = st.number_input("Kilogramos de Pollo Entero extraídos para corte *", min_value=0.0, step=0.1, format="%.2f")
            st.write("---")
            prod_procesado_seleccionado = st.selectbox("Subproducto Obtenido:", list(productos_procesados_dict.keys()))
            kg_pros = st.number_input("Kilogramos de Carne Limpia Obtenidos *", min_value=0.0, step=0.1, format="%.2f")
            fecha_proceso = st.date_input("Fecha de Procesamiento *")
            boton_guardar_proceso = st.form_submit_button("Registrar Salida de Producción")

        if boton_guardar_proceso:
            if kg_materia_prima_a_cortar <= 0 or kg_pros <= 0: st.error("⚠️ Valores deben ser mayores a cero.")
            elif kg_pros > kg_materia_prima_a_cortar: st.error("⚠️ Error lógico en pesos.")
            else:
                id_lote_real = [id_num for lbl, id_num in lotes_lista if lbl == lote_seleccionado_texto][0]
                id_prod_real = productos_procesados_dict[prod_procesado_seleccionado]
                conn = obtener_conexion()
                if conn is not None:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO salidas_procesado (id_lote, id_producto, kg_materia_prima, kg_procesados, fecha_proceso) VALUES (%s, %s, %s, %s, %s);", (id_lote_real, id_prod_real, kg_materia_prima_a_cortar, kg_pros, fecha_proceso))
                        conn.commit()
                        st.success("🎉 ¡Transformación registrada!")
                    except Exception as e: st.error(f"❌ Error: {e}")
                    finally: cursor.close(); conn.close()

    st.write("---")
    st.subheader("📋 Historial de Pollo Procesado")
    conn = obtener_conexion()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT s.id_procesado, s.id_lote, p.nombre_producto, s.kg_materia_prima, s.kg_procesados, s.fecha_proceso FROM salidas_procesado s JOIN productos p ON s.id_producto = p.id_producto ORDER BY s.id_procesado DESC;")
            datos_proceso = cursor.fetchall()
            if datos_proceso:
                st.table([{"ID": f[0], "Lote Origen": f[1], "Corte": f[2], "Kg MP": float(f[3]), "Kg Obtenidos": float(f[4]), "Fecha": str(f[5])} for f in datos_proceso])
        except Exception as e: st.error(f"Error: {e}")
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
        clientes_dict, lotes_lista, productos_dict = {}, [], {}
        conn = obtener_conexion()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id_cliente, nombre_cliente FROM clientes;")
                for cl in cursor.fetchall(): clientes_dict[cl[1]] = cl[0]
                cursor.execute("SELECT id_lote, fecha_entrada FROM lotes_entrada;")
                for lt in cursor.fetchall(): lotes_lista.append((f"Lote #{lt[0]} (Ingreso: {lt[1]})", lt[0]))
                cursor.execute("SELECT id_producto, nombre_producto, tipo_producto FROM productos;")
                for pr in cursor.fetchall(): productos_dict[f"{pr[1]} [{pr[2]}]"] = pr[0]
            except Exception as e: st.error(f"Error: {e}")
            finally: cursor.close(); conn.close()

        if clientes_dict and lotes_lista and productos_dict:
            col1, col2 = st.columns(2)
            with col1: c_sel = st.selectbox("Selecciona el Cliente:", list(clientes_dict.keys()))
            with col2: fecha_v = st.date_input("Fecha de la Nota *")
            st.write("---")
            
            st.markdown("#### 🛒 Agregar Productos")
            with st.form("form_renglon_venta", clear_on_submit=False):
                col_l, col_p, col_k, col_pr = st.columns([2, 2, 1, 1])
                with col_l: l_sel_text = st.selectbox("Lote:", [lbl for lbl, _ in lotes_lista])
                with col_p: p_sel = st.selectbox("Producto:", list(productos_dict.keys()))
                with col_k: kg_v = st.number_input("Kilos *", min_value=0.0, step=0.1)
                with col_pr: precio_v = st.number_input("Precio/Kg *", min_value=0.0, step=0.5)
                btn_agregar_carrito = st.form_submit_button("➕ Agregar Producto")

            if btn_agregar_carrito:
                if kg_v <= 0 or precio_v <= 0: st.error("⚠️ Valores requeridos.")
                else:
                    id_l = [id_num for lbl, id_num in lotes_lista if lbl == l_sel_text][0]
                    st.session_state.carrito_ventas.append({"id_lote": id_l, "producto_nombre": p_sel, "id_producto": productos_dict[p_sel], "kg": kg_v, "precio": precio_v, "total": kg_v * precio_v})
                    st.toast(f"✅ Añadido: {p_sel}")

            if st.session_state.carrito_ventas:
                st.write("### 📝 Vista Previa")
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
                                    cursor.execute("INSERT INTO ventas (fecha_venta, id_cliente, id_lote, id_producto, kg_vendidos, precio_por_kg) VALUES (%s, %s, %s, %s, %s, %s);", (fecha_v, id_c, item["id_lote"], item["id_producto"], item["kg"], item["precio"]))
                                conn.commit()
                                st.success("🎉 ¡Nota guardada!")
                                st.session_state.carrito_ventas = []
                                st.rerun()
                            except Exception as e: st.error(f"Error: {e}")
                            finally: cursor.close(); conn.close()
                with b_del:
                    if st.button("🗑️ Vaciar Nota"):
                        st.session_state.carrito_ventas = []
                        st.rerun()

# ==========================================
# MÓDULO 6: DASHBOARD Y MÉTRICAS (SOLO ADMIN)
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
                cursor.execute("SELECT kg_recibidos, costo_por_kg FROM lotes_entrada WHERE id_lote = %s;", (id_l,))
                dc = cursor.fetchone()
                kg_init = float(dc[0]); inv = kg_init * float(dc[1])
                
                cursor.execute("SELECT SUM(kg_materia_prima), SUM(kg_procesados) FROM salidas_procesado WHERE id_lote = %s;", (id_l,))
                rp = cursor.fetchone()
                kg_corte = float(rp[0]) if rp[0] else 0.0; kg_limpio = float(rp[1]) if rp[1] else 0.0
                
                cursor.execute("SELECT SUM(v.kg_vendidos) FROM ventas v JOIN productos p ON v.id_producto = p.id_producto WHERE v.id_lote = %s AND p.tipo_producto = 'Materia Prima';", (id_l,))
                kg_v_mp = float(cursor.fetchone()[0] or 0.0)
                
                cursor.execute("SELECT SUM(kg_vendidos * precio_por_kg) FROM ventas WHERE id_lote = %s;", (id_l,))
                ing = float(cursor.fetchone()[0] or 0.0)
                
                resg = max(0.0, kg_init - kg_v_mp - kg_corte)
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