import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Clientes", layout="wide")
st.title("📊 Reporte de Cliente")

# === URL de tu BD de clientes en formato CSV ===
BD_CLIENTS_URL = "https://docs.google.com/spreadsheets/d/1-m5M_SYYlD--xzRmPx6_7BnKmftPTbgzswKq1Tp1TH8/export?format=csv"

# === Función para cargar BD de clientes (con cache) ===
@st.cache_data(ttl=300)  # 5 minutos
def load_clients_db(url):
    df = pd.read_csv(url)
    # Limpiar espacios y asegurar strings
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].astype(str).str.strip()
    return df

# === Función para cargar datos del cliente (con cache) ===
@st.cache_data(ttl=60)  # 1 minuto
def load_client_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

# === Leer parámetro ?cliente= desde la URL ===
params = st.query_params

cliente_id = params.get("cliente")

if not cliente_id:
    st.error("❌ No se especificó el cliente en la URL. Usa: ?cliente=ID")
    st.stop()

cliente_id = str(cliente_id).strip()

# === Cargar BD de clientes ===
try:
    df_clients = load_clients_db(BD_CLIENTS_URL)
except Exception as e:
    st.error("❌ No se pudo cargar la BD de clientes")
    st.stop()

# === Debug opcional (si algo falla, descomenta estas líneas) ===
# st.write("IDs en BD:", df_clients["ID"].head(10))
# st.write("Buscando ID:", cliente_id)

# === Buscar cliente ===
row = df_clients[df_clients["ID"] == cliente_id]

if row.empty:
    st.error("❌ Cliente no encontrado en la BD de clientes")
    st.stop()

# === Obtener datos del cliente ===
cliente_nombre = row.iloc[0]["Client"]
estado = row.iloc[0]["Estado"]
pais = row.iloc[0]["Pais"]
sheet_url = row.iloc[0]["URL Sheets"]

st.success(f"👤 Cliente: {cliente_nombre} | 📌 Estado: {estado} | 🌍 País: {pais}")

# === Convertir URL de Google Sheets a CSV si es necesario ===
if "export?format=csv" not in sheet_url:
    if "/edit" in sheet_url:
        sheet_url = sheet_url.split("/edit")[0] + "/export?format=csv"

# === Cargar datos del cliente ===
try:
    df = load_client_data(sheet_url)
except Exception as e:
    st.error("❌ No se pudo cargar el Google Sheets del cliente")
    st.stop()

st.subheader("📄 Datos del cliente")
st.dataframe(df, use_container_width=True)

# === Ejemplo de métricas ===
if "Monto" in df.columns:
    total = df["Monto"].sum()
    st.metric("💰 Total", round(total, 2))

# Aquí luego puedes agregar:
# - Presupuesto del mes
# - Gastos del mes
# - % usado
# - Gráficos

