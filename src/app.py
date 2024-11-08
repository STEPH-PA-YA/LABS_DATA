from flask import Flask, render_template, request, redirect, url_for, flash
from config import config
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask import send_file
from utils import generate_maintenance_report

# Models
from models.ModelUser import ModelUser
from models.ModelRol import ModelRol
from models.ModelLab import ModelLaboratorio, Laboratorio
from models.ModelCarrera import ModelCarrera
from models.ModelAsignacion import ModelAsignacion
from models.ModelEquipo import ModelEquipo, Equipo
from models.ModelMantenimiento import ModelMantenimiento

app = Flask(__name__)

csrf=CSRFProtect()

db = MySQL(app)


login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

@app.route('/')
def index():
    return redirect(url_for('login'))
#USUARIOS
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            user = ModelUser.login(db, username, password)
            
            if user:
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("Credenciales inválidas")
            
        except Exception as ex:
            flash(str(ex))
        
        return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username'].strip()
            password = request.form['password'].strip()
            fullname = request.form.get('fullname', '').strip()
            rol_id = request.form.get('rol_id')  
            
            if not username or not password:
                flash("El usuario y la contraseña son requeridos")
                return render_template('auth/register.html')
            
            success, message = ModelUser.register(db, fullname, username, password, rol_id)
            
            if success:
                flash(message)
                return redirect(url_for('login'))
            else:
                flash(message)
            
        except Exception as ex:
            flash(str(ex))
        
        return render_template('auth/register.html')
    
    roles = ModelRol.get_roles_for_dropdown(db)
    return render_template('auth/register.html', roles=roles)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            fullname = request.form.get('fullname')
            username = request.form.get('username')
            password = request.form.get('password')
            
            success, message = ModelUser.update_user(
                db, 
                current_user.id,
                fullname=fullname,
                username=username,
                password=password if password else None
            )
            
            if success:
                flash("Perfil actualizado exitosamente", "success")
                return redirect(url_for('profile'))
            else:
                flash(message, "danger")
            
        except Exception as ex:
            flash(str(ex), "danger")
    rol_nombre = ModelRol.get_name_rol(db, current_user.rol_id)
    if rol_nombre is None:
        rol_nombre = "Rol no encontrado"
    
    return render_template('dashboard/profile.html', rol_nombre=rol_nombre)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    # Obtener total de laboratorios
    total_laboratorios = ModelLaboratorio.get_total_laboratorios(db)
    
    # Obtener total de equipos disponibles
    total_equipos = ModelEquipo.get_total_equipos(db)
    
    # Obtener mantenimientos programados
    mantenimientos_programados = ModelMantenimiento.get_total_mantenimientos_programados(db)
    
    # Actividad reciente (lo que ya tenías)
    mantenimientos_realizados = ModelMantenimiento.get_total_mantenimientos_realizados(db)
    
    return render_template('home.html', 
        total_laboratorios=total_laboratorios,
        total_equipos=total_equipos,
        mantenimientos_programados=mantenimientos_programados,
        mantenimientos_realizados=mantenimientos_realizados
    )
#LABORATORIOS

@app.route('/laboratorios')
@login_required
def laboratorios():
    user_id = current_user.id
    user_rol = current_user.rol_id
    laboratorios = ModelLaboratorio.get_laboratorios(db, user_id, user_rol)
    return render_template('dashboard/laboratorios.html', laboratorios=laboratorios)

@app.route('/eliminar_laboratorio/<int:id>')
@login_required
def eliminar_laboratorio(id):
    ModelLaboratorio.eliminar_laboratorio(db, id)
    return redirect(url_for('laboratorios'))

@app.route('/agregar_laboratorio', methods=['GET', 'POST'])
@login_required
def agregar_laboratorio():
    if request.method == 'POST':
        laboratorio = Laboratorio(
            id=None,  # El id será asignado por la base de datos
            nombre=request.form['nombre'],
            ubicacion=request.form['ubicacion'],
            carrera_id=request.form['carrera_id']
        )
        ModelLaboratorio.agregar_laboratorio(db, laboratorio)
        return redirect(url_for('laboratorios'))
    
    carreras = ModelCarrera.get_carreras_for_dropdown(db)
    return render_template('dashboard/agregar_laboratorio.html', carreras=carreras)


@app.route('/editar_laboratorio/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_laboratorio(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        ubicacion = request.form['ubicacion']
        carrera_id = request.form['carrera_id']
        
        # Imprime para debug
        print(f"carrera_id recibido: {carrera_id}")
        
        laboratorio = Laboratorio(id, nombre, ubicacion, carrera_id)
        ModelLaboratorio.editar_laboratorio(db, laboratorio)
        flash('Laboratorio actualizado con éxito', 'success')
        return redirect(url_for('laboratorios'))
    
    laboratorio = ModelLaboratorio.obtener_laboratorio(db, id)
    carreras = ModelCarrera.get_carreras_for_dropdown(db)
    return render_template('dashboard/editar_laboratorio.html', laboratorio=laboratorio, carreras=carreras)
#Asignar laboratorios

@app.route('/asignaciones')
@login_required
def asignaciones():
    if current_user.rol_id != 1:  # Asumiendo que 1 es el rol de administrador
        flash("No tiene permisos para acceder a esta página")
        return redirect(url_for('home'))
    
    asignaciones = ModelAsignacion.get_asignaciones(db)
    return render_template('dashboard/asignaciones.html', asignaciones=asignaciones)

@app.route('/agregar_asignacion', methods=['GET', 'POST'])
@login_required
def agregar_asignacion():
    if current_user.rol_id != 1:
        flash("No tiene permisos para acceder a esta página")
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        asistente_id = request.form['asistente_id']
        laboratorio_id = request.form['laboratorio_id']
        
        try:
            ModelAsignacion.agregar_asignacion(db, asistente_id, laboratorio_id)
            flash("Asignación agregada exitosamente")
            return redirect(url_for('asignaciones'))
        except Exception as ex:
            flash(str(ex))
    
    asistentes = ModelUser.get_all_asistentes(db)
    laboratorios = ModelLaboratorio.get_all_labs(db)
    return render_template('dashboard/agregar_asignacion.html', asistentes=asistentes, laboratorios=laboratorios)

@app.route('/eliminar_asignacion/<int:id>')
@login_required
def eliminar_asignacion(id):
    if current_user.rol_id != 1:
        flash("No tiene permisos para acceder a esta página")
        return redirect(url_for('home'))
    
    try:
        ModelAsignacion.eliminar_asignacion(db, id)
        flash("Asignación eliminada exitosamente")
        return redirect(url_for('asignaciones'))
    except Exception as ex:
        flash(str(ex))
        return redirect(url_for('asignaciones'))

@app.route('/editar_asignacion/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_asignacion(id):
    if current_user.rol_id != 1:
        flash("No tiene permisos para acceder a esta página")
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        asistente_id = request.form['asistente_id']
        laboratorio_id = request.form['laboratorio_id']
        
        try:
            ModelAsignacion.editar_asignacion(db, id, asistente_id, laboratorio_id)
            flash("Asignación actualizada exitosamente")
            return redirect(url_for('asignaciones'))
        except Exception as ex:
            flash(str(ex))
    
    # Obtener la asignación actual
    asignacion = ModelAsignacion.obtener_asignacion(db, id)
    # Obtener las listas para los dropdowns
    asistentes = ModelUser.get_all_asistentes(db)
    laboratorios = ModelLaboratorio.get_all_labs(db)
    
    return render_template('dashboard/editar_asignacion.html', asignacion=asignacion, asistentes=asistentes, laboratorios=laboratorios)

#Equipos
@app.route('/equipos')
@login_required
def equipos():
    user_id = current_user.id
    user_rol = current_user.rol_id
    equipos = ModelEquipo.get_equipos(db, user_id, user_rol)
    return render_template('dashboard/equipos.html', equipos=equipos)

@app.route('/agregar_equipo', methods=['GET', 'POST'])
@login_required
def agregar_equipo():
    if request.method == 'POST':
        equipo = Equipo(
            id=None,
            codigo=request.form['codigo'],
            nombre=request.form['nombre'],
            marca=request.form['marca'],
            modelo=request.form['modelo'],
            serie=request.form['serie'],
            laboratorio_id=request.form['laboratorio_id']
        )
        
        try:
            ModelEquipo.agregar_equipo(db, equipo, current_user.id, current_user.rol_id)
            flash("Equipo agregado exitosamente", "success")
            return redirect(url_for('equipos'))
        except Exception as ex:
            flash(str(ex), "danger")
    
    # Obtener laboratorios disponibles según el rol del usuario
    laboratorios = ModelEquipo.get_laboratorios_disponibles(db, current_user.id, current_user.rol_id)
    return render_template('dashboard/agregar_equipo.html', laboratorios=laboratorios)

@app.route('/editar_equipo/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_equipo(id):
    if request.method == 'POST':
        equipo = Equipo(
            id=id,
            codigo=request.form['codigo'],
            nombre=request.form['nombre'],
            marca=request.form['marca'],
            modelo=request.form['modelo'],
            serie=request.form['serie'],
            laboratorio_id=request.form['laboratorio_id']
        )
        
        try:
            ModelEquipo.editar_equipo(db, equipo, current_user.id, current_user.rol_id)
            flash("Equipo actualizado exitosamente", "success")
            return redirect(url_for('equipos'))
        except Exception as ex:
            flash(str(ex), "danger")
    
    equipo = ModelEquipo.obtener_equipo(db, id, current_user.id, current_user.rol_id)
    if not equipo:
        flash("Equipo no encontrado", "danger")
        return redirect(url_for('equipos'))
    
    laboratorios = ModelEquipo.get_laboratorios_disponibles(db, current_user.id, current_user.rol_id)
    return render_template('dashboard/editar_equipo.html', equipo=equipo, laboratorios=laboratorios)

@app.route('/eliminar_equipo/<int:id>')
@login_required
def eliminar_equipo(id):
    try:
        ModelEquipo.eliminar_equipo(db, id, current_user.id, current_user.rol_id)
        flash("Equipo eliminado exitosamente", "success")
    except Exception as ex:
        flash(str(ex), "danger")
    return redirect(url_for('equipos'))

#Mantenimientos

@app.route('/mantenimientos')
@login_required
def mantenimientos():
    try:
        programaciones = ModelMantenimiento.get_programacion_mantenimiento(db, current_user.id, current_user.rol_id)
        return render_template('dashboard/mantenimiento.html', programaciones=programaciones)
    except Exception as ex:
        flash(str(ex), "danger")
        return redirect(url_for('home'))

@app.route('/programar_mantenimiento', methods=['GET', 'POST'])
@login_required
def programar_mantenimiento():
    # Verificar si el usuario es administrador
    if current_user.rol_id != 1:  # 1 es el rol de administrador
        flash("No tienes permisos para acceder a esta página", "danger")
        return redirect(url_for('mantenimientos'))
        
    if request.method == 'POST':
        try:
            equipo_id = request.form['equipo_id']
            tipo_mantenimiento_id = request.form['tipo_mantenimiento_id']
            anio = request.form['anio']
            mes = request.form['mes']
            
            ModelMantenimiento.programar_mantenimiento(
                db, equipo_id, tipo_mantenimiento_id, anio, mes
            )
            flash("Mantenimiento programado exitosamente", "success")
            return redirect(url_for('mantenimientos'))
        except Exception as ex:
            flash(str(ex), "danger")
    
    # Obtener datos para los dropdowns
    tipos_mantenimiento = ModelMantenimiento.get_tipos_mantenimiento(db)
    equipos = ModelEquipo.get_equipos(db, current_user.id, current_user.rol_id)
    
    return render_template('dashboard/programar_mantenimiento.html',
                         tipos_mantenimiento=tipos_mantenimiento,
                         equipos=equipos)


@app.route('/eliminar_mantenimiento/<int:programacion_id>')
@login_required
def eliminar_mantenimiento(programacion_id):
    try:
        ModelMantenimiento.eliminar_programacion(db, programacion_id, current_user.id, current_user.rol_id)
        flash("Programación de mantenimiento eliminada", "success")
    except Exception as ex:
        flash(str(ex), "danger")
    return redirect(url_for('mantenimientos'))

#### Agregar nueva función

@app.route('/registrar_mantenimiento/<int:programacion_id>', methods=['GET', 'POST'])
@login_required
def registrar_mantenimiento(programacion_id):
    if request.method == 'POST':
        try:
            fecha_realizado = request.form['fecha_realizado']
            realizado_por = request.form['realizado_por']
            observaciones = request.form['observaciones']

            # Actualizar el registro de mantenimiento
            ModelMantenimiento.registrar_mantenimiento(db, programacion_id, fecha_realizado, realizado_por, observaciones, current_user.id)
            flash("Mantenimiento registrado exitosamente", "success")
            return redirect(url_for('mantenimientos'))
        except Exception as ex:
            flash(str(ex), "danger")
    
    # Obtener los datos de la programación de mantenimiento
    programacion = ModelMantenimiento.get_programacion_by_id(db, programacion_id, current_user.id, current_user.rol_id)
    
    if not programacion:
        flash("No se encontró la programación de mantenimiento", "danger")
        return redirect(url_for('mantenimientos'))
    
    # Obtener los asistentes asignados al laboratorio del equipo
    asistentes = ModelMantenimiento.get_asistentes_laboratorio(db, programacion['laboratorio_id'])
    
    return render_template('dashboard/registrar_mantenimiento.html', programacion=programacion, asistentes=asistentes)


@app.route('/descargar_reporte_mantenimiento/<int:programacion_id>', methods=['GET'])
@login_required
def descargar_reporte_mantenimiento(programacion_id):
    try:
        # Obtener los detalles de la programación de mantenimiento
        programacion = ModelMantenimiento.get_programacion_details(db, programacion_id, current_user.id, current_user.rol_id)

        # Generar el PDF
        pdf_buffer = generate_maintenance_report(programacion)
        return send_file(pdf_buffer, as_attachment=True, download_name=f'reporte_mantenimiento_{programacion_id}.pdf')

    except Exception as ex:
        flash(str(ex), "danger")
        return redirect(url_for('mantenimientos'))



#Manejo de errores

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Página no encontrada</h1>", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()