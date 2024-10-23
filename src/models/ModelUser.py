from .entities.User import User
from werkzeug.security import check_password_hash, generate_password_hash

class ModelUser():
    @classmethod
    def login(self, db, username, password):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, fullname, username, password, rol_id, created_at   FROM asistentes WHERE username = %s"
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            
            if row:
                user = User(row[0], row[1], row[2], row[3], row[4], row[5])
                if check_password_hash(user.password, password):
                    return user
            return None
            
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, fullname, username, password, rol_id, created_at  FROM asistentes WHERE id = %s"
            cursor.execute(sql, (id,))
            row = cursor.fetchone()
            
            if row:
                return User(row[0], row[1], row[2], row[3], row[4], row[5])
            return None
            
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def register(self, db, fullname, username, password, rol_id):
        try:
            cursor = db.connection.cursor()
            
            # Verificar si el usuario ya existe
            if self.get_by_username(db, username):
                return False, "El usuario ya existe"
            
            # Generar hash de la contraseña
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Insertar nuevo usuario
            sql = "INSERT INTO asistentes (fullname, username, password, rol_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (fullname, username, hashed_password, rol_id))
            db.connection.commit()
            
            return True, "Usuario registrado exitosamente"
            
        except Exception as ex:
            db.connection.rollback()
            return False, str(ex)
        finally:
            cursor.close()

    @classmethod
    def get_by_username(self, db, username):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, fullname, username, password, rol_id  FROM asistentes WHERE username = %s"
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            
            if row:
                return User(row[0], row[1], row[2], row[3], row[4])
            return None
            
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def update_user(self, db, user_id, fullname=None, username=None, password=None, rol_id=None):
        try:
            cursor = db.connection.cursor()
            updates = []
            params = []
            
            
            if fullname:
                updates.append("fullname = %s")
                params.append(fullname)

            if username:
                updates.append("username = %s")
                params.append(username)
            
            if password:
                updates.append("password = %s")
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                params.append(hashed_password)

            if rol_id:
                updates.append("rol_id = %s")
                params.append(rol_id)
            
            if updates:
                sql = f"UPDATE asistentes SET {', '.join(updates)} WHERE id = %s"
                params.append(user_id)
                cursor.execute(sql, tuple(params))
                db.connection.commit()
                return True, "Usuario actualizado exitosamente"
            
            return False, "No hay datos para actualizar"
            
        except Exception as ex:
            db.connection.rollback()
            return False, str(ex)
        finally:
            cursor.close()

    @classmethod
    def get_all_asistentes(self, db):
        """Obtener todos los asistentes para el dropdown"""
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id, fullname, username 
                    FROM asistentes 
                    WHERE rol_id = 2"""  # Asumiendo que rol_id 2 es para asistentes
            cursor.execute(sql)
            asistentes = cursor.fetchall()
            return asistentes
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()