import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="Dashboard Pokémon",
    page_icon="⚡",
    layout="wide"
)

@st.cache_data
def cargar_datos():
    df = pd.read_csv('data/pokedex_enriquecida.csv')
    return df

df = cargar_datos()

st.title("⚡ Dashboard Pokémon - Análisis Global")

# Barra lateral (sidebar) con filtros
with st.sidebar:
    st.header("🎮 Panel de Control")
    
    # Selector de dashboard
    dashboard_seleccionado = st.selectbox(
        "📊 Selecciona un Dashboard",
        ["Explorador de Combate", "Geografía Pokémon"]
    )
    
    st.markdown("---")
    st.subheader("Filtros")
    
    # Filtro país
    paises_disponibles = ['Todos'] + sorted(df['País'].dropna().unique().tolist())
    pais_seleccionado = st.multiselect(
        "🌍 País",
        paises_disponibles,
        default=['Todos']
    )
    
    # Filtro tipo
    tipos_disponibles = ['Todos'] + sorted(df['Tipo'].dropna().unique().tolist())
    tipo_seleccionado = st.multiselect(
        "⚔️ Tipo",
        tipos_disponibles,
        default=['Todos']
    )
    
    # Slider total stats
    min_stats = int(df['Total'].min())
    max_stats = int(df['Total'].max())
    rango_stats = st.slider(
        "📊 Rango de Total Stats",
        min_value=min_stats,
        max_value=max_stats,
        value=(min_stats, max_stats)
    )

# Filtrar datos según selección
df_filtrado = df.copy()
if 'Todos' not in pais_seleccionado and len(pais_seleccionado) > 0:
    df_filtrado = df_filtrado[df_filtrado['País'].isin(pais_seleccionado)]
if 'Todos' not in tipo_seleccionado and len(tipo_seleccionado) > 0:
    df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(tipo_seleccionado)]
df_filtrado = df_filtrado[
    (df_filtrado['Total'] >= rango_stats[0]) & 
    (df_filtrado['Total'] <= rango_stats[1])
]

if dashboard_seleccionado == "Explorador de Combate":
    st.header("⚔️ Explorador de Combate")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        idx_fuerte = df_filtrado['Ataque'].idxmax() if not df_filtrado.empty else None
        if idx_fuerte is not None:
            pokemon_fuerte = df_filtrado.loc[idx_fuerte]
            st.metric(
                label="💪 Pokémon más fuerte",
                value=pokemon_fuerte['Nombre'],
                delta=f"Ataque: {pokemon_fuerte['Ataque']}"
            )
    with col2:
        idx_rapido = df_filtrado['Velocidad'].idxmax() if not df_filtrado.empty else None
        if idx_rapido is not None:
            pokemon_rapido = df_filtrado.loc[idx_rapido]
            st.metric(
                label="⚡ Pokémon más rápido",
                value=pokemon_rapido['Nombre'],
                delta=f"Velocidad: {pokemon_rapido['Velocidad']}"
            )
    with col3:
        idx_defensivo = df_filtrado['Defensa'].idxmax() if not df_filtrado.empty else None
        if idx_defensivo is not None:
            pokemon_defensivo = df_filtrado.loc[idx_defensivo]
            st.metric(
                label="🛡️ Mejor defensa",
                value=pokemon_defensivo['Nombre'],
                delta=f"Defensa: {pokemon_defensivo['Defensa']}"
            )
    with col4:
        st.metric(
            label="📋 Total Pokémon",
            value=len(df_filtrado)
        )
    st.markdown("---")
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("🎯 Ataque vs. Defensa")
        if not df_filtrado.empty:
            fig_scatter = px.scatter(
                df_filtrado,
                x='Ataque',
                y='Defensa',
                color='Tipo',
                hover_name='Nombre',
                title="Dispersión: Ataque vs Defensa"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    with col_der:
        st.subheader("❤️ Distribución de HP")
        if not df_filtrado.empty:
            fig_hist = px.histogram(
                df_filtrado,
                x='HP',
                nbins=30,
                title="Distribución de Puntos de Vida (HP)"
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("📊 Datos filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

elif dashboard_seleccionado == "Geografía Pokémon":
    st.header("🌍 Geografía Pokémon")
    st.subheader("🗺️ Mapa Mundial - Fuerza Promedio por País")
    if not df_filtrado.empty:
        stats_por_pais = df_filtrado.groupby('País')['Total'].mean().reset_index()
        stats_por_pais.columns = ['País', 'Promedio']
        fig_mapa = px.choropleth(
            stats_por_pais,
            locations='País',
            locationmode='country names',
            color='Promedio',
            color_continuous_scale='Viridis',
            title='Fuerza Promedio de Pokémon por País',
            labels={'Promedio': 'Stats Promedio'}
        )
        fig_mapa.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth')
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Top 10 Pokémon por País")
        if not df_filtrado.empty:
            pais_para_top = st.selectbox(
                "Selecciona un país",
                df_filtrado['País'].unique()
            )
            df_pais = df_filtrado[df_filtrado['País'] == pais_para_top]
            top_pokemon = df_pais.nlargest(10, 'Total')
            fig_top = px.bar(
                top_pokemon,
                x='Total',
                y='Nombre',
                orientation='h',
                title=f"Top 10 Pokémon en {pais_para_top}"
            )
            st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.subheader("🎨 Distribución de Tipos")
        if not df_filtrado.empty:
            tipo_counts = df_filtrado['Tipo'].value_counts().reset_index()
            tipo_counts.columns = ['Tipo', 'Cantidad']
            fig_tipos = px.pie(
                tipo_counts,
                values='Cantidad',
                names='Tipo',
                title='Distribución de Tipos de Pokémon'
            )
            st.plotly_chart(fig_tipos, use_container_width=True)
