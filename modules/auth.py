"""
Módulo de autenticación y manejo de sesiones
Integración con streamlit-authenticator
"""

import sqlite3
import hashlib
from pathlib import Path
import streamlit as st
import streamlit_authenticator as stauth

def obtener_ruta_db():
    """Obtiene la ruta de la base de datos"""
    ruta_proyecto = Path(__file__).parent.parent
    return str(ruta_proyecto / "agro_sistema.db")

def hash_contraseña(contraseña):
    """Genera hash SHA256 de la contraseña"""
    return hashlib.sha256(contraseña.encode()).hexdigest()

def crear_usuario(usuario, contraseña, nombre, email):
    """Crea un nuevo usuario en la base de datos"""
    conexion = sqlite3.connect(obtener_ruta_db())
    cursor = conexion.cursor()
    
    try:
        contraseña_hash = hash_contraseña(contraseña)
        cursor.execute(
            """INSERT INTO usuarios (usuario, contrasena, nombre, email) 
               VALUES (?, ?, ?, ?)""",
            (usuario, contraseña_hash, nombre, email)
        )
        conexion.commit()
        return True, "Usuario creado exitosamente"
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            return False, "El usuario o email ya existe"
        return False, f"Error: {str(e)}"
    finally:
        conexion.close()

def verificar_usuario(usuario, contraseña):
    """Verifica credenciales del usuario"""
    conexion = sqlite3.connect(obtener_ruta_db())
    cursor = conexion.cursor()
    
    contraseña_hash = hash_contraseña(contraseña)
    cursor.execute(
        """SELECT id_usuario, nombre, email, activo 
           FROM usuarios 
           WHERE usuario = ? AND contrasena = ?""",
        (usuario, contraseña_hash)
    )
    
    resultado = cursor.fetchone()
    conexion.close()
    
    if resultado and resultado[3]:  # resultado[3] es 'activo'
        return True, {
            'id': resultado[0],
            'nombre': resultado[1],
            'email': resultado[2]
        }
    return False, None

def obtener_usuario_por_id(id_usuario):
    """Obtiene información del usuario por ID"""
    conexion = sqlite3.connect(obtener_ruta_db())
    cursor = conexion.cursor()
    
    cursor.execute(
        """SELECT id_usuario, usuario, nombre, email, fecha_creacion 
           FROM usuarios WHERE id_usuario = ?""",
        (id_usuario,)
    )
    
    resultado = cursor.fetchone()
    conexion.close()
    
    if resultado:
        return {
            'id': resultado[0],
            'usuario': resultado[1],
            'nombre': resultado[2],
            'email': resultado[3],
            'fecha_creacion': resultado[4]
        }
    return None

def inicializar_sesion():
    """Inicializa variables de sesión"""
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.id_usuario = None
        st.session_state.usuario = None
        st.session_state.nombre_usuario = None
        st.session_state.email_usuario = None

def realizar_login(usuario, contraseña):
    """Realiza el login del usuario"""
    valido, info = verificar_usuario(usuario, contraseña)
    
    if valido:
        st.session_state.autenticado = True
        st.session_state.id_usuario = info['id']
        st.session_state.usuario = usuario
        st.session_state.nombre_usuario = info['nombre']
        st.session_state.email_usuario = info['email']
        return True, "Login exitoso"
    else:
        return False, "Usuario o contraseña incorrectos"

def realizar_logout():
    """Cierra la sesión del usuario"""
    st.session_state.autenticado = False
    st.session_state.id_usuario = None
    st.session_state.usuario = None
    st.session_state.nombre_usuario = None
    st.session_state.email_usuario = None

def estoy_autenticado():
    """Verifica si el usuario está autenticado"""
    return st.session_state.get('autenticado', False)

def obtener_id_usuario_actual():
    """Obtiene el ID del usuario autenticado"""
    return st.session_state.get('id_usuario', None)

def obtener_nombre_usuario_actual():
    """Obtiene el nombre del usuario autenticado"""
    return st.session_state.get('nombre_usuario', None)
