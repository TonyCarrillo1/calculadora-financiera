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
    
    # NUEVO: Fecha de inicio para calcular cuándo caen los abonos
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
    
    # NUEVA SECCIÓN: Abonos Extraordinarios
    with st.expander("4. Abonos Extraordinarios (Opcional)", expanded=False):
        st.caption("Añade fechas específicas para inyectar capital extra (ej. Aguinaldos).")
        
        # Creamos una estructura base
        df_base = pd.DataFrame(columns=["Fecha", "Monto"])
        
        # Editor interactivo (Tabla donde puedes escribir)
        abonos_df = st.data_editor(
            df_base,
            num_rows="dynamic", # Permite al usuario agregar filas
            column_config={
                "Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY", required=True),
                "Monto": st.column_config.NumberColumn("Monto (₡)", format="%d", min_value=0, required=True)
            },
            key="abonos_editor"
        )

# --- LÓGICA DE CÁLCULO ---

def calcular_escenario_completo(tasa_bruta_pct, anos, aporte, inicial, comision_pct, inflacion_pct, abonos_extra_df, start_date):
    meses = int(anos * 12)
    
    # --- Procesamiento de Abonos Extraordinarios ---
    # Convertimos la tabla de fechas a un diccionario: { numero_de_mes: monto_extra }
    abonos_map = {}
    
    if not abonos_extra_df.empty:
        for index, row in abonos_extra_df.iterrows():
            # Validamos que los datos existan
            if pd.notnull(row["Fecha"]) and pd.notnull(row["Monto"]):
                fecha_abono = row["Fecha"]
                monto_abono = row["Monto"]
                
                # Calculamos cuántos meses hay desde el inicio hasta esa fecha
                # Fórmula: (Diferencia Años * 12) + Diferencia Meses
                diff_meses = (fecha_abono.year - start_date.year) * 12 + (fecha_abono.month - start_date.month)
                
                # Si el abono cae dentro del plazo del proyecto (y no es pasado), lo sumamos
                if 0 <= diff_meses < meses:
                    if diff_meses in abonos_map:
                        abonos_map[diff_meses] += monto_abono
                    else:
                        abonos_map[diff_meses] = monto_abono

    # --- Tasas ---
    tasa_neta_nominal_anual = (tasa_bruta_pct / 100) * (1 - (comision_pct / 100))
    tasa_real_neta_anual = ((1 + tasa_neta_nominal_anual) / (1 + (inflacion_pct / 100))) - 1
    tasa_mensual_efectiva = (1 + tasa_neta_nominal_anual)**(1/12) - 1
    
    # --- Proyección Mes a Mes ---
    valores_nominales = [inicial]
    total_depositado = inicial
    
    for i in range(meses):
        # 1. Calculamos interés sobre el saldo del mes anterior
        interes = valores_nominales[-1] * tasa_mensual_efectiva
        
        # 2. Verificamos si hay abono extra en ESTE mes específico 'i'
        extra_este_mes = abonos_map.get(i, 0)
        
        # 3. Sumamos todo: Saldo anterior + Interés + Aporte Mensual + Extra
        nuevo_saldo = valores_nominales[-1] + interes + aporte + extra_este_mes
        
        valores_nominales.append(nuevo_saldo)
        total_depositado += (aporte + extra_este_mes)
        
    saldo_final_nominal = valores_nominales[-1]
    
    # Valor Real
    factor_descuento = (1 + (inflacion_pct / 100)) ** anos
    saldo_final_real = saldo_final_nominal / factor_descuento
    
    return {
        "serie_nominal": valores_nominales,
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

# Iteramos sobre los 3 escenarios
for (nombre, tasa_input), col in zip(escenarios_data.items(), cols):
    res = calcular_escenario_completo(
        tasa_input, plazo_anos, aporte_mensual, saldo_inicial, comision, inflacion, abonos_df, fecha_inicio
    )
    
    # Datos para el gráfico
    puntos = [res["serie_nominal"][i*12] for i in range(plazo_anos + 1)]
    datos_grafico[nombre] = puntos
    
    with col:
        st.subheader(f"{nombre} ({tasa_input}%)")
        st.metric(label="Saldo Nominal Futuro", value=f"₡ {res['saldo_nominal']:,.0f}")
        
        st.markdown(f"""
        <div style="margin-top: -10px;">
            <span style="font-size: 0.9em; color: gray;">Valor Real (Poder de compra hoy)</span><br>
            <span style="font-size: 1.3em; font-weight: bold; color: #2ca02c;">₡ {res['saldo_real']:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        ganancia_pura = res['saldo_nominal'] - res['total_depositado']
        st.info(f"""
        **Inversión Total:** ₡ {res['total_depositado']:,.0f}
        <br>**Ganancia Intereses:** ₡ {ganancia_pura:,.0f}
        """, icon="💰")

st.markdown("---")

tab1, tab2 = st.tabs(["📈 Gráfico de Crecimiento", "📋 Tabla Detallada"])

with tab1:
    st.subheader(f"Evolución del Saldo Nominal a {plazo_anos} años")
    st.line_chart(datos_grafico, use_container_width=True)
    st.caption(f"Nota: Los valores muestran el saldo nominal proyectado incluyendo aportes extraordinarios.")

with tab2:
    st.dataframe(datos_grafico.style.format("₡ {:,.0f}"))
