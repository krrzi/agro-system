"""
Módulo de Predicción de Rendimientos
Utiliza el modelo ensemble learning (Random Forest + Gradient Boosting)
"""

import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from models.ensemble_model import ModeloEnsemble

def obtener_ruta_db():
    """Obtiene la ruta de la base de datos"""
    ruta_proyecto = Path(__file__).parent.parent
    return str(ruta_proyecto / "agro_sistema.db")

def obtener_sensores_cultivo(id_cultivo):
    """Obtiene sensores de un cultivo"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute(
        """SELECT id_sensor, tipo_sensor, ubicacion 
           FROM sensores WHERE id_cultivo = ? AND activo = 1""",
        (id_cultivo,)
    )
    
    sensores = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return sensores

def obtener_ultimos_datos_sensor(id_cultivo):
    """Obtiene los últimos datos de sensores de un cultivo"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT 
            AVG(valor_temperatura) as temp_promedio,
            AVG(valor_humedad) as humedad_promedio,
            AVG(valor_ph) as ph_promedio,
            AVG(valor_precipitacion) as precip_promedio,
            AVG(valor_radiacion) as radiacion_promedio
        FROM datos_sensor 
        WHERE id_cultivo = ? 
            AND valor_temperatura IS NOT NULL
            AND valor_humedad IS NOT NULL
        ORDER BY fecha_lectura DESC 
        LIMIT 100
    """, (id_cultivo,))
    
    resultado = cursor.fetchone()
    conexion.close()
    
    if resultado:
        return dict(resultado)
    return None

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

def guardar_prediccion(id_cultivo, id_usuario, rendimiento_predicho, confianza, error_mae):
    """Guarda la predicción en la base de datos"""
    conexion = sqlite3.connect(obtener_ruta_db())
    cursor = conexion.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO predicciones 
            (id_cultivo, id_usuario, rendimiento_predicho, confianza, modelo_usado, error_mae)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_cultivo, id_usuario, rendimiento_predicho, confianza, 'Ensemble', error_mae))
        
        conexion.commit()
        id_prediccion = cursor.lastrowid
        conexion.close()
        return id_prediccion
    except Exception as e:
        conexion.close()
        return None

def obtener_historial_predicciones(id_cultivo, limite=10):
    """Obtiene historial de predicciones de un cultivo"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id_prediccion, rendimiento_predicho, confianza, 
               fecha_prediccion, error_mae
        FROM predicciones 
        WHERE id_cultivo = ?
        ORDER BY fecha_prediccion DESC 
        LIMIT ?
    """, (id_cultivo, limite))
    
    predicciones = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return predicciones

def realizar_prediccion(id_cultivo, id_usuario, modelo_ensemble):
    """Realiza predicción para un cultivo"""
    # Obtener datos del cultivo
    cultivo_info = obtener_cultivo_info(id_cultivo)
    area_hectareas = cultivo_info['area_hectareas']
    
    # Obtener últimos datos de sensores
    datos_sensor = obtener_ultimos_datos_sensor(id_cultivo)
    
    if datos_sensor is None:
        return None, "No hay datos de sensores disponibles para este cultivo"
    
    # Usar valores promedio o valores por defecto
    temperatura = datos_sensor['temp_promedio'] or 24.0
    humedad = datos_sensor['humedad_promedio'] or 65.0
    ph = datos_sensor['ph_promedio'] or 6.8
    precipitacion = datos_sensor['precip_promedio'] or 3.0
    radiacion = datos_sensor['radiacion_promedio'] or 19.0
    
    # Realizar predicción con el modelo
    prediccion = modelo_ensemble.predecir(
        temperatura, humedad, ph, precipitacion, radiacion, area_hectareas
    )
    
    # Guardar en BD
    id_prediccion = guardar_prediccion(
        id_cultivo, id_usuario,
        prediccion['rendimiento_predicho'],
        prediccion['confianza'],
        prediccion['error_mae']
    )
    
    return prediccion, id_prediccion

def mostrar_panel_prediccion(id_cultivo, id_usuario, modelo_ensemble):
    """Muestra el panel de predicción de rendimientos"""
    st.subheader("🔮 Predicción de Rendimientos")
    
    cultivo_info = obtener_cultivo_info(id_cultivo)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Cultivo:** {cultivo_info['nombre_cultivo']}")
        st.write(f"**Tipo:** {cultivo_info['tipo_cultivo']}")
        st.write(f"**Área:** {cultivo_info['area_hectareas']:.1f} ha")
    
    with col2:
        st.write(f"**Estado:** {cultivo_info['estado']}")
    
    st.divider()
    
    # Datos de sensores
    datos_sensor = obtener_ultimos_datos_sensor(id_cultivo)
    
    if datos_sensor is None:
        st.warning("⚠ No hay datos de sensores para realizar predicción")
        return
    
    st.write("**📊 Datos de Sensores Actuales:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temp = datos_sensor['temp_promedio'] or 24.0
        st.metric("Temperatura", f"{temp:.1f}°C")
    
    with col2:
        hum = datos_sensor['humedad_promedio'] or 65.0
        st.metric("Humedad", f"{hum:.1f}%")
    
    with col3:
        ph = datos_sensor['ph_promedio'] or 6.8
        st.metric("pH", f"{ph:.2f}")
    
    st.divider()
    
    # Botón para realizar predicción
    if st.button("🚀 Realizar Predicción", use_container_width=True, key=f"predict_{id_cultivo}"):
        prediccion, id_prediccion = realizar_prediccion(id_cultivo, id_usuario, modelo_ensemble)
        
        if prediccion:
            # Mostrar resultados
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "📈 Rendimiento Predicho",
                    f"{prediccion['rendimiento_predicho']:.0f} kg/ha"
                )
            
            with col2:
                confianza_pct = prediccion['confianza'] * 100
                color = '🟢' if confianza_pct > 85 else '🟡' if confianza_pct > 70 else '🔴'
                st.metric(
                    f"{color} Confianza",
                    f"{confianza_pct:.1f}%"
                )
            
            with col3:
                st.metric(
                    "📊 Error MAE",
                    f"{prediccion['error_mae']:.0f}",
                    "kg/ha"
                )
            
            st.success(f"✓ Predicción guardada con ID: {id_prediccion}")
        else:
            st.error("No fue posible realizar la predicción")
    
    st.divider()
    
    # Historial de predicciones
    st.subheader("📋 Historial de Predicciones")
    historial = obtener_historial_predicciones(id_cultivo)
    
    if historial:
        df_historial = pd.DataFrame(historial)
        df_historial['fecha_prediccion'] = pd.to_datetime(df_historial['fecha_prediccion'])
        df_historial['confianza_pct'] = (df_historial['confianza'] * 100).round(1)
        
        # Gráfico de evolución de predicciones
        fig = px.line(
            df_historial.sort_values('fecha_prediccion'),
            x='fecha_prediccion',
            y='rendimiento_predicho',
            title='Evolución de Rendimientos Predichos',
            markers=True,
            labels={'rendimiento_predicho': 'Rendimiento (kg/ha)', 'fecha_prediccion': 'Fecha'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de predicciones
        df_display = df_historial[['fecha_prediccion', 'rendimiento_predicho', 'confianza_pct', 'error_mae']].copy()
        df_display = df_display.rename(columns={
            'fecha_prediccion': 'Fecha',
            'rendimiento_predicho': 'Rendimiento (kg/ha)',
            'confianza_pct': 'Confianza (%)',
            'error_mae': 'Error MAE'
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No hay predicciones realizadas aún para este cultivo")

def mostrar_importancia_features(modelo_ensemble):
    """Muestra la importancia de características del modelo"""
    importancia = modelo_ensemble.obtener_importancia_features()
    
    if importancia:
        df = pd.DataFrame({
            'Característica': importancia['features'],
            'Importancia': importancia['importancias']
        }).sort_values('Importancia', ascending=False)
        
        fig = px.bar(
            df,
            x='Importancia',
            y='Característica',
            title='Importancia de Características del Modelo',
            labels={'Importancia': 'Importancia Relativa', 'Característica': 'Característica'},
            orientation='h'
        )
        
        st.plotly_chart(fig, use_container_width=True)
