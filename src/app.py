from flask import Flask, render_template, request, redirect, url_for, flash
from config import config
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect

# Models
from models.ModelUser import ModelUser
from models.ModelRol import ModelRol
from models.ModelLab import ModelLaboratorio

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
    return render_template('home.html')
#LABORATORIOS

@app.route('/laboratorios')
@login_required
def laboratorios():
    user_id = current_user.id
    user_rol = current_user.rol_id
    laboratorios = ModelLaboratorio.get_laboratorios(db, user_id, user_rol)
    return render_template('dashboard/laboratorios.html', laboratorios=laboratorios)



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