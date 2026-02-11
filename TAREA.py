import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="Control de Finanzas",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# ESTILOS CSS PERSONALIZADOS
# ============================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@300;400;700&display=swap');
    
    * {
        font-family: 'Roboto Condensed', sans-serif !important;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Roboto Condensed', sans-serif !important;
        color: #0081FF;
    }
    
    .stMetric {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .stMetric label {
        font-family: 'Roboto Condensed', sans-serif !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        color: #0081FF !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-family: 'Roboto Condensed', sans-serif !important;
        font-size: 32px !important;
        font-weight: 400 !important;
        margin-top: 8px !important;
    }
    
    /* Métrica con color condicional */
    .metric-rojo [data-testid="stMetricValue"] {
        color: #FF4444 !important;
    }
    
    .metric-amarillo [data-testid="stMetricValue"] {
        color: #FFA333 !important;
    }
    
    .metric-verde [data-testid="stMetricValue"] {
        color: #00C851 !important;
    }
    
    div[data-testid="stDataFrameResizeHandle"] {
        display: none;
    }
    
    .dataframe {
        font-family: 'Roboto Condensed', sans-serif !important;
        font-size: 12px !important;
        background-color: #FFFFFF !important;
    }
    
    .dataframe tbody tr td {
        background-color: #FFFFFF !important;
        color: #333333 !important;
    }
    
    .stSelectbox label, .stMultiSelect label {
        display: none !important;
    }
    
    .stButton button {
        font-family: 'Roboto Condensed', sans-serif !important;
        background-color: #0081FF;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s;
        width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 14px !important;
        min-height: 38px;
        height: 38px;
        max-height: 38px;
    }
    
    .stButton button:hover {
        background-color: #FF2E95;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* ======================================
       HEADER WRAPPER - Fondo azul suave
    ====================================== */
    .header-wrapper {
        background-color: #F0F7FF;
        padding: 18px 25px 18px 25px;
        margin-bottom: 20px;
        margin-left: -4rem;
        margin-right: -4rem;
        margin-top: -1rem;
        box-shadow: 0 2px 8px rgba(0, 129, 255, 0.10);
        border-bottom: 1.5px solid #C8DFFE;
    }
    
    .titulo-principal {
        color: #0081FF !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
    }
    
    .nombre-usuario {
        color: #666 !important;
        font-size: 12px !important;
        font-weight: 400 !important;
        margin: -7px 0 0 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }
    
    /* Ajustes responsivos para móviles */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .header-wrapper {
            margin-left: -1rem;
            margin-right: -1rem;
            padding: 12px 15px;
        }
        
        .stMetric {
            height: auto;
            min-height: 100px;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            font-size: 24px !important;
        }
    }
    
    /* Ajustes para modo oscuro en móviles */
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
        }
        
        .stMetric label {
            color: #FFFFFF !important;
        }
        
        .stMetric {
            background-color: #2d3748 !important;
            border: 1px solid #4A5568;
            height: 120px;
        }
        
        .header-wrapper {
            background-color: #1a2a3a !important;
            border-bottom: 1.5px solid #2d4a6a;
        }
        
        .titulo-principal {
            color: #FFFFFF !important;
        }
        
        .nombre-usuario {
            color: #CBD5E0 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Evitar que las imágenes se recorten */
img {
    max-height: none !important;
    height: auto !important;
    object-fit: contain !important;
}

/* Asegurar que el contenedor no recorte */
div[data-testid="stImage"] {
    overflow: visible !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# COLORES DE LA MARCA
# ============================================
COLORS = {
    'azul': '#0081FF',
    'rosa': '#FF2E95',
    'naranja': '#FF9D00',
    'cian': '#00E5FF'
}

COLOR_PALETTE = [COLORS['azul'], COLORS['rosa'], COLORS['naranja'], COLORS['cian']]

# ============================================
# CATEGORÍAS DE GASTO
# ============================================
CATEGORIAS_GASTO = [
    "Transporte", "Alimentación", "Discoteca/Bar", "Restaurant",
    "Vestimenta", "Antojos", "Mascota", "Hogar", "Servicios",
    "Salud", "Educación", "Entretenimiento", "Otros"
]

# ============================================
# MESES EN ESPAÑOL
# ============================================
MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# ============================================
# FUNCIONES DE CARGA DE DATOS
# ============================================
@st.cache_data(ttl=300)
def load_clients_db(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].astype(str).str.strip()
    return df

@st.cache_data(ttl=60)
def load_client_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    if 'Monto' in df.columns:
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
    if 'Año' in df.columns:
        df['Año'] = pd.to_numeric(df['Año'], errors='coerce').fillna(datetime.now().year).astype(int)
    if 'Mes' in df.columns:
        df['Mes'] = pd.to_numeric(df['Mes'], errors='coerce').fillna(datetime.now().month).astype(int)
    if 'Dia' in df.columns:
        df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce').fillna(1).astype(int)
    
    return df

def load_logo(url):
    try:
        file_id = url.split('/d/')[1].split('/')[0]
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(download_url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

# ============================================
# FUNCIONES DE CÁLCULO
# ============================================
def calcular_presupuesto_disponible(df, año_filtro, mes_filtro):
    presupuestos_mes = df[
        (df['Tipo'] == 'Presupuesto') & 
        (df['Año'] == año_filtro) & 
        (df['Mes'] == mes_filtro)
    ].sort_values('Fecha', ascending=False)
    
    if len(presupuestos_mes) > 0:
        ultimo_presupuesto = presupuestos_mes.iloc[0]['Monto']
    else:
        ultimo_presupuesto = 0
    
    gastos_mes = df[
        (df['Tipo'] == 'Gasto') & 
        (df['Año'] == año_filtro) & 
        (df['Mes'] == mes_filtro)
    ]['Monto'].sum()
    
    presupuesto_disponible = ultimo_presupuesto - gastos_mes
    
    return presupuesto_disponible, ultimo_presupuesto, gastos_mes

def obtener_ultimo_presupuesto_mes(df, año, mes):
    presupuestos = df[
        (df['Tipo'] == 'Presupuesto') & 
        (df['Año'] == año) & 
        (df['Mes'] == mes)
    ].sort_values('Fecha', ascending=False)
    
    if len(presupuestos) > 0:
        return presupuestos.iloc[0]['Monto']
    return 0

# ============================================
# FUNCIONES DE GRÁFICOS
# ============================================
def crear_gauge_presupuesto(df_filtrado, presupuesto_mes):
    gasto_total = df_filtrado[df_filtrado['Tipo'] == 'Gasto']['Monto'].sum()
    
    if presupuesto_mes == 0:
        max_value = gasto_total if gasto_total > 0 else 100
    else:
        max_value = presupuesto_mes
    
    if presupuesto_mes > 0:
        porcentaje = (gasto_total / presupuesto_mes) * 100
    else:
        porcentaje = 0
    
    if porcentaje <= 50:
        color = COLORS['cian']
    elif porcentaje <= 75:
        color = COLORS['naranja']
    else:
        color = COLORS['rosa']
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = gasto_total,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {
                'range': [None, max_value],
                'tickwidth': 2,
                'tickcolor': COLORS['azul'],
                'tickfont': {'family': 'Roboto Condensed', 'size': 13}
            },
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': COLORS['azul'],
            'steps': [
                {'range': [0, max_value * 0.5], 'color': '#E5F5FF'},
                {'range': [max_value * 0.5, max_value * 0.75], 'color': '#FFF4E5'},
                {'range': [max_value * 0.75, max_value], 'color': '#FFE5F2'}
            ],
            'threshold': {
                'line': {'color': COLORS['azul'], 'width': 4},
                'thickness': 0.75,
                'value': presupuesto_mes
            }
        },
        number = {
            'font': {'family': 'Roboto Condensed', 'size': 36, 'color': COLORS['azul']},
            'prefix': "$",
            'suffix': f"<br><span style='font-size:16px; color:#666'>Objetivo: ${presupuesto_mes:,.0f}</span>"
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="white",
        font={'color': COLORS['azul'], 'family': 'Roboto Condensed'},
        height=380,
        margin=dict(l=20, r=20, t=80, b=20),
        dragmode=False,
        title={
            'text': "Cumplimiento del Presupuesto",
            'font': {'size': 20, 'family': 'Roboto Condensed', 'color': COLORS['azul']},
            'x': 0,
            'xanchor': 'left',
            'y': 0.98,
            'yanchor': 'top'
        },
        modebar={'remove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']},
        xaxis={'fixedrange': True},
        yaxis={'fixedrange': True}
    )
    
    return fig

def crear_barras_horizontales_categorias(df_filtrado):
    gastos = df_filtrado[df_filtrado['Tipo'] == 'Gasto'].copy()
    
    if len(gastos) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos de gastos para mostrar",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={'size': 16, 'family': 'Roboto Condensed', 'color': COLORS['azul']}
        )
    else:
        por_categoria = gastos.groupby('Categoría')['Monto'].sum().sort_values(ascending=True)
        colors_list = [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(len(por_categoria))]
        max_valor = por_categoria.max()
        text_positions = ['inside' if v > max_valor * 0.15 else 'outside' for v in por_categoria.values]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=por_categoria.index,
            x=por_categoria.values,
            orientation='h',
            text=[f'${v:,.0f}' for v in por_categoria.values],
            textposition=text_positions,
            textfont={'family': 'Roboto Condensed', 'size': 13, 'color': 'white'},
            insidetextanchor='middle',
            marker=dict(color=colors_list, line=dict(color='white', width=2)),
            hovertemplate='<b>%{y}</b><br>Monto: $%{x:,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': 'Gastos por Categoría',
            'font': {'size': 20, 'family': 'Roboto Condensed', 'color': COLORS['azul']},
            'x': 0,
            'xanchor': 'left'
        },
        xaxis_title='Monto ($)',
        yaxis_title='',
        font={'family': 'Roboto Condensed'},
        paper_bgcolor='white',
        plot_bgcolor='#F8F9FA',
        height=380,
        margin=dict(l=150, r=80, t=80, b=60),
        xaxis=dict(gridcolor='#E0E0E0', tickfont={'family': 'Roboto Condensed', 'size': 12},
                   title_font={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']}, fixedrange=True),
        yaxis=dict(tickfont={'family': 'Roboto Condensed', 'size': 12}, fixedrange=True),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Roboto Condensed"),
        dragmode=False,
        modebar={'remove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']}
    )
    
    return fig

def crear_lineas_presupuesto_gasto_anual(df, año_filtro):
    df_año = df[df['Año'] == año_filtro].copy()
    meses_numeros = list(range(1, 13))
    meses_nombres = [MESES[m] for m in meses_numeros]
    
    presupuestos = []
    gastos = []
    
    for mes in meses_numeros:
        presupuesto = obtener_ultimo_presupuesto_mes(df_año, año_filtro, mes)
        presupuestos.append(presupuesto)
        gasto = df_año[(df_año['Tipo'] == 'Gasto') & (df_año['Mes'] == mes)]['Monto'].sum()
        gastos.append(gasto)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=meses_nombres, y=presupuestos, mode='lines+markers+text', name='Presupuesto',
        line=dict(color=COLORS['azul'], width=3), marker=dict(size=10, color=COLORS['azul']),
        text=[f'${v:,.0f}' if v > 0 else '' for v in presupuestos], textposition='top center',
        textfont={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']},
        hovertemplate='<b>%{x}</b><br>Presupuesto: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=meses_nombres, y=gastos, mode='lines+markers+text', name='Gasto',
        line=dict(color=COLORS['rosa'], width=3), marker=dict(size=10, color=COLORS['rosa']),
        text=[f'${v:,.0f}' if v > 0 else '' for v in gastos], textposition='top center',
        textfont={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['rosa']},
        hovertemplate='<b>%{x}</b><br>Gasto: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={'text': f'Análisis de Gasto y Presupuesto Mensual - {año_filtro}',
               'font': {'size': 20, 'family': 'Roboto Condensed', 'color': COLORS['azul']}, 'x': 0, 'xanchor': 'left'},
        xaxis_title='Mes', yaxis_title='Monto ($)',
        font={'family': 'Roboto Condensed'}, paper_bgcolor='white', plot_bgcolor='#F8F9FA',
        height=450, margin=dict(l=80, r=40, t=100, b=60),
        xaxis=dict(gridcolor='#E0E0E0', tickfont={'family': 'Roboto Condensed', 'size': 11},
                   tickangle=-45, title_font={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']}, fixedrange=True),
        yaxis=dict(gridcolor='#E0E0E0', tickfont={'family': 'Roboto Condensed', 'size': 12},
                   title_font={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']}, fixedrange=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                    font={'family': 'Roboto Condensed', 'size': 14}),
        hovermode='x unified', hoverlabel=dict(bgcolor="white", font_size=13, font_family="Roboto Condensed"),
        dragmode=False,
        modebar={'remove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']}
    )
    
    return fig

def crear_barras_ingreso_gasto_mensual(df, año_filtro):
    df_año = df[df['Año'] == año_filtro].copy()
    meses_numeros = list(range(1, 13))
    meses_nombres = [MESES[m] for m in meses_numeros]
    
    ingresos = []
    gastos = []
    
    for mes in meses_numeros:
        ingreso = df_año[(df_año['Tipo'] == 'Ingreso') & (df_año['Mes'] == mes)]['Monto'].sum()
        ingresos.append(ingreso)
        gasto = df_año[(df_año['Tipo'] == 'Gasto') & (df_año['Mes'] == mes)]['Monto'].sum()
        gastos.append(gasto)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=meses_nombres, y=ingresos, name='Ingreso', marker_color=COLORS['cian'],
        text=[f'${v:,.0f}' if v > 0 else '' for v in ingresos], textposition='outside',
        textfont={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['cian']},
        hovertemplate='<b>%{x}</b><br>Ingreso: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=meses_nombres, y=gastos, name='Gasto', marker_color=COLORS['naranja'],
        text=[f'${v:,.0f}' if v > 0 else '' for v in gastos], textposition='outside',
        textfont={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['naranja']},
        hovertemplate='<b>%{x}</b><br>Gasto: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={'text': f'Ingresos vs Gastos Mensuales - {año_filtro}',
               'font': {'size': 20, 'family': 'Roboto Condensed', 'color': COLORS['azul']}, 'x': 0, 'xanchor': 'left'},
        xaxis_title='Mes', yaxis_title='Monto ($)', barmode='group',
        font={'family': 'Roboto Condensed'}, paper_bgcolor='white', plot_bgcolor='#F8F9FA',
        height=450, margin=dict(l=80, r=40, t=100, b=60),
        xaxis=dict(gridcolor='#E0E0E0', tickfont={'family': 'Roboto Condensed', 'size': 11},
                   tickangle=-45, title_font={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']}, fixedrange=True),
        yaxis=dict(gridcolor='#E0E0E0', tickfont={'family': 'Roboto Condensed', 'size': 12},
                   title_font={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']}, fixedrange=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                    font={'family': 'Roboto Condensed', 'size': 14}),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Roboto Condensed"),
        dragmode=False,
        modebar={'remove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']}
    )
    
    return fig

# ============================================
# APLICACIÓN PRINCIPAL
# ============================================

# === BD de clientes ===
BD_CLIENTS_URL = "https://docs.google.com/spreadsheets/d/1-m5M_SYYlD--xzRmPx6_7BnKmftPTbgzswKq1Tp1TH8/export?format=csv"

# === Obtener parámetro del cliente ===
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

# === Buscar cliente ===
row = df_clients[df_clients["ID"] == cliente_id]

if row.empty:
    st.error("❌ Cliente no encontrado en la BD de clientes")
    st.stop()

# === Datos del cliente ===
cliente_nombre = row.iloc[0]["Client"]
sheet_url = row.iloc[0]["URL Sheets"]

if "export?format=csv" not in sheet_url:
    if "/edit" in sheet_url:
        sheet_url = sheet_url.split("/edit")[0] + "/export?format=csv"

# === Cargar datos del cliente ===
try:
    df = load_client_data(sheet_url)
except Exception as e:
    st.error("❌ No se pudo cargar los datos del cliente")
    st.stop()

# ============================================
# ENCABEZADO CON FONDO #F0F7FF
# ============================================

# Abrir el div con la clase header-wrapper (fondo azul suave)
st.markdown('<div class="header-wrapper">', unsafe_allow_html=True)

header_col1, header_col2 = st.columns([2, 3])

with header_col1:
    # Logo y Título juntos
    logo_subcol, titulo_subcol = st.columns([1, 4])
    
    with logo_subcol:
        logo = load_logo("https://drive.google.com/file/d/1Bt1zKrOtAL-nZWZlqWr3x4CdTkTHGbnA/view?usp=sharing")
        if logo:
            st.image(logo, use_column_width=True)
    
    with titulo_subcol:
        st.markdown(f"""
            <div style="padding: 0 0 0 8px; margin-top: 0;">
                <h1 class="titulo-principal" style="margin: 0 0 0 0; line-height: 1.1;">
                    CONTROL DE FINANZAS
                </h1>
                <p class="nombre-usuario" style="margin: -3px 0 0 0; padding: 0;">
                    {cliente_nombre}
                </p>
            </div>
        """, unsafe_allow_html=True)

with header_col2:
    st.markdown('<div style="padding-top: 10px;">', unsafe_allow_html=True)
    
    # Obtener valores únicos para filtros
    años_disponibles = sorted(df['Año'].unique(), reverse=True)
    año_actual = datetime.now().year
    mes_actual = datetime.now().month
    
    # Inicializar session_state para filtros si no existe
    if 'filtros_aplicados' not in st.session_state:
        todos_dias = sorted(df[(df['Año'] == año_actual) & (df['Mes'] == mes_actual)]['Dia'].unique()) if len(df[(df['Año'] == año_actual) & (df['Mes'] == mes_actual)]) > 0 else []
        
        st.session_state.filtros_aplicados = {
            'categoria': CATEGORIAS_GASTO.copy(),
            'año': año_actual if año_actual in años_disponibles else años_disponibles[0],
            'mes': mes_actual,
            'dia': todos_dias
        }
    
    if 'widget_key' not in st.session_state:
        st.session_state.widget_key = 0
    
    filtro_col1, filtro_col2, filtro_col3, filtro_col4, filtro_col5 = st.columns([2, 1.2, 1.2, 1.2, 1.3])
    
    with filtro_col1:
        default_categorias = [] if len(st.session_state.filtros_aplicados['categoria']) == len(CATEGORIAS_GASTO) else st.session_state.filtros_aplicados['categoria']
        
        categorias_seleccionadas = st.multiselect(
            "Categoría",
            options=CATEGORIAS_GASTO,
            default=default_categorias,
            key=f'filtro_categoria_{st.session_state.widget_key}',
            placeholder="Categoría"
        )
        
        if not categorias_seleccionadas:
            categorias_seleccionadas = CATEGORIAS_GASTO.copy()
    
    with filtro_col2:
        año_seleccionado = st.selectbox(
            "Año",
            options=años_disponibles,
            index=años_disponibles.index(st.session_state.filtros_aplicados['año']) if st.session_state.filtros_aplicados['año'] in años_disponibles else 0,
            key=f'filtro_año_{st.session_state.widget_key}',
            placeholder="Año"
        )
    
    with filtro_col3:
        meses_disponibles = sorted(df[df['Año'] == año_seleccionado]['Mes'].unique())
        
        if mes_actual in meses_disponibles:
            default_mes_index = meses_disponibles.index(mes_actual)
        else:
            default_mes_index = meses_disponibles.index(st.session_state.filtros_aplicados['mes']) if st.session_state.filtros_aplicados['mes'] in meses_disponibles else 0
        
        mes_seleccionado = st.selectbox(
            "Mes",
            options=meses_disponibles,
            format_func=lambda x: MESES[x],
            index=default_mes_index,
            key=f'filtro_mes_{st.session_state.widget_key}',
            placeholder="Mes"
        )
    
    with filtro_col4:
        df_temp = df[(df['Año'] == año_seleccionado) & (df['Mes'] == mes_seleccionado)]
        dias_disponibles = sorted(df_temp['Dia'].unique()) if len(df_temp) > 0 else list(range(1, 32))
        
        default_dias = [] if len(st.session_state.filtros_aplicados['dia']) == len(dias_disponibles) else [d for d in st.session_state.filtros_aplicados['dia'] if d in dias_disponibles]
        
        dias_seleccionados = st.multiselect(
            "Día",
            options=dias_disponibles,
            default=default_dias,
            key=f'filtro_dia_{st.session_state.widget_key}',
            placeholder="Día"
        )
        
        if not dias_seleccionados:
            dias_seleccionados = dias_disponibles.copy()
    
    with filtro_col5:
        if st.button("Limpiar Filtros", use_container_width=True):
            st.session_state.widget_key += 1
            
            todos_dias_reset = sorted(df[(df['Año'] == año_actual) & (df['Mes'] == mes_actual)]['Dia'].unique()) if len(df[(df['Año'] == año_actual) & (df['Mes'] == mes_actual)]) > 0 else []
            
            st.session_state.filtros_aplicados = {
                'categoria': CATEGORIAS_GASTO.copy(),
                'año': año_actual if año_actual in años_disponibles else años_disponibles[0],
                'mes': mes_actual,
                'dia': todos_dias_reset
            }
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Cerrar el div del header-wrapper
st.markdown('</div>', unsafe_allow_html=True)

# Actualizar session_state
st.session_state.filtros_aplicados = {
    'categoria': categorias_seleccionadas,
    'año': año_seleccionado,
    'mes': mes_seleccionado,
    'dia': dias_seleccionados
}

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# APLICAR FILTROS
# ============================================
df_filtrado = df.copy()

df_filtrado = df_filtrado[
    (df_filtrado['Año'] == año_seleccionado) & 
    (df_filtrado['Mes'] == mes_seleccionado)
]

if categorias_seleccionadas and len(categorias_seleccionadas) < len(CATEGORIAS_GASTO):
    df_filtrado = df_filtrado[df_filtrado['Categoría'].isin(categorias_seleccionadas)]

if dias_seleccionados and len(dias_seleccionados) < len(dias_disponibles):
    df_filtrado = df_filtrado[df_filtrado['Dia'].isin(dias_seleccionados)]

# ============================================
# CALCULAR MÉTRICAS
# ============================================
presupuesto_disponible, presupuesto_mes, gastos_mes = calcular_presupuesto_disponible(
    df, año_seleccionado, mes_seleccionado
)

df_año_completo = df[df['Año'] == año_seleccionado].copy()

ingresos_total = df_filtrado[df_filtrado['Tipo'] == 'Ingreso']['Monto'].sum()
gastos_total = df_filtrado[df_filtrado['Tipo'] == 'Gasto']['Monto'].sum()

# ============================================
# MÉTRICAS PRINCIPALES CON MES
# ============================================

# Determinar color del presupuesto disponible
if presupuesto_disponible <= 0:
    color_disponible = "#FF4444"
elif presupuesto_disponible <= 100:
    color_disponible = "#FFA333"
else:
    color_disponible = "#00C851"

CARD_STYLE = "background-color: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); height: 120px; display: flex; flex-direction: column; justify-content: center;"
LABEL_STYLE = "font-family: 'Roboto Condensed', sans-serif; font-size: 14px; font-weight: 400; color: #0081FF; margin-bottom: 6px;"
VALUE_STYLE = "font-family: 'Roboto Condensed', sans-serif; font-size: 32px; font-weight: 400; color: #333333; margin-top: 8px;"

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
        <div style="{CARD_STYLE} align-items: center;">
            <div style="{LABEL_STYLE} text-align: center;">Mes</div>
            <div style="{VALUE_STYLE} color: #0081FF; font-weight: 700; text-align: center;">
                {MESES[mes_seleccionado].upper()}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style="{CARD_STYLE}">
            <div style="{LABEL_STYLE}">Ingreso</div>
            <div style="{VALUE_STYLE}">${ingresos_total:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style="{CARD_STYLE}">
            <div style="{LABEL_STYLE}">Gasto</div>
            <div style="{VALUE_STYLE}">${gastos_total:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div style="{CARD_STYLE}">
            <div style="{LABEL_STYLE}">Presupuesto</div>
            <div style="{VALUE_STYLE}">${presupuesto_mes:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div style="{CARD_STYLE}">
            <div style="{LABEL_STYLE}">Presupuesto Disponible</div>
            <div style="{VALUE_STYLE} color: {color_disponible};">${presupuesto_disponible:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# GRÁFICOS
# ============================================

col1, col2 = st.columns(2)

with col1:
    fig_gauge = crear_gauge_presupuesto(df_filtrado, presupuesto_mes)
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

with col2:
    fig_barras_h = crear_barras_horizontales_categorias(df_filtrado)
    st.plotly_chart(fig_barras_h, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig_lineas = crear_lineas_presupuesto_gasto_anual(df, año_seleccionado)
    st.plotly_chart(fig_lineas, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

with col2:
    fig_barras_v = crear_barras_ingreso_gasto_mensual(df, año_seleccionado)
    st.plotly_chart(fig_barras_v, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# TABLAS DE GASTOS E INGRESOS
# ============================================
st.markdown("### Detalle de Transacciones")

df_gastos = df_filtrado[df_filtrado['Tipo'] == 'Gasto'].copy()
df_ingresos = df_filtrado[df_filtrado['Tipo'] == 'Ingreso'].copy()

def formatear_fecha_espanol(fecha):
    meses_abrev = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    dia = fecha.day
    mes = meses_abrev[fecha.month]
    año = fecha.year
    hora = fecha.strftime('%H:%M:%S')
    return f"{dia} {mes} {año} {hora}"

if len(df_gastos) > 0:
    df_gastos['Fecha_formato'] = df_gastos['Fecha'].apply(formatear_fecha_espanol)
    df_gastos_tabla = df_gastos[['Fecha_formato', 'Descripción', 'Categoría', 'Monto']].copy()
    df_gastos_tabla.columns = ['Fecha', 'Descripción', 'Categoría', 'Monto']
    df_gastos_tabla = df_gastos_tabla.reset_index(drop=True)
    df_gastos_tabla.index = df_gastos_tabla.index + 1
else:
    df_gastos_tabla = pd.DataFrame(columns=['Fecha', 'Descripción', 'Categoría', 'Monto'])

if len(df_ingresos) > 0:
    df_ingresos['Fecha_formato'] = df_ingresos['Fecha'].apply(formatear_fecha_espanol)
    df_ingresos_tabla = df_ingresos[['Fecha_formato', 'Descripción', 'Categoría', 'Monto']].copy()
    df_ingresos_tabla.columns = ['Fecha', 'Descripción', 'Categoría', 'Monto']
    df_ingresos_tabla = df_ingresos_tabla.reset_index(drop=True)
    df_ingresos_tabla.index = df_ingresos_tabla.index + 1
else:
    df_ingresos_tabla = pd.DataFrame(columns=['Fecha', 'Descripción', 'Categoría', 'Monto'])

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### Gastos ({len(df_gastos_tabla)} registros)")
    
    def style_gastos(df):
        return df.style.set_table_styles([
            {'selector': 'thead th', 'props': [
                ('background-color', '#00C851'), ('color', 'white'),
                ('font-weight', 'bold'), ('padding', '8px')
            ]},
            {'selector': 'tbody td', 'props': [
                ('background-color', '#FFFFFF'), ('color', '#333333')
            ]}
        ])
    
    if len(df_gastos_tabla) > 0:
        styled_gastos = style_gastos(df_gastos_tabla)
        st.dataframe(styled_gastos, use_container_width=True, height=350, hide_index=False,
            column_config={
                "Fecha": st.column_config.TextColumn("Fecha", width="medium"),
                "Descripción": st.column_config.TextColumn("Descripción", width="medium"),
                "Categoría": st.column_config.TextColumn("Categoría", width="small"),
                "Monto": st.column_config.NumberColumn("Monto", format="$%.2f", width="small"),
            })
    else:
        st.dataframe(df_gastos_tabla, use_container_width=True, height=350, hide_index=False)

with col2:
    st.markdown(f"#### Ingresos ({len(df_ingresos_tabla)} registros)")
    
    def style_ingresos(df):
        return df.style.set_table_styles([
            {'selector': 'thead th', 'props': [
                ('background-color', '#0081FF'), ('color', 'white'),
                ('font-weight', 'bold'), ('padding', '8px')
            ]},
            {'selector': 'tbody td', 'props': [
                ('background-color', '#FFFFFF'), ('color', '#333333')
            ]}
        ])
    
    if len(df_ingresos_tabla) > 0:
        styled_ingresos = style_ingresos(df_ingresos_tabla)
        st.dataframe(styled_ingresos, use_container_width=True, height=350, hide_index=False,
            column_config={
                "Fecha": st.column_config.TextColumn("Fecha", width="medium"),
                "Descripción": st.column_config.TextColumn("Descripción", width="medium"),
                "Categoría": st.column_config.TextColumn("Categoría", width="small"),
                "Monto": st.column_config.NumberColumn("Monto", format="$%.2f", width="small"),
            })
    else:
        st.dataframe(df_ingresos_tabla, use_container_width=True, height=350, hide_index=False)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown(f"""
    <div style='text-align: center; color: #666; padding: 20px; font-size: 14px;'>
        Control de Finanzas - {cliente_nombre} | Desarrollado con ❤️ usando Streamlit
    </div>
""", unsafe_allow_html=True)
