from .entities.Laboratorio import Laboratorio

class ModelLaboratorio:
    @staticmethod
    def get_laboratorios(db, user_id, user_rol):
        try:
            cursor = db.connection.cursor()
            if user_rol == 1:  # Asumiendo que 1 es el ID del rol de administrador
                sql = """SELECT l.codigo, l.nombre, l.ubicacion, c.nombre as carrera_nombre
                         FROM Laboratorios l
                         LEFT JOIN Carreras c ON l.carrera_id = c.id"""
                cursor.execute(sql)
            else:
                sql = """SELECT l.codigo, l.nombre, l.ubicacion, c.nombre as carrera_nombre
                         FROM Laboratorios l
                         LEFT JOIN Carreras c ON l.carrera_id = c.id
                         JOIN AsignacionesAsistente aa ON l.codigo = aa.laboratorio_codigo
                         WHERE aa.asistente_id = %s"""
                cursor.execute(sql, (user_id,))
            
            laboratorios = [Laboratorio.from_tuple(row) for row in cursor.fetchall()]
            return laboratorios
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def agregar_laboratorio(db, laboratorio):
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO Laboratorios (codigo, nombre, ubicacion, carrera_id) 
                     VALUES (%s, %s, %s, (SELECT id FROM Carreras WHERE nombre = %s))"""
            cursor.execute(sql, (laboratorio.codigo, laboratorio.nombre, laboratorio.ubicacion, laboratorio.carrera_nombre))
            db.connection.commit()
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def editar_laboratorio(db, laboratorio):
        try:
            cursor = db.connection.cursor()
            sql = """UPDATE Laboratorios SET nombre = %s, ubicacion = %s, 
                     carrera_id = (SELECT id FROM Carreras WHERE nombre = %s)
                     WHERE codigo = %s"""
            cursor.execute(sql, (laboratorio.nombre, laboratorio.ubicacion, laboratorio.carrera_nombre, laboratorio.codigo))
            db.connection.commit()
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def eliminar_laboratorio(db, codigo):
        try:
            cursor = db.connection.cursor()
            sql = "DELETE FROM Laboratorios WHERE codigo = %s"
            cursor.execute(sql, (codigo,))
            db.connection.commit()
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()