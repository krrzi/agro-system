"""
Módulo de Generación de Reportes en PDF
Reportes operacional y de gestión
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import io
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

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
        """SELECT nombre_cultivo, tipo_cultivo, area_hectareas, estado, 
                  rendimiento_real, fecha_siembra, fecha_cosecha_estimada
           FROM cultivos WHERE id_cultivo = ?""",
        (id_cultivo,)
    )
    
    cultivo = cursor.fetchone()
    conexion.close()
    return dict(cultivo) if cultivo else None

def obtener_usuario_info(id_usuario):
    """Obtiene información del usuario"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute(
        """SELECT nombre, email, fecha_creacion FROM usuarios WHERE id_usuario = ?""",
        (id_usuario,)
    )
    
    usuario = cursor.fetchone()
    conexion.close()
    return dict(usuario) if usuario else None

def obtener_datos_sensores_periodo(id_cultivo, dias=7):
    """Obtiene datos de sensores del último período"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute(f"""
        SELECT 
            valor_temperatura,
            valor_humedad,
            valor_ph,
            valor_precipitacion,
            valor_radiacion,
            fecha_lectura
        FROM datos_sensor 
        WHERE id_cultivo = ?
            AND fecha_lectura >= datetime('now', '-{dias} days')
        ORDER BY fecha_lectura DESC
    """, (id_cultivo,))
    
    datos = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return datos

def obtener_predicciones_periodo(id_cultivo, dias=30):
    """Obtiene predicciones recientes"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute(f"""
        SELECT 
            rendimiento_predicho,
            confianza,
            fecha_prediccion,
            error_mae
        FROM predicciones 
        WHERE id_cultivo = ?
            AND fecha_prediccion >= datetime('now', '-{dias} days')
        ORDER BY fecha_prediccion DESC
    """, (id_cultivo,))
    
    predicciones = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return predicciones

def obtener_optimizaciones_periodo(id_cultivo, dias=30):
    """Obtiene análisis de optimización reciente"""
    conexion = sqlite3.connect(obtener_ruta_db())
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute(f"""
        SELECT 
            agua_recomendada,
            agua_actual,
            ahorro_potencial,
            recomendacion,
            fecha_analisis
        FROM optimizacion 
        WHERE id_cultivo = ?
            AND fecha_analisis >= datetime('now', '-{dias} days')
        ORDER BY fecha_analisis DESC
    """, (id_cultivo,))
    
    optimizaciones = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return optimizaciones

def crear_reporte_operacional(id_cultivo, id_usuario, nombre_archivo=None):
    """Genera reporte operacional (datos diarios/semanales)"""
    
    cultivo_info = obtener_cultivo_info(id_cultivo)
    usuario_info = obtener_usuario_info(id_usuario)
    datos_sensores = obtener_datos_sensores_periodo(id_cultivo, dias=7)
    predicciones = obtener_predicciones_periodo(id_cultivo, dias=7)
    
    if nombre_archivo is None:
        fecha_hoy = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        nombre_archivo = f"reporte_operacional_{cultivo_info['nombre_cultivo']}_{fecha_hoy}.pdf"
    
    # Crear PDF
    ruta_proyecto = Path(__file__).parent.parent
    ruta_reporte = ruta_proyecto / "reports" / nombre_archivo
    
    doc = SimpleDocTemplate(
        str(ruta_reporte),
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1B4D3E'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'Encabezado',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2D5A3D'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    # Contenido
    contenido = []
    
    # Título
    contenido.append(Paragraph("📋 REPORTE OPERACIONAL", titulo_style))
    contenido.append(Spacer(1, 0.2*inch))
    
    # Información del cultivo
    contenido.append(Paragraph("Información del Cultivo", heading_style))
    datos_cultivo = [
        ['Cultivo:', cultivo_info['nombre_cultivo']],
        ['Tipo:', cultivo_info['tipo_cultivo']],
        ['Área:', f"{cultivo_info['area_hectareas']:.1f} ha"],
        ['Estado:', cultivo_info['estado']],
        ['Siembra:', cultivo_info['fecha_siembra']],
        ['Cosecha Estimada:', cultivo_info['fecha_cosecha_estimada']],
    ]
    tabla_cultivo = Table(datos_cultivo, colWidths=[2*inch, 4*inch])
    tabla_cultivo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    contenido.append(tabla_cultivo)
    contenido.append(Spacer(1, 0.3*inch))
    
    # Datos de sensores
    if datos_sensores:
        contenido.append(Paragraph("Datos de Sensores (Últimos 7 días)", heading_style))
        
        datos_tabla = [['Fecha', 'Temp (°C)', 'Humedad (%)', 'pH', 'Precip (mm)']]
        for dato in datos_sensores[:10]:  # Últimos 10 registros
            datos_tabla.append([
                dato['fecha_lectura'][:10] if dato['fecha_lectura'] else '-',
                f"{dato['valor_temperatura']:.1f}" if dato['valor_temperatura'] else '-',
                f"{dato['valor_humedad']:.1f}" if dato['valor_humedad'] else '-',
                f"{dato['valor_ph']:.2f}" if dato['valor_ph'] else '-',
                f"{dato['valor_precipitacion']:.1f}" if dato['valor_precipitacion'] else '-',
            ])
        
        tabla_sensores = Table(datos_tabla, colWidths=[1.5*inch, 1*inch, 1.2*inch, 0.8*inch, 1*inch])
        tabla_sensores.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5A3D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8F5')])
        ]))
        contenido.append(tabla_sensores)
        contenido.append(Spacer(1, 0.3*inch))
    
    # Predicciones
    if predicciones:
        contenido.append(Paragraph("Predicciones Realizadas", heading_style))
        
        datos_pred = [['Fecha', 'Rendimiento (kg/ha)', 'Confianza (%)', 'Error MAE']]
        for pred in predicciones:
            datos_pred.append([
                pred['fecha_prediccion'][:10] if pred['fecha_prediccion'] else '-',
                f"{pred['rendimiento_predicho']:.0f}",
                f"{pred['confianza']*100:.1f}%",
                f"{pred['error_mae']:.0f}" if pred['error_mae'] else '-'
            ])
        
        tabla_pred = Table(datos_pred, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        tabla_pred.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5A3D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8F5')])
        ]))
        contenido.append(tabla_pred)
    
    # Pie de página
    contenido.append(Spacer(1, 0.5*inch))
    fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    contenido.append(Paragraph(
        f"<font size=8>Reporte generado: {fecha_reporte} | Usuario: {usuario_info['nombre']}</font>",
        styles['Normal']
    ))
    
    # Construir PDF
    doc.build(contenido)
    
    return str(ruta_reporte)

def crear_reporte_gestion(id_cultivo, id_usuario, nombre_archivo=None):
    """Genera reporte de gestión (resumen ejecutivo con gráficos y KPIs)"""
    
    cultivo_info = obtener_cultivo_info(id_cultivo)
    usuario_info = obtener_usuario_info(id_usuario)
    predicciones = obtener_predicciones_periodo(id_cultivo, dias=30)
    optimizaciones = obtener_optimizaciones_periodo(id_cultivo, dias=30)
    
    if nombre_archivo is None:
        fecha_hoy = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        nombre_archivo = f"reporte_gestion_{cultivo_info['nombre_cultivo']}_{fecha_hoy}.pdf"
    
    ruta_proyecto = Path(__file__).parent.parent
    ruta_reporte = ruta_proyecto / "reports" / nombre_archivo
    
    doc = SimpleDocTemplate(
        str(ruta_reporte),
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1B4D3E'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'Encabezado',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2D5A3D'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    # Contenido
    contenido = []
    
    # Título
    contenido.append(Paragraph("📊 REPORTE DE GESTIÓN", titulo_style))
    contenido.append(Paragraph("Resumen Ejecutivo con KPIs y Análisis", styles['Normal']))
    contenido.append(Spacer(1, 0.3*inch))
    
    # KPIs principales
    contenido.append(Paragraph("KPIs Principales", heading_style))
    
    kpi_data = [['Métrica', 'Valor']]
    kpi_data.append(['Cultivo', cultivo_info['nombre_cultivo']])
    kpi_data.append(['Área Total', f"{cultivo_info['area_hectareas']:.1f} ha"])
    kpi_data.append(['Estado', cultivo_info['estado']])
    
    if predicciones:
        rendimiento_promedio = sum(p['rendimiento_predicho'] for p in predicciones) / len(predicciones)
        confianza_promedio = sum(p['confianza'] for p in predicciones) / len(predicciones)
        kpi_data.append(['Rendimiento Promedio', f"{rendimiento_promedio:.0f} kg/ha"])
        kpi_data.append(['Confianza Promedio', f"{confianza_promedio*100:.1f}%"])
        kpi_data.append(['Predicciones Realizadas', str(len(predicciones))])
    
    if optimizaciones:
        ahorro_promedio = sum(o['ahorro_potencial'] for o in optimizaciones) / len(optimizaciones)
        kpi_data.append(['Ahorro Potencial Promedio', f"{ahorro_promedio:.1f}%"])
        kpi_data.append(['Análisis de Optimización', str(len(optimizaciones))])
    
    tabla_kpi = Table(kpi_data, colWidths=[3*inch, 3*inch])
    tabla_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B4D3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8F5')])
    ]))
    contenido.append(tabla_kpi)
    contenido.append(Spacer(1, 0.3*inch))
    
    # Análisis de predicciones
    if predicciones:
        contenido.append(Paragraph("Análisis de Predicciones", heading_style))
        
        pred_text = f"""
        Se han realizado <b>{len(predicciones)}</b> predicciones en el período analizado. 
        El rendimiento predicho promedio es de <b>{rendimiento_promedio:.0f} kg/ha</b> con 
        una confianza promedio de <b>{confianza_promedio*100:.1f}%</b>. 
        El margen de error promedio (MAE) es de <b>{sum(p['error_mae'] for p in predicciones if p['error_mae'])/len([p for p in predicciones if p['error_mae']]):.0f} kg/ha</b>.
        """
        
        contenido.append(Paragraph(pred_text, styles['Normal']))
        contenido.append(Spacer(1, 0.2*inch))
    
    # Análisis de optimización
    if optimizaciones:
        contenido.append(Paragraph("Análisis de Optimización Hídrica", heading_style))
        
        opt = optimizaciones[0]  # Más reciente
        opt_text = f"""
        Según el análisis más reciente, el cultivo requiere <b>{opt['agua_recomendada']:.1f} m³/ha</b> de agua,
        mientras que actualmente recibe <b>{opt['agua_actual']:.1f} m³/ha</b>. 
        Esto representa un <b>ahorro potencial del {opt['ahorro_potencial']:.1f}%</b> sin afectar el rendimiento.
        """
        
        contenido.append(Paragraph(opt_text, styles['Normal']))
        contenido.append(Spacer(1, 0.2*inch))
        
        contenido.append(Paragraph("Recomendación:", ParagraphStyle('SubHeading', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold')))
        contenido.append(Paragraph(opt['recomendacion'], styles['Normal']))
    
    # Conclusiones
    contenido.append(Spacer(1, 0.3*inch))
    contenido.append(Paragraph("Conclusiones", heading_style))
    
    conclusiones = """
    El sistema de información agrícola de precisión ha proporcionado un análisis integral del cultivo.
    Se recomienda continuar monitoreando las métricas indicadas y realizar predicciones periódicamente
    para optimizar el rendimiento y el uso de recursos naturales.
    """
    
    contenido.append(Paragraph(conclusiones, styles['Normal']))
    
    # Pie de página
    contenido.append(Spacer(1, 0.5*inch))
    fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    contenido.append(Paragraph(
        f"<font size=8>Reporte generado: {fecha_reporte} | Usuario: {usuario_info['nombre']} | Email: {usuario_info['email']}</font>",
        styles['Normal']
    ))
    
    # Construir PDF
    doc.build(contenido)
    
    return str(ruta_reporte)

def guardar_reporte_en_bd(id_usuario, id_cultivo, tipo_reporte, nombre_archivo, ruta_archivo):
    """Guarda registro del reporte en BD"""
    conexion = sqlite3.connect(obtener_ruta_db())
    cursor = conexion.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO reportes (id_usuario, id_cultivo, tipo_reporte, nombre_archivo, ruta_archivo)
            VALUES (?, ?, ?, ?, ?)
        """, (id_usuario, id_cultivo, tipo_reporte, nombre_archivo, ruta_archivo))
        
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al guardar reporte en BD: {e}")
        conexion.close()
        return False
