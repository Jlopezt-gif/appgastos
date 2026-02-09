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
        background-color: #FFFFFF;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Roboto Condensed', sans-serif !important;
        color: #4E54D4;
    }
    
    .stMetric {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stMetric label {
        font-family: 'Roboto Condensed', sans-serif !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #4E54D4 !important;
    }
    
    .stMetric .metric-value {
        font-family: 'Roboto Condensed', sans-serif !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stDataFrameResizeHandle"] {
        display: none;
    }
    
    .dataframe {
        font-family: 'Roboto Condensed', sans-serif !important;
    }
    
    .stSelectbox label, .stMultiSelect label {
        font-family: 'Roboto Condensed', sans-serif !important;
        font-weight: 600 !important;
        color: #4E54D4 !important;
    }
    
    .stButton button {
        font-family: 'Roboto Condensed', sans-serif !important;
        background-color: #4E54D4;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: #F72D93;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .header-container {
        background: linear-gradient(135deg, #4E54D4 0%, #F72D93 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .titulo-principal {
        color: white;
        font-size: 36px;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .nombre-usuario {
        color: white;
        font-size: 20px;
        font-weight: 400;
        margin: 5px 0 0 0;
        text-align: center;
        opacity: 0.95;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# COLORES DE LA MARCA
# ============================================
COLORS = {
    'azul': '#4E54D4',
    'rosa': '#F72D93',
    'naranja': '#FFA333',
    'cian': '#00C1D4'
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
    
    # Convertir Fecha a datetime
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # Asegurar tipos numéricos
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
        # Extraer el ID del archivo de Google Drive
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
    """
    Calcula el presupuesto disponible del mes
    """
    # Filtrar presupuestos del mes
    presupuestos_mes = df[
        (df['Tipo'] == 'Presupuesto') & 
        (df['Año'] == año_filtro) & 
        (df['Mes'] == mes_filtro)
    ].sort_values('Fecha', ascending=False)
    
    # Obtener el último presupuesto del mes
    if len(presupuestos_mes) > 0:
        ultimo_presupuesto = presupuestos_mes.iloc[0]['Monto']
    else:
        ultimo_presupuesto = 0
    
    # Sumar todos los gastos del mes
    gastos_mes = df[
        (df['Tipo'] == 'Gasto') & 
        (df['Año'] == año_filtro) & 
        (df['Mes'] == mes_filtro)
    ]['Monto'].sum()
    
    presupuesto_disponible = ultimo_presupuesto - gastos_mes
    
    return presupuesto_disponible, ultimo_presupuesto, gastos_mes

def obtener_ultimo_presupuesto_mes(df, año, mes):
    """
    Obtiene el último presupuesto ingresado de un mes específico
    """
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
    """
    Crea el gráfico de gauge para el cumplimiento del presupuesto
    """
    gasto_total = df_filtrado[df_filtrado['Tipo'] == 'Gasto']['Monto'].sum()
    
    # Si no hay presupuesto, usar el gasto como máximo
    if presupuesto_mes == 0:
        max_value = gasto_total if gasto_total > 0 else 100
    else:
        max_value = presupuesto_mes
    
    # Calcular porcentaje
    if presupuesto_mes > 0:
        porcentaje = (gasto_total / presupuesto_mes) * 100
    else:
        porcentaje = 0
    
    # Determinar color según porcentaje
    if porcentaje <= 50:
        color = COLORS['cian']
    elif porcentaje <= 75:
        color = COLORS['naranja']
    else:
        color = COLORS['rosa']
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = gasto_total,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {
            'text': "Cumplimiento del Presupuesto",
            'font': {'size': 24, 'family': 'Roboto Condensed', 'color': COLORS['azul']}
        },
        delta = {'reference': presupuesto_mes, 'increasing': {'color': COLORS['rosa']}},
        gauge = {
            'axis': {
                'range': [None, max_value],
                'tickwidth': 1,
                'tickcolor': COLORS['azul'],
                'tickfont': {'family': 'Roboto Condensed', 'size': 14}
            },
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': COLORS['azul'],
            'steps': [
                {'range': [0, max_value * 0.5], 'color': '#E8F4F8'},
                {'range': [max_value * 0.5, max_value * 0.75], 'color': '#FFE8CC'},
                {'range': [max_value * 0.75, max_value], 'color': '#FFE0EB'}
            ],
            'threshold': {
                'line': {'color': COLORS['azul'], 'width': 4},
                'thickness': 0.75,
                'value': presupuesto_mes
            }
        },
        number = {
            'font': {'family': 'Roboto Condensed', 'size': 40, 'color': COLORS['azul']},
            'prefix': "$"
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="white",
        font={'color': COLORS['azul'], 'family': 'Roboto Condensed'},
        height=400,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    return fig

def crear_barras_horizontales_categorias(df_filtrado):
    """
    Crea el gráfico de barras horizontales por categoría
    """
    gastos = df_filtrado[df_filtrado['Tipo'] == 'Gasto'].copy()
    
    if len(gastos) == 0:
        # Gráfico vacío
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos de gastos para mostrar",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={'size': 16, 'family': 'Roboto Condensed', 'color': COLORS['azul']}
        )
    else:
        # Agrupar por categoría
        por_categoria = gastos.groupby('Categoría')['Monto'].sum().sort_values(ascending=True)
        
        # Asignar colores cíclicamente
        colors_list = [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(len(por_categoria))]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=por_categoria.index,
            x=por_categoria.values,
            orientation='h',
            text=[f'${v:,.0f}' for v in por_categoria.values],
            textposition='outside',
            textfont={'family': 'Roboto Condensed', 'size': 13, 'color': COLORS['azul']},
            marker=dict(
                color=colors_list,
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>%{y}</b><br>Monto: $%{x:,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': 'Gastos por Categoría',
            'font': {'size': 24, 'family': 'Roboto Condensed', 'color': COLORS['azul']},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Monto ($)',
        yaxis_title='',
        font={'family': 'Roboto Condensed'},
        paper_bgcolor='white',
        plot_bgcolor='#F8F9FA',
        height=400,
        margin=dict(l=150, r=80, t=80, b=60),
        xaxis=dict(
            gridcolor='#E0E0E0',
            tickfont={'family': 'Roboto Condensed', 'size': 12},
            title_font={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']}
        ),
        yaxis=dict(
            tickfont={'family': 'Roboto Condensed', 'size': 12}
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Roboto Condensed"
        )
    )
    
    return fig

def crear_lineas_presupuesto_gasto_anual(df, año_filtro):
    """
    Crea el gráfico de líneas comparando Presupuesto y Gasto mensual
    (Este gráfico muestra TODOS los meses del año, sin filtro de mes)
    """
    # Filtrar solo por año
    df_año = df[df['Año'] == año_filtro].copy()
    
    # Preparar datos para todos los meses
    meses_numeros = list(range(1, 13))
    meses_nombres = [MESES[m] for m in meses_numeros]
    
    presupuestos = []
    gastos = []
    
    for mes in meses_numeros:
        # Presupuesto: último del mes
        presupuesto = obtener_ultimo_presupuesto_mes(df_año, año_filtro, mes)
        presupuestos.append(presupuesto)
        
        # Gasto: suma del mes
        gasto = df_año[(df_año['Tipo'] == 'Gasto') & (df_año['Mes'] == mes)]['Monto'].sum()
        gastos.append(gasto)
    
    fig = go.Figure()
    
    # Línea de Presupuesto
    fig.add_trace(go.Scatter(
        x=meses_nombres,
        y=presupuestos,
        mode='lines+markers+text',
        name='Presupuesto',
        line=dict(color=COLORS['azul'], width=3),
        marker=dict(size=10, color=COLORS['azul']),
        text=[f'${v:,.0f}' if v > 0 else '' for v in presupuestos],
        textposition='top center',
        textfont={'family': 'Roboto Condensed', 'size': 11, 'color': COLORS['azul']},
        hovertemplate='<b>%{x}</b><br>Presupuesto: $%{y:,.0f}<extra></extra>'
    ))
    
    # Línea de Gasto
    fig.add_trace(go.Scatter(
        x=meses_nombres,
        y=gastos,
        mode='lines+markers+text',
        name='Gasto',
        line=dict(color=COLORS['rosa'], width=3),
        marker=dict(size=10, color=COLORS['rosa']),
        text=[f'${v:,.0f}' if v > 0 else '' for v in gastos],
        textposition='bottom center',
        textfont={'family': 'Roboto Condensed', 'size': 11, 'color': COLORS['rosa']},
        hovertemplate='<b>%{x}</b><br>Gasto: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Análisis de Gasto y Presupuesto Mensual - {año_filtro}',
            'font': {'size': 24, 'family': 'Roboto Condensed', 'color': COLORS['azul']},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Mes',
        yaxis_title='Monto ($)',
        font={'family': 'Roboto Condensed'},
        paper_bgcolor='white',
        plot_bgcolor='#F8F9FA',
        height=450,
        margin=dict(l=80, r=40, t=80, b=60),
        xaxis=dict(
            gridcolor='#E0E0E0',
            tickfont={'family': 'Roboto Condensed', 'size': 12},
            title_font={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']}
        ),
        yaxis=dict(
            gridcolor='#E0E0E0',
            tickfont={'family': 'Roboto Condensed', 'size': 12},
            title_font={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']}
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font={'family': 'Roboto Condensed', 'size': 14}
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Roboto Condensed"
        )
    )
    
    return fig

def crear_barras_ingreso_gasto_mensual(df, año_filtro):
    """
    Crea el gráfico de barras verticales comparando Ingresos y Gastos por mes
    (Este gráfico muestra TODOS los meses del año)
    """
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
    
    # Barras de Ingreso
    fig.add_trace(go.Bar(
        x=meses_nombres,
        y=ingresos,
        name='Ingreso',
        marker_color=COLORS['cian'],
        text=[f'${v:,.0f}' if v > 0 else '' for v in ingresos],
        textposition='outside',
        textfont={'family': 'Roboto Condensed', 'size': 11, 'color': COLORS['cian']},
        hovertemplate='<b>%{x}</b><br>Ingreso: $%{y:,.0f}<extra></extra>'
    ))
    
    # Barras de Gasto
    fig.add_trace(go.Bar(
        x=meses_nombres,
        y=gastos,
        name='Gasto',
        marker_color=COLORS['naranja'],
        text=[f'${v:,.0f}' if v > 0 else '' for v in gastos],
        textposition='outside',
        textfont={'family': 'Roboto Condensed', 'size': 11, 'color': COLORS['naranja']},
        hovertemplate='<b>%{x}</b><br>Gasto: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Ingresos vs Gastos Mensuales - {año_filtro}',
            'font': {'size': 24, 'family': 'Roboto Condensed', 'color': COLORS['azul']},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Mes',
        yaxis_title='Monto ($)',
        barmode='group',
        font={'family': 'Roboto Condensed'},
        paper_bgcolor='white',
        plot_bgcolor='#F8F9FA',
        height=450,
        margin=dict(l=80, r=40, t=80, b=60),
        xaxis=dict(
            gridcolor='#E0E0E0',
            tickfont={'family': 'Roboto Condensed', 'size': 12},
            title_font={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']}
        ),
        yaxis=dict(
            gridcolor='#E0E0E0',
            tickfont={'family': 'Roboto Condensed', 'size': 12},
            title_font={'family': 'Roboto Condensed', 'size': 14, 'color': COLORS['azul']}
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font={'family': 'Roboto Condensed', 'size': 14}
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Roboto Condensed"
        )
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
# ENCABEZADO CON LOGO Y TÍTULO
# ============================================
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    logo = load_logo("https://drive.google.com/file/d/1qlZkn7u6xTgVmKu34U9i2mD_3XL7XF6N/view?usp=sharing")
    if logo:
        st.image(logo, width=120)

with col_titulo:
    st.markdown(f"""
        <div class="header-container">
            <h1 class="titulo-principal">CONTROL DE FINANZAS</h1>
            <p class="nombre-usuario">{cliente_nombre}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# FILTROS
# ============================================
st.markdown(f"### 🔍 Filtros")

# Obtener valores únicos para filtros
años_disponibles = sorted(df['Año'].unique(), reverse=True)
año_actual = datetime.now().year
mes_actual = datetime.now().month

# Inicializar session_state para filtros
if 'filtros_aplicados' not in st.session_state:
    st.session_state.filtros_aplicados = {
        'categoria': [],
        'año': año_actual if año_actual in años_disponibles else años_disponibles[0],
        'mes': mes_actual,
        'dia': []
    }

col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])

with col1:
    categorias_seleccionadas = st.multiselect(
        "Categoría",
        options=CATEGORIAS_GASTO,
        default=st.session_state.filtros_aplicados['categoria'],
        key='filtro_categoria'
    )

with col2:
    año_seleccionado = st.selectbox(
        "Año",
        options=años_disponibles,
        index=años_disponibles.index(st.session_state.filtros_aplicados['año']) if st.session_state.filtros_aplicados['año'] in años_disponibles else 0,
        key='filtro_año'
    )

with col3:
    # Crear lista de meses disponibles en los datos
    meses_disponibles = sorted(df[df['Año'] == año_seleccionado]['Mes'].unique())
    
    # Si el mes actual está en los datos, usarlo como default, sino el primero disponible
    if mes_actual in meses_disponibles:
        default_mes_index = meses_disponibles.index(mes_actual)
    else:
        default_mes_index = meses_disponibles.index(st.session_state.filtros_aplicados['mes']) if st.session_state.filtros_aplicados['mes'] in meses_disponibles else 0
    
    mes_seleccionado = st.selectbox(
        "Mes",
        options=meses_disponibles,
        format_func=lambda x: MESES[x],
        index=default_mes_index,
        key='filtro_mes'
    )

with col4:
    # Obtener días disponibles según filtros de año y mes
    df_temp = df[(df['Año'] == año_seleccionado) & (df['Mes'] == mes_seleccionado)]
    dias_disponibles = sorted(df_temp['Dia'].unique()) if len(df_temp) > 0 else list(range(1, 32))
    
    dias_seleccionados = st.multiselect(
        "Día",
        options=dias_disponibles,
        default=st.session_state.filtros_aplicados['dia'] if st.session_state.filtros_aplicados['dia'] else [],
        key='filtro_dia'
    )

with col5:
    if st.button("🔄 Limpiar Filtros", use_container_width=True):
        st.session_state.filtros_aplicados = {
            'categoria': [],
            'año': año_actual if año_actual in años_disponibles else años_disponibles[0],
            'mes': mes_actual,
            'dia': []
        }
        st.rerun()

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

# Filtro de año y mes (siempre activos)
df_filtrado = df_filtrado[
    (df_filtrado['Año'] == año_seleccionado) & 
    (df_filtrado['Mes'] == mes_seleccionado)
]

# Filtro de categoría (opcional)
if categorias_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado['Categoría'].isin(categorias_seleccionadas)]

# Filtro de día (opcional)
if dias_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['Dia'].isin(dias_seleccionados)]

# ============================================
# CALCULAR MÉTRICAS
# ============================================
presupuesto_disponible, presupuesto_mes, gastos_mes = calcular_presupuesto_disponible(
    df, año_seleccionado, mes_seleccionado
)

# Para los gráficos anuales (sin filtro de mes)
df_año_completo = df[df['Año'] == año_seleccionado].copy()

# Sumar ingresos totales del periodo filtrado
ingresos_total = df_filtrado[df_filtrado['Tipo'] == 'Ingreso']['Monto'].sum()

# Sumar gastos totales del periodo filtrado
gastos_total = df_filtrado[df_filtrado['Tipo'] == 'Gasto']['Monto'].sum()

# ============================================
# MÉTRICAS PRINCIPALES
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Ingreso",
        value=f"${ingresos_total:,.2f}"
    )

with col2:
    st.metric(
        label="💸 Gasto",
        value=f"${gastos_total:,.2f}"
    )

with col3:
    st.metric(
        label="📊 Presupuesto",
        value=f"${presupuesto_mes:,.2f}"
    )

with col4:
    delta_color = "normal" if presupuesto_disponible >= 0 else "inverse"
    st.metric(
        label="💼 Presupuesto Disponible",
        value=f"${presupuesto_disponible:,.2f}",
        delta=f"{(presupuesto_disponible/presupuesto_mes*100):.1f}%" if presupuesto_mes > 0 else "0%",
        delta_color=delta_color
    )

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# GRÁFICOS
# ============================================

# Fila 1: Gauge y Barras Horizontales
col1, col2 = st.columns(2)

with col1:
    fig_gauge = crear_gauge_presupuesto(df_filtrado, presupuesto_mes)
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    fig_barras_h = crear_barras_horizontales_categorias(df_filtrado)
    st.plotly_chart(fig_barras_h, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Fila 2: Gráficos de líneas y barras (ANUALES - Sin filtro de mes)
col1, col2 = st.columns(2)

with col1:
    fig_lineas = crear_lineas_presupuesto_gasto_anual(df, año_seleccionado)
    st.plotly_chart(fig_lineas, use_container_width=True)

with col2:
    fig_barras_v = crear_barras_ingreso_gasto_mensual(df, año_seleccionado)
    st.plotly_chart(fig_barras_v, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# TABLAS DE GASTOS E INGRESOS
# ============================================
st.markdown("### 📋 Detalle de Transacciones")

# Preparar datos para tablas
df_gastos = df_filtrado[df_filtrado['Tipo'] == 'Gasto'].copy()
df_ingresos = df_filtrado[df_filtrado['Tipo'] == 'Ingreso'].copy()

# Función para formatear fecha en español
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

# Formatear fecha
if len(df_gastos) > 0:
    df_gastos['Fecha_formato'] = df_gastos['Fecha'].apply(formatear_fecha_espanol)
    df_gastos_tabla = df_gastos[['ID', 'Fecha_formato', 'Descripción', 'Categoría', 'Monto']].copy()
    df_gastos_tabla.columns = ['#', 'Fecha', 'Descripción', 'Categoría', 'Monto']
    df_gastos_tabla = df_gastos_tabla.reset_index(drop=True)
    df_gastos_tabla.index = df_gastos_tabla.index + 1
else:
    df_gastos_tabla = pd.DataFrame(columns=['#', 'Fecha', 'Descripción', 'Categoría', 'Monto'])

if len(df_ingresos) > 0:
    df_ingresos['Fecha_formato'] = df_ingresos['Fecha'].apply(formatear_fecha_espanol)
    df_ingresos_tabla = df_ingresos[['ID', 'Fecha_formato', 'Descripción', 'Categoría', 'Monto']].copy()
    df_ingresos_tabla.columns = ['#', 'Fecha', 'Descripción', 'Categoría', 'Monto']
    df_ingresos_tabla = df_ingresos_tabla.reset_index(drop=True)
    df_ingresos_tabla.index = df_ingresos_tabla.index + 1
else:
    df_ingresos_tabla = pd.DataFrame(columns=['#', 'Fecha', 'Descripción', 'Categoría', 'Monto'])

# Mostrar tablas lado a lado
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### 💸 Gastos ({len(df_gastos_tabla)} registros)")
    st.dataframe(
        df_gastos_tabla,
        use_container_width=True,
        height=400,
        hide_index=False,
        column_config={
            "#": st.column_config.NumberColumn(
                "#",
                width="small",
            ),
            "Fecha": st.column_config.TextColumn(
                "Fecha",
                width="medium",
            ),
            "Descripción": st.column_config.TextColumn(
                "Descripción",
                width="large",
            ),
            "Categoría": st.column_config.TextColumn(
                "Categoría",
                width="medium",
            ),
            "Monto": st.column_config.NumberColumn(
                "Monto",
                format="$%.2f",
                width="medium",
            ),
        }
    )

with col2:
    st.markdown(f"#### 💰 Ingresos ({len(df_ingresos_tabla)} registros)")
    st.dataframe(
        df_ingresos_tabla,
        use_container_width=True,
        height=400,
        hide_index=False,
        column_config={
            "#": st.column_config.NumberColumn(
                "#",
                width="small",
            ),
            "Fecha": st.column_config.TextColumn(
                "Fecha",
                width="medium",
            ),
            "Descripción": st.column_config.TextColumn(
                "Descripción",
                width="large",
            ),
            "Categoría": st.column_config.TextColumn(
                "Categoría",
                width="medium",
            ),
            "Monto": st.column_config.NumberColumn(
                "Monto",
                format="$%.2f",
                width="medium",
            ),
        }
    )

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown(f"""
    <div style='text-align: center; color: #666; padding: 20px; font-size: 14px;'>
        Control de Finanzas - {cliente_nombre} | Desarrollado con ❤️ usando Streamlit
    </div>
""", unsafe_allow_html=True)
