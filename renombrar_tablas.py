import pymysql

# Conectar a la base de datos
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='proyectointegradodb'
)

cursor = conn.cursor()

# Tablas a renombrar
tablas_renombrar = [
    ('proyectoapp_favorito', 'core_favorito'),
    ('proyectoapp_pedido', 'core_pedido'),
    ('proyectoapp_producto', 'core_producto'),
    ('proyectoapp_resenadeproducto', 'core_resenadeproducto'),
    ('proyectoapp_resenadetienda', 'core_resenadetienda'),
    ('proyectoapp_tienda', 'core_tienda'),
]

# Eliminar tablas core duplicadas si existen
tablas_eliminar = ['core_categoria', 'core_perfil', 'core_notificacion']
for tabla in tablas_eliminar:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {tabla}")
        print(f"Eliminada tabla duplicada: {tabla}")
    except Exception as e:
        print(f"Error eliminando {tabla}: {e}")

# Renombrar tablas de proyectoapp_ a core_
tablas_renombrar_completo = [
    ('proyectoapp_categoria', 'core_categoria'),
    ('proyectoapp_perfil', 'core_perfil'),
    ('proyectoapp_notificacion', 'core_notificacion'),
] + tablas_renombrar

for old_name, new_name in tablas_renombrar_completo:
    try:
        cursor.execute(f"RENAME TABLE {old_name} TO {new_name}")
        print(f"Renombrada: {old_name} -> {new_name}")
    except Exception as e:
        print(f"Error renombrando {old_name}: {e}")

conn.commit()
cursor.close()
conn.close()

print("\n¡Renombrado completado!")
