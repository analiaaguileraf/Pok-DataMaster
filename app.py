from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = "pokemon"

DB_HOST = "localhost"
DB_NAME = "Pokemon"
DB_USER = "postgres"
DB_PASS = "123456"
DB_PORT = "5433"  

# Crear un cursor para ejecutar consultas
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    options='-c client_encoding=UTF8'
)

@app.route('/')
def index():
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM entrenadores")
        entrenadores = cur.fetchall()
        cur.execute("SELECT * FROM pokemones")
        pokemones = cur.fetchall()
        cur.execute("""
            SELECT b.id, e1.nombre AS entrenador1, e2.nombre AS entrenador2, g.nombre AS ganador, b.fecha
            FROM batallas b
            JOIN entrenadores e1 ON b.entrenadores_id_1 = e1.id
            JOIN entrenadores e2 ON b.entrenadores_id_2 = e2.id
            JOIN entrenadores g ON b.ganador_id = g.id
        """)
        resultados = cur.fetchall()
        cur.close()
    except psycopg2.Error as e:
        flash(f'Error al obtener los datos: {e}', 'danger')
        entrenadores = []
        pokemones = []
        resultados = []
    return render_template('index.html', entrenadores=entrenadores, pokemones=pokemones, resultados=resultados)
# registrar entrenador 
@app.route('/registrar_entrenador', methods=['POST'])
def registrar_entrenador():
    if request.method == 'POST':
        nombre = request.form['nombre']
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("INSERT INTO entrenadores (nombre) VALUES (%s)", (nombre,))
            conn.commit()
            cur.close()
            flash('Entrenador registrado', 'success')
        except psycopg2.Error as e:
            conn.rollback()
            flash(f'Error al registrar el entrenador: {e}', 'danger')
        return redirect(url_for('index'))
# ruta para editar entrenador
@app.route('/editar_entrenador/<int:id>', methods=['POST'])
def editar_entrenador(id):
    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("UPDATE entrenadores SET nombre = %s WHERE id = %s", (nuevo_nombre, id))
            conn.commit()
            cur.close()
            flash('Entrenador actualizado', 'success')
        except psycopg2.Error as e:
            conn.rollback()
            flash(f'Error al actualizar el entrenador: {e}', 'danger')
        return redirect(url_for('index'))

@app.route('/eliminar_entrenador/<int:id>', methods=['POST'])
def eliminar_entrenador(id):
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Eliminar registros relacionados
        cur.execute("DELETE FROM entrenador_pokes WHERE entrenadores_id = %s", (id,))
        cur.execute("DELETE FROM equipos WHERE entrenador_id = %s", (id,))
        cur.execute("DELETE FROM batallas WHERE entrenadores_id_1 = %s OR entrenadores_id_2 = %s OR ganador_id = %s", (id, id, id))
        # Eliminar entrenador
        cur.execute("DELETE FROM entrenadores WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        flash('Entrenador eliminado', 'success')
    except psycopg2.Error as e:
        conn.rollback()
        flash(f'Error al eliminar el entrenador: {e}', 'danger')
    return redirect(url_for('index'))

@app.route('/asignar_pokemon', methods=['POST'])
def asignar_pokemon():
    if request.method == 'POST':
        entrenador_id = request.form['entrenador_id']
        pokemon_id = request.form['pokemon_id']
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("INSERT INTO entrenador_pokes (entrenadores_id, pokemones_id) VALUES (%s, %s)", (entrenador_id, pokemon_id))
            conn.commit()
            cur.close()
            flash('Pokémon asignado al entrenador', 'success')
        except psycopg2.Error as e:
            conn.rollback()
            flash(f'Error al asignar el Pokémon: {e}', 'danger')
        return redirect(url_for('index'))

@app.route('/registrar_batalla', methods=['POST'])
def registrar_batalla():
    if request.method == 'POST':
        entrenador1_id = request.form['entrenador1_id']
        entrenador2_id = request.form['entrenador2_id']
        ganador_id = request.form['ganador_id']
        fecha = request.form['fecha']
        
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("INSERT INTO batallas (entrenadores_id_1, entrenadores_id_2, ganador_id, fecha) VALUES (%s, %s, %s, %s)", 
                        (entrenador1_id, entrenador2_id, ganador_id, fecha))
            conn.commit()
            cur.close()
            flash('Batalla registrada', 'success')
        except psycopg2.Error as e:
            conn.rollback()
            flash(f'Error al registrar la batalla: {e}', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
