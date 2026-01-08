import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import textwrap
import io # Necesario para manejar el archivo Excel en memoria

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Calculadora Financiera Pro",
    page_icon="📈",
    layout="wide"
)

# --- DATOS DE NEGOCIO: MATRIZ DE BONIFICACIÓN BN VITAL ---
def obtener_tasa_bonificacion(meses_antiguedad, saldo_acumulado):
    # Definir índice de columna basado en Antigüedad (Meses)
    if meses_antiguedad < 24:
        col_idx = 0 # 1 a < 24 meses
    elif meses_antiguedad < 48:
        col_idx = 1 # 24 a < 48 meses
    elif meses_antiguedad < 72:
        col_idx = 2 # 48 a < 72 meses
    elif meses_antiguedad < 96:
        col_idx = 3 # 72 a < 96 meses
    else:
        col_idx = 4 # 96 meses o más

    # Definir fila y porcentaje basado en Saldo
    if saldo_acumulado < 1000000:
        porcentajes = [0.0, 1.00, 2.50, 4.50, 6.00]
    elif saldo_acumulado < 2000000:
        porcentajes = [1.00, 2.50, 4.00, 6.00, 8.00]
    elif saldo_acumulado < 5000000:
        porcentajes = [2.00, 4.50, 6.00, 8.00, 12.00]
    elif saldo_acumulado < 10000000:
        porcentajes = [3.00, 6.50, 9.00, 12.00, 15.00]
    elif saldo_acumulado < 50000000:
        porcentajes = [5.50, 8.50, 12.00, 15.00, 18.00]
    elif saldo_acumulado < 100000000:
        porcentajes = [7.50, 10.50, 15.00, 18.00, 21.00]
    else: # 100.000.000 en adelante
        porcentajes = [9.50, 12.50, 18.00, 21.00, 25.00]
    
    return porcentajes[col_idx]

# --- ESTILOS CSS PROFESIONALES (THEME PREMIUM) ---
st.markdown("""
<style>
    /* FONDO PREMIUM CON GRADIENTE PROFUNDO */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        background-attachment: fixed;
    }
    
    /* HEADER TRANSPARENTE */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    header[data-testid="stHeader"] .stActionIcon {
        color: #cbd5e1 !important;
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
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #fbbf24, #f59e0b) !important;
        border: none;
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.4);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] p {
        color: #0f172a !important; 
        font-weight: 800 !important;
    }
    
    /* TABLAS Y DATA EDITOR (SIN FONDO BLANCO) */
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        background-color: transparent !important;
        border: none !important;
    }
    
    [data-testid="stDataFrame"] th, [data-testid="stDataEditor"] th {
        background-color: #1e293b !important;
        color: #fbbf24 !important;
        border-bottom: 1px solid rgba(251, 191, 36, 0.2) !important;
    }
    
    [data-testid="stDataFrame"] td, [data-testid="stDataEditor"] td {
        background-color: #0f172a !important;
        color: #cbd5e1 !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1) !important;
    }
    
    /* EXPANDER */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.6) !important;
        color: #fbbf24 !important;
        border: 1px solid rgba(251, 191, 36, 0.1);
        border-radius: 8px;
    }
    
    .streamlit-expanderContent {
        background-color: transparent !important;
        border: none !important;
        padding-top: 10px !important;
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

    # --- SELECTOR DE MONEDA ---
    tipo_moneda = st.radio("Moneda", ["Colones (₡)", "Dólares ($)"], horizontal=True)
    simbolo = "₡" if "Colones" in tipo_moneda else "$"
    
    fecha_inicio = st.date_input("Fecha de Inicio", value=date.today())
    
    if fecha_inicio < (date.today() - timedelta(days=365*5)):
        st.warning("⚠️ Fecha muy antigua. Se recomienda usar fechas recientes.")
    
    # Etiquetas dinámicas con el símbolo seleccionado
    saldo_inicial = st.number_input(f"Saldo Inicial ({simbolo})", value=0, min_value=0, step=1000, format="%d")
    aporte_mensual = st.number_input(f"Aporte Mensual ({simbolo})", value=200, min_value=0, step=10, format="%d")
    plazo_anos = st.number_input("Plazo (Años)", value=30, min_value=1, max_value=50, step=1)
    
    if saldo_inicial == 0 and aporte_mensual == 0:
        st.error(f"⛔ Ingresa un **Saldo Inicial** o **Aporte Mensual**")
        st.stop()
    
    st.markdown("---")
    st.header("2. Variables del Entorno")
    inflacion = st.number_input("Inflación Anual (%)", value=3.0, min_value=0.0, max_value=50.0, step=0.1, format="%.1f")
    comision = st.number_input("Comisión Rendimientos (%)", value=10.0, min_value=0.0, max_value=99.9, step=0.5, format="%.1f")
    
    if comision >= 100:
        st.error("⛔ La comisión no puede ser 100% o mayor")
        st.stop()

    st.markdown("---")
    st.header("3. Escenarios (Tasas Brutas)")
    st.caption("Rendimiento anual antes de comisiones")
    tasa_conservador = st.number_input("🛡️ Conservador (%)", value=9.0, min_value=0.0, step=0.25, format="%.2f")
    tasa_moderado = st.number_input("⚖️ Moderado (%)", value=10.0, min_value=0.0, step=0.25, format="%.2f")
    tasa_optimista = st.number_input("🚀 Optimista (%)", value=17.0, min_value=0.0, step=0.25, format="%.2f")

    st.markdown("---")
    st.header("4. Abonos Extraordinarios")
    
    with st.expander("Gestionar Abonos", expanded=True):
        df_base = pd.DataFrame(columns=["Fecha", "Monto"])
        abonos_df = st.data_editor(
            df_base,
            num_rows="dynamic",
            column_config={
                "Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY", required=True),
                # Columna Monto dinámica con el símbolo
                "Monto": st.column_config.NumberColumn(f"Monto ({simbolo})", format=f"{simbolo}%d", min_value=0, required=True)
            },
            key="abonos_editor"
        )
        
        if not abonos_df.empty:
            df_valido = abonos_df.dropna(subset=["Fecha", "Monto"])
            if len(df_valido) > 0:
                try:
                    montos_numericos = pd.to_numeric(df_valido['Monto'], errors='coerce')
                    total_abonos = montos_numericos.sum()
                    if total_abonos > 0:
                        num_abonos = len(df_valido)
                        st.success(f"✅ **{num_abonos} abono{'s' if num_abonos > 1 else ''}** por **{simbolo}{total_abonos:,.0f}**")
                except Exception:
                    pass 
    
    st.markdown("---")
    st.header("5. Visualización")
    escenario_view = st.selectbox("Seleccionar Escenario", ["Todos", "Conservador", "Moderado", "Optimista"])

# --- FUNCIÓN DE CÁLCULO (CON MATRIZ DE BONIFICACIÓN) ---
@st.cache_data
def calcular_escenario_completo(tasa_bruta_pct, anos, aporte, inicial, comision_pct, inflacion_pct, abonos_extra_df, start_date):
    meses = int(anos * 12)
    abonos_map = {}
    abonos_ignorados = []
    
    if start_date is None: 
        start_date = date.today()
    
    # --- Procesamiento de Abonos ---
    if not abonos_extra_df.empty:
        df_limpio = abonos_extra_df.copy()
        for index, row in df_limpio.iterrows():
            try:
                raw_fecha = row.get("Fecha")
                fecha_abono = None
                
                if isinstance(raw_fecha, (date, datetime)):
                    fecha_abono = raw_fecha if isinstance(raw_fecha, date) else raw_fecha.date()
                elif isinstance(raw_fecha, pd.Timestamp):
                    fecha_abono = raw_fecha.date()
                elif isinstance(raw_fecha, str) and raw_fecha.strip():
                    try:
                        ts = pd.to_datetime(raw_fecha, dayfirst=True)
                        fecha_abono = ts.date()
                    except:
                         pass
                
                if not fecha_abono: continue
                
                monto_raw = row.get("Monto")
                if isinstance(monto_raw, str):
                    # Limpiamos ambos símbolos para evitar errores si el usuario cambia de moneda con datos cargados
                    monto_raw = monto_raw.replace(",", "").replace("₡", "").replace("$", "").strip()
                
                monto_abono = pd.to_numeric(monto_raw, errors='coerce')
                
                if pd.isna(monto_abono) or monto_abono <= 0: continue
                
                monto_abono = float(monto_abono)
                
                diff_meses = (fecha_abono.year - start_date.year) * 12 + (fecha_abono.month - start_date.month)
                
                if 0 <= diff_meses < meses:
                    abonos_map[diff_meses] = abonos_map.get(diff_meses, 0) + monto_abono
                elif diff_meses < 0:
                    abonos_ignorados.append(f"Fila {index+1}: Fecha {fecha_abono.strftime('%d/%m/%Y')} es anterior al inicio")
                else:
                    abonos_ignorados.append(f"Fila {index+1}: Fecha fuera del plazo ({anos} años)")
                    
            except Exception:
                continue

    # --- Tasas Mensuales ---
    tasa_anual_bruta = tasa_bruta_pct / 100
    tasa_mensual_bruta = (1 + tasa_anual_bruta)**(1/12) - 1
    inflacion_mensual = (1 + inflacion_pct/100)**(1/12) - 1
    
    # Listas
    valores_nominales = [inicial]
    serie_aportes = [inicial] 
    serie_real = [inicial]
    filas_detalle = []
    
    saldo_actual = inicial
    total_depositado = inicial
    
    # Fila Inicial
    filas_detalle.append({
        "Mes": 0,
        "Fecha": start_date,
        "Antigüedad (Meses)": 0,
        "Saldo Inicial": 0,
        "Aporte Total": inicial,
        "Rendimiento Bruto": 0,
        "Comisión Bruta": 0,
        "% Bonificación": 0,
        "Monto Bonificación": 0,
        "Comisión Real": 0,
        "Rendimiento Neto": 0,
        "Saldo Final": inicial
    })
    
    for i in range(1, meses + 1):
        # Fecha
        fecha_mes = pd.Timestamp(start_date) + pd.DateOffset(months=i)
        
        # Abonos
        extra_este_mes = abonos_map.get(i, 0)
        
        # 1. Saldo Base
        saldo_inicial_mes = saldo_actual
        
        # 2. Rendimiento Bruto (sobre saldo inicial)
        rendimiento_bruto = saldo_inicial_mes * tasa_mensual_bruta
        
        # 3. Comisión Bruta (Standard)
        comision_bruta = rendimiento_bruto * (comision_pct / 100)
        
        # 4. Lógica de Bonificación BN Vital (Matriz Bidimensional)
        pct_bonificacion = obtener_tasa_bonificacion(i, saldo_inicial_mes)
        monto_bonificacion = comision_bruta * (pct_bonificacion / 100)
        
        # 5. Comisión Real a Descontar
        comision_real = comision_bruta - monto_bonificacion
        
        # 6. Rendimiento Neto
        rendimiento_neto = rendimiento_bruto - comision_real
        
        # 7. Aporte Total
        aporte_total_mes = aporte + extra_este_mes
        
        # 8. Saldo Final
        nuevo_saldo = saldo_inicial_mes + rendimiento_neto + aporte_total_mes
        
        # Acumulados
        nuevo_aporte_acumulado = total_depositado + aporte_total_mes
        factor_inflacion = (1 + inflacion_mensual)**i
        saldo_real = nuevo_saldo / factor_inflacion
        
        # Guardar
        valores_nominales.append(nuevo_saldo)
        serie_aportes.append(nuevo_aporte_acumulado)
        serie_real.append(saldo_real)
        
        filas_detalle.append({
            "Mes": i,
            "Fecha": fecha_mes.date(),
            "Antigüedad (Meses)": i,
            "Saldo Inicial": saldo_inicial_mes,
            "Aporte Total": aporte_total_mes,
            "Rendimiento Bruto": rendimiento_bruto,
            "Comisión Bruta": comision_bruta,
            "% Bonificación": pct_bonificacion,
            "Monto Bonificación": monto_bonificacion,
            "Comisión Real": comision_real,
            "Rendimiento Neto": rendimiento_neto,
            "Saldo Final": nuevo_saldo
        })
        
        saldo_actual = nuevo_saldo
        total_depositado = nuevo_aporte_acumulado
        
    df_detalle = pd.DataFrame(filas_detalle)
    
    return {
        "serie_nominal": valores_nominales,
        "serie_aportes": serie_aportes,
        "serie_real": serie_real,
        "saldo_nominal": valores_nominales[-1],
        "saldo_real": serie_real[-1],
        "total_depositado": total_depositado,
        "abonos_ignorados": abonos_ignorados,
        "df_detalle": df_detalle
    }

escenarios_data = {
    "Conservador": tasa_conservador, 
    "Moderado": tasa_moderado, 
    "Optimista": tasa_optimista
}

# --- VISUALIZACIÓN DE RESULTADOS ---
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.05)); border-left: 4px solid #fbbf24; border-radius: 12px; padding: 16px 20px; margin: 2rem 0 1.5rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
    <h2 style="margin: 0; font-size: 1.8rem; color: #fbbf24; font-weight: 700;">💰 Resultados de tu Inversión</h2>
    <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 0.9rem;">Compara tres escenarios y visualiza el crecimiento de tu patrimonio</p>
</div>
""", unsafe_allow_html=True)

# Control de advertencias
advertencias_mostradas = False

cols = st.columns(3)
datos_grafico = pd.DataFrame()
resultados_completos = {}

for (nombre, tasa_input), col in zip(escenarios_data.items(), cols):
    res = calcular_escenario_completo(
        tasa_input, plazo_anos, aporte_mensual, saldo_inicial, 
        comision, inflacion, abonos_df, fecha_inicio
    )
    resultados_completos[nombre] = res
    datos_grafico[nombre] = [res["serie_nominal"][i*12] for i in range(plazo_anos + 1)]
    
    if not advertencias_mostradas and res["abonos_ignorados"]:
        with st.container():
            st.warning(f"⚠️ **{len(res['abonos_ignorados'])} abonos no procesados (revisar fechas):**")
            for adv in res["abonos_ignorados"][:5]:
                st.caption(f"  • {adv}")
        advertencias_mostradas = True
    
    with col:
        is_selected = (escenario_view == nombre)
        
        if is_selected:
            border = "2px solid #fbbf24"
            bg = "rgba(251, 191, 36, 0.12)"
            shadow = "0 8px 24px rgba(251, 191, 36, 0.3)"
            opacity = "1"
            icon = "⭐"
        else:
            border = "1px solid rgba(148, 163, 184, 0.15)"
            bg = "rgba(51, 65, 85, 0.5)"
            shadow = "0 4px 12px rgba(0, 0, 0, 0.2)"
            opacity = "0.88"
            icon = "📊"

        ganancia = res['saldo_nominal'] - res['total_depositado']
        roi = (ganancia / res['total_depositado']) * 100 if res['total_depositado'] > 0 else 0

        # Tarjetas HTML con Símbolo Dinámico
        card_html = textwrap.dedent(f"""
            <div style="background: {bg}; border: {border}; border-radius: 12px; padding: 20px; box-shadow: {shadow}; margin-bottom: 20px; opacity: {opacity}; backdrop-filter: blur(10px); transition: all 0.3s ease;">
                <h3 style="margin: 0 0 15px 0; font-size: 1.3rem; color: #fff; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
                    {icon} {nombre} <span style="font-size: 0.8rem; color: #cbd5e1; font-weight: normal;">({tasa_input}%)</span>
                </h3>
                <div style="margin-bottom: 15px;">
                    <div style="font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">💰 Saldo Futuro</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #fff;">{simbolo}{res['saldo_nominal']:,.0f}</div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
                    <div style="font-size: 0.8rem; color: #86efac; text-transform: uppercase; letter-spacing: 1px;">🎯 Poder de Compra Hoy</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #10b981;">{simbolo}{res['saldo_real']:,.0f}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 12px; font-size: 0.9rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="color: #cbd5e1;">💵 Inversión:</span>
                        <span style="color: #fff; font-weight: 600;">{simbolo}{res['total_depositado']:,.0f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: #cbd5e1;">📈 Ganancia:</span>
                        <span style="color: #60a5fa; font-weight: 600;">{simbolo}{ganancia:,.0f}</span>
                    </div>
                    <div style="height: 1px; background: rgba(255,255,255,0.1); margin: 10px 0;"></div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #fbbf24; font-weight: 600; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px;">⚡ ROI</span>
                        <span style="font-size: 1.3rem; font-weight: 800; color: #fbbf24;">{roi:.1f}%</span>
                    </div>
                </div>
            </div>
        """)
        st.markdown(card_html, unsafe_allow_html=True)

st.markdown("---")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Crecimiento", "🍰 Composición", "💸 Inflación", "📋 Tabla Detallada"])

target_escenario = "Moderado" if escenario_view == "Todos" else escenario_view
res_target = resultados_completos[target_escenario]

# TAB 1: Crecimiento
with tab1:
    if escenario_view == "Todos":
        st.subheader("📊 Evolución Comparativa")
        st.line_chart(datos_grafico, use_container_width=True, color=["#6366f1", "#fbbf24", "#10b981"])
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 12px; margin-top: 12px; text-align: center;">
            <span style="color: #6366f1; font-weight: 600;">━━</span> Conservador &nbsp;|&nbsp; 
            <span style="color: #fbbf24; font-weight: 600;">━━</span> Moderado &nbsp;|&nbsp; 
            <span style="color: #10b981; font-weight: 600;">━━</span> Optimista
        </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader(f"📈 Proyección - {escenario_view}")
        colors = {"Conservador": "#6366f1", "Moderado": "#fbbf24", "Optimista": "#10b981"}
        st.line_chart(datos_grafico[escenario_view], use_container_width=True, color=colors[escenario_view])
        st.caption(f"Visualizando proyección del escenario **{escenario_view}** a lo largo del tiempo.")

# TAB 2: Composición
with tab2:
    st.subheader(f"💎 Composición de Tu Patrimonio")
    
    datos_area = pd.DataFrame({
        "💵 Tu Capital": [res_target["serie_aportes"][i*12] for i in range(plazo_anos + 1)],
        "✨ Intereses": [(res_target["serie_nominal"][i*12] - res_target["serie_aportes"][i*12]) for i in range(plazo_anos + 1)]
    })
    st.area_chart(datos_area, color=["#475569", "#fbbf24"], use_container_width=True)
    st.info("💡 La zona **dorada** representa el dinero que trabaja para ti (Intereses).")

# TAB 3: Inflación
with tab3:
    st.subheader(f"⚖️ Impacto de la Inflación")
    
    datos_realidad = pd.DataFrame({
        "💵 Saldo Nominal": [res_target["serie_nominal"][i*12] for i in range(plazo_anos + 1)],
        "💎 Poder de Compra Real": [res_target["serie_real"][i*12] for i in range(plazo_anos + 1)]
    })
    st.line_chart(datos_realidad, color=["#60a5fa", "#10b981"], use_container_width=True)
    
    perdida_inflacion = res_target["saldo_nominal"] - res_target["saldo_real"]
    porcentaje_perdida = (perdida_inflacion / res_target["saldo_nominal"]) * 100 if res_target["saldo_nominal"] > 0 else 0
    
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05)); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 20px; margin-top: 16px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div style="font-size: 1.5rem;">⚠️</div>
            <div>
                <div style="color: #fbbf24; font-weight: 700;">Erosión por Inflación ({inflacion}%)</div>
            </div>
        </div>
        <div style="color: #cbd5e1; font-size: 0.95rem;">
            Pérdida estimada de poder adquisitivo: <strong style="color: #f87171;">{simbolo}{perdida_inflacion:,.0f}</strong> ({porcentaje_perdida:.1f}%)
            <br><em style="font-size: 0.85rem; opacity: 0.8;">La brecha entre ambas líneas es el "costo invisible" de la inflación.</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

# TAB 4: Tabla Detallada Mensual
with tab4:
    st.subheader(f"📊 Desglose Mensual Detallado - {target_escenario}")
    
    if escenario_view == "Todos":
        st.info(f"ℹ️ Mostrando detalles del escenario **{target_escenario}**. Selecciona un escenario específico arriba para ver sus detalles.")
    
    df_mostrar = res_target["df_detalle"].copy()
    
    # Configuración de columnas
    column_config = {
        "Mes": st.column_config.NumberColumn("Mes", format="%d"),
        "Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
        "Antigüedad (Meses)": st.column_config.NumberColumn("Antigüedad", format="%d m"),
        "Saldo Inicial": st.column_config.NumberColumn(f"Saldo Inicial ({simbolo})"),
        "Aporte Total": st.column_config.NumberColumn(f"Aporte Total ({simbolo})"),
        "Rendimiento Bruto": st.column_config.NumberColumn(f"Rend. Bruto ({simbolo})"),
        "Comisión Bruta": st.column_config.NumberColumn(f"Com. Bruta ({simbolo})"),
        "% Bonificación": st.column_config.NumberColumn("% Bonif.", format="%.2f%%"),
        "Monto Bonificación": st.column_config.NumberColumn(f"Bonificación (+) ({simbolo})"),
        "Comisión Real": st.column_config.NumberColumn(f"Com. Real (-) ({simbolo})"),
        "Rendimiento Neto": st.column_config.NumberColumn(f"Ganancia Neta ({simbolo})"),
        "Saldo Final": st.column_config.NumberColumn(f"Saldo Final ({simbolo})")
    }
    
    # Formateo con Styler
    format_str = f"{simbolo}{{:,.2f}}"
    format_dict = {
        "Saldo Inicial": format_str,
        "Aporte Total": format_str,
        "Rendimiento Bruto": format_str,
        "Comisión Bruta": format_str,
        "Monto Bonificación": format_str,
        "Comisión Real": format_str,
        "Rendimiento Neto": format_str,
        "Saldo Final": format_str
    }

    cols_to_show = [
        "Fecha", "Saldo Inicial", "Rendimiento Bruto", 
        "Comisión Bruta", "% Bonificación", "Monto Bonificación", 
        "Rendimiento Neto", "Saldo Final"
    ]
    
    st.dataframe(
        df_mostrar[cols_to_show].style.format(format_dict),
        column_config=column_config,
        use_container_width=True,
        height=500,
        hide_index=True
    )
    
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); border-radius: 8px; padding: 12px; margin-top: 10px; font-size: 0.9rem; color: #cbd5e1;">
        📥 <strong>Exportación:</strong> El archivo descargable incluye TODAS las columnas, incluyendo el desglose de la bonificación.
    </div>
    """, unsafe_allow_html=True)
    
    # --- BOTONES DE DESCARGA (CSV Y EXCEL) ---
    col_d1, col_d2 = st.columns([1, 1])
    
    # 1. CSV
    csv = df_mostrar.to_csv(index=False).encode('utf-8')
    with col_d1:
        st.download_button(
            label=f"📄 Descargar CSV", 
            data=csv, 
            file_name=f"detalle_{target_escenario}_{date.today()}.csv", 
            mime="text/csv"
        )
    
    # 2. EXCEL (XLSX) con Formato de Tabla
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_mostrar.to_excel(writer, sheet_name='Proyeccion', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Proyeccion']
        
        # Obtener dimensiones
        (max_row, max_col) = df_mostrar.shape
        
        # Crear tabla de Excel con estilo
        worksheet.add_table(0, 0, max_row, max_col - 1, {
            'columns': [{'header': col} for col in df_mostrar.columns],
            'style': 'TableStyleMedium9',
            'name': 'ProyeccionFinanciera'
        })
        
        # Formato de moneda para columnas numéricas
        currency_fmt = workbook.add_format({'num_format': f'{simbolo}#,##0.00'})
        pct_fmt = workbook.add_format({'num_format': '0.00%'})
        
        for i, col_name in enumerate(df_mostrar.columns):
            if col_name == "% Bonificación":
                worksheet.set_column(i, i, 12, pct_fmt)
            elif col_name in ["Saldo Inicial", "Aporte Total", "Rendimiento Bruto", "Comisión Bruta", 
                              "Monto Bonificación", "Comisión Real", "Rendimiento Neto", "Saldo Final"]:
                worksheet.set_column(i, i, 18, currency_fmt)
            elif col_name == "Fecha":
                worksheet.set_column(i, i, 12)
            else:
                worksheet.set_column(i, i, 10)
                
    buffer.seek(0)
    
    with col_d2:
        st.download_button(
            label=f"📊 Descargar Excel (.xlsx)", 
            data=buffer, 
            file_name=f"proyeccion_excel_{target_escenario}_{date.today()}.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
