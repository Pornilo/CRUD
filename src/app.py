from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'promart.mysql.database.azure.com'  
app.config['MYSQL_USER'] = 'azuremysql' 
app.config['MYSQL_PASSWORD'] = '@admin123'  
app.config['MYSQL_DB'] = 'promart'  

def conectar_db():
    return pymysql.connect(host=app.config['MYSQL_HOST'],
                           user=app.config['MYSQL_USER'],
                           password=app.config['MYSQL_PASSWORD'],
                           db=app.config['MYSQL_DB'])

@app.route('/')
def index():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("SELECT productos.id, productos.nombre, productos.descripcion, productos.precio, categorias.descripcion AS categoria_descripcion FROM productos INNER JOIN categorias ON productos.categoria_id = categorias.id")
    productos = cursor.fetchall()
    db.close()
    return render_template('index.html', productos=productos)


@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        categoria_descripcion = request.form['categoria_descripcion']  # Obtener la descripción de la categoría del formulario
        db = conectar_db()
        cursor = db.cursor()
        # Buscar el ID de la categoría basado en la descripción
        cursor.execute("SELECT id FROM categorias WHERE descripcion = %s", (categoria_descripcion,))
        categoria_id = cursor.fetchone()[0]  # Obtener el ID de la categoría
        cursor.execute("INSERT INTO productos (nombre, descripcion, precio, categoria_id) VALUES (%s, %s, %s, %s)", (nombre, descripcion, precio, categoria_id))
        db.commit()
        db.close()
        return redirect(url_for('index'))
    else:
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("SELECT descripcion FROM categorias")
        categorias = cursor.fetchall()
        db.close()
        return render_template('nuevo_producto.html', categorias=categorias)


@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    db = conectar_db()
    cursor = db.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        categoria_id = request.form['categoria_id']
        cursor.execute("UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, categoria_id=%s WHERE id=%s", (nombre, descripcion, precio, categoria_id, id))
        db.commit()
        db.close()
        return redirect(url_for('index'))
    cursor.execute("SELECT * FROM productos WHERE id=%s", (id,))
    producto = cursor.fetchone()
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    db.close()
    return render_template('editar_producto.html', producto=producto, categorias=categorias)

@app.route('/productos/eliminar/<int:id>')
def eliminar_producto(id):
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM productos WHERE id=%s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
