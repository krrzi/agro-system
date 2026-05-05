"""
SISTEMA DE INFORMACIÓN AGRÍCOLA DE PRECISIÓN
Aplicación principal de Streamlit
Con predicción de rendimientos y optimización de recursos hídricos usando Ensemble Learning
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

# Agregar rutas de módulos
ruta_proyecto = Path(__file__).parent
sys.path.append(str(ruta_proyecto))

from database.init_db import inicializar_base_datos, obtener_ruta_db
from modules import auth, dashboard, prediccion, optimizacion, reportes
from models.ensemble_model import ModeloEnsemble

# Configuración de Streamlit
st.set_page_config(
    page_title="🌾 Sistema Agrícola de Precisión",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main { padding-top: 2rem; }
    .stMetric {
        background-color: #f0f8f5;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #1B4D3E;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background-color: #2D5A3D;
        color: white;
        font-weight: bold;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover { background-color: #1B4D3E; }
</style>
""", unsafe_allow_html=True)

# Inicializar sesión
auth.inicializar_sesion()

# Verificar/Crear BD
def verificar_base_datos():
    ruta_db = Path(obtener_ruta_db())
    if not ruta_db.exists():
        with st.spinner("📊 Inicializando base de datos..."):
            inicializar_base_datos()
        st.rerun()

verificar_base_datos()

# Página de Login
def mostrar_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 🌾 Sistema Agrícola de Precisión")
        st.markdown("### Predicción de Rendimientos & Optimización Hídrica")
        st.divider()
        st.markdown("#### Iniciar Sesión")
        usuario = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
        contraseña = st.text_input("🔐 Contraseña", type="password", placeholder="Ingrese su contraseña")
        col1_login, col2_login = st.columns(2)
        with col1_login:
            if st.button("✅ Ingresar", use_container_width=True):
                if usuario and contraseña:
                    exitoso, mensaje = auth.realizar_login(usuario, contraseña)
                    if exitoso:
                        st.success("✓ Login exitoso")
                        st.rerun()
                    else:
                        st.error("❌ " + mensaje)
                else:
                    st.warning("Por favor complete todos los campos")
        with col2_login:
            if st.button("📝 Registrarse", use_container_width=True):
                st.info("Contacte al administrador para crear una nueva cuenta")
        st.divider()
        st.markdown("### Credenciales de Prueba")
        st.markdown("""
        - **Usuario:** `admin` | **Contraseña:** `admin123`
        """)

# Página principal
def mostrar_app_principal():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🌾 Sistema Agrícola de Precisión")
        st.markdown(f"**Bienvenido:** {auth.obtener_nombre_usuario_actual()}")
    with col3:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            auth.realizar_logout()
            st.rerun()
    st.divider()

    # Inicializar modelo Ensemble
    modelo_ensemble = ModeloEnsemble()
    modelo_entrenado = modelo_ensemble.entrenar()
    if not modelo_entrenado:
        st.error("Error al entrenar el modelo")
        return

    # Sidebar
    st.sidebar.markdown("## 📋 Navegación")
    pagina = st.sidebar.radio(
        "Selecciona una sección:",
        [
            "📊 Dashboard",
            "🌾 Mis Cultivos",
            "🔮 Predicciones",
            "💧 Optimización Hídrica",
            "📄 Reportes",
            "ℹ️ Sistema ML"
        ]
    )
    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Usuario Autenticado:**
    - 👤 {auth.obtener_nombre_usuario_actual()}
    - 🆔 ID: {auth.obtener_id_usuario_actual()}
    """)

    # DASHBOARD
    if pagina == "📊 Dashboard":
        st.header("📊 Dashboard Principal")
        st.markdown("Visualización general de métricas, KPIs y gráficos interactivos")
        st.divider()
        dashboard.mostrar_metricas_kpi(auth.obtener_id_usuario_actual())
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📈 Rendimientos por Cultivo")
            dashboard.mostrar_grafico_rendimientos(auth.obtener_id_usuario_actual())
        with col2:
            st.subheader("🎯 Confianza vs Rendimiento")
            dashboard.mostrar_grafico_confianza(auth.obtener_id_usuario_actual())
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🌡️ Temperatura vs Humedad")
            dashboard.mostrar_grafico_temperatura_humedad(auth.obtener_id_usuario_actual())
        with col2:
            st.subheader("🥧 Distribución de Cultivos")
            dashboard.mostrar_distribucion_tipos_cultivos(auth.obtener_id_usuario_actual())
        st.divider()
        st.subheader("📊 Estadísticas Descriptivas")
        dashboard.mostrar_estadisticas_descriptivas(auth.obtener_id_usuario_actual())

    # MIS CULTIVOS
    elif pagina == "🌾 Mis Cultivos":
        st.header("🌾 Mis Cultivos")
        st.markdown("Listado de cultivos bajo tu administración")
        st.divider()
        dashboard.mostrar_tabla_cultivos(auth.obtener_id_usuario_actual())
        cultivos = dashboard.obtener_cultivos_usuario(auth.obtener_id_usuario_actual())
        if cultivos:
            st.divider()
            st.subheader("➕ Agregar Nuevo Cultivo")
            col1, col2 = st.columns(2)
            with col1:
                nombre_cultivo = st.text_input("Nombre del Cultivo")
                tipo_cultivo = st.selectbox("Tipo de Cultivo", ["Maíz", "Trigo", "Soja", "Arroz", "Cebada", "Otro"])
            with col2:
                area = st.number_input("Área (hectáreas)", min_value=1.0, step=1.0)
                estado = st.selectbox("Estado", ["Activo", "Completado", "Planificado"])
            if st.button("✅ Registrar Nuevo Cultivo"):
                st.info("Funcionalidad disponible para ampliar")
        else:
            st.info("No tienes cultivos registrados aún")

    # PREDICCIONES
    elif pagina == "🔮 Predicciones":
        st.header("🔮 Predicción de Rendimientos")
        st.markdown("Predicción con Ensemble Learning (Random Forest + Gradient Boosting)")
        st.divider()
        cultivos = dashboard.obtener_cultivos_usuario(auth.obtener_id_usuario_actual())
        if cultivos:
            cultivo_nombres = {c['id_cultivo']: c['nombre_cultivo'] for c in cultivos}
            cultivo_seleccionado = st.selectbox(
                "Selecciona un cultivo para predecir:",
                options=list(cultivo_nombres.keys()),
                format_func=lambda x: cultivo_nombres[x]
            )
            st.divider()
            prediccion.mostrar_panel_prediccion(
                cultivo_seleccionado,
                auth.obtener_id_usuario_actual(),
                modelo_ensemble
            )
            st.divider()
            st.subheader("🎯 Importancia de Características del Modelo")
            prediccion.mostrar_importancia_features(modelo_ensemble)
            st.divider()
            st.subheader("📊 Métricas de Entrenamiento del Modelo")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Random Forest MAE", f"{modelo_entrenado['mae_rf']:.0f}")
            with col2:
                st.metric("Gradient Boosting MAE", f"{modelo_entrenado['mae_gb']:.0f}")
            with col3:
                st.metric("Ensemble MAE", f"{modelo_entrenado['mae_ensemble']:.0f}")
            with col4:
                st.metric("R² Score", f"{modelo_entrenado['r2_ensemble']:.3f}")
            st.markdown(f"""
            **Información del Entrenamiento:**
            - Muestras de entrenamiento: {modelo_entrenado['muestras_entrenamiento']}
            - Muestras de evaluación: {modelo_entrenado['muestras_evaluacion']}
            - Modelo: Ensemble (Random Forest + Gradient Boosting)
            """)
        else:
            st.warning("No tienes cultivos. Agrega uno primero desde 'Mis Cultivos'")

    # OPTIMIZACIÓN HÍDRICA
    elif pagina == "💧 Optimización Hídrica":
        st.header("💧 Optimización de Recursos Hídricos")
        st.markdown("Análisis y optimización del consumo de agua basada en predicciones")
        st.divider()
        cultivos = dashboard.obtener_cultivos_usuario(auth.obtener_id_usuario_actual())
        if cultivos:
            cultivo_nombres = {c['id_cultivo']: c['nombre_cultivo'] for c in cultivos}
            cultivo_seleccionado = st.selectbox(
                "Selecciona un cultivo para optimizar:",
                options=list(cultivo_nombres.keys()),
                format_func=lambda x: cultivo_nombres[x],
                key="opt_select"
            )
            st.divider()
            optimizacion.mostrar_panel_optimizacion(
                cultivo_seleccionado,
                auth.obtener_id_usuario_actual()
            )
        else:
            st.warning("No tienes cultivos. Agrega uno primero")

    # REPORTES — corregido para usar bytes en memoria
    elif pagina == "📄 Reportes":
        st.header("📄 Generación de Reportes PDF")
        st.markdown("Descarga reportes operacional y de gestión")
        st.divider()

        cultivos = dashboard.obtener_cultivos_usuario(auth.obtener_id_usuario_actual())

        if cultivos:
            cultivo_nombres = {c['id_cultivo']: c['nombre_cultivo'] for c in cultivos}
            cultivo_seleccionado = st.selectbox(
                "Selecciona un cultivo para generar reporte:",
                options=list(cultivo_nombres.keys()),
                format_func=lambda x: cultivo_nombres[x],
                key="report_select"
            )
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📋 Reporte Operacional")
                st.markdown("Datos de sensores y predicciones de los últimos 7 días.")
                if st.button("📋 Generar Reporte Operacional", use_container_width=True):
                    with st.spinner("Generando reporte operacional..."):
                        pdf_bytes = reportes.crear_reporte_operacional(
                            cultivo_seleccionado,
                            auth.obtener_id_usuario_actual()
                        )
                    if pdf_bytes:
                        nombre_archivo = f"reporte_operacional_{cultivo_nombres[cultivo_seleccionado]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        st.success("✓ Reporte generado correctamente")
                        st.download_button(
                            label="⬇️ Descargar Reporte Operacional",
                            data=pdf_bytes,
                            file_name=nombre_archivo,
                            mime="application/pdf",
                            use_container_width=True
                        )
                        reportes.guardar_reporte_en_bd(
                            auth.obtener_id_usuario_actual(),
                            cultivo_seleccionado,
                            "Operacional",
                            nombre_archivo
                        )
                    else:
                        st.error("No se pudo generar el reporte. Verifica que el cultivo tenga datos.")

            with col2:
                st.markdown("#### 📊 Reporte de Gestión")
                st.markdown("Resumen ejecutivo con KPIs, predicciones y optimización hídrica.")
                if st.button("📊 Generar Reporte de Gestión", use_container_width=True):
                    with st.spinner("Generando reporte de gestión..."):
                        pdf_bytes = reportes.crear_reporte_gestion(
                            cultivo_seleccionado,
                            auth.obtener_id_usuario_actual()
                        )
                    if pdf_bytes:
                        nombre_archivo = f"reporte_gestion_{cultivo_nombres[cultivo_seleccionado]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        st.success("✓ Reporte generado correctamente")
                        st.download_button(
                            label="⬇️ Descargar Reporte de Gestión",
                            data=pdf_bytes,
                            file_name=nombre_archivo,
                            mime="application/pdf",
                            use_container_width=True
                        )
                        reportes.guardar_reporte_en_bd(
                            auth.obtener_id_usuario_actual(),
                            cultivo_seleccionado,
                            "Gestion",
                            nombre_archivo
                        )
                    else:
                        st.error("No se pudo generar el reporte. Verifica que el cultivo tenga datos.")
        else:
            st.warning("No tienes cultivos. Agrega uno primero")

    # SISTEMA ML
    elif pagina == "ℹ️ Sistema ML":
        st.header("ℹ️ Información del Sistema ML")
        st.markdown("Detalles técnicos del modelo Ensemble Learning")
        st.divider()
        st.subheader("🤖 Arquitectura del Modelo")
        st.markdown("""
        El sistema utiliza un **Ensemble Learning** que combina dos modelos:

        1. **Random Forest Regressor**
           - 100 árboles de decisión
           - Profundidad máxima: 15 niveles
           - Excelente para capturar relaciones no lineales

        2. **Gradient Boosting Regressor**
           - 100 estimadores secuenciales
           - Tasa de aprendizaje: 0.1
           - Optimización iterativa del error

        **Predicción Final:** Promedio ponderado de ambos modelos
        """)
        st.divider()
        st.subheader("📊 Características Utilizadas")
        for f in ["🌡️ Temperatura del aire (°C)", "💧 Humedad relativa (%)",
                  "⚗️ pH del suelo", "🌧️ Precipitación (mm)",
                  "☀️ Radiación solar (MJ/m²)", "📍 Área de cultivo (hectáreas)"]:
            st.markdown(f"- {f}")
        st.divider()
        st.subheader("📈 Métricas de Desempeño")
        st.markdown(f"""
        - **MAE Random Forest:** {modelo_entrenado['mae_rf']:.2f} kg/ha
        - **MAE Gradient Boosting:** {modelo_entrenado['mae_gb']:.2f} kg/ha
        - **MAE Ensemble:** {modelo_entrenado['mae_ensemble']:.2f} kg/ha
        - **R² Score:** {modelo_entrenado['r2_ensemble']:.4f}
        - **Muestras entrenamiento:** {modelo_entrenado['muestras_entrenamiento']}
        - **Muestras validación:** {modelo_entrenado['muestras_evaluacion']}
        """)


# Ejecutar
if __name__ == "__main__":
    if auth.estoy_autenticado():
        mostrar_app_principal()
    else:
        mostrar_login()