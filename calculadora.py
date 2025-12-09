import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import textwrap # Para limpiar indentación HTML

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Calculadora Financiera Pro",
    page_icon="📈",
    layout="wide"
)

# --- ESTILOS CSS PROFESIONALES (THEME PREMIUM) ---
st.markdown("""
<style>
    /* FONDO PREMIUM CON GRADIENTE PROFUNDO */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        background-attachment: fixed;
    }
    
    /* ESTILOS GLOBALES DE TEXTO */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-weight: 700;
        letter-spacing: -0.03em;
    }
    
    h1 {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    p, label, .stMarkdown, .caption {
        color: #cbd5e1 !important;
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    /* SIDEBAR CON GLASSMORPHISM */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(251, 191, 36, 0.1);
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    /* INPUTS PREMIUM CON MEJOR CONTRASTE */
    .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #f8fafc !important; 
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 8px;
        font-weight: 500;
    }
    
    .stNumberInput input:focus, .stDateInput input:focus {
        border-color: #fbbf24 !important;
        box-shadow: 0 0 0 2px rgba(251, 191, 36, 0.2);
    }
    
    /* TABS PREMIUM */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: #cbd5e1;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #fbbf24, #f59e0b) !important;
        color: #0f172a !important;
        font-weight: 700;
        border: none;
    }
    
    /* DATAFRAME FIX - Forzar fondo transparente en contenedor */
    .stDataFrame {
        background: transparent !important;
    }
    
    /* SCROLLBAR */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 5px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #fbbf24;
    }
</style>
""", unsafe_allow_html=True)

# --- TÍTULOS ---
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem; line-height: 1.2;">
        Simulador de Inversión Avanzado
    </h1>
    <p style="font-size: 1.1rem; color: #94a3b8; margin: 0;">
        Proyecta el crecimiento de tu patrimonio con 
        <span style="color: #fbbf24; font-weight: 600;">aportes mensuales</span> y 
        <span style="color: #10b981; font-weight: 600;">extraordinarios</span>
    </p>
</div>
""", unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("1. Tu Inversión")
    fecha_inicio = st.date_input("Fecha de Inicio", value=date.today())
    saldo_inicial = st.number_input("Saldo Inicial (₡)", value=0, min_value=0, step=100000, format="%d")
    aporte_mensual = st.number_input("Aporte Mensual (₡)", value=20000, min_value=0, step=5000, format="%d")
    plazo_anos = st.number_input("Plazo (Años)", value=30, min_value=1, max_value=50, step=1)
    
    if saldo_inicial == 0 and aporte_mensual == 0:
        st.error("⛔ Ingresa un Saldo Inicial o Aporte Mensual")
        st.stop()
    
    st.markdown("---")
    st.header("2. Variables")
    inflacion = st.number_input("Inflación Anual (%)", value=3.0, min_value=0.0, step=0.1, format="%.1f")
    comision = st.number_input("Comisión Rendimientos (%)", value=10.0, min_value=0.0, step=0.5, format="%.1f")

    st.markdown("---")
    st.header("3. Escenarios (Tasas Brutas)")
    tasa_conservador = st.number_input("🛡️ Conservador (%)", value=9.0, min_value=0.0, step=0.25, format="%.2f")
    tasa_moderado = st.number_input("⚖️ Moderado (%)", value=10.0, min_value=0.0, step=0.25, format="%.2f")
    tasa_optimista = st.number_input("🚀 Optimista (%)", value=17.0, min_value=0.0, step=0.25, format="%.2f")

    st.markdown("---")
    st.header("4. Abonos Extraordinarios")
    with st.expander("Gestionar Abonos", expanded=False):
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
        if not abonos_df.empty:
            df_valido = abonos_df.dropna(subset=["Fecha", "Monto"])
            if not df_valido.empty:
                st.success(f"✅ {len(df_valido)} abonos registrados")
    
    st.markdown("---")
    st.header("5. Visualización")
    escenario_view = st.selectbox("Seleccionar Escenario", ["Todos", "Conservador", "Moderado", "Optimista"])

# --- CÁLCULO ---
def calcular_escenario_completo(tasa_bruta_pct, anos, aporte, inicial, comision_pct, inflacion_pct, abonos_extra_df, start_date):
    meses = int(anos * 12)
    abonos_map = {}
    abonos_ignorados = []
    
    if start_date is None: start_date = date.today()
    
    if not abonos_extra_df.empty:
        df_limpio = abonos_extra_df.dropna(subset=["Fecha", "Monto"]).copy()
        for index, row in df_limpio.iterrows():
            try:
                fecha_abono = pd.to_datetime(row["Fecha"]).date()
                monto_abono = float(row["Monto"])
                if fecha_abono < start_date:
                    abonos_ignorados.append(f"Fila {index+1}: Fecha pasada")
                    continue
                diff_meses = (fecha_abono.year - start_date.year) * 12 + (fecha_abono.month - start_date.month)
                if 0 <= diff_meses < meses:
                    abonos_map[diff_meses] = abonos_map.get(diff_meses, 0) + monto_abono
                else:
                    abonos_ignorados.append(f"Fila {index+1}: Fecha fuera de plazo")
            except Exception:
                continue

    tasa_neta_nominal_anual = (tasa_bruta_pct / 100) * (1 - (comision_pct / 100))
    tasa_mensual_efectiva = (1 + tasa_neta_nominal_anual)**(1/12) - 1
    inflacion_mensual = (1 + inflacion_pct/100)**(1/12) - 1
    
    valores_nominales = [inicial]
    serie_aportes = [inicial] 
    serie_real = [inicial]    
    total_depositado = inicial
    
    for i in range(meses):
        interes = valores_nominales[-1] * tasa_mensual_efectiva
        extra_este_mes = abonos_map.get(i, 0)
        nuevo_saldo = valores_nominales[-1] + interes + aporte + extra_este_mes
        nuevo_aporte_acumulado = total_depositado + aporte + extra_este_mes
        factor_inflacion = (1 + inflacion_mensual)**(i+1)
        
        valores_nominales.append(nuevo_saldo)
        serie_aportes.append(nuevo_aporte_acumulado)
        serie_real.append(nuevo_saldo/factor_inflacion)
        total_depositado += (aporte + extra_este_mes)
        
    return {
        "serie_nominal": valores_nominales,
        "serie_aportes": serie_aportes,
        "serie_real": serie_real,
        "saldo_nominal": valores_nominales[-1],
        "saldo_real": serie_real[-1],
        "total_depositado": total_depositado,
        "abonos_ignorados": abonos_ignorados
    }

escenarios_data = {"Conservador": tasa_conservador, "Moderado": tasa_moderado, "Optimista": tasa_optimista}

# --- VISUALIZACIÓN DE RESULTADOS ---
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.05)); border-left: 4px solid #fbbf24; border-radius: 12px; padding: 16px 20px; margin: 2rem 0 1.5rem 0;">
    <h2 style="margin: 0; font-size: 1.8rem; color: #fbbf24; font-weight: 700;">💰 Resultados de tu Inversión</h2>
</div>
""", unsafe_allow_html=True)

cols = st.columns(3)
datos_grafico = pd.DataFrame()
resultados_completos = {}

for (nombre, tasa_input), col in zip(escenarios_data.items(), cols):
    res = calcular_escenario_completo(tasa_input, plazo_anos, aporte_mensual, saldo_inicial, comision, inflacion, abonos_df, fecha_inicio)
    resultados_completos[nombre] = res
    datos_grafico[nombre] = [res["serie_nominal"][i*12] for i in range(plazo_anos + 1)]
    
    with col:
        is_selected = (escenario_view == nombre)
        
        # LOGICA DE ESTILOS CORREGIDA
        if is_selected:
            # Seleccionado: Verde brillante, glow
            border = "2px solid #4ade80"
            bg = "rgba(74, 222, 128, 0.15)"
            shadow = "0 0 20px rgba(74, 222, 128, 0.2)"
            opacity = "1"
            icon = "🌟"
        else:
            # No Seleccionado: Gris azulado traslúcido
            border = "1px solid rgba(148, 163, 184, 0.2)"
            bg = "rgba(51, 65, 85, 0.7)" 
            shadow = "0 4px 6px rgba(0, 0, 0, 0.1)"
            opacity = "0.9"
            icon = "🔹"

        ganancia = res['saldo_nominal'] - res['total_depositado']
        roi = (ganancia / res['total_depositado']) * 100 if res['total_depositado'] > 0 else 0

        # FIX CRÍTICO: Usamos textwrap.dedent para evitar que Streamlit interprete el HTML como código
        card_html = textwrap.dedent(f"""
            <div style="background-color: {bg}; border: {border}; border-radius: 12px; padding: 20px; box-shadow: {shadow}; margin-bottom: 20px; opacity: {opacity}; backdrop-filter: blur(10px);">
                <h3 style="margin: 0 0 15px 0; font-size: 1.3rem; color: #fff; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
                    {icon} {nombre} <span style="font-size: 0.8rem; color: #cbd5e1; font-weight: normal;">({tasa_input}%)</span>
                </h3>
                <div style="margin-bottom: 15px;">
                    <div style="font-size: 0.85rem; color: #94a3b8; text-transform: uppercase;">Saldo Nominal Futuro</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #fff;">₡ {res['saldo_nominal']:,.0f}</div>
                </div>
                <div style="margin-bottom: 20px;">
                    <div style="font-size: 0.85rem; color: #94a3b8;">Valor Real (Poder de compra)</div>
                    <div style="font-size: 1.4rem; font-weight: 600; color: #4ade80;">₡ {res['saldo_real']:,.0f}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 12px; font-size: 0.9rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="color: #cbd5e1;">Inversión:</span>
                        <span style="color: #fff; font-weight: 500;">₡ {res['total_depositado']:,.0f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #cbd5e1;">Ganancia:</span>
                        <span style="color: #60a5fa; font-weight: 500;">₡ {ganancia:,.0f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <span style="color: #cbd5e1;">ROI:</span>
                        <span style="color: #facc15; font-weight: 700;">{roi:.1f}%</span>
                    </div>
                </div>
            </div>
        """)
        st.markdown(card_html, unsafe_allow_html=True)

st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs(["📈 Crecimiento", "🍰 Composición", "💸 Inflación", "📋 Tabla Detallada"])

with tab1:
    if escenario_view == "Todos":
        st.line_chart(datos_grafico, use_container_width=True, color=["#6366f1", "#fbbf24", "#10b981"])
    else:
        colors = {"Conservador": "#6366f1", "Moderado": "#fbbf24", "Optimista": "#10b981"}
        st.line_chart(datos_grafico[escenario_view], use_container_width=True, color=colors[escenario_view])

target_escenario = "Moderado" if escenario_view == "Todos" else escenario_view
res_target = resultados_completos[target_escenario]

with tab2:
    datos_area = pd.DataFrame({
        "Tu Capital": [res_target["serie_aportes"][i*12] for i in range(plazo_anos + 1)],
        "Intereses": [(res_target["serie_nominal"][i*12] - res_target["serie_aportes"][i*12]) for i in range(plazo_anos + 1)]
    })
    st.area_chart(datos_area, color=["#475569", "#fbbf24"], use_container_width=True)

with tab3:
    datos_realidad = pd.DataFrame({
        "Nominal": [res_target["serie_nominal"][i*12] for i in range(plazo_anos + 1)],
        "Real": [res_target["serie_real"][i*12] for i in range(plazo_anos + 1)]
    })
    st.line_chart(datos_realidad, color=["#60a5fa", "#10b981"], use_container_width=True)

with tab4:
    # Preparar tabla detallada
    tabla_completa = pd.DataFrame({"Año": range(plazo_anos + 1)})
    for nombre in escenarios_data.keys():
        r = resultados_completos[nombre]
        tabla_completa[f"{nombre} (Nominal)"] = [r["serie_nominal"][i*12] for i in range(plazo_anos + 1)]
        tabla_completa[f"{nombre} (Real)"] = [r["serie_real"][i*12] for i in range(plazo_anos + 1)]
    
    # FIX: Se eliminó .background_gradient() para evitar errores si falta matplotlib
    # Esto soluciona el error en la tabla y la hace más robusta
    st.dataframe(
        tabla_completa.style.format({col: "₡ {:,.0f}" for col in tabla_completa.columns if col != "Año"}),
        use_container_width=True,
        height=400
    )
    
    csv = tabla_completa.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar Excel (CSV)", data=csv, file_name="proyeccion.csv", mime="text/csv", use_container_width=True)
