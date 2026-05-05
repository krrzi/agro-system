"""
Script de Verificación Rápida del Sistema
Valida que todos los componentes estén funcionando
"""

import sys
from pathlib import Path

# Agregar ruta del proyecto
ruta_proyecto = Path(__file__).parent
sys.path.append(str(ruta_proyecto))

def verificar_imports():
    """Verifica que todos los módulos se importan correctamente"""
    print("🔍 Verificando importaciones...\n")
    
    try:
        print("  ✓ import streamlit")
        import streamlit
    except ImportError as e:
        print(f"  ✗ import streamlit - {e}")
        return False
    
    try:
        print("  ✓ import pandas")
        import pandas
    except ImportError as e:
        print(f"  ✗ import pandas - {e}")
        return False
    
    try:
        print("  ✓ import numpy")
        import numpy
    except ImportError as e:
        print(f"  ✗ import numpy - {e}")
        return False
    
    try:
        print("  ✓ import plotly")
        import plotly.express
    except ImportError as e:
        print(f"  ✗ import plotly - {e}")
        return False
    
    try:
        print("  ✓ import sklearn")
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    except ImportError as e:
        print(f"  ✗ import sklearn - {e}")
        return False
    
    try:
        print("  ✓ import reportlab")
        from reportlab.lib.pagesizes import A4
    except ImportError as e:
        print(f"  ✗ import reportlab - {e}")
        return False
    
    print("  ✓ import sqlite3")
    import sqlite3
    
    print("\n✅ Todas las importaciones correctas\n")
    return True

def verificar_archivos():
    """Verifica que existan todos los archivos necesarios"""
    print("📁 Verificando archivos...\n")
    
    archivos_requeridos = [
        "app.py",
        "config.py",
        "requirements.txt",
        "database/schema.sql",
        "database/init_db.py",
        "modules/__init__.py",
        "modules/auth.py",
        "modules/dashboard.py",
        "modules/prediccion.py",
        "modules/optimizacion.py",
        "modules/reportes.py",
        "models/__init__.py",
        "models/ensemble_model.py",
        ".streamlit/config.toml",
        "README.md",
        "DESPLIEGUE_RAPIDO.md",
    ]
    
    todos_existen = True
    for archivo in archivos_requeridos:
        ruta = ruta_proyecto / archivo
        if ruta.exists():
            print(f"  ✓ {archivo}")
        else:
            print(f"  ✗ {archivo} - NO ENCONTRADO")
            todos_existen = False
    
    if todos_existen:
        print("\n✅ Todos los archivos presentes\n")
    else:
        print("\n❌ Faltan archivos\n")
    
    return todos_existen

def verificar_base_datos():
    """Verifica la base de datos"""
    print("💾 Verificando base de datos...\n")
    
    from database.init_db import obtener_ruta_db, inicializar_base_datos
    import sqlite3
    
    ruta_db = Path(obtener_ruta_db())
    
    if not ruta_db.exists():
        print("  ⚠ BD no existe. Creando...\n")
        inicializar_base_datos()
    else:
        print(f"  ✓ BD existe: {ruta_db}\n")
    
    # Verificar tablas
    conexion = sqlite3.connect(str(ruta_db))
    cursor = conexion.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    
    print("  Tablas encontradas:")
    for tabla in tablas:
        cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
        cantidad = cursor.fetchone()[0]
        print(f"    ✓ {tabla[0]} ({cantidad} registros)")
    
    conexion.close()
    print("\n✅ Base de datos verificada\n")
    return True

def verificar_modelo_ml():
    """Verifica el modelo de ML"""
    print("🤖 Verificando modelo ML...\n")
    
    try:
        from models.ensemble_model import ModeloEnsemble
        
        print("  ✓ Clase ModeloEnsemble importada")
        
        # Crear instancia
        modelo = ModeloEnsemble()
        print("  ✓ Instancia de modelo creada")
        
        # Entrenar
        print("  ⏳ Entrenando modelo (puede tardar ~5 segundos)...")
        resultados = modelo.entrenar()
        
        if resultados:
            print("  ✓ Modelo entrenado exitosamente")
            print(f"    - MAE Ensemble: {resultados['mae_ensemble']:.2f} kg/ha")
            print(f"    - R² Score: {resultados['r2_ensemble']:.4f}")
            print(f"    - Muestras train: {resultados['muestras_entrenamiento']}")
            print(f"    - Muestras test: {resultados['muestras_evaluacion']}")
        else:
            print("  ✗ Error al entrenar modelo")
            return False
        
        # Hacer predicción de prueba
        prediccion = modelo.predecir(24, 65, 6.8, 3, 19, 50)
        print("  ✓ Predicción de prueba realizada")
        print(f"    - Rendimiento: {prediccion['rendimiento_predicho']:.0f} kg/ha")
        print(f"    - Confianza: {prediccion['confianza']*100:.1f}%")
        
        print("\n✅ Modelo ML verificado\n")
        return True
    except Exception as e:
        print(f"  ✗ Error en modelo ML: {e}\n")
        return False

def verificar_modulos():
    """Verifica los módulos principales"""
    print("🔧 Verificando módulos...\n")
    
    try:
        from modules import auth, dashboard, prediccion, optimizacion, reportes
        print("  ✓ auth")
        print("  ✓ dashboard")
        print("  ✓ prediccion")
        print("  ✓ optimizacion")
        print("  ✓ reportes")
        print("\n✅ Todos los módulos importables\n")
        return True
    except ImportError as e:
        print(f"  ✗ Error importando módulos: {e}\n")
        return False

def main():
    """Ejecuta todas las verificaciones"""
    
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN RÁPIDA DEL SISTEMA AGRÍCOLA")
    print("="*60 + "\n")
    
    resultados = []
    
    # Verificar archivos primero (rápido)
    resultados.append(("Archivos", verificar_archivos()))
    
    # Verificar imports (rápido)
    resultados.append(("Importaciones", verificar_imports()))
    
    # Verificar módulos (rápido)
    resultados.append(("Módulos", verificar_modulos()))
    
    # Verificar BD (incluye init si es necesario)
    resultados.append(("Base de Datos", verificar_base_datos()))
    
    # Verificar modelo ML (más lento)
    resultados.append(("Modelo ML", verificar_modelo_ml()))
    
    # Resumen
    print("="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60 + "\n")
    
    todos_ok = True
    for nombre, resultado in resultados:
        estado = "✅" if resultado else "❌"
        print(f"  {estado} {nombre}")
        if not resultado:
            todos_ok = False
    
    print("\n" + "="*60)
    
    if todos_ok:
        print("\n✅ ¡SISTEMA COMPLETAMENTE FUNCIONAL!\n")
        print("Próximo paso: streamlit run app.py\n")
        print("="*60 + "\n")
        return 0
    else:
        print("\n❌ Hay problemas a resolver\n")
        print("Revisa los errores anteriores\n")
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    exit(main())
