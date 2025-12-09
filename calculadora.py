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

# --- ESTILOS CSS PROFESIONALES (THEME OVERRIDE) ---
st.markdown("""
<style>
    /* FONDO "MIDNIGHT DEEP" - Más oscuro y elegante */
    .stApp {
        background-color: #0e1117;
        background-image: radial-gradient(circle at 50% 0%, #1c2331 0%, #0e1117 70%);
        background-attachment: fixed;
    }
    
    /* ESTILOS GLOBALES DE TEXTO */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    p, label, .stMarkdown, .caption {
        color: #cfd8dc !important;
    }
    
    /* INPUTS & WIDGETS */
    .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1a1f29; 
        color: white; 
        border: 1px solid #2d3748;
    }
    
    /* EXPANDER ESTILIZADO */
    .streamlit-expanderHeader {
        background-color: #1a1f29 !important;
        border: 1px solid #2d3748;
        border-radius: 8px;
        color: white !important;
    }
    
    /* QUITANDO PADDING EXTRA SUPERIOR */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- TÍTULOS ---
st.title("Simulador de Inversión Avanzado")
st.markdown("Proyecta el crecimiento de tu patrimonio con aportes mensuales y **extraordinarios**.")

# --- BARRA LATERAL (CONTROLES) ---
with st.sidebar:
    st.header("1. Tu Inversión")
    
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
    
    # SECCIÓN: Abonos Extraordinarios
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
    
    # Control de Visualización
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
                # Conversión forzada de fecha
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
                continue

    # --- Tasas ---
    tasa_neta_nominal_anual = (tasa_bruta_pct / 100) * (1 - (comision_pct / 100))
    tasa_real_neta_anual = ((1 + tasa_neta_nominal_anual) / (1 + (inflacion_pct / 100))) - 1
    tasa_mensual_efectiva = (1 + tasa_neta_nominal_anual)**(1/12) - 1
    
    # --- Proyección Mes a Mes ---
    valores_nominales = [inicial]
    serie_aportes = [inicial] 
    serie_real = [inicial]   
    
    total_depositado = inicial
    
    for i in range(meses):
        interes = valores_nominales[-1] * tasa_mensual_efectiva
        
        # Verificar abono extra este mes
        extra_este_mes = abonos_map.get(i, 0)
        
        # Totales
        nuevo_saldo = valores_nominales[-1] + interes + aporte + extra_este_mes
        nuevo_aporte_acumulado = total_depositado + aporte + extra_este_mes
        
        # Calculo de Valor Real mes a mes
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
        "serie_aportes": serie_aportes,
        "serie_real": serie_real,
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
st.markdown("### Resultados Comparativos")

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
        # --- DISEÑO DE TARJETA UNIFICADO ---
        # Definimos estilos dinámicos según selección
        is_selected = (escenario_view == nombre)
        
        if is_selected:
            border_color = "#ffd700"  # Dorado
            bg_color = "rgba(255, 215, 0, 0.08)" # Fondo dorado muy sutil
            shadow = "0 0 20px rgba(255, 215, 0, 0.15)" # Resplandor
            icon_header = "🌟"
            opacity = "1"
        else:
            border_color = "rgba(255, 255, 255, 0.1)" # Borde sutil
            bg_color = "rgba(255, 255, 255, 0.03)" # Fondo casi transparente
            shadow = "none"
            icon_header = "🔹"
            opacity = "0.85" # Un poco más apagado para que no compita

        # Generamos la tarjeta COMPLETA en HTML
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 20px;
            box-shadow: {shadow};
            margin-bottom: 20px;
            transition: all 0.3s ease;
            opacity: {opacity};
        ">
            <!-- Encabezado -->
            <h3 style="margin-top: 0; font-size: 1.3rem; color: #fff; border-bottom: 1px solid {border_color}; padding-bottom: 10px; margin-bottom: 15px;">
                {icon_header} {nombre} <span style="font-size: 0.8rem; color: #aaa; font-weight: normal;">({tasa_input}%)</span>
            </h3>

            <!-- Dato Principal -->
            <div style="margin-bottom: 15px;">
                <div style="font-size: 0.85rem; color: #a0aec0; text-transform: uppercase; letter-spacing: 1px;">Saldo Nominal Futuro</div>
                <div style="font-size: 2rem; font-weight: 700; color: #fff;">₡ {res['saldo_nominal']:,.0f}</div>
            </div>

            <!-- Dato Secundario (Valor Real) -->
            <div style="margin-bottom: 20px;">
                <div style="font-size: 0.85rem; color: #a0aec0;">Valor Real (Poder de compra hoy)</div>
                <div style="font-size: 1.4rem; font-weight: 600; color: #48bb78;">₡ {res['saldo_real']:,.0f}</div>
            </div>

            <!-- Footer con Datos Extra -->
            <div style="background-color: rgba(0,0,0,0.2); border-radius: 8px; padding: 12px; font-size: 0.9rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="color: #cbd5e0;">Inversión:</span>
                    <span style="color: #fff; font-weight: 500;">₡ {res['total_depositado']:,.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #cbd5e0;">Ganancia:</span>
                    <span style="color: #63b3ed; font-weight: 500;">₡ {res['saldo_nominal'] - res['total_depositado']:,.0f}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
    st.area_chart(datos_area, color=["#3182ce", "#90cdf4"]) # Azules corporativos
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
    
    st.line_chart(datos_realidad, color=["#63b3ed", "#48bb78"]) # Azul claro y Verde éxito
    st.warning(f"⚠️ **Atención:** La brecha entre la línea azul y la verde es el efecto de la inflación ({inflacion}% anual).")

# TAB 4: Tabla
with tab4:
    st.dataframe(datos_grafico.style.format("₡ {:,.0f}"))
