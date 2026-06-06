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
