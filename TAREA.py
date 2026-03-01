import streamlit as st
import streamlit.components.v1 as components
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
st.markdown("""
<style>
/* Empuja todo el contenido hacia abajo para que no lo tape el header de Streamlit */
.block-container {
    padding-top: 3rem !important;
}
</style>
""", unsafe_allow_html=True)

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
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Roboto Condensed', sans-serif !important;
        color: #111111;
    }
    
    /* Espaciado uniforme título → recuadro gráfico */
    div[data-testid="stVerticalBlock"] h4 {
        margin-top: 12px !important;
        margin-bottom: 4px !important;
    }
    div[data-testid="stVerticalBlock"] h4 + div[data-testid="stPlotlyChart"] {
        margin-top: 0 !important;
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
        font-size: 18px !important;
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
    
    .header-box {
        background-color: #FFFFFF;
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
    
    /* Forzar tamaño del h1 dentro de header-box */
    .header-box h1 {
        font-size: 14px !important;
    }
    
    .header-box p {
        font-size: 12px !important;
    }

    /* ===== CHART BOX: apunta al contenedor nativo de plotly en Streamlit ===== */
    div[data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04);
        padding: 12px 12px 8px 12px;
        margin-bottom: 4px;
        overflow: hidden;
    }
    /* Forzar que el SVG interno no desborde */
    div[data-testid="stPlotlyChart"] svg {
        max-height: 330px !important;
    }
    /* Eliminar el fondo blanco interno que Plotly agrega al iframe/svg */
    div[data-testid="stPlotlyChart"] > div {
        background: transparent !important;
    }

    /* Ajustes responsivos para móviles */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
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
        
        .header-box {
            background-color: #2d3748 !important;
            border: 1px solid #4A5568;
        }
        
        .titulo-principal {
            color: #FFFFFF !important;
        }
        
        .nombre-usuario {
            color: #CBD5E0 !important;
        }

        .chart-box {
            background-color: #2d3748 !important;
            border: 1px solid #4A5568;
        }

        div[data-testid="stPlotlyChart"] {
            background-color: #1e2530 !important;
            border: 1px solid #4A5568;
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
TICK_COLOR = "#999999"
GRID_COLOR_LIGHT = "#E8E8E8"
GRID_COLOR_DARK  = "rgba(255,255,255,0.12)"
CHART_H = 320

# ── Tamaños de fuente unificados ──────────────────────────────────────────────
FONT_AXIS  = 12
FONT_LABEL = 12
FONT_GAUGE_TICK = 12
# ─────────────────────────────────────────────────────────────────────────────

def crear_gauge_presupuesto(df_filtrado, presupuesto_mes):
    tema = st.get_option("theme.base")
    number_color = "#FFFFFF" if tema == "dark" else "#222222"
    text_color   = "#FFFFFF" if tema == "dark" else "#222222"

    gasto_total = df_filtrado[df_filtrado['Tipo'] == 'Gasto']['Monto'].sum()
    max_value   = presupuesto_mes if presupuesto_mes > 0 else (gasto_total if gasto_total > 0 else 100)
    porcentaje  = (gasto_total / presupuesto_mes * 100) if presupuesto_mes > 0 else 0

    if porcentaje <= 50:   bar_color = COLORS['cian']
    elif porcentaje <= 75: bar_color = COLORS['naranja']
    else:                  bar_color = COLORS['rosa']

    step_colors = (
        ['#E5F5FF', '#FFF4E5', '#FFE5F2'] if tema != "dark"
        else ['rgba(0,129,255,0.2)', 'rgba(255,157,0,0.2)', 'rgba(255,46,149,0.2)']
    )

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=gasto_total,
        domain={'x': [0.0, 1.0], 'y': [0.2, 1.0]},
        gauge={
            'axis': {
                'range': [None, max_value],
                'showticklabels': True,
                'tickwidth': 0,
                'tickcolor': TICK_COLOR,
                'tickfont': {'family': 'Roboto Condensed', 'size': FONT_GAUGE_TICK, 'color': TICK_COLOR},
                'nticks': 5,
            },
            'bar': {'color': bar_color, 'thickness': 0.65},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': [0,              max_value*0.5],  'color': step_colors[0]},
                {'range': [max_value*0.5,  max_value*0.75], 'color': step_colors[1]},
                {'range': [max_value*0.75, max_value],      'color': step_colors[2]},
            ],
            'threshold': {
                'line': {'color': TICK_COLOR, 'width': 2},
                'thickness': 0.65,
                'value': presupuesto_mes
            }
        },
        number={
            'font': {'family': 'Roboto Condensed', 'size': 24, 'color': TICK_COLOR},
            'prefix': "$",
        }
    ))
    fig.add_annotation(
        text=f"Objetivo: ${presupuesto_mes:,.0f}",
        xref="paper", yref="paper",
        x=0.5, y=0.04,
        showarrow=False,
        font={'family': 'Roboto Condensed', 'size': 11, 'color': TICK_COLOR},
        align="center"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': TICK_COLOR, 'family': 'Roboto Condensed'},
        height=CHART_H,
        margin=dict(l=60, r=60, t=10, b=28),
        dragmode=False,
        modebar={'remove': ['zoom','pan','select','lasso2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d']},
    )
    return fig

def crear_barras_horizontales_categorias(df_filtrado):
    tema     = st.get_option("theme.base")
    grid_c   = GRID_COLOR_DARK if tema == "dark" else GRID_COLOR_LIGHT
    bar_text = "white"

    gastos = df_filtrado[df_filtrado['Tipo'] == 'Gasto'].copy()

    if len(gastos) == 0:
        fig = go.Figure()
        fig.add_annotation(text="Sin datos", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font={'size': 13, 'color': TICK_COLOR})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          height=CHART_H, margin=dict(l=10,r=10,t=5,b=5))
        return fig

    por_cat  = gastos.groupby('Categoría')['Monto'].sum().sort_values(ascending=True)
    n        = len(por_cat)
    colors   = [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(n)]
    mx       = por_cat.max()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=por_cat.index, x=por_cat.values,
        orientation='h',
        text=[f'${v:,.0f}' for v in por_cat.values],
        textposition='outside', cliponaxis=False,
        textfont=dict(family='Roboto Condensed', size=FONT_LABEL, color=TICK_COLOR),
        texttemplate="%{text}",
        marker=dict(color=colors, opacity=0.9, line=dict(width=0)),
        hovertemplate='<b>%{y}</b><br>$%{x:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={'family': 'Roboto Condensed', 'color': TICK_COLOR},
        height=CHART_H,
        margin=dict(l=105, r=15, t=4, b=40),
        xaxis=dict(showgrid=True, gridcolor=grid_c,
                   tickfont={'family':'Roboto Condensed','size':FONT_AXIS,'color':TICK_COLOR},
                   fixedrange=True, zeroline=False,
                   range=[0, mx * 1.40]),
        yaxis=dict(tickfont={'family':'Roboto Condensed','size':FONT_AXIS,'color':TICK_COLOR},
                   fixedrange=True),
        dragmode=False,
        modebar={'remove': ['zoom','pan','select','lasso2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d']}
    )
    return fig

def crear_lineas_presupuesto_gasto_anual(df, año_filtro):
    tema   = st.get_option("theme.base")
    grid_c = GRID_COLOR_DARK if tema == "dark" else GRID_COLOR_LIGHT
    bg_label = "rgba(150,150,150,0.12)" if tema != "dark" else "rgba(80,80,80,0.12)"

    df_año = df[df['Año'] == año_filtro].copy()
    meses_n = list(range(1, 13))
    meses_l = [MESES[m] for m in meses_n]

    presupuestos = [obtener_ultimo_presupuesto_mes(df_año, año_filtro, m) for m in meses_n]
    gastos_list  = [df_año[(df_año['Tipo']=='Gasto')&(df_año['Mes']==m)]['Monto'].sum() for m in meses_n]

    max_v = max(max(presupuestos), max(gastos_list)) if any(presupuestos) or any(gastos_list) else 100
    y_max = max_v * 1.35

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=meses_l, y=presupuestos, mode='lines+markers',
        name='Presupuesto',
        line=dict(color=COLORS['azul'], width=1),
        marker=dict(size=4, color=COLORS['azul']),
        hovertemplate='<b>%{x}</b><br>Presupuesto: $%{y:,.0f}<extra></extra>',
        cliponaxis=False))
    fig.add_trace(go.Scatter(x=meses_l, y=gastos_list, mode='lines+markers',
        name='Gasto',
        line=dict(color=COLORS['rosa'], width=1),
        marker=dict(size=4, color=COLORS['rosa']),
        hovertemplate='<b>%{x}</b><br>Gasto: $%{y:,.0f}<extra></extra>',
        cliponaxis=False))

    annotations = []
    for mes, val in zip(meses_l, presupuestos):
        if val > 0:
            annotations.append(dict(
                x=mes, y=val,
                text=f'${val:,.0f}',
                showarrow=False,
                yshift=14,
                font=dict(family='Roboto Condensed', size=FONT_LABEL, color=COLORS['azul']),
                bgcolor=bg_label,
                borderpad=2,
            ))
    for mes, val in zip(meses_l, gastos_list):
        if val > 0:
            annotations.append(dict(
                x=mes, y=val,
                text=f'${val:,.0f}',
                showarrow=False,
                yshift=14,
                font=dict(family='Roboto Condensed', size=FONT_LABEL, color=COLORS['rosa']),
                bgcolor=bg_label,
                borderpad=2,
            ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font={'family':'Roboto Condensed','color':TICK_COLOR},
        height=CHART_H,
        margin=dict(l=52, r=8, t=28, b=90),
        xaxis=dict(gridcolor=grid_c,
                   tickfont={'family':'Roboto Condensed','size':FONT_AXIS,'color':TICK_COLOR},
                   tickangle=-45, fixedrange=True),
        yaxis=dict(gridcolor=grid_c,
                   tickfont={'family':'Roboto Condensed','size':FONT_AXIS,'color':TICK_COLOR},
                   fixedrange=True, range=[0, y_max]),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                    font={'family':'Roboto Condensed','size':11,'color':TICK_COLOR},
                    bgcolor="rgba(0,0,0,0)"),
        annotations=annotations,
        hovermode='x unified',
        hoverlabel=dict(bgcolor="white" if tema!="dark" else "#1F2937", font_size=11),
        dragmode=False,
        modebar={'remove': ['zoom','pan','select','lasso2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d']}
    )
    return fig

def crear_lineas_ingreso_gasto_mensual(df, año_filtro):
    tema   = st.get_option("theme.base")
    grid_c = GRID_COLOR_DARK if tema == "dark" else GRID_COLOR_LIGHT
    bg_label = "rgba(150,150,150,0.12)" if tema != "dark" else "rgba(80,80,80,0.12)"

    df_año  = df[df['Año'] == año_filtro].copy()
    meses_n = list(range(1, 13))
    meses_l = [MESES[m] for m in meses_n]

    ingresos = [df_año[(df_año['Tipo']=='Ingreso')&(df_año['Mes']==m)]['Monto'].sum() for m in meses_n]
    gastos_l = [df_año[(df_año['Tipo']=='Gasto') &(df_año['Mes']==m)]['Monto'].sum() for m in meses_n]

    max_v = max(max(ingresos), max(gastos_l)) if any(ingresos) or any(gastos_l) else 100
    y_max = max_v * 1.35

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=meses_l, y=ingresos, mode='lines+markers',
        name='Ingreso',
        line=dict(color=COLORS['cian'], width=1),
        marker=dict(size=4, color=COLORS['cian']),
        hovertemplate='<b>%{x}</b><br>Ingreso: $%{y:,.0f}<extra></extra>',
        cliponaxis=False))
    fig.add_trace(go.Scatter(x=meses_l, y=gastos_l, mode='lines+markers',
        name='Gasto',
        line=dict(color=COLORS['naranja'], width=1),
        marker=dict(size=4, color=COLORS['naranja']),
        hovertemplate='<b>%{x}</b><br>Gasto: $%{y:,.0f}<extra></extra>',
        cliponaxis=False))

    annotations = []
    for mes, val in zip(meses_l, ingresos):
        if val > 0:
            annotations.append(dict(
                x=mes, y=val,
                text=f'${val:,.0f}',
                showarrow=False,
                yshift=14,
                font=dict(family='Roboto Condensed', size=FONT_LABEL, color=COLORS['cian']),
                bgcolor=bg_label,
                borderpad=2,
            ))
    for mes, val in zip(meses_l, gastos_l):
        if val > 0:
            annotations.append(dict(
                x=mes, y=val,
                text=f'${val:,.0f}',
                showarrow=False,
                yshift=14,
                font=dict(family='Roboto Condensed', size=FONT_LABEL, color=COLORS['naranja']),
                bgcolor=bg_label,
                borderpad=2,
            ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font={'family':'Roboto Condensed','color':TICK_COLOR},
        height=CHART_H,
        margin=dict(l=52, r=8, t=28, b=90),
        xaxis=dict(gridcolor=grid_c,
                   tickfont={'family':'Roboto Condensed','size':FONT_AXIS,'color':TICK_COLOR},
                   tickangle=-45, fixedrange=True),
        yaxis=dict(gridcolor=grid_c,
                   tickfont={'family':'Roboto Condensed','size':FONT_AXIS,'color':TICK_COLOR},
                   fixedrange=True, range=[0, y_max]),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                    font={'family':'Roboto Condensed','size':11,'color':TICK_COLOR},
                    bgcolor="rgba(0,0,0,0)"),
        annotations=annotations,
        hovermode='x unified',
        hoverlabel=dict(bgcolor="white" if tema!="dark" else "#1F2937", font_size=11),
        dragmode=False,
        modebar={'remove': ['zoom','pan','select','lasso2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d']}
    )
    return fig

# ============================================
# APLICACIÓN PRINCIPAL
# ============================================

BD_CLIENTS_URL = "https://docs.google.com/spreadsheets/d/1-m5M_SYYlD--xzRmPx6_7BnKmftPTbgzswKq1Tp1TH8/export?format=csv"

params = st.query_params
cliente_id = params.get("cliente")

if not cliente_id:
    st.error("❌ No se especificó el cliente en la URL. Usa: ?cliente=ID")
    st.stop()

cliente_id = str(cliente_id).strip()

try:
    df_clients = load_clients_db(BD_CLIENTS_URL)
except Exception as e:
    st.error("❌ No se pudo cargar la BD de clientes")
    st.stop()

row = df_clients[df_clients["ID"] == cliente_id]

if row.empty:
    st.error("❌ Cliente no encontrado en la BD de clientes")
    st.stop()

cliente_nombre = row.iloc[0]["Client"]
sheet_url = row.iloc[0]["URL Sheets"]

if "export?format=csv" not in sheet_url:
    if "/edit" in sheet_url:
        sheet_url = sheet_url.split("/edit")[0] + "/export?format=csv"

try:
    df = load_client_data(sheet_url)
except Exception as e:
    st.error("❌ No se pudo cargar los datos del cliente")
    st.stop()

# ============================================
# ENCABEZADO CON LOGO, TÍTULO Y FILTROS
# ============================================
header_col1, header_col2 = st.columns([2, 3])

with header_col1:
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
    
    años_disponibles = sorted(df['Año'].unique(), reverse=True)
    año_actual = datetime.now().year
    mes_actual = datetime.now().month
    
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
# MÉTRICAS PRINCIPALES
# ============================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
        <div class="stMetric" style="
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-bottom: 16px;
        ">
            <div style="font-family: 'Roboto Condensed', sans-serif; font-size: 32px; font-weight: 400; color: #0081FF; text-align: center;">
                {MESES[mes_seleccionado].upper()}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.metric(
        label="Ingreso",
        value=f"${ingresos_total:,.2f}"
    )

with col3:
    st.metric(
        label="Gasto",
        value=f"${gastos_total:,.2f}"
    )

with col4:
    st.metric(
        label="Presupuesto",
        value=f"${presupuesto_mes:,.2f}"
    )

with col5:
    if presupuesto_disponible <= 0:
        color_valor = "#FF4444"
    elif presupuesto_disponible <= 100:
        color_valor = "#FFA333"
    else:
        color_valor = "#00C851"
    
    st.markdown(f"""
        <div class="stMetric" style="background-color: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); height: 120px; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-family: 'Roboto Condensed', sans-serif; font-size: 14px; font-weight: 400; color: #0081FF;">Vas Ahorrando</div>
            <div style="font-family: 'Roboto Condensed', sans-serif; font-size: 32px; font-weight: 400; color: {color_valor}; margin-top: 8px;">
                ${presupuesto_disponible:,.2f}
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# HELPER: título de gráfico
# ============================================
def chart_title(texto):
    st.markdown(
        f"<h4 style='font-weight:500; margin:0 0 4px 0; font-size:18px;'>{texto}</h4>",
        unsafe_allow_html=True
    )

# ============================================
# GRÁFICOS — fila 1
# ============================================

col1, col2 = st.columns(2)

with col1:
    chart_title("Cumplimiento del Presupuesto")
    fig_gauge = crear_gauge_presupuesto(df_filtrado, presupuesto_mes)
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

with col2:
    chart_title("Gastos por Categoría")
    fig_barras_h = crear_barras_horizontales_categorias(df_filtrado)
    st.plotly_chart(fig_barras_h, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# GRÁFICOS — fila 2
# ============================================

col1, col2 = st.columns(2)

with col1:
    chart_title(f"Análisis Gasto y Presupuesto — {año_seleccionado}")
    fig_lineas = crear_lineas_presupuesto_gasto_anual(df, año_seleccionado)
    st.plotly_chart(fig_lineas, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

with col2:
    chart_title(f"Ingresos vs Gastos Mensuales — {año_seleccionado}")
    fig_barras_v = crear_lineas_ingreso_gasto_mensual(df, año_seleccionado)
    st.plotly_chart(fig_barras_v, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# TABLAS DE GASTOS E INGRESOS
# ============================================

df_gastos = df_filtrado[df_filtrado['Tipo'] == 'Gasto'].copy()
df_ingresos = df_filtrado[df_filtrado['Tipo'] == 'Ingreso'].copy()

def formatear_fecha_espanol(fecha):
    meses_abrev = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    return f"{fecha.day} {meses_abrev[fecha.month]} {fecha.year} {fecha.strftime('%H:%M')}"

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

def render_tabla_html(df, header_color, table_id):
    """Genera tabla HTML con ordenamiento por columna, sin drag, columnas auto-fit."""
    if len(df) == 0:
        return "<p style='color:#999;font-size:12px;'>Sin registros</p>"

    filas_html = ""
    for i, row in df.iterrows():
        monto = row['Monto']
        filas_html += f"""
        <tr>
          <td>{i}</td>
          <td style='white-space:nowrap'>{row['Fecha']}</td>
          <td>{row['Descripción']}</td>
          <td style='white-space:nowrap'>{row['Categoría']}</td>
          <td style='white-space:nowrap;text-align:right'>${monto:,.0f}</td>
        </tr>"""

    return f"""
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
      #{table_id}-wrap {{
        overflow-x: auto;
        overflow-y: auto;
        max-height: 260px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
      }}
      #{table_id} {{
        width: 100%;
        border-collapse: collapse;
        font-family: 'Roboto Condensed', sans-serif;
        font-size: 11px;
      }}
      #{table_id} thead th {{
        background-color: {header_color};
        color: white;
        padding: 6px 8px;
        text-align: left;
        white-space: nowrap;
        cursor: pointer;
        user-select: none;
        position: sticky;
        top: 0;
        z-index: 1;
      }}
      #{table_id} thead th:hover {{ opacity: 0.85; }}
      #{table_id} thead th::after {{
        content: ' ⇅';
        font-size: 9px;
        opacity: 0.6;
      }}
      #{table_id} tbody tr:nth-child(even) td {{
        background-color: #F9FAFB;
      }}
      #{table_id} tbody tr:nth-child(odd) td {{
        background-color: #FFFFFF;
      }}
      #{table_id} tbody td {{
        padding: 5px 8px;
        color: #333;
        border-bottom: 1px solid #F0F0F0;
      }}
      @media (prefers-color-scheme: dark) {{
        #{table_id}-wrap {{ border-color: #4A5568; }}
        #{table_id} tbody tr:nth-child(even) td {{ background-color: #2d3748 !important; color: #E2E8F0; }}
        #{table_id} tbody tr:nth-child(odd) td  {{ background-color: #1e2530 !important; color: #E2E8F0; }}
        #{table_id} tbody td {{ border-bottom-color: #4A5568; }}
      }}
    </style>
    <div id="{table_id}-wrap">
      <table id="{table_id}">
        <thead>
          <tr>
            <th onclick="sortTable('{table_id}',0)">#</th>
            <th onclick="sortTable('{table_id}',1)">Fecha</th>
            <th onclick="sortTable('{table_id}',2)">Descripción</th>
            <th onclick="sortTable('{table_id}',3)">Categoría</th>
            <th onclick="sortTable('{table_id}',4)">Monto</th>
          </tr>
        </thead>
        <tbody>{filas_html}</tbody>
      </table>
    </div>
    <script>
    function sortTable(id, col) {{
      var table = document.getElementById(id);
      var tbody = table.querySelector('tbody');
      var rows = Array.from(tbody.querySelectorAll('tr'));
      var asc = table.dataset.sortCol == col && table.dataset.sortDir == 'asc';
      rows.sort(function(a, b) {{
        var av = a.cells[col].innerText.replace(/[$,]/g,'');
        var bv = b.cells[col].innerText.replace(/[$,]/g,'');
        var an = parseFloat(av), bn = parseFloat(bv);
        if (!isNaN(an) && !isNaN(bn)) return asc ? bn - an : an - bn;
        return asc ? bv.localeCompare(av) : av.localeCompare(bv);
      }});
      rows.forEach(function(r) {{ tbody.appendChild(r); }});
      table.dataset.sortCol = col;
      table.dataset.sortDir = asc ? 'desc' : 'asc';
    }}
    </script>
    """

with col1:
    chart_title("Detalle Gastos")
    components.html(render_tabla_html(df_gastos_tabla, "#00C851", "tbl_gastos"), height=280, scrolling=False)

with col2:
    chart_title("Detalle Ingresos")
    components.html(render_tabla_html(df_ingresos_tabla, "#0081FF", "tbl_ingresos"), height=280, scrolling=False)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown(f"""
    <div style='text-align: center; color: #666; padding: 20px; font-size: 14px;'>
        Control de Finanzas - {cliente_nombre} | Desarrollado con ❤️ usando Streamlit
    </div>
""", unsafe_allow_html=True)
