import sqlite3
import hashlib

conn = sqlite3.connect('agro_sistema.db')
pwd = hashlib.sha256('admin123'.encode()).hexdigest()

conn.execute(
    "INSERT OR IGNORE INTO usuarios (usuario, contrasena, nombre, email, activo) VALUES ('admin', ?, 'Administrador', 'admin@agro.com', 1)",
    (pwd,)
)
conn.commit()
conn.close()
print('Usuario creado exitosamente: admin / admin123')
