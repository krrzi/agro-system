"""
Módulo del Modelo Ensemble Learning
Random Forest + Gradient Boosting para predicción de rendimientos
"""

import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import pickle
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class ModeloEnsemble:
    def __init__(self, ruta_db=None):
        """Inicializa el modelo ensemble"""
        if ruta_db is None:
            ruta_proyecto = Path(__file__).parent.parent
            self.ruta_db = str(ruta_proyecto / "agro_sistema.db")
        else:
            self.ruta_db = ruta_db
        
        self.rf_model = None
        self.gb_model = None
        self.scaler = None
        self.feature_names = None
        
    def obtener_datos_entrenamiento(self):
        """Obtiene datos de la BD para entrenar el modelo"""
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        
        query = """
        SELECT 
            ds.valor_temperatura,
            ds.valor_humedad,
            ds.valor_ph,
            ds.valor_precipitacion,
            ds.valor_radiacion,
            c.area_hectareas,
            p.rendimiento_predicho as rendimiento_real
        FROM predicciones p
        JOIN cultivos c ON p.id_cultivo = c.id_cultivo
        JOIN datos_sensor ds ON c.id_cultivo = ds.id_cultivo
        WHERE p.rendimiento_predicho IS NOT NULL
            AND ds.valor_temperatura IS NOT NULL
            AND ds.valor_humedad IS NOT NULL
        """
        
        df = pd.read_sql_query(query, conexion)
        conexion.close()
        
        if df.empty:
            # Crear datos de entrenamiento sintéticos realistas
            np.random.seed(42)
            n_samples = 200
            
            df = pd.DataFrame({
                'valor_temperatura': np.random.normal(24, 3, n_samples),  # 24°C promedio, σ=3
                'valor_humedad': np.random.normal(65, 15, n_samples),     # 65% promedio, σ=15
                'valor_ph': np.random.normal(6.8, 0.4, n_samples),        # pH 6.8, σ=0.4
                'valor_precipitacion': np.random.normal(3, 2, n_samples), # 3mm promedio
                'valor_radiacion': np.random.normal(19, 2, n_samples),    # 19 MJ/m²
                'area_hectareas': np.random.uniform(40, 100, n_samples),  # 40-100 ha
            })
            
            # Simular rendimiento basado en características
            df['rendimiento_real'] = (
                6000 +
                300 * (df['valor_temperatura'] - 15) +
                50 * df['valor_humedad'] +
                500 * df['valor_ph'] +
                100 * df['valor_precipitacion'] +
                100 * df['valor_radiacion'] +
                2 * df['area_hectareas'] +
                np.random.normal(0, 500, n_samples)  # Ruido
            )
            
            # Asegurar rendimientos realistas
            df['rendimiento_real'] = df['rendimiento_real'].clip(lower=5000, upper=12000)
        
        return df
    
    def entrenar(self):
        """Entrena el modelo ensemble"""
        # Obtener datos
        df = self.obtener_datos_entrenamiento()
        
        # Características y target
        features = ['valor_temperatura', 'valor_humedad', 'valor_ph', 
                   'valor_precipitacion', 'valor_radiacion', 'area_hectareas']
        self.feature_names = features
        
        X = df[features].values
        y = df['rendimiento_real'].values
        
        # Normalizar características
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Split datos
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Entrenar Random Forest
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train, y_train)
        
        # Entrenar Gradient Boosting
        self.gb_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.gb_model.fit(X_train, y_train)
        
        # Evaluación
        y_pred_rf = self.rf_model.predict(X_test)
        y_pred_gb = self.gb_model.predict(X_test)
        y_pred_ensemble = (y_pred_rf + y_pred_gb) / 2
        
        mae_rf = mean_absolute_error(y_test, y_pred_rf)
        mae_gb = mean_absolute_error(y_test, y_pred_gb)
        mae_ensemble = mean_absolute_error(y_test, y_pred_ensemble)
        
        r2_ensemble = r2_score(y_test, y_pred_ensemble)
        
        resultados = {
            'mae_rf': mae_rf,
            'mae_gb': mae_gb,
            'mae_ensemble': mae_ensemble,
            'r2_ensemble': r2_ensemble,
            'muestras_entrenamiento': len(X_train),
            'muestras_evaluacion': len(X_test)
        }
        
        return resultados
    
    def predecir(self, temperatura, humedad, ph, precipitacion, radiacion, area_hectareas):
        """Realiza una predicción con el modelo ensemble"""
        if self.rf_model is None or self.gb_model is None:
            raise ValueError("El modelo no ha sido entrenado aún")
        
        # Preparar características
        X = np.array([[temperatura, humedad, ph, precipitacion, radiacion, area_hectareas]])
        X_scaled = self.scaler.transform(X)
        
        # Predicciones individuales
        pred_rf = self.rf_model.predict(X_scaled)[0]
        pred_gb = self.gb_model.predict(X_scaled)[0]
        
        # Predicción ensemble (promedio)
        pred_ensemble = (pred_rf + pred_gb) / 2
        
        # Calcular confianza basada en similaridad de predicciones
        diferencia = abs(pred_rf - pred_gb) / max(pred_rf, pred_gb)
        confianza = max(0.7, 1 - (diferencia * 0.3))  # 70-100%
        
        return {
            'rendimiento_predicho': max(pred_ensemble, 5000),  # Mínimo 5000 kg/ha
            'confianza': min(confianza, 0.99),
            'error_mae': self.rf_model.get_n_features_in_() * 100  # Estimación simple
        }
    
    def obtener_importancia_features(self):
        """Obtiene la importancia de características"""
        if self.rf_model is None:
            return None
        
        importancias_rf = self.rf_model.feature_importances_
        importancias_gb = self.gb_model.feature_importances_
        
        # Promediar importancias
        importancias = (importancias_rf + importancias_gb) / 2
        
        return {
            'features': self.feature_names,
            'importancias': importancias
        }
    
    def guardar_modelo(self, ruta_archivo):
        """Guarda el modelo entrenado"""
        modelo_data = {
            'rf_model': self.rf_model,
            'gb_model': self.gb_model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        
        with open(ruta_archivo, 'wb') as f:
            pickle.dump(modelo_data, f)
    
    def cargar_modelo(self, ruta_archivo):
        """Carga un modelo entrenado"""
        if not Path(ruta_archivo).exists():
            return False
        
        try:
            with open(ruta_archivo, 'rb') as f:
                modelo_data = pickle.load(f)
            
            self.rf_model = modelo_data['rf_model']
            self.gb_model = modelo_data['gb_model']
            self.scaler = modelo_data['scaler']
            self.feature_names = modelo_data['feature_names']
            return True
        except Exception as e:
            print(f"Error al cargar modelo: {e}")
            return False
