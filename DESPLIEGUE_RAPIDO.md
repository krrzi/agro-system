# 📘 GUÍA DE DESPLIEGUE - SISTEMA AGRÍCOLA DE PRECISIÓN

## ⚡ DESPLIEGUE RÁPIDO EN 4 PASOS

### PASO 1️⃣: Preparar Ambiente

```bash
# Crear entorno virtual Python
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

**Duración:** ~2 minutos  
**Verifica:** `pip list` debe mostrar streamlit, pandas, scikit-learn, reportlab

---

### PASO 2️⃣: Inicializar Base de Datos

```bash
# Crear BD SQLite con datos de ejemplo
python database/init_db.py
```

**Salida esperada:**
```
✓ Conexión a BD establecida: c:\...\agro_sistema.db
✓ Script database/schema.sql ejecutado correctamente

✓ Base de datos inicializada con 8 tablas:
  - usuarios
  - cultivos
  - sensores
  - datos_sensor
  - predicciones
  - optimizacion
  - reportes

📊 Datos de ejemplo cargados:
  - Usuarios: 4
  - Cultivos: 6
  - Sensores: 10
  - Lecturas de sensores: 18
  - Predicciones: 6
  
✓ Base de datos inicializada correctamente
```

**Duración:** ~5 segundos

---

### PASO 3️⃣: Ejecutar Aplicación Localmente

```bash
# Lanzar Streamlit
streamlit run app.py
```

**Salida esperada:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**La app se abre automáticamente en el navegador**

**Duración:** ~3 segundos

---

### PASO 4️⃣: Acceder a la Aplicación

**URL Local:** `http://localhost:8501`

**Credenciales de prueba:**
- Usuario: `usuario1` | Contraseña: `pass123`
- Usuario: `usuario2` | Contraseña: `pass456`
- Usuario: `usuario3` | Contraseña: `pass789`

**Duración:** Inmediata

---

## 🌐 DESPLIEGUE EN STREAMLIT CLOUD (Bonus)

### Opción A: Deploy Automático (5 min)

1. **Ir a:** https://share.streamlit.io
2. **Conectar:** Repositorio GitHub
3. **Seleccionar:**
   - Repository: `tu-usuario/agro-system`
   - Branch: `main`
   - Main file: `app.py`
4. **Deploy:** ¡Hecho!

**URL:** `https://share.streamlit.io/tu-usuario/agro-system`

### Opción B: Usando Git

```bash
# Inicializar repositorio Git
git init
git add .
git commit -m "Sistema Agrícola - Inicial"

# Agregar remote
git remote add origin https://github.com/TU_USUARIO/agro-system.git
git branch -M main
git push -u origin main

# Luego en Streamlit Cloud: Connect repository
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] Python 3.8+ instalado (`python --version`)
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip list | grep streamlit`)
- [ ] Base de datos creada (`file exists: agro_sistema.db`)
- [ ] Aplicación ejecutándose en `http://localhost:8501`
- [ ] Login exitoso con `usuario1 / pass123`
- [ ] Dashboard visible con KPIs y gráficos
- [ ] Predicción funcionando con cultivos de ejemplo
- [ ] Reporte PDF generado correctamente

---

## 🚨 TROUBLESHOOTING RÁPIDO

### ❌ Error: "No module named streamlit"
```bash
pip install -r requirements.txt
```

### ❌ Error: "database not found"
```bash
python database/init_db.py
```

### ❌ Error: "Permission denied on reports/"
```bash
mkdir -p reports
```

### ❌ Streamlit no abre el navegador
```bash
Abre manualmente: http://localhost:8501
```

### ❌ Puerto 8501 en uso
```bash
streamlit run app.py --server.port 8502
```

---

## 📊 RESULTADOS ESPERADOS

### Después del Paso 1
```
✓ Entorno virtual listo
✓ Paquetes instalados: streamlit, pandas, scikit-learn, plotly, reportlab
```

### Después del Paso 2
```
✓ Archivo: agro_sistema.db creado
✓ 8 tablas SQLite inicializadas
✓ 50+ registros de datos de ejemplo cargados
```

### Después del Paso 3
```
✓ Terminal muestra: "You can now view your Streamlit app"
✓ Navegador abre http://localhost:8501
```

### Después del Paso 4
```
✓ Pantalla de login visible
✓ Login exitoso con usuario1/pass123
✓ Dashboard con 5 KPIs principales
✓ Navegación a todas las secciones funciona
✓ Predicciones generadas exitosamente
✓ PDFs descargables
```

---

## 📱 FUNCIONALIDADES DISPONIBLES

### Dashboard 📊
- 5 KPIs principales
- 4 gráficos interactivos
- Tabla con últimas lecturas de sensores
- Estadísticas descriptivas

### Predicciones 🔮
- Modelo Ensemble (Random Forest + Gradient Boosting)
- Confianza 70-99%
- Historial de predicciones
- Importancia de características

### Optimización 💧
- Cálculo automático de agua recomendada
- Gauge de eficiencia hídrica
- Recomendaciones personalizadas
- Ahorro potencial

### Reportes 📄
- Reporte Operacional (PDF)
- Reporte de Gestión (PDF)
- Descargas directas

---

## ⏱️ TIEMPOS ESTIMADOS

| Paso | Descripción | Tiempo |
|------|------------|--------|
| 1 | Preparar ambiente | 2 min |
| 2 | Inicializar BD | 10 seg |
| 3 | Ejecutar app | 5 seg |
| 4 | Acceder | Inmediato |
| **TOTAL** | **Despliegue completo** | **~2.5 min** ✅ |

---

## 📁 ARCHIVOS CLAVE

```
agro_system/
├── app.py                    # Ejecutar esto: streamlit run app.py
├── requirements.txt          # pip install -r requirements.txt
├── database/
│   ├── schema.sql           # Esquema de 8 tablas
│   └── init_db.py           # python database/init_db.py
├── modules/                 # Lógica de negocio (auth, dashboard, etc)
├── models/ensemble_model.py # Modelo ML (Random Forest + GB)
└── reports/                 # PDFs generados aquí
```

---

## 🎯 DATOS DE PRUEBA

Precargados en la BD:
- **4 usuarios** con login funcional
- **6 cultivos** (Maíz, Trigo, Soja)
- **10 sensores** activos
- **18+ lecturas** de sensores
- **6 predicciones** de rendimiento
- **5 análisis** de optimización

---

## 🔐 SEGURIDAD NOTAS

- Contraseñas hasheadas con SHA256
- Sesiones gestionadas por Streamlit
- BD SQLite local (no expuesta)
- Reportes guardados en servidor

---

**¡LISTO PARA COMENZAR! 🚀**

Ejecuta los 4 pasos y tendrás un sistema agrícola completo funcional en 2.5 minutos.
