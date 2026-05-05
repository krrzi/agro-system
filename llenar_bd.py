"""
Script para llenar la base de datos con datos de ejemplo
Estructura real de la BD
"""
import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('agro_sistema.db')
cursor = conn.cursor()

ID_USUARIO = 1  # admin

# ── CULTIVOS ─────────────────────────────────────────────────────────────────
cultivos_data = [
    (ID_USUARIO, 'Maíz Amarillo', 'cereal',      45.5, '2025-01-10', '2025-06-15', 'activo',    6.8),
    (ID_USUARIO, 'Papa Blanca',   'tuberculo',   30.0, '2025-02-01', '2025-07-01', 'activo',    5.2),
    (ID_USUARIO, 'Trigo Duro',    'cereal',      60.0, '2024-11-15', '2025-04-20', 'cosechado', 4.9),
    (ID_USUARIO, 'Arroz Largo',   'cereal',      25.5, '2025-03-01', '2025-08-10', 'activo',    None),
    (ID_USUARIO, 'Quinua Real',   'pseudocereal',15.0, '2025-01-20', '2025-06-30', 'activo',    3.1),
    (ID_USUARIO, 'Cebada',        'cereal',      20.0, '2024-12-01', '2025-05-15', 'cosechado', 4.3),
]
cursor.executemany(
    """INSERT INTO cultivos
       (id_usuario, nombre_cultivo, tipo_cultivo, area_hectareas,
        fecha_siembra, fecha_cosecha_estimada, estado, rendimiento_real)
       VALUES (?,?,?,?,?,?,?,?)""",
    cultivos_data
)
ids_cultivos = [r[0] for r in cursor.execute("SELECT id_cultivo FROM cultivos WHERE id_usuario=?", (ID_USUARIO,)).fetchall()]
print(f"✓ {len(ids_cultivos)} cultivos insertados: {ids_cultivos}")

# ── SENSORES ─────────────────────────────────────────────────────────────────
sensores_data = []
tipos = ['temperatura', 'humedad', 'ph', 'precipitacion']
for id_cultivo in ids_cultivos:
    for tipo in tipos:
        sensores_data.append((
            ID_USUARIO, id_cultivo, tipo,
            f'Zona {id_cultivo}',
            round(-12.05 + random.uniform(-0.1, 0.1), 6),
            round(-77.03 + random.uniform(-0.1, 0.1), 6),
            '2025-01-01', 1
        ))
cursor.executemany(
    """INSERT INTO sensores
       (id_usuario, id_cultivo, tipo_sensor, ubicacion, latitud, longitud,
        fecha_instalacion, activo)
       VALUES (?,?,?,?,?,?,?,?)""",
    sensores_data
)
ids_sensores = [r[0] for r in cursor.execute("SELECT id_sensor FROM sensores WHERE id_usuario=?", (ID_USUARIO,)).fetchall()]
print(f"✓ {len(ids_sensores)} sensores insertados")

# ── DATOS SENSOR (últimos 60 días) ───────────────────────────────────────────
datos = []
fecha_base = datetime.now() - timedelta(days=60)
for dia in range(60):
    fecha = (fecha_base + timedelta(days=dia)).strftime('%Y-%m-%d %H:%M:%S')
    for id_cultivo in ids_cultivos:
        datos.append((
            random.choice(ids_sensores),
            id_cultivo,
            round(random.uniform(15.0, 35.0), 2),
            round(random.uniform(40.0, 90.0), 2),
            round(random.uniform(5.5,  7.5),  2),
            round(random.uniform(0.0,  25.0), 2),
            round(random.uniform(100.0,800.0),2),
            fecha
        ))
cursor.executemany(
    """INSERT INTO datos_sensor
       (id_sensor, id_cultivo, valor_temperatura, valor_humedad,
        valor_ph, valor_precipitacion, valor_radiacion, fecha_lectura)
       VALUES (?,?,?,?,?,?,?,?)""",
    datos
)
print(f"✓ {len(datos)} lecturas de sensores insertadas")

# ── PREDICCIONES ─────────────────────────────────────────────────────────────
predicciones = []
for id_cultivo in ids_cultivos:
    for mes in range(1, 4):
        fecha = (datetime.now() + timedelta(days=mes*30)).strftime('%Y-%m-%d')
        predicciones.append((
            id_cultivo, ID_USUARIO,
            round(random.uniform(3.5, 9.0), 2),
            round(random.uniform(0.78, 0.97), 2),
            fecha,
            'Random Forest + Gradient Boosting',
            round(random.uniform(0.1, 0.5), 3)
        ))
cursor.executemany(
    """INSERT INTO predicciones
       (id_cultivo, id_usuario, rendimiento_predicho, confianza,
        fecha_prediccion, modelo_usado, error_mae)
       VALUES (?,?,?,?,?,?,?)""",
    predicciones
)
ids_pred = [r[0] for r in cursor.execute("SELECT id_prediccion FROM predicciones WHERE id_usuario=?", (ID_USUARIO,)).fetchall()]
print(f"✓ {len(ids_pred)} predicciones insertadas")

# ── OPTIMIZACION ─────────────────────────────────────────────────────────────
optimizacion = []
for i, id_cultivo in enumerate(ids_cultivos):
    agua_actual = round(random.uniform(1000, 3000), 2)
    agua_rec    = round(agua_actual * random.uniform(0.7, 0.95), 2)
    ahorro      = round(agua_actual - agua_rec, 2)
    optimizacion.append((
        id_cultivo,
        ids_pred[i] if i < len(ids_pred) else ids_pred[0],
        agua_rec,
        agua_actual,
        ahorro,
        f'Reducir riego en {round((ahorro/agua_actual)*100,1)}% según condiciones actuales',
        datetime.now().strftime('%Y-%m-%d')
    ))
cursor.executemany(
    """INSERT INTO optimizacion
       (id_cultivo, id_prediccion, agua_recomendada, agua_actual,
        ahorro_potencial, recomendacion, fecha_analisis)
       VALUES (?,?,?,?,?,?,?)""",
    optimizacion
)
print(f"✓ {len(optimizacion)} registros de optimización insertados")

conn.commit()
conn.close()
print("\n✅ Base de datos llenada correctamente")
print("   Recarga la app en el navegador con F5")