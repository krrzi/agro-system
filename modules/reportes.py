"""
Módulo de Generación de Reportes en PDF
Genera PDFs en memoria (compatible con Streamlit Cloud)
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import io
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

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
        SELECT valor_temperatura, valor_humedad, valor_ph,
               valor_precipitacion, valor_radiacion, fecha_lectura
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
        SELECT rendimiento_predicho, confianza, fecha_prediccion, error_mae
        FROM predicciones
        WHERE id_cultivo = ?
        ORDER BY fecha_prediccion DESC
        LIMIT 10
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
        SELECT agua_recomendada, agua_actual, ahorro_potencial,
               recomendacion, fecha_analisis
        FROM optimizacion
        WHERE id_cultivo = ?
        ORDER BY fecha_analisis DESC
        LIMIT 5
    """, (id_cultivo,))
    optimizaciones = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return optimizaciones

def _estilos():
    """Retorna estilos comunes para los reportes"""
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1B4D3E'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'Encabezado',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#2D5A3D'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    return styles, titulo_style, heading_style

def crear_reporte_operacional(id_cultivo, id_usuario):
    """
    Genera reporte operacional en memoria y retorna bytes del PDF.
    """
    cultivo_info = obtener_cultivo_info(id_cultivo)
    usuario_info = obtener_usuario_info(id_usuario)
    datos_sensores = obtener_datos_sensores_periodo(id_cultivo, dias=7)
    predicciones = obtener_predicciones_periodo(id_cultivo, dias=7)

    if not cultivo_info:
        return None

    # Generar PDF en memoria
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles, titulo_style, heading_style = _estilos()
    contenido = []

    # Título
    contenido.append(Paragraph("REPORTE OPERACIONAL", titulo_style))
    contenido.append(Paragraph("Sistema Agricola de Precision", styles['Normal']))
    contenido.append(Spacer(1, 0.2*inch))

    # Información del cultivo
    contenido.append(Paragraph("Informacion del Cultivo", heading_style))
    datos_cultivo = [
        ['Cultivo:', cultivo_info['nombre_cultivo']],
        ['Tipo:', cultivo_info['tipo_cultivo']],
        ['Area:', f"{cultivo_info['area_hectareas']:.1f} ha"],
        ['Estado:', cultivo_info['estado']],
        ['Siembra:', str(cultivo_info['fecha_siembra'])],
        ['Cosecha Estimada:', str(cultivo_info['fecha_cosecha_estimada'])],
    ]
    tabla_cultivo = Table(datos_cultivo, colWidths=[2*inch, 4*inch])
    tabla_cultivo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    contenido.append(tabla_cultivo)
    contenido.append(Spacer(1, 0.3*inch))

    # Datos de sensores
    if datos_sensores:
        contenido.append(Paragraph("Datos de Sensores (Ultimos 7 dias)", heading_style))
        datos_tabla = [['Fecha', 'Temp (C)', 'Humedad (%)', 'pH', 'Precip (mm)']]
        for dato in datos_sensores[:10]:
            datos_tabla.append([
                str(dato['fecha_lectura'])[:10] if dato['fecha_lectura'] else '-',
                f"{dato['valor_temperatura']:.1f}" if dato['valor_temperatura'] else '-',
                f"{dato['valor_humedad']:.1f}" if dato['valor_humedad'] else '-',
                f"{dato['valor_ph']:.2f}" if dato['valor_ph'] else '-',
                f"{dato['valor_precipitacion']:.1f}" if dato['valor_precipitacion'] else '-',
            ])
        tabla_sensores = Table(datos_tabla, colWidths=[1.5*inch, 1.1*inch, 1.2*inch, 0.9*inch, 1.1*inch])
        tabla_sensores.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5A3D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        contenido.append(tabla_sensores)
        contenido.append(Spacer(1, 0.3*inch))

    # Predicciones
    if predicciones:
        contenido.append(Paragraph("Predicciones Recientes", heading_style))
        datos_pred = [['Fecha', 'Rendimiento (t/ha)', 'Confianza (%)']]
        for pred in predicciones:
            datos_pred.append([
                str(pred['fecha_prediccion'])[:10] if pred['fecha_prediccion'] else '-',
                f"{pred['rendimiento_predicho']:.2f}",
                f"{pred['confianza']*100:.1f}%",
            ])
        tabla_pred = Table(datos_pred, colWidths=[2*inch, 2*inch, 2*inch])
        tabla_pred.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5A3D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        contenido.append(tabla_pred)

    # Pie de página
    contenido.append(Spacer(1, 0.4*inch))
    fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nombre_usuario = usuario_info['nombre'] if usuario_info else 'N/A'
    contenido.append(Paragraph(
        f"Reporte generado: {fecha_reporte} | Usuario: {nombre_usuario}",
        styles['Normal']
    ))

    doc.build(contenido)
    buffer.seek(0)
    return buffer.getvalue()


def crear_reporte_gestion(id_cultivo, id_usuario):
    """
    Genera reporte de gestión en memoria y retorna bytes del PDF.
    """
    cultivo_info = obtener_cultivo_info(id_cultivo)
    usuario_info = obtener_usuario_info(id_usuario)
    predicciones = obtener_predicciones_periodo(id_cultivo, dias=30)
    optimizaciones = obtener_optimizaciones_periodo(id_cultivo, dias=30)

    if not cultivo_info:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles, titulo_style, heading_style = _estilos()
    contenido = []

    # Título
    contenido.append(Paragraph("REPORTE DE GESTION", titulo_style))
    contenido.append(Paragraph("Resumen Ejecutivo con KPIs y Analisis", styles['Normal']))
    contenido.append(Spacer(1, 0.3*inch))

    # KPIs
    contenido.append(Paragraph("KPIs Principales", heading_style))
    kpi_data = [['Metrica', 'Valor']]
    kpi_data.append(['Cultivo', cultivo_info['nombre_cultivo']])
    kpi_data.append(['Area Total', f"{cultivo_info['area_hectareas']:.1f} ha"])
    kpi_data.append(['Estado', cultivo_info['estado']])

    if predicciones:
        rend_prom = sum(p['rendimiento_predicho'] for p in predicciones) / len(predicciones)
        conf_prom = sum(p['confianza'] for p in predicciones) / len(predicciones)
        kpi_data.append(['Rendimiento Promedio Predicho', f"{rend_prom:.2f} t/ha"])
        kpi_data.append(['Confianza Promedio', f"{conf_prom*100:.1f}%"])
        kpi_data.append(['Total Predicciones', str(len(predicciones))])

    if optimizaciones:
        ahorro_prom = sum(o['ahorro_potencial'] for o in optimizaciones) / len(optimizaciones)
        kpi_data.append(['Ahorro Hidrico Potencial', f"{ahorro_prom:.1f} L/ha"])

    tabla_kpi = Table(kpi_data, colWidths=[3*inch, 3*inch])
    tabla_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B4D3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
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
        contenido.append(Paragraph("Analisis de Predicciones", heading_style))
        texto = (
            f"Se realizaron {len(predicciones)} predicciones. "
            f"Rendimiento promedio: {rend_prom:.2f} t/ha. "
            f"Confianza promedio: {conf_prom*100:.1f}%."
        )
        contenido.append(Paragraph(texto, styles['Normal']))
        contenido.append(Spacer(1, 0.2*inch))

    # Análisis de optimización
    if optimizaciones:
        contenido.append(Paragraph("Analisis de Optimizacion Hidrica", heading_style))
        opt = optimizaciones[0]
        texto_opt = (
            f"Agua recomendada: {opt['agua_recomendada']:.1f} L/ha. "
            f"Agua actual: {opt['agua_actual']:.1f} L/ha. "
            f"Ahorro potencial: {opt['ahorro_potencial']:.1f} L/ha."
        )
        contenido.append(Paragraph(texto_opt, styles['Normal']))
        contenido.append(Spacer(1, 0.1*inch))
        contenido.append(Paragraph(f"Recomendacion: {opt['recomendacion']}", styles['Normal']))
        contenido.append(Spacer(1, 0.2*inch))

    # Conclusiones
    contenido.append(Paragraph("Conclusiones", heading_style))
    contenido.append(Paragraph(
        "El sistema de informacion agricola de precision ha proporcionado un analisis integral. "
        "Se recomienda continuar monitoreando las metricas y realizar predicciones periodicas "
        "para optimizar el rendimiento y el uso de recursos naturales.",
        styles['Normal']
    ))

    # Pie de página
    contenido.append(Spacer(1, 0.4*inch))
    fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nombre_usuario = usuario_info['nombre'] if usuario_info else 'N/A'
    email_usuario = usuario_info['email'] if usuario_info else 'N/A'
    contenido.append(Paragraph(
        f"Reporte generado: {fecha_reporte} | Usuario: {nombre_usuario} | Email: {email_usuario}",
        styles['Normal']
    ))

    doc.build(contenido)
    buffer.seek(0)
    return buffer.getvalue()


def guardar_reporte_en_bd(id_usuario, id_cultivo, tipo_reporte, nombre_archivo, ruta_archivo='memoria'):
    """Guarda registro del reporte en BD"""
    conexion = sqlite3.connect(obtener_ruta_db())
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO reportes (id_usuario, id_cultivo, tipo_reporte, nombre_archivo, ruta_archivo)
            VALUES (?, ?, ?, ?, ?)
        """, (id_usuario, id_cultivo, tipo_reporte, nombre_archivo, ruta_archivo))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al guardar reporte en BD: {e}")
        return False
    finally:
        conexion.close()