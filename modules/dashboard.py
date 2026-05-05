"""
Módulo de Dashboard - Métricas, KPIs y gráficos interactivos
"""

import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def obtener_ruta_db():
    """Obtiene la ruta de la base de datos"""
    ruta_proyecto = Path(__file__).parent.parent
    return str(ruta_proyecto / "agro_sistema.db")

def obtener_cultivos_usuario(id_usuario):
    """Obtiene los cultivos del usuario autenticado"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute(
        """SELECT id_cultivo, nombre_cultivo, tipo_cultivo, area_hectareas, 
                  estado, rendimiento_real, fecha_siembra, fecha_cosecha_estimada
           FROM cultivos WHERE id_usuario = ? ORDER BY id_cultivo DESC""",
        (id_usuario,)
    )
    
    cultivos = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return cultivos

def obtener_estadisticas_generales(id_usuario):
    """Obtiene estadísticas generales del usuario"""
    conexion = sqlite3.connect(obtener_ruta_db())
    cursor = conexion.cursor()
    
    # Total de cultivos
    cursor.execute("SELECT COUNT(*) FROM cultivos WHERE id_usuario = ?", (id_usuario,))
    total_cultivos = cursor.fetchone()[0]
    
    # Área total
    cursor.execute("SELECT SUM(area_hectareas) FROM cultivos WHERE id_usuario = ?", (id_usuario,))
    area_total = cursor.fetchone()[0] or 0
    
    # Total de sensores
    cursor.execute("SELECT COUNT(*) FROM sensores WHERE id_usuario = ?", (id_usuario,))
    total_sensores = cursor.fetchone()[0]
    
    # Predicciones realizadas
    cursor.execute("SELECT COUNT(*) FROM predicciones WHERE id_usuario = ?", (id_usuario,))
    total_predicciones = cursor.fetchone()[0]
    
    # Rendimiento promedio
    cursor.execute("""SELECT AVG(rendimiento_predicho) FROM predicciones 
                      WHERE id_usuario = ?""", (id_usuario,))
    rendimiento_promedio = cursor.fetchone()[0] or 0
    
    conexion.close()
    
    return {
        'total_cultivos': total_cultivos,
        'area_total': area_total,
        'total_sensores': total_sensores,
        'total_predicciones': total_predicciones,
        'rendimiento_promedio': rendimiento_promedio
    }

def obtener_datos_sensor_ultimo_dia(id_usuario):
    """Obtiene datos de sensores del último día"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT ds.id_dato, ds.valor_temperatura, ds.valor_humedad, 
               ds.valor_ph, ds.valor_precipitacion, ds.valor_radiacion,
               ds.fecha_lectura, c.nombre_cultivo, s.tipo_sensor
        FROM datos_sensor ds
        JOIN cultivos c ON ds.id_cultivo = c.id_cultivo
        JOIN sensores s ON ds.id_sensor = s.id_sensor
        WHERE c.id_usuario = ? 
        AND ds.fecha_lectura >= datetime('now', '-1 day')
        ORDER BY ds.fecha_lectura DESC
        LIMIT 100
    """, (id_usuario,))
    
    datos = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return datos

def obtener_predicciones_recientes(id_usuario):
    """Obtiene predicciones recientes del usuario"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT p.id_prediccion, p.rendimiento_predicho, p.confianza,
               p.fecha_prediccion, c.nombre_cultivo, p.error_mae
        FROM predicciones p
        JOIN cultivos c ON p.id_cultivo = c.id_cultivo
        WHERE p.id_usuario = ?
        ORDER BY p.fecha_prediccion DESC
        LIMIT 10
    """, (id_usuario,))
    
    predicciones = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return predicciones

def mostrar_metricas_kpi(id_usuario):
    """Muestra las métricas KPI principales"""
    stats = obtener_estadisticas_generales(id_usuario)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🌾 Cultivos",
            stats['total_cultivos'],
            "activos"
        )
    
    with col2:
        st.metric(
            "📊 Área (ha)",
            f"{stats['area_total']:.1f}",
            "total"
        )
    
    with col3:
        st.metric(
            "📡 Sensores",
            stats['total_sensores'],
            "instalados"
        )
    
    with col4:
        st.metric(
            "🔮 Predicciones",
            stats['total_predicciones'],
            "realizadas"
        )
    
    with col5:
        st.metric(
            "📈 Rend. Promedio",
            f"{stats['rendimiento_promedio']:.0f}",
            "kg/ha"
        )

def mostrar_grafico_rendimientos(id_usuario):
    """Gráfico de rendimientos predichos por cultivo"""
    predicciones = obtener_predicciones_recientes(id_usuario)
    
    if predicciones:
        df = pd.DataFrame(predicciones)
        df['fecha_prediccion'] = pd.to_datetime(df['fecha_prediccion'])
        
        fig = px.bar(
            df,
            x='nombre_cultivo',
            y='rendimiento_predicho',
            title='Rendimientos Predichos por Cultivo (kg/ha)',
            labels={'rendimiento_predicho': 'Rendimiento (kg/ha)', 'nombre_cultivo': 'Cultivo'},
            color='rendimiento_predicho',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay predicciones disponibles")

def mostrar_grafico_confianza(id_usuario):
    """Gráfico de confianza de predicciones"""
    predicciones = obtener_predicciones_recientes(id_usuario)
    
    if predicciones:
        df = pd.DataFrame(predicciones)
        df['confianza_pct'] = df['confianza'] * 100
        
        fig = px.scatter(
            df,
            x='confianza_pct',
            y='rendimiento_predicho',
            hover_data=['nombre_cultivo', 'error_mae'],
            title='Confianza vs Rendimiento Predicho',
            labels={'confianza_pct': 'Confianza (%)', 'rendimiento_predicho': 'Rendimiento (kg/ha)'},
            size='confianza_pct',
            color='confianza_pct',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay predicciones disponibles")

def mostrar_grafico_temperatura_humedad(id_usuario):
    """Gráfico de temperatura vs humedad de sensores"""
    datos = obtener_datos_sensor_ultimo_dia(id_usuario)
    
    if datos:
        df = pd.DataFrame(datos)
        df = df.dropna(subset=['valor_temperatura', 'valor_humedad'])
        
        if not df.empty:
            fig = px.scatter(
                df,
                x='valor_temperatura',
                y='valor_humedad',
                hover_data=['nombre_cultivo', 'tipo_sensor'],
                title='Temperatura vs Humedad (Últimas 24 horas)',
                labels={'valor_temperatura': 'Temperatura (°C)', 'valor_humedad': 'Humedad (%)'},
                color='nombre_cultivo'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de temperatura y humedad")
    else:
        st.info("No hay datos de sensores disponibles")

def mostrar_estadisticas_descriptivas(id_usuario):
    """Muestra estadísticas descriptivas completas de los datos agrícolas"""
    datos = obtener_datos_sensor_ultimo_dia(id_usuario)
    
    if datos:
        df = pd.DataFrame(datos)
        
        st.subheader("📊 Estadísticas Descriptivas de Sensores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Temperatura (°C)**")
            temp_stats = df['valor_temperatura'].dropna().describe()
            st.dataframe(temp_stats.round(2))
        
        with col2:
            st.write("**Humedad (%)**")
            hum_stats = df['valor_humedad'].dropna().describe()
            st.dataframe(hum_stats.round(2))
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.write("**pH del Suelo**")
            ph_stats = df['valor_ph'].dropna().describe()
            st.dataframe(ph_stats.round(2))
        
        with col4:
            st.write("**Precipitación (mm)**")
            precip_stats = df['valor_precipitacion'].dropna().describe()
            st.dataframe(precip_stats.round(2))
        
        # Tabla completa de últimos datos
        st.subheader("📋 Últimas Lecturas de Sensores")
        df_display = df[['nombre_cultivo', 'tipo_sensor', 'valor_temperatura', 
                         'valor_humedad', 'valor_ph', 'valor_precipitacion', 'fecha_lectura']].copy()
        df_display = df_display.rename(columns={
            'nombre_cultivo': 'Cultivo',
            'tipo_sensor': 'Tipo de Sensor',
            'valor_temperatura': 'Temp (°C)',
            'valor_humedad': 'Humedad (%)',
            'valor_ph': 'pH',
            'valor_precipitacion': 'Precip (mm)',
            'fecha_lectura': 'Fecha'
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos de sensores disponibles para mostrar estadísticas")

def mostrar_tabla_cultivos(id_usuario):
    """Muestra tabla de cultivos del usuario"""
    cultivos = obtener_cultivos_usuario(id_usuario)
    
    if cultivos:
        df = pd.DataFrame(cultivos)
        df_display = df[['nombre_cultivo', 'tipo_cultivo', 'area_hectareas', 
                         'estado', 'rendimiento_real', 'fecha_siembra', 'fecha_cosecha_estimada']].copy()
        df_display = df_display.rename(columns={
            'nombre_cultivo': 'Nombre',
            'tipo_cultivo': 'Tipo',
            'area_hectareas': 'Área (ha)',
            'estado': 'Estado',
            'rendimiento_real': 'Rend. Real (kg/ha)',
            'fecha_siembra': 'Siembra',
            'fecha_cosecha_estimada': 'Cosecha Est.'
        })
        
        st.subheader("🌾 Mis Cultivos")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No tienes cultivos registrados")

def mostrar_distribucion_tipos_cultivos(id_usuario):
    """Gráfico de distribución de tipos de cultivos"""
    cultivos = obtener_cultivos_usuario(id_usuario)
    
    if cultivos:
        df = pd.DataFrame(cultivos)
        dist = df['tipo_cultivo'].value_counts()
        
        fig = px.pie(
            values=dist.values,
            names=dist.index,
            title='Distribución de Tipos de Cultivos',
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay cultivos para mostrar distribución")
