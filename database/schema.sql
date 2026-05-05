-- ================================================================
-- ESQUEMA DE BASE DE DATOS - SISTEMA AGRÍCOLA DE PRECISIÓN
-- Compatible con SQLite
-- ================================================================

-- Tabla de Usuarios
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    contrasena TEXT NOT NULL,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1
);

-- Tabla de Cultivos
CREATE TABLE cultivos (
    id_cultivo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    nombre_cultivo TEXT NOT NULL,
    tipo_cultivo TEXT NOT NULL,
    area_hectareas REAL NOT NULL,
    fecha_siembra DATETIME NOT NULL,
    fecha_cosecha_estimada DATETIME NOT NULL,
    estado TEXT DEFAULT 'Activo',
    rendimiento_real REAL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- Tabla de Sensores
CREATE TABLE sensores (
    id_sensor INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_cultivo INTEGER NOT NULL,
    tipo_sensor TEXT NOT NULL,
    ubicacion TEXT NOT NULL,
    latitud REAL NOT NULL,
    longitud REAL NOT NULL,
    fecha_instalacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_cultivo) REFERENCES cultivos(id_cultivo) ON DELETE CASCADE
);

-- Tabla de Datos de Sensores
CREATE TABLE datos_sensor (
    id_dato INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sensor INTEGER NOT NULL,
    id_cultivo INTEGER NOT NULL,
    valor_temperatura REAL,
    valor_humedad REAL,
    valor_ph REAL,
    valor_precipitacion REAL,
    valor_radiacion REAL,
    fecha_lectura DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_sensor) REFERENCES sensores(id_sensor) ON DELETE CASCADE,
    FOREIGN KEY (id_cultivo) REFERENCES cultivos(id_cultivo) ON DELETE CASCADE
);

-- Tabla de Predicciones
CREATE TABLE predicciones (
    id_prediccion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cultivo INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    rendimiento_predicho REAL NOT NULL,
    confianza REAL NOT NULL,
    fecha_prediccion DATETIME DEFAULT CURRENT_TIMESTAMP,
    modelo_usado TEXT DEFAULT 'Ensemble',
    error_mae REAL,
    FOREIGN KEY (id_cultivo) REFERENCES cultivos(id_cultivo) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- Tabla de Optimización Hídrica
CREATE TABLE optimizacion (
    id_optimizacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cultivo INTEGER NOT NULL,
    id_prediccion INTEGER NOT NULL,
    agua_recomendada REAL NOT NULL,
    agua_actual REAL NOT NULL,
    ahorro_potencial REAL NOT NULL,
    recomendacion TEXT,
    fecha_analisis DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cultivo) REFERENCES cultivos(id_cultivo) ON DELETE CASCADE,
    FOREIGN KEY (id_prediccion) REFERENCES predicciones(id_prediccion) ON DELETE CASCADE
);

-- Tabla de Reportes
CREATE TABLE reportes (
    id_reporte INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_cultivo INTEGER NOT NULL,
    tipo_reporte TEXT NOT NULL,
    nombre_archivo TEXT NOT NULL,
    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    ruta_archivo TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_cultivo) REFERENCES cultivos(id_cultivo) ON DELETE CASCADE
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_cultivos_usuario ON cultivos(id_usuario);
CREATE INDEX idx_sensores_cultivo ON sensores(id_cultivo);
CREATE INDEX idx_datos_sensor_sensor ON datos_sensor(id_sensor);
CREATE INDEX idx_predicciones_cultivo ON predicciones(id_cultivo);
CREATE INDEX idx_optimizacion_cultivo ON optimizacion(id_cultivo);
CREATE INDEX idx_reportes_usuario ON reportes(id_usuario);

-- ================================================================
-- INSERCIÓN DE DATOS DE EJEMPLO (30+ registros)
-- ================================================================

-- Usuarios de prueba
INSERT INTO usuarios (usuario, contrasena, nombre, email) VALUES
('admin', 'admin123', 'Administrador', 'admin@agro.com'),
('usuario1', 'pass123', 'Juan Pérez', 'juan@agro.com'),
('usuario2', 'pass456', 'María García', 'maria@agro.com'),
('usuario3', 'pass789', 'Carlos López', 'carlos@agro.com');

-- Cultivos de ejemplo
INSERT INTO cultivos (id_usuario, nombre_cultivo, tipo_cultivo, area_hectareas, fecha_siembra, fecha_cosecha_estimada, estado) VALUES
(2, 'Maíz Campo A', 'Maíz', 50.5, '2026-04-01', '2026-09-01', 'Activo'),
(2, 'Trigo Campo B', 'Trigo', 75.0, '2026-03-15', '2026-08-15', 'Activo'),
(3, 'Soja Campo C', 'Soja', 100.0, '2026-04-15', '2026-10-01', 'Activo'),
(3, 'Maíz Campo D', 'Maíz', 60.0, '2026-04-05', '2026-09-05', 'Activo'),
(4, 'Trigo Campo E', 'Trigo', 80.0, '2026-03-20', '2026-08-20', 'Activo'),
(2, 'Maíz Anterior', 'Maíz', 45.0, '2025-04-01', '2025-09-01', 'Completado');

-- Sensores de ejemplo
INSERT INTO sensores (id_usuario, id_cultivo, tipo_sensor, ubicacion, latitud, longitud, activo) VALUES
(2, 1, 'Temperatura', 'Zona A-1', -32.8895, -68.8477, 1),
(2, 1, 'Humedad', 'Zona A-2', -32.8900, -68.8480, 1),
(2, 1, 'pH', 'Zona A-3', -32.8905, -68.8485, 1),
(2, 2, 'Temperatura', 'Zona B-1', -32.8910, -68.8490, 1),
(2, 2, 'Humedad', 'Zona B-2', -32.8915, -68.8495, 1),
(3, 3, 'Temperatura', 'Zona C-1', -32.8920, -68.8500, 1),
(3, 3, 'Humedad', 'Zona C-2', -32.8925, -68.8505, 1),
(3, 4, 'Precipitación', 'Zona D-1', -32.8930, -68.8510, 1),
(4, 5, 'Temperatura', 'Zona E-1', -32.8935, -68.8515, 1),
(4, 5, 'Radiación', 'Zona E-2', -32.8940, -68.8520, 1);

-- Datos de sensores (históricos y actuales)
INSERT INTO datos_sensor (id_sensor, id_cultivo, valor_temperatura, valor_humedad, valor_ph, valor_precipitacion, valor_radiacion, fecha_lectura) VALUES
(1, 1, 24.5, 65.2, 6.8, 2.5, 18.5, '2026-05-05 08:00:00'),
(1, 1, 25.1, 63.8, 6.7, 0.0, 19.2, '2026-05-05 12:00:00'),
(1, 1, 23.8, 68.5, 6.8, 1.2, 17.8, '2026-05-05 16:00:00'),
(2, 1, 64.5, 65.2, 6.8, 2.5, 18.5, '2026-05-05 08:00:00'),
(2, 1, 62.1, 63.8, 6.7, 0.0, 19.2, '2026-05-05 12:00:00'),
(2, 1, 66.8, 68.5, 6.8, 1.2, 17.8, '2026-05-05 16:00:00'),
(3, 1, 6.8, 65.2, 6.8, 2.5, 18.5, '2026-05-05 08:00:00'),
(4, 2, 22.5, 60.2, 7.0, 1.5, 18.0, '2026-05-05 08:00:00'),
(4, 2, 23.2, 58.8, 7.1, 0.0, 19.5, '2026-05-05 12:00:00'),
(5, 2, 59.8, 60.2, 7.0, 1.5, 18.0, '2026-05-05 08:00:00'),
(6, 3, 26.0, 70.5, 6.5, 3.2, 20.1, '2026-05-05 08:00:00'),
(6, 3, 27.1, 68.2, 6.4, 0.0, 21.3, '2026-05-05 12:00:00'),
(7, 3, 70.2, 70.5, 6.5, 3.2, 20.1, '2026-05-05 08:00:00'),
(8, 4, 3.8, 75.5, 6.6, 4.2, 19.5, '2026-05-05 08:00:00'),
(8, 4, 4.5, 73.2, 6.6, 2.1, 20.8, '2026-05-05 12:00:00'),
(9, 5, 21.5, 55.2, 7.2, 1.0, 17.5, '2026-05-05 08:00:00'),
(10, 5, 20.8, 18.5, 7.1, 0.5, 17.9, '2026-05-05 08:00:00'),
(10, 5, 21.2, 19.2, 7.0, 0.3, 18.5, '2026-05-05 12:00:00');

-- Predicciones de ejemplo
INSERT INTO predicciones (id_cultivo, id_usuario, rendimiento_predicho, confianza, modelo_usado, error_mae) VALUES
(1, 2, 9500.0, 0.92, 'Ensemble', 150.5),
(2, 2, 7800.0, 0.88, 'Ensemble', 200.3),
(3, 3, 10200.0, 0.94, 'Ensemble', 120.8),
(4, 3, 9300.0, 0.91, 'Ensemble', 160.2),
(5, 4, 7600.0, 0.87, 'Ensemble', 210.5),
(1, 2, 9600.0, 0.93, 'Ensemble', 145.2);

-- Optimización hídrica
INSERT INTO optimizacion (id_cultivo, id_prediccion, agua_recomendada, agua_actual, ahorro_potencial, recomendacion) VALUES
(1, 1, 450.0, 520.0, 13.5, 'Reducir riego en 15% sin afectar rendimiento'),
(2, 2, 380.0, 420.0, 9.5, 'Mantener riego actual, condiciones óptimas'),
(3, 3, 520.0, 550.0, 5.5, 'Incrementar riego 2% en próximas 2 semanas'),
(4, 4, 480.0, 510.0, 5.9, 'Reducir riego ligeramente'),
(5, 5, 420.0, 460.0, 8.7, 'Incrementar eficiencia del riego');

-- Reportes generados
INSERT INTO reportes (id_usuario, id_cultivo, tipo_reporte, nombre_archivo) VALUES
(2, 1, 'Operacional', 'reporte_operacional_cultivo_1_2026_05_05.pdf'),
(2, 2, 'Gestión', 'reporte_gestion_cultivo_2_2026_05_05.pdf'),
(3, 3, 'Operacional', 'reporte_operacional_cultivo_3_2026_05_05.pdf');
