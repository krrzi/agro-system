# 🚀 PRIMEROS PASOS - COMIENZA AQUÍ

## 👋 Bienvenido al Sistema Agrícola de Precisión

Este archivo te guía paso a paso para comenzar a usar el sistema.

---

## 📋 QUICKSTART (2.5 MINUTOS)

### 1️⃣ Abre una terminal en la carpeta del proyecto

```bash
# Navega a la carpeta
cd "LAB 04/agro_system"
```

### 2️⃣ Copia y pega estos comandos (uno por uno)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
python database/init_db.py

# Ejecutar aplicación
streamlit run app.py
```

### 3️⃣ Verifica que aparezca esto en la terminal

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

### 4️⃣ Usa estas credenciales para entrar

- **Usuario:** `usuario1`
- **Contraseña:** `pass123`

---

## ✅ VERIFICACIÓN RÁPIDA

Antes de nada, verifica que todo está bien:

```bash
python verificar_sistema.py
```

Deberías ver: ✅ Todos los módulos OK

---

## 📁 ¿QUÉ HAY EN CADA CARPETA?

```
agro_system/
├── app.py                  ← Ejecuta esto: streamlit run app.py
├── requirements.txt        ← pip install -r requirements.txt
├── verificar_sistema.py    ← python verificar_sistema.py (opcional)
│
├── database/               ← Base de datos SQLite
│   ├── schema.sql         (Esquema SQL)
│   └── init_db.py         (Crear BD con datos)
│
├── modules/               ← Lógica de la aplicación
│   ├── auth.py           (Login)
│   ├── dashboard.py       (Gráficos y KPIs)
│   ├── prediccion.py      (Rendimientos)
│   ├── optimizacion.py    (Agua)
│   └── reportes.py        (PDFs)
│
├── models/                ← Machine Learning
│   └── ensemble_model.py  (Random Forest + Gradient Boosting)
│
└── docs/
    ├── README.md                 ← Lee esto para más info
    ├── DESPLIEGUE_RAPIDO.md      ← Guía detallada
    ├── RESUMEN_PROYECTO.md       ← Resumen ejecutivo
    └── CHECKLIST_VALIDACION.md   ← Verificación completa
```

---

## 🎯 SECCIONES DE LA APLICACIÓN

Una vez dentro con login, verás estas secciones:

### 📊 Dashboard
- 5 métricas principales (cultivos, área, sensores, predicciones)
- 4 gráficos interactivos
- Tabla de cultivos
- Estadísticas descriptivas

### 🌾 Mis Cultivos
- Lista de tus cultivos
- Información detallada

### 🔮 Predicciones
- Predecir rendimiento de un cultivo
- Ver historial
- Importancia de características

### 💧 Optimización Hídrica
- Calcular agua recomendada
- Ver ahorro potencial
- Gauge de eficiencia

### 📄 Reportes
- Descargar reporte operacional (PDF)
- Descargar reporte de gestión (PDF)

### ℹ️ Sistema ML
- Info del modelo Ensemble
- Características utilizadas
- Métricas de desempeño

---

## 🔑 DATOS DE PRUEBA PRECARGADOS

La aplicación ya tiene datos listos para usar:

| Tipo | Cantidad | Detalles |
|------|----------|----------|
| Usuarios | 4 | usuario1, usuario2, usuario3, admin |
| Cultivos | 6 | Maíz, Trigo, Soja |
| Sensores | 10 | Temp, Humedad, pH, Radiación |
| Lecturas | 18+ | Datos reales de sensores |
| Predicciones | 6 | Rendimientos predichos |
| Análisis | 5 | Optimización hídrica |

**Todo listo para experimentar sin configurar nada más.**

---

## 🐛 SI ALGO FALLA

### Error: "No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### Error: "BD not found"
```bash
python database/init_db.py
```

### Puerto 8501 en uso
```bash
streamlit run app.py --server.port 8502
```

### No abre el navegador
Abre manualmente: `http://localhost:8501`

---

## 📚 DOCUMENTACIÓN

Hay 4 documentos importantes:

1. **README.md** - Descripción general y guía completa
2. **DESPLIEGUE_RAPIDO.md** - 4 pasos de despliegue
3. **RESUMEN_PROYECTO.md** - Resumen ejecutivo
4. **CHECKLIST_VALIDACION.md** - Verificación línea por línea

---

## 🎓 CONCEPTOS CLAVE

### Modelo Machine Learning
- **Tipo:** Ensemble Learning
- **Componentes:** Random Forest + Gradient Boosting
- **Función:** Predecir rendimiento (kg/ha) de cultivos
- **Confianza:** 70-99%

### Base de Datos
- **Tipo:** SQLite (sin servidor)
- **Tablas:** 8 principales
- **Datos:** 30+ registros de ejemplo

### Stack
- **Frontend:** Streamlit
- **Backend:** Python puro
- **ML:** scikit-learn
- **PDF:** ReportLab
- **BD:** SQLite

---

## ⏱️ TIMELINE

```
0 min  → Terminal abierta en carpeta proyecto
2 min  → Entorno virtual activado + dependencias instaladas
2.1 min → BD creada con datos de ejemplo
2.5 min → App ejecutándose en http://localhost:8501
2.6 min → Login exitoso con usuario1/pass123
2.7 min → ¡Usando el sistema!
```

---

## 🚀 PRÓXIMO PASO

```bash
streamlit run app.py
```

¡Eso es todo! El sistema está listo para usar.

---

## 💡 TIPS

1. **Dashboard:** Muestra gráficos interactivos - haz zoom, desplaza, exporta
2. **Predicciones:** Pulsa botón "Realizar Predicción" para ver en vivo
3. **Reportes:** Descarga PDFs profesionales directamente desde la app
4. **Sensores:** Los datos se actualizan automáticamente
5. **Terminal:** Déjala abierta mientras uses la app

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Necesito internet?**
R: No para la app local. Sí para Streamlit Cloud si la deploys.

**P: ¿Puedo cambiar los datos de ejemplo?**
R: Sí, modifica `database/schema.sql` e inicializa de nuevo.

**P: ¿Cómo agrego más cultivos?**
R: Desde la sección "Mis Cultivos" (funcionalidad lista para expandir).

**P: ¿Puedo desplegar en internet?**
R: Sí, usa Streamlit Community Cloud (gratis).

**P: ¿Qué versión de Python necesito?**
R: Python 3.8 o superior.

---

## 📞 SOPORTE

Si tienes problemas:
1. Lee README.md
2. Ejecuta `python verificar_sistema.py`
3. Revisa DESPLIEGUE_RAPIDO.md (Troubleshooting)

---

**¡Ahora estás listo! 🎉**

Ejecuta `streamlit run app.py` y comienza a explorar.

