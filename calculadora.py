import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import textwrap

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
    
    /* DATAFRAME FIX */
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
    
    # VALIDACIÓN: Fecha no puede ser muy antigua
    if fecha_inicio < (date.today() - timedelta(days=365*5)):
        st.warning("⚠️ Fecha muy antigua. Se recomienda usar fechas recientes.")
    
    saldo_inicial = st.number_input("Saldo Inicial (₡)", value=0, min_value=0, step=100000, format="%d")
    aporte_mensual = st.number_input("Aporte Mensual (₡)", value=20000, min_value=0, step=5000, format="%d")
    plazo_anos = st.number_input("Plazo (Años)", value=30, min_value=1, max_value=50, step=1)
    
    # VALIDACIÓN: Al menos uno debe tener valor
    if saldo_inicial == 0 and aporte_mensual == 0:
        st.error("⛔ Ingresa un **Saldo Inicial** o **Aporte Mensual** (o ambos)")
        st.stop()
    
    st.markdown("---")
    st.header("2. Variables del Entorno")
    inflacion = st.number_input("Inflación Anual (%)", value=3.0, min_value=0.0, max_value=50.0, step=0.1, format="%.1f")
    comision = st.number_input("Comisión Rendimientos (%)", value=10.0, min_value=0.0, max_value=99.9, step=0.5, format="%.1f")
    
    # VALIDACIÓN: Comisión no puede ser 100% o más
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
                "Monto": st.column_config.NumberColumn("Monto (₡)", format="%d", min_value=0, required=True)
            },
            key="abonos_editor"
        )
        
        # Resumen de abonos válidos
        if not abonos_df.empty:
            df_valido = abonos_df.dropna(subset=["Fecha", "Monto"])
            
            if len(df_valido) > 0:
                try:
                    montos_numericos = pd.to_numeric(df_valido['Monto'], errors='coerce')
                    total_abonos = montos_numericos.sum()
                    
                    if total_abonos > 0:
                        num_abonos = len(df_valido)
                        st.success(f"✅ **{num_abonos} abono{'s' if num_abonos > 1 else ''}** por **₡{total_abonos:,.0f}**")
                except Exception:
                    pass 
    
    st.markdown("---")
    st.header("5. Visualización")
    escenario_view = st.selectbox("Seleccionar Escenario", ["Todos", "Conservador", "Moderado", "Optimista"])

# --- FUNCIÓN DE CÁLCULO (OPTIMIZADA CON CACHÉ) ---
@st.cache_data
def calcular_escenario_completo(tasa_bruta_pct, anos, aporte, inicial, comision_pct, inflacion_pct, abonos_extra_df, start_date):
    meses = int(anos * 12)
    abonos_map = {}
    abonos_ignorados = []
    
    if start_date is None: 
        start_date = date.today()
    
    # Procesar abonos extraordinarios (CORREGIDO PARA EVITAR ERRORES)
    if not abonos_extra_df.empty:
        # 1. Aseguramos copia para no afectar el original
        df_limpio = abonos_extra_df.copy()
        
        for index, row in df_limpio.iterrows():
            try:
                # 2. Validación estricta de Fecha
                raw_fecha = row["Fecha"]
                if pd.isna(raw_fecha) or str(raw_fecha).strip() == "":
                    continue # Ignorar filas vacías
                
                # Convertir a Timestamp de Pandas primero (más robusto)
                ts = pd.to_datetime(raw_fecha, errors='coerce')
                
                # Si falló la conversión (NaT), saltar
                if pd.isna(ts):
                    abonos_ignorados.append(f"Fila {index+1}: Fecha inválida")
                    continue
                    
                # Ahora es seguro convertir a .date()
                fecha_abono = ts.date()
                
                # 3. Validación estricta de Monto
                monto_raw = row["Monto"]
                if isinstance(monto_raw, str):
                    monto_raw = monto_raw.replace(",", "").replace("₡", "").strip()
                
                monto_abono = pd.to_numeric(monto_raw, errors='coerce')
                
                if pd.isna(monto_abono):
                    abonos_ignorados.append(f"Fila {index+1}: Monto inválido")
                    continue
                
                monto_abono = float(monto_abono)
                
                if monto_abono <= 0:
                    continue 
                
                # 4. Cálculo de tiempo (diff_meses)
                diff_meses = (fecha_abono.year - start_date.year) * 12 + (fecha_abono.month - start_date.month)
                
                if 0 <= diff_meses < meses:
                    abonos_map[diff_meses] = abonos_map.get(diff_meses, 0) + monto_abono
                elif diff_meses < 0:
                    abonos_ignorados.append(f"Fila {index+1}: Fecha anterior al inicio")
                else:
                    abonos_ignorados.append(f"Fila {index+1}: Fecha fuera del plazo de {anos} años")
                    
            except Exception as e:
                # Captura genérica para evitar pantalla roja
                abonos_ignorados.append(f"Fila {index+1}: Error de procesamiento")
                continue

    # Cálculos de tasas (Comisión sobre Rendimiento)
    # Tasa Neta = Tasa Bruta * (1 - %Comisión)
    tasa_neta_nominal_anual = (tasa_bruta_pct / 100) * (1 - (comision_pct / 100))
    tasa_mensual_efectiva = (1 + tasa_neta_nominal_anual)**(1/12) - 1
    inflacion_mensual = (1 + inflacion_pct/100)**(1/12) - 1
    
    # Proyección
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
        serie_real.append(nuevo_saldo / factor_inflacion)
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
    
    # Mostrar advertencias solo una vez
    if not advertencias_mostradas and res["abonos_ignorados"]:
        with st.container():
            st.warning(f"⚠️ **{len(res['abonos_ignorados'])} abonos ignorados:**")
            for adv in res["abonos_ignorados"][:3]:
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

        # Tarjetas HTML
        card_html = textwrap.dedent(f"""
            <div style="background: {bg}; border: {border}; border-radius: 12px; padding: 20px; box-shadow: {shadow}; margin-bottom: 20px; opacity: {opacity}; backdrop-filter: blur(10px); transition: all 0.3s ease;">
                <h3 style="margin: 0 0 15px 0; font-size: 1.3rem; color: #fff; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
                    {icon} {nombre} <span style="font-size: 0.8rem; color: #cbd5e1; font-weight: normal;">({tasa_input}%)</span>
                </h3>
                <div style="margin-bottom: 15px;">
                    <div style="font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">💰 Saldo Futuro</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #fff;">₡{res['saldo_nominal']:,.0f}</div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
                    <div style="font-size: 0.8rem; color: #86efac; text-transform: uppercase; letter-spacing: 1px;">🎯 Poder de Compra Hoy</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #10b981;">₡{res['saldo_real']:,.0f}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 12px; font-size: 0.9rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="color: #cbd5e1;">💵 Inversión:</span>
                        <span style="color: #fff; font-weight: 600;">₡{res['total_depositado']:,.0f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: #cbd5e1;">📈 Ganancia:</span>
                        <span style="color: #60a5fa; font-weight: 600;">₡{ganancia:,.0f}</span>
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

# --- TABS CON MEJORAS ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Crecimiento", "🍰 Composición", "💸 Inflación", "📋 Tabla Detallada"])

# Determinar escenario objetivo
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

# TAB 2: Composición
with tab2:
    st.subheader(f"💎 Composición de Tu Patrimonio")
    
    datos_area = pd.DataFrame({
        "💵 Tu Capital": [res_target["serie_aportes"][i*12] for i in range(plazo_anos + 1)],
        "✨ Intereses": [(res_target["serie_nominal"][i*12] - res_target["serie_aportes"][i*12]) for i in range(plazo_anos + 1)]
    })
    st.area_chart(datos_area, color=["#475569", "#fbbf24"], use_container_width=True)

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
            Pérdida de poder adquisitivo: <strong style="color: #f87171;">₡{perdida_inflacion:,.0f}</strong> ({porcentaje_perdida:.1f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)

# TAB 4: Tabla
with tab4:
    st.subheader("📊 Tabla de Datos")
    
    tabla_completa = pd.DataFrame({"Año": range(plazo_anos + 1)})
    for nombre in escenarios_data.keys():
        r = resultados_completos[nombre]
        tabla_completa[f"{nombre} (Nominal)"] = [r["serie_nominal"][i*12] for i in range(plazo_anos + 1)]
        tabla_completa[f"{nombre} (Real)"] = [r["serie_real"][i*12] for i in range(plazo_anos + 1)]
    
    st.dataframe(
        tabla_completa.style.format({col: "₡ {:,.0f}" for col in tabla_completa.columns if col != "Año"}),
        use_container_width=True,
        height=400
    )
    
    csv = tabla_completa.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar Excel (CSV)", data=csv, file_name=f"proyeccion_{date.today()}.csv", mime="text/csv")
