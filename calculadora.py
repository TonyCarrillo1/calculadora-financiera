import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Calculadora Financiera Pro",
    page_icon="📈",
    layout="wide"
)

# Estilos CSS ligeros (Solo para ajustar márgenes)
st.markdown("""
<style>
    /* Ajuste sutil para separar las métricas */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Simulador de Inversión Avanzado")
st.markdown("Proyecta el crecimiento de tu patrimonio ajustando tasas, inflación y comisiones.")

# --- BARRA LATERAL (CONTROLES) ---
with st.sidebar:
    st.header("1. Tu Inversión")
    saldo_inicial = st.number_input("Saldo Inicial (₡)", value=0, step=100000, format="%d")
    aporte_mensual = st.number_input("Aporte Mensual (₡)", value=20000, step=5000, format="%d")
    plazo_anos = st.number_input("Plazo (Años)", value=30, min_value=1, step=1)
    
    st.markdown("---")
    
    # CORRECCIÓN: Variables en cascada (una debajo de otra)
    st.header("2. Variables del Entorno")
    inflacion = st.number_input("Inflación Anual (%)", value=3.0, step=0.1, format="%.1f")
    # Espacio vacío para separar visualmente si se desea, o simplemente el siguiente input
    comision = st.number_input("Comisión Rendimientos (%)", value=10.0, step=0.5, format="%.1f", help="Se cobra sobre las ganancias")

    st.markdown("---")
    st.header("3. Tasas de Escenarios (Brutas)")
    st.caption("Rendimiento anual esperado antes de comisiones.")
    
    tasa_conservador = st.number_input("🛡️ Conservador (%)", value=9.0, step=0.25, format="%.2f")
    tasa_moderado = st.number_input("⚖️ Moderado (%)", value=10.0, step=0.25, format="%.2f")
    tasa_optimista = st.number_input("🚀 Optimista (%)", value=17.0, step=0.25, format="%.2f")

# --- LÓGICA DE CÁLCULO ---

def calcular_escenario_completo(tasa_bruta_pct, anos, aporte, inicial, comision_pct, inflacion_pct):
    meses = int(anos * 12)
    
    # 1. Tasa Neta Nominal
    tasa_neta_nominal_anual = (tasa_bruta_pct / 100) * (1 - (comision_pct / 100))
    
    # 2. Tasa Real Neta (Ecuación de Fisher)
    tasa_real_neta_anual = ((1 + tasa_neta_nominal_anual) / (1 + (inflacion_pct / 100))) - 1
    
    # 3. Proyección
    tasa_mensual_efectiva = (1 + tasa_neta_nominal_anual)**(1/12) - 1
    
    valores_nominales = [inicial]
    
    for _ in range(meses):
        interes = valores_nominales[-1] * tasa_mensual_efectiva
        nuevo_saldo = valores_nominales[-1] + interes + aporte
        valores_nominales.append(nuevo_saldo)
        
    saldo_final_nominal = valores_nominales[-1]
    
    # 4. Valor Real
    factor_descuento = (1 + (inflacion_pct / 100)) ** anos
    saldo_final_real = saldo_final_nominal / factor_descuento
    
    return {
        "serie_nominal": valores_nominales,
        "saldo_nominal": saldo_final_nominal,
        "saldo_real": saldo_final_real,
        "tasa_real_neta": tasa_real_neta_anual
    }

# Diccionario de inputs
escenarios_data = {
    "Conservador": tasa_conservador,
    "Moderado": tasa_moderado,
    "Optimista": tasa_optimista
}

# --- VISUALIZACIÓN DE RESULTADOS ---

st.markdown("### 🏁 Resultados Comparativos")

cols = st.columns(3)
datos_grafico = pd.DataFrame()

for (nombre, tasa_input), col in zip(escenarios_data.items(), cols):
    res = calcular_escenario_completo(
        tasa_input, plazo_anos, aporte_mensual, saldo_inicial, comision, inflacion
    )
    
    # Guardar datos para gráfico
    puntos = [res["serie_nominal"][i*12] for i in range(plazo_anos + 1)]
    datos_grafico[nombre] = puntos
    
    # CORRECCIÓN: Uso de componentes nativos (st.metric) para evitar errores HTML
    with col:
        st.subheader(f"{nombre} ({tasa_input}%)")
        
        # Saldo Nominal
        st.metric(
            label="Saldo Nominal Futuro",
            value=f"₡ {res['saldo_nominal']:,.0f}"
        )
        
        # Valor Real (Destacado)
        st.markdown(f"""
        <div style="margin-top: -10px;">
            <span style="font-size: 0.9em; color: gray;">Valor Real (Poder de compra hoy)</span><br>
            <span style="font-size: 1.3em; font-weight: bold; color: #2ca02c;">₡ {res['saldo_real']:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Rentabilidad Real
        st.info(f"**Rentabilidad Real Neta:** {res['tasa_real_neta']*100:.2f}%")

st.markdown("---")

# Gráfico y Tablas
tab1, tab2 = st.tabs(["📈 Gráfico de Crecimiento", "📋 Tabla Detallada"])

with tab1:
    st.subheader(f"Evolución del Saldo Nominal a {plazo_anos} años")
    st.line_chart(datos_grafico, use_container_width=True)
    st.caption(f"Nota: Los valores muestran el saldo nominal proyectado. La inflación utilizada es del {inflacion}%.")

with tab2:
    st.dataframe(datos_grafico.style.format("₡ {:,.0f}"))
EOF
