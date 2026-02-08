import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Clientes", layout="wide")
st.title("📊 Reporte de Cliente")

# === URL de tu BD de clientes en formato CSV ===
BD_CLIENTS_URL = "https://docs.google.com/spreadsheets/d/1-m5M_SYYlD--xzRmPx6_7BnKmftPTbgzswKq1Tp1TH8/export?format=csv"

# === Función para cargar BD de clientes (con cache) ===
@st.cache_data(ttl=300)  # 5 minutos
def load_clients_db(url):
    return pd.read_csv(url)

# === Función para cargar datos del cliente (con cache) ===
@st.cache_data(ttl=60)  # 1 minuto
def load_client_data(url):
    return pd.read_csv(url)

# Leer parámetro ?cliente=
params = st.query_params
cliente_id = params.get("cliente", [""])[0]

if cliente_id == "":
    st.error("❌ No se especificó el cliente en la URL. Usa: ?cliente=ID")
    st.stop()

# Cargar BD de clientes
df_clients = load_clients_db(BD_CLIENTS_URL)

# Asegurar que la columna ID sea string para comparar bien
df_clients["ID"] = df_clients["ID"].astype(str)

# Buscar cliente
row = df_clients[df_clients["ID"] == str(cliente_id)]

if row.empty:
    st.error("❌ Cliente no encontrado en la BD de clientes")
    st.stop()

# Obtener datos del cliente
cliente_nombre = row.iloc[0]["Client"]
estado = row.iloc[0]["Estado"]
pais = row.iloc[0]["Pais"]
sheet_url = row.iloc[0]["URL Sheets"]

st.success(f"Cliente: {cliente_nombre} | Estado: {estado} | País: {pais}")

# Convertir URL normal de Google Sheets a CSV si es necesario
if "export?format=csv" not in sheet_url:
    if "/edit" in sheet_url:
        sheet_url = sheet_url.split("/edit")[0] + "/export?format=csv"

# Cargar datos del cliente
try:
    df = load_client_data(sheet_url)
except Exception as e:
    st.error("❌ No se pudo cargar el Google Sheets del cliente")
    st.stop()

st.subheader("📄 Datos del cliente")
st.dataframe(df, use_container_width=True)

# === Ejemplo de métricas (ajústalo a tus columnas reales) ===
if "Monto" in df.columns:
    total = df["Monto"].sum()
    st.metric("💰 Total", round(total, 2))

# Puedes agregar más KPIs aquí:
# - Gastos del mes
# - Presupuesto
# - Porcentaje usado
# - Gráficos, etc.
