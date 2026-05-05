"""
Módulo de inicialización de base de datos SQLite
Crea el esquema y carga datos de ejemplo
"""

import sqlite3
import os
from pathlib import Path

def obtener_ruta_db():
    """Obtiene la ruta de la base de datos"""
    ruta_proyecto = Path(__file__).parent.parent
    ruta_db = ruta_proyecto / "agro_sistema.db"
    return str(ruta_db)

def ejecutar_script_sql(conexion, archivo_sql):
    """Ejecuta un script SQL completo"""
    with open(archivo_sql, 'r', encoding='utf-8') as f:
        script_sql = f.read()
    
    cursor = conexion.cursor()
    cursor.executescript(script_sql)
    conexion.commit()
    print(f"✓ Script {archivo_sql} ejecutado correctamente")

def inicializar_base_datos():
    """Crea la base de datos e inicializa con datos de ejemplo"""
    ruta_db = obtener_ruta_db()
    ruta_sql = Path(__file__).parent / "schema.sql"
    
    # Eliminar BD anterior si existe (para desarrollo)
    if os.path.exists(ruta_db):
        print(f"⚠ Eliminando base de datos anterior: {ruta_db}")
        os.remove(ruta_db)
    
    # Crear conexión
    conexion = sqlite3.connect(ruta_db)
    print(f"✓ Conexión a BD establecida: {ruta_db}")
    
    # Ejecutar esquema SQL
    if ruta_sql.exists():
        ejecutar_script_sql(conexion, ruta_sql)
    else:
        print(f"✗ Archivo {ruta_sql} no encontrado")
        return False
    
    # Verificar tablas creadas
    cursor = conexion.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    print(f"\n✓ Base de datos inicializada con {len(tablas)} tablas:")
    for tabla in tablas:
        print(f"  - {tabla[0]}")
    
    # Mostrar estadísticas
    cursor.execute("SELECT COUNT(*) FROM usuarios;")
    print(f"\n📊 Datos de ejemplo cargados:")
    print(f"  - Usuarios: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM cultivos;")
    print(f"  - Cultivos: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM sensores;")
    print(f"  - Sensores: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM datos_sensor;")
    print(f"  - Lecturas de sensores: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM predicciones;")
    print(f"  - Predicciones: {cursor.fetchone()[0]}")
    
    conexion.close()
    print("\n✓ Base de datos inicializada correctamente\n")
    return True

if __name__ == "__main__":
    inicializar_base_datos()
