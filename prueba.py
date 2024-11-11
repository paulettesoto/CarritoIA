import pymysql
from pyDatalog import pyDatalog
import os
from dotenv import load_dotenv

load_dotenv(override=True)
# Definir términos (hechos y variables)
pyDatalog.create_terms('alergicoa, plato, ingrediente, X, Y, Z, Ingrediente, Platillo, plato_tiene_ingrediente, ver_ingredientes, tendra_alergia, Cliente')

# Conectar a la base de datos MySQL
def conectar_db():
    return pymysql.connect(
        host = os.getenv('HOST_DB'),          
        user = os.getenv('USER_DB'),               
        password = os.getenv('PSWRD_DB'),      
        database = os.getenv('DB_NAME'), 
        port = int(os.getenv('DB_PORT')),     
        cursorclass =pymysql.cursors.DictCursor 
    )

# Cargar platos desde la base de datos
def cargar_platos():
    connection = conectar_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nombre, descripcion, precio FROM Platos")
        platos = cursor.fetchall()
        for plato_data in platos:
            plato(plato_data['nombre'], plato_data['descripcion'], plato_data['precio'])
    connection.close()

# Cargar ingredientes desde la base de datos
def cargar_ingredientes():
    connection = conectar_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre FROM Ingredientes")
        ingredientes = cursor.fetchall()
        for ingrediente_data in ingredientes:
            ingrediente(ingrediente_data['nombre'])
    connection.close()

# Cargar la relación entre platos e ingredientes
def cargar_ingredientes_por_plato():
    connection = conectar_db()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT P.nombre as plato_nombre, I.nombre as ingrediente_nombre
            FROM Ingredientes_por_Plato IP
            INNER JOIN Platos P ON P.id = IP.plato_id
            INNER JOIN Ingredientes I ON I.id = IP.ingrediente_id
        """)
        relaciones = cursor.fetchall()
        for relacion in relaciones:
            plato_tiene_ingrediente(relacion['plato_nombre'], relacion['ingrediente_nombre'])
            #print(f"Hecho insertado: {relacion['plato_nombre']} -> {relacion['ingrediente_nombre']}")
    connection.close()

# Alergias de las personas (esto se puede agregar desde la base de datos también si tienes una tabla)
def cargar_alergias():
    alergicoa('Juan', 'Pepino')  # Ejemplo de alergia (esto podría ser cargado desde una tabla)
    alergicoa('Ana', 'Tomate')

# Regla para obtener ingredientes de un platillo
ver_ingredientes(Platillo) <= plato_tiene_ingrediente(Platillo, Ingrediente)

# Regla para verificar si un cliente tiene alergia a algún ingrediente de un platillo
tendra_alergia(Cliente, Platillo) <= (
    plato_tiene_ingrediente(Platillo, Ingrediente) & alergicoa(Cliente, Ingrediente)
)

# Función para verificar alergias
def verificar_alergias(cliente, platillo):
    if tendra_alergia(cliente, platillo):
        print(f"{cliente} es alérgico a uno o más ingredientes en el platillo {platillo}.")
    else:
        print(f"{cliente} no tiene alergias a ningún ingrediente en el platillo {platillo}.")

# Función para listar ingredientes de un platillo
def listar_ingredientes(platillo):
    ingredientes = list(ver_ingredientes(platillo, X))
    if ingredientes:
        print(f"Ingredientes de {platillo}: {', '.join([i[0] for i in ingredientes])}")
    else:
        print(f"No se encontraron ingredientes para el platillo {platillo}.")
        
# Función para obtener el platillo con menor precio desde la base de datos
def platillo_con_menor_precio():
    connection = conectar_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre, precio FROM Platos ORDER BY precio ASC LIMIT 1")
        resultado = cursor.fetchone()
    connection.close()
    if resultado:
        print(f"Platillo con menor precio: {resultado['nombre']} - Precio: {resultado['precio']}")
    else:
        print("No se encontró el platillo con el menor precio.")

# Función para obtener el platillo con mayor precio desde la base de datos
def platillo_con_mayor_precio():
    connection = conectar_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre, precio FROM Platos ORDER BY precio DESC LIMIT 1")
        resultado = cursor.fetchone()
    connection.close()
    if resultado:
        print(f"Platillo con mayor precio: {resultado['nombre']} - Precio: {resultado['precio']}")
    else:
        print("No se encontró el platillo con el mayor precio.")

# Cargar los datos
cargar_platos()
cargar_ingredientes()
cargar_ingredientes_por_plato()
cargar_alergias()

# Ejemplo de uso de la regla de alergias y consulta de ingredientes
print("Verificando alergias para Juan:")
verificar_alergias('Juan', 'Ensalada')  # Aquí, 'Juan' tiene alergia al pepino y la ensalada lo contiene.

print("\nIngredientes de la Ensalada:")
listar_ingredientes('Ensalada')  # Ver los ingredientes de la ensalada

# Consultar el platillo con menor precio
platillo_con_menor_precio()

# Consultar el platillo con mayor precio
platillo_con_mayor_precio()