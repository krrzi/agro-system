"""
Configuración global del Sistema Agrícola de Precisión
"""

from pathlib import Path

# Rutas del proyecto
RUTA_PROYECTO = Path(__file__).parent
RUTA_DB = RUTA_PROYECTO / "agro_sistema.db"
RUTA_REPORTES = RUTA_PROYECTO / "reports"
RUTA_MODELS = RUTA_PROYECTO / "models"

# Asegurar que existan las carpetas
RUTA_REPORTES.mkdir(exist_ok=True)

# Configuración de la Aplicación
NOMBRE_APP = "Sistema Agrícola de Precisión"
TITULO_APP = "🌾 Sistema de Información Agrícola con ML"
VERSION = "1.0.0"
AUTOR = "Ingeniero Agrónomo - AI"

# Configuración de Autenticación
TIEMPO_SESION_MINUTOS = 120  # 2 horas
INTENTOS_LOGIN_MAXIMOS = 5

# Configuración del Modelo ML
MODELO_ENSEMBLE_CONFIG = {
    'random_forest': {
        'n_estimators': 100,
        'max_depth': 15,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'random_state': 42,
        'n_jobs': -1
    },
    'gradient_boosting': {
        'n_estimators': 100,
        'learning_rate': 0.1,
        'max_depth': 5,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'random_state': 42
    }
}

# Features del modelo
FEATURES_MODELO = [
    'valor_temperatura',
    'valor_humedad',
    'valor_ph',
    'valor_precipitacion',
    'valor_radiacion',
    'area_hectareas'
]

# Rangos realistas de rendimiento
RENDIMIENTO_MINIMO_KG_HA = 5000
RENDIMIENTO_MAXIMO_KG_HA = 12000
RENDIMIENTO_PROMEDIO_KG_HA = 8000

# Configuración de Optimización Hídrica
REQUERIMIENTOS_AGUA_MM = {
    'Maíz': {'optimo': 120, 'minimo': 80, 'maximo': 160},
    'Trigo': {'optimo': 100, 'minimo': 60, 'maximo': 140},
    'Soja': {'optimo': 110, 'minimo': 70, 'maximo': 150},
    'Arroz': {'optimo': 150, 'minimo': 100, 'maximo': 200},
    'Cebada': {'optimo': 90, 'minimo': 50, 'maximo': 130},
}

HUMEDAD_OPTIMA_PORCENTAJE = 65.0

# Conversión mm a m³/ha
MM_A_M3_HA = 10

# Configuración de Reportes
FORMATO_FECHA = "%d/%m/%Y"
FORMATO_DATETIME = "%d/%m/%Y %H:%M:%S"

# Colores del tema (Hex)
COLOR_PRIMARIO = "#1B4D3E"
COLOR_SECUNDARIO = "#2D5A3D"
COLOR_FONDO_SECUNDARIO = "#F0F8F5"
COLOR_EXITO = "#6BCB77"
COLOR_ADVERTENCIA = "#FFD93D"
COLOR_ERROR = "#FF6B6B"

# Configuración de Gráficos
ANCHO_GRAFICO_DEFECTO = "use_container_width"
ALTURA_GRAFICO_DEFECTO = 500

# Límites de datos
LIMITE_PREDICCIONES_MOSTRAR = 10
LIMITE_OPTIMIZACIONES_MOSTRAR = 10
LIMITE_SENSORES_MOSTRAR = 100
DIAS_HISTORICO_DEFECTO = 30

# Mensajes del sistema
MENSAJES = {
    'bienvenida': "Bienvenido al Sistema Agrícola de Precisión",
    'login_exitoso': "✓ Login exitoso",
    'login_fallido': "❌ Usuario o contraseña incorrectos",
    'base_datos_inicializada': "✓ Base de datos inicializada correctamente",
    'prediccion_exitosa': "✓ Predicción realizada exitosamente",
    'reporte_generado': "✓ Reporte generado correctamente",
    'error_generico': "❌ Ha ocurrido un error",
    'sin_datos': "No hay datos disponibles",
    'sin_cultivos': "No tienes cultivos registrados",
}

# Validaciones
VALIDACIONES = {
    'usuario_min_length': 3,
    'contraseña_min_length': 6,
    'email_pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'area_minima': 0.1,
    'area_maxima': 10000.0,
    'confianza_minima': 0.7,  # 70%
    'confianza_maxima': 0.99,  # 99%
}

# Información de Contacto/Soporte
EMAIL_SOPORTE = "admin@agro-sistema.com"
TELEFONO_SOPORTE = "+54 (xxx) xxx-xxxx"
SITIO_WEB = "https://agro-sistema.com"

print(f"✓ Configuración cargada: {NOMBRE_APP} v{VERSION}")
