import requests
import psycopg2

# Conectar a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname='Pokemon',
    user='postgres',
    password='123456',
    host='localhost',
    port='5433',  # Asegúrate de que este es el puerto correcto
    options='-c client_encoding=UTF8'
)

# Crear un cursor para ejecutar consultas
cursor = conn.cursor()

def cargar_pokemon(id):
    """Carga información de un Pokémon desde la API y la guarda en la base de datos."""
    api_url = f"https://pokeapi.co/api/v2/pokemon/{id}/"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()

        # Obtener datos del Pokémon
        pokemon_name = data.get('name')
        pokemon_number = data.get('id')
        pokemon_type = data['types'][0]['type']['name']
        pokemon_move = data['moves'][0]['move']['name']
        pokemon_image = data['sprites']['front_default']

        try:
            # Insertar datos del Pokémon en la base de datos
            cursor.execute("""
            INSERT INTO pokemones (nombre, tipo, habilidad, numero, imagen)
            VALUES (%s, %s, %s, %s, %s)
            """, (pokemon_name, pokemon_type, pokemon_move, pokemon_number, pokemon_image))
            conn.commit()  # Confirmar la transacción
            print(f"Pokémon {pokemon_name} (ID: {pokemon_number}) guardado correctamente.")
        
        except psycopg2.Error as e:
            print(f"Error al guardar el Pokémon {pokemon_name} (ID: {pokemon_number}): {e}")
            conn.rollback()  # Deshacer cambios en caso de error

    else:
        print(f"Falló la carga del Pokémon ID: {id}. Status code: {response.status_code}")

# Cargar Pokémon desde el ID 3 hasta el 151
for i in range(3, 152):
    cargar_pokemon(i)

# Cerrar el cursor y la conexión a la base de datos
cursor.close()
conn.close()
