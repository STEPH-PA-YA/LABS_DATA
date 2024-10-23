from .entities.Laboratorio import Laboratorio

class ModelLaboratorio:
    @staticmethod
    def get_laboratorios(db, user_id, user_rol):
        try:
            cursor = db.connection.cursor()
            if user_rol == 1:  # Asumiendo que 1 es el ID del rol de administrador
                sql = """SELECT l.id, l.nombre, l.ubicacion, c.nombre as carrera_nombre
                         FROM Laboratorios l
                         LEFT JOIN Carreras c ON l.carrera_id = c.id"""
                cursor.execute(sql)
            else:
                sql = """SELECT l.id, l.nombre, l.ubicacion, c.nombre as carrera_nombre
                         FROM Laboratorios l
                         LEFT JOIN Carreras c ON l.carrera_id = c.id
                         JOIN AsignacionesAsistente aa ON l.id = aa.laboratorio_id
                         WHERE aa.asistente_id = %s"""
                cursor.execute(sql, (user_id,))
            
            laboratorios = [Laboratorio.from_tuple(row) for row in cursor.fetchall()]
            return laboratorios
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def agregar_laboratorio(cls, db, laboratorio):
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO Laboratorios (nombre, ubicacion, carrera_id) 
                     VALUES (%s, %s, %s)"""
            cursor.execute(sql, (laboratorio.nombre, 
                                 laboratorio.ubicacion, laboratorio.carrera_id))
            db.connection.commit()
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def editar_laboratorio(cls, db, laboratorio):
        try:
            cursor = db.connection.cursor()
            sql = """UPDATE Laboratorios 
                    SET nombre = %s, ubicacion = %s, carrera_id = %s 
                    WHERE id = %s"""
            
            # Asegúrate de que carrera_id no sea None
            if laboratorio.carrera_id is None:
                raise ValueError("carrera_id no puede ser None")
            
            cursor.execute(sql, (laboratorio.nombre, laboratorio.ubicacion, 
                                laboratorio.carrera_id, laboratorio.id))
            db.connection.commit()
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def eliminar_laboratorio(db, id):
        try:
            cursor = db.connection.cursor()
            sql = "DELETE FROM Laboratorios WHERE id = %s"
            cursor.execute(sql, (id,))
            db.connection.commit()
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def obtener_laboratorio(cls, db, id):
        try:
            cursor = db.connection.cursor()
            sql = """
                SELECT id, nombre, ubicacion, carrera_id
                FROM Laboratorios
                WHERE id = %s
            """
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
            
            if result:
                return Laboratorio(
                    id=result[0],
                    nombre=result[1],
                    ubicacion=result[2],
                    carrera_id=result[3]
                )
            return None
        except Exception as ex:
            raise Exception(ex)
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_all_labs(self, db):
        """Obtener todos los laboratorios para el dropdown"""
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, nombre FROM laboratorios"
            cursor.execute(sql)
            laboratorios = cursor.fetchall()
            return laboratorios
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()