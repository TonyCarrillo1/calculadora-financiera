import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Calculadora Financiera Pro",
    page_icon="📈",
    layout="wide"
)

# Estilos CSS ligeros
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Simulador de Inversión Avanzado")
st.markdown("Proyecta el crecimiento de tu patrimonio con aportes mensuales y **extraordinarios**.")

# --- BARRA LATERAL (CONTROLES) ---
with st.sidebar:
    st.header("1. Tu Inversión")
    
    # Fecha de inicio para calcular cuándo caen los abonos
    fecha_inicio = st.date_input("Fecha de Inicio", value=date.today())
    
    saldo_inicial = st.number_input("Saldo Inicial (₡)", value=0, step=100000, format="%d")
    aporte_mensual = st.number_input("Aporte Mensual (₡)", value=20000, step=5000, format="%d")
    plazo_anos = st.number_input("Plazo (Años)", value=30, min_value=1, step=1)
    
    st.markdown("---")
    
    st.header("2. Variables del Entorno")
    inflacion = st.number_input("Inflación Anual (%)", value=3.0, step=0.1, format="%.1f")
    comision = st.number_input("Comisión Rendimientos (%)", value=10.0, step=0.5, format="%.1f", help="Se cobra sobre las ganancias")

    st.markdown("---")
    st.header("3. Tasas de Escenarios (Brutas)")
    st.caption("Rendimiento anual esperado antes de comisiones.")
    
    tasa_conservador = st.number_input("🛡️ Conservador (%)", value=9.0, step=0.25, format="%.2f")
    tasa_moderado = st.number_input("⚖️ Moderado (%)", value=10.0, step=0.25, format="%.2f")
    tasa_optimista = st.number_input("🚀 Optimista (%)", value=17.0, step=0.25, format="%.2f")

    st.markdown("---")
    
    # SECCIÓN: Abonos Extraordinarios (MEJORADA)
    st.header("4. Abonos Extraordinarios")
    st.caption("Añade fechas específicas para inyectar capital extra (ej. Aguinaldos).")
    
    with st.expander("Gestionar Tabla de Abonos", expanded=False):
        df_base = pd.DataFrame(columns=["Fecha", "Monto"])
        
        abonos_df = st.data_editor(
            df_base,
            num_rows="dynamic",
            column_config={
                "Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY", required=True),
                "Monto": st.column_config.NumberColumn("Monto (₡)", format="%d", min_value=0, required=True)
            },
            key="abonos_editor"
        )
    
    st.markdown("---")
    
    # NUEVO: Control de Visualización
    st.header("5. Visualización")
    escenario_view = st.selectbox(
        "Seleccionar Escenario a Detallar", 
        ["Todos", "Conservador", "Moderado", "Optimista"]
    )

# --- LÓGICA DE CÁLCULO ---

def calcular_escenario_completo(tasa_bruta_pct, anos, aporte, inicial, comision_pct, inflacion_pct, abonos_extra_df, start_date):
    meses = int(anos * 12)
    
    # --- Procesamiento de Abonos Extraordinarios ---
    abonos_map = {}
    
    if start_date is None:
        start_date = date.today()
    
    if not abonos_extra_df.empty:
        # Limpiamos filas vacías
        df_limpio = abonos_extra_df.dropna(subset=["Fecha", "Monto"]).copy()
        
        for index, row in df_limpio.iterrows():
            try:
                # CORRECCIÓN CLAVE: Forzamos la conversión a fecha real
                # Esto evita que una fecha en formato texto sea ignorada
                fecha_abono = pd.to_datetime(row["Fecha"])
                monto_abono = float(row["Monto"])
                
                # Calcular meses de diferencia
                diff_meses = (fecha_abono.year - start_date.year) * 12 + (fecha_abono.month - start_date.month)
                
                # Solo sumar si cae dentro del plazo (y es futuro)
                if 0 <= diff_meses < meses:
                    if diff_meses in abonos_map:
                        abonos_map[diff_meses] += monto_abono
                    else:
                        abonos_map[diff_meses] = monto_abono
            except Exception:
                # Si la fila tiene datos basura, la saltamos sin romper la app
                continue

    # --- Tasas ---
    tasa_neta_nominal_anual = (tasa_bruta_pct / 100) * (1 - (comision_pct / 100))
    tasa_real_neta_anual = ((1 + tasa_neta_nominal_anual) / (1 + (inflacion_pct / 100))) - 1
    tasa_mensual_efectiva = (1 + tasa_neta_nominal_anual)**(1/12) - 1
    
    # --- Proyección Mes a Mes ---
    valores_nominales = [inicial]
    serie_aportes = [inicial] # Nueva lista para graficar composición
    serie_real = [inicial]    # Nueva lista para graficar valor real mes a mes
    
    total_depositado = inicial
    
    for i in range(meses):
        interes = valores_nominales[-1] * tasa_mensual_efectiva
        
        # Verificar abono extra este mes
        extra_este_mes = abonos_map.get(i, 0)
        
        # Totales
        nuevo_saldo = valores_nominales[-1] + interes + aporte + extra_este_mes
        nuevo_aporte_acumulado = total_depositado + aporte + extra_este_mes
        
        # Calculo de Valor Real mes a mes (descontando inflación mensual aprox)
        inflacion_mensual = (1 + inflacion_pct/100)**(1/12) - 1
        nuevo_saldo_real = nuevo_saldo / ((1 + inflacion_mensual)**(i+1))

        # Guardar en listas
        valores_nominales.append(nuevo_saldo)
        serie_aportes.append(nuevo_aporte_acumulado)
        serie_real.append(nuevo_saldo_real)
        
        total_depositado += (aporte + extra_este_mes)
        
    saldo_final_nominal = valores_nominales[-1]
    
    # Valor Real Final
    saldo_final_real = serie_real[-1]
    
    return {
        "serie_nominal": valores_nominales,
        "serie_aportes": serie_aportes, # Necesario para gráfico composición
        "serie_real": serie_real,       # Necesario para gráfico inflación
        "saldo_nominal": saldo_final_nominal,
        "saldo_real": saldo_final_real,
        "tasa_real_neta": tasa_real_neta_anual,
        "total_depositado": total_depositado
    }

escenarios_data = {
    "Conservador": tasa_conservador,
    "Moderado": tasa_moderado,
    "Optimista": tasa_optimista
}

# --- VISUALIZACIÓN ---
st.markdown("### 🏁 Resultados Comparativos")

cols = st.columns(3)
datos_grafico = pd.DataFrame()

# Guardaremos los resultados completos para usar en los otros tabs
resultados_completos = {}

for (nombre, tasa_input), col in zip(escenarios_data.items(), cols):
    res = calcular_escenario_completo(
        tasa_input, plazo_anos, aporte_mensual, saldo_inicial, comision, inflacion, abonos_df, fecha_inicio
    )
    resultados_completos[nombre] = res
    
    puntos = [res["serie_nominal"][i*12] for i in range(plazo_anos + 1)]
    datos_grafico[nombre] = puntos
    
    with col:
        # Detectar si este escenario es el seleccionado
        is_selected = (escenario_view == nombre)
        
        if is_selected:
            # Resaltado visual con fondo dorado y borde
            st.markdown(f"""
            <div style="background-color: rgba(255, 215, 0, 0.15); padding: 10px; border-radius: 8px; border: 1px solid #ffd700; text-align: center; margin-bottom: 10px;">
                <h4 style="margin:0; color: #d4af37;">🎯 {nombre} ({tasa_input}%)</h4>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.subheader(f"{nombre} ({tasa_input}%)")
            
        st.metric(label="Saldo Nominal Futuro", value=f"₡ {res['saldo_nominal']:,.0f}")
        
        st.markdown(f"""
        <div style="margin-top: -10px;">
            <span style="font-size: 0.9em; color: gray;">Valor Real (Poder de compra hoy)</span><br>
            <span style="font-size: 1.3em; font-weight: bold; color: #2ca02c;">₡ {res['saldo_real']:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        ganancia_pura = res['saldo_nominal'] - res['total_depositado']
        
        # Mensaje final: Verde si es seleccionado, Azul si no
        msg = f"**Inversión Total:** ₡ {res['total_depositado']:,.0f}\n\n**Ganancia Intereses:** ₡ {ganancia_pura:,.0f}"
        
        if is_selected:
            st.success(msg, icon="🌟")
        else:
            st.info(msg, icon="💰")

st.markdown("---")

# PESTAÑAS AMPLIADAS
tab1, tab2, tab3, tab4 = st.tabs(["📈 Crecimiento", "🍰 Composición (Interés vs Capital)", "💸 Impacto Inflación", "📋 Tabla Detallada"])

# TAB 1: Gráfico de Crecimiento
with tab1:
    if escenario_view == "Todos":
        st.subheader("Evolución Comparativa (Todos los Escenarios)")
        st.line_chart(datos_grafico, use_container_width=True)
        st.caption("Comparación de los saldos nominales de los 3 escenarios.")
    else:
        st.subheader(f"Evolución - Escenario {escenario_view}")
        # Filtramos solo la columna seleccionada
        st.line_chart(datos_grafico[escenario_view], use_container_width=True)
        st.caption(f"Proyección detallada para el perfil {escenario_view}.")

# Lógica para determinar qué escenario mostrar en los detalles
if escenario_view == "Todos":
    target_escenario = "Moderado"
    aviso_escenario = "Mostrando escenario **Moderado** por defecto (selecciona uno específico en el menú para cambiar)."
else:
    target_escenario = escenario_view
    aviso_escenario = f"Analizando escenario: **{target_escenario}**"

# TAB 2: Gráfico de Área (Composición)
with tab2:
    st.subheader(f"¿Cuánto es mi esfuerzo y cuánto es ganancia? ({target_escenario})")
    st.caption(aviso_escenario)
    
    # Usamos el escenario seleccionado
    res_target = resultados_completos[target_escenario]
    
    # Preparamos datos anuales
    datos_area = pd.DataFrame({
        "Tu Aporte": [res_target["serie_aportes"][i*12] for i in range(plazo_anos + 1)],
        "Intereses Ganados": [(res_target["serie_nominal"][i*12] - res_target["serie_aportes"][i*12]) for i in range(plazo_anos + 1)]
    })
    
    # Gráfico de área apilada
    st.area_chart(datos_area, color=["#1f77b4", "#aec7e8"])
    st.info("💡 **Observa:** La zona clara (Intereses) empieza pequeña, pero con el tiempo se vuelve más grande que la zona oscura (Tu Aporte).")

# TAB 3: Nominal vs Real
with tab3:
    st.subheader(f"La ilusión del dinero: Nominal vs Real ({target_escenario})")
    st.caption(aviso_escenario)
    
    res_target = resultados_completos[target_escenario]
    
    datos_realidad = pd.DataFrame({
        "Saldo Nominal (Billetes)": [res_target["serie_nominal"][i*12] for i in range(plazo_anos + 1)],
        "Valor Real (Poder de Compra)": [res_target["serie_real"][i*12] for i in range(plazo_anos + 1)]
    })
    
    st.line_chart(datos_realidad, color=["#1f77b4", "#2ca02c"])
    st.warning(f"⚠️ **Atención:** La brecha entre la línea azul y la verde es el efecto de la inflación ({inflacion}% anual).")

# TAB 4: Tabla
with tab4:
    st.dataframe(datos_grafico.style.format("₡ {:,.0f}"))
