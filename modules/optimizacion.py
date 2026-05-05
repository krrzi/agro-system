"""
Módulo de Optimización de Recursos Hídricos
Basado en predicciones del modelo ML
"""

import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def obtener_ruta_db():
    """Obtiene la ruta de la base de datos"""
    ruta_proyecto = Path(__file__).parent.parent
    return str(ruta_proyecto / "agro_sistema.db")

def obtener_cultivo_info(id_cultivo):
    """Obtiene información del cultivo"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute(
        """SELECT nombre_cultivo, tipo_cultivo, area_hectareas, estado 
           FROM cultivos WHERE id_cultivo = ?""",
        (id_cultivo,)
    )
    
    cultivo = cursor.fetchone()
    conexion.close()
    
    return dict(cultivo) if cultivo else None

def obtener_prediccion_reciente(id_cultivo):
    """Obtiene la predicción más reciente de un cultivo"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id_prediccion, rendimiento_predicho, confianza
        FROM predicciones 
        WHERE id_cultivo = ?
        ORDER BY fecha_prediccion DESC 
        LIMIT 1
    """, (id_cultivo,))
    
    prediccion = cursor.fetchone()
    conexion.close()
    
    return dict(prediccion) if prediccion else None

def obtener_humedad_promedio(id_cultivo):
    """Obtiene la humedad promedio del cultivo"""
    conexion = sqlite3.connect(obtener_ruta_db())
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT AVG(valor_humedad) as humedad_promedio
        FROM datos_sensor 
        WHERE id_cultivo = ? 
        ORDER BY fecha_lectura DESC 
        LIMIT 100
    """, (id_cultivo,))
    
    resultado = cursor.fetchone()
    conexion.close()
    
    return resultado[0] if resultado[0] else 65.0

# Tablas de referencia de requerimientos de agua por cultivo (mm/mes)
REQUERIMIENTOS_AGUA_POR_CULTIVO = {
    'Maíz': {'optimo': 120, 'minimo': 80, 'maximo': 160},
    'Trigo': {'optimo': 100, 'minimo': 60, 'maximo': 140},
    'Soja': {'optimo': 110, 'minimo': 70, 'maximo': 150},
    'Arroz': {'optimo': 150, 'minimo': 100, 'maximo': 200},
    'Cebada': {'optimo': 90, 'minimo': 50, 'maximo': 130},
}

def calcular_agua_recomendada(tipo_cultivo, area_hectareas, rendimiento_predicho, humedad_actual):
    """Calcula el agua recomendada basada en predicciones"""
    
    # Obtener requerimientos base
    requerimientos = REQUERIMIENTOS_AGUA_POR_CULTIVO.get(tipo_cultivo, {'optimo': 110, 'minimo': 70, 'maximo': 150})
    agua_optima_mm = requerimientos['optimo']
    
    # Ajuste por rendimiento predicho
    rendimiento_base = 8000  # kg/ha base
    factor_rendimiento = rendimiento_predicho / rendimiento_base
    
    # Ajuste por humedad actual
    humedad_optima = 65.0  # Porcentaje óptimo
    factor_humedad = 1 - ((humedad_actual - humedad_optima) / 100)
    
    # Calcular agua recomendada
    agua_recomendada_mm = agua_optima_mm * factor_rendimiento * (1 + factor_humedad * 0.3)
    
    # Convertir mm a m³/ha
    agua_recomendada_m3_ha = agua_recomendada_mm * 10  # 1 mm = 10 m³/ha
    
    # Agua total en m³
    agua_recomendada_total = agua_recomendada_m3_ha * area_hectareas
    
    return {
        'agua_recomendada_mm': agua_recomendada_mm,
        'agua_recomendada_m3_ha': agua_recomendada_m3_ha,
        'agua_recomendada_total_m3': agua_recomendada_total
    }

def estimar_agua_actual(humedad_actual, tipo_cultivo, area_hectareas):
    """Estima el agua actual aplicada basada en humedad"""
    
    humedad_optima = 65.0
    desviacion = abs(humedad_actual - humedad_optima)
    
    # Si la humedad es baja, se asume riego insuficiente
    if humedad_actual < humedad_optima:
        factor = 0.7  # 70% de lo óptimo
    else:
        factor = 1.1  # 110% de lo óptimo
    
    requerimientos = REQUERIMIENTOS_AGUA_POR_CULTIVO.get(tipo_cultivo, {'optimo': 110})
    agua_actual_mm = requerimientos['optimo'] * factor
    agua_actual_m3_ha = agua_actual_mm * 10
    agua_actual_total = agua_actual_m3_ha * area_hectareas
    
    return {
        'agua_actual_mm': agua_actual_mm,
        'agua_actual_m3_ha': agua_actual_m3_ha,
        'agua_actual_total_m3': agua_actual_total
    }

def guardar_optimizacion(id_cultivo, id_prediccion, agua_recomendada, agua_actual, 
                        ahorro_potencial, recomendacion):
    """Guarda el análisis de optimización en BD"""
    conexion = sqlite3.connect(obtener_ruta_db())
    cursor = conexion.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO optimizacion 
            (id_cultivo, id_prediccion, agua_recomendada, agua_actual, ahorro_potencial, recomendacion)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_cultivo, id_prediccion, agua_recomendada, agua_actual, ahorro_potencial, recomendacion))
        
        conexion.commit()
        id_optimizacion = cursor.lastrowid
        conexion.close()
        return id_optimizacion
    except Exception as e:
        conexion.close()
        print(f"Error al guardar optimización: {e}")
        return None

def obtener_historial_optimizaciones(id_cultivo, limite=10):
    """Obtiene historial de optimizaciones"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id_optimizacion, agua_recomendada, agua_actual, 
               ahorro_potencial, recomendacion, fecha_analisis
        FROM optimizacion 
        WHERE id_cultivo = ?
        ORDER BY fecha_analisis DESC 
        LIMIT ?
    """, (id_cultivo, limite))
    
    optimizaciones = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return optimizaciones

def generar_recomendacion_texto(agua_recomendada, agua_actual, ahorro_potencial, tipo_cultivo):
    """Genera recomendación en texto legible"""
    
    diferencia = agua_actual - agua_recomendada
    
    if diferencia > 50:
        recomendacion = f"⚠️ REDUCIR RIEGO: El cultivo de {tipo_cultivo} está recibiendo demasiada agua ({agua_actual:.0f} m³/ha). "
        recomendacion += f"Se recomienda reducir a {agua_recomendada:.0f} m³/ha para ahorrar {ahorro_potencial:.1f}% de agua sin afectar rendimiento."
    elif diferencia < -50:
        recomendacion = f"🔼 INCREMENTAR RIEGO: El cultivo de {tipo_cultivo} necesita más agua ({agua_recomendada:.0f} m³/ha). "
        recomendacion += f"Incrementar riego a {agua_recomendada:.0f} m³/ha para optimizar rendimiento."
    else:
        recomendacion = f"✅ RIEGO ÓPTIMO: El cultivo de {tipo_cultivo} está recibiendo cantidad adecuada de agua. "
        recomendacion += f"Mantener riego actual en {agua_actual:.0f} m³/ha."
    
    return recomendacion

def mostrar_panel_optimizacion(id_cultivo, id_usuario):
    """Muestra el panel de optimización hídrica"""
    st.subheader("💧 Optimización de Recursos Hídricos")
    
    cultivo_info = obtener_cultivo_info(id_cultivo)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Cultivo:** {cultivo_info['nombre_cultivo']}")
        st.write(f"**Tipo:** {cultivo_info['tipo_cultivo']}")
    
    with col2:
        st.write(f"**Área:** {cultivo_info['area_hectareas']:.1f} ha")
        st.write(f"**Estado:** {cultivo_info['estado']}")
    
    st.divider()
    
    # Obtener predicción reciente
    prediccion = obtener_prediccion_reciente(id_cultivo)
    
    if prediccion is None:
        st.warning("⚠ No hay predicciones disponibles. Realiza una predicción primero.")
        return
    
    # Obtener humedad actual
    humedad_actual = obtener_humedad_promedio(id_cultivo)
    
    # Calcular agua recomendada
    calc_recomendado = calcular_agua_recomendada(
        cultivo_info['tipo_cultivo'],
        cultivo_info['area_hectareas'],
        prediccion['rendimiento_predicho'],
        humedad_actual
    )
    
    # Estimar agua actual
    calc_actual = estimar_agua_actual(
        humedad_actual,
        cultivo_info['tipo_cultivo'],
        cultivo_info['area_hectareas']
    )
    
    agua_recomendada = calc_recomendado['agua_recomendada_m3_ha']
    agua_actual = calc_actual['agua_actual_m3_ha']
    
    # Calcular ahorro potencial
    ahorro_potencial = abs((agua_actual - agua_recomendada) / agua_actual * 100) if agua_actual > 0 else 0
    
    # Generar recomendación
    recomendacion = generar_recomendacion_texto(
        agua_recomendada, agua_actual, ahorro_potencial, cultivo_info['tipo_cultivo']
    )
    
    # Mostrar métricas
    st.write("**📊 Análisis de Agua:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💧 Agua Actual", f"{agua_actual:.1f}", "m³/ha")
    
    with col2:
        st.metric("💧 Agua Recomendada", f"{agua_recomendada:.1f}", "m³/ha")
    
    with col3:
        ahorro_color = "🟢" if ahorro_potencial > 0 else "🔵"
        st.metric(f"{ahorro_color} Ahorro Potencial", f"{ahorro_potencial:.1f}%")
    
    st.divider()
    
    # Mostrar recomendación
    st.info(recomendacion)
    
    st.divider()
    
    # Botón para guardar optimización
    if st.button("💾 Guardar Análisis de Optimización", use_container_width=True, key=f"opt_{id_cultivo}"):
        id_opt = guardar_optimizacion(
            id_cultivo,
            prediccion['id_prediccion'],
            agua_recomendada,
            agua_actual,
            ahorro_potencial,
            recomendacion
        )
        
        if id_opt:
            st.success(f"✓ Optimización guardada con ID: {id_opt}")
        else:
            st.error("Error al guardar la optimización")
    
    st.divider()
    
    # Gráfico comparativo
    col1, col2 = st.columns(2)
    
    with col1:
        datos_agua = pd.DataFrame({
            'Tipo': ['Actual', 'Recomendada'],
            'Agua (m³/ha)': [agua_actual, agua_recomendada]
        })
        
        fig = px.bar(
            datos_agua,
            x='Tipo',
            y='Agua (m³/ha)',
            title='Comparación de Agua: Actual vs Recomendada',
            color='Tipo',
            color_discrete_map={'Actual': '#FF6B6B', 'Recomendada': '#4ECDC4'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gauge de eficiencia
        eficiencia = (agua_recomendada / agua_actual) * 100 if agua_actual > 0 else 0
        eficiencia = min(eficiencia, 100)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=eficiencia,
            title="Eficiencia Hídrica",
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "#FF6B6B"},
                    {'range': [50, 80], 'color': "#FFD93D"},
                    {'range': [80, 100], 'color': "#6BCB77"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Historial de optimizaciones
    st.subheader("📋 Historial de Optimizaciones")
    historial = obtener_historial_optimizaciones(id_cultivo)
    
    if historial:
        df_historial = pd.DataFrame(historial)
        df_historial['fecha_analisis'] = pd.to_datetime(df_historial['fecha_analisis'])
        
        # Gráfico de evolución
        fig = px.line(
            df_historial.sort_values('fecha_analisis'),
            x='fecha_analisis',
            y=['agua_actual', 'agua_recomendada'],
            title='Evolución del Consumo de Agua',
            markers=True,
            labels={'value': 'Agua (m³/ha)', 'fecha_analisis': 'Fecha', 'variable': 'Tipo'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla
        df_display = df_historial[['fecha_analisis', 'agua_actual', 'agua_recomendada', 'ahorro_potencial']].copy()
        df_display = df_display.rename(columns={
            'fecha_analisis': 'Fecha',
            'agua_actual': 'Agua Actual (m³/ha)',
            'agua_recomendada': 'Agua Recomendada (m³/ha)',
            'ahorro_potencial': 'Ahorro (%)'
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No hay análisis de optimización guardados aún")
