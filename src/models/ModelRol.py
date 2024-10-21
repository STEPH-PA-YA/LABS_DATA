from .entities.Rol import Rol

class ModelRol():
    # ... (other methods)

    @classmethod
    def get_roles_for_dropdown(cls, db):
        """Obtiene todos los roles para un dropdown."""
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, nombre FROM Roles"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [(row[0], row[1]) for row in rows]
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def get_name_rol(cls, db, rol_id):
        """Obtiene el nombre del rol para un id dado."""
        try:
            cursor = db.connection.cursor()
            sql = "SELECT nombre FROM Roles WHERE id=%s"
            cursor.execute(sql, (rol_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()