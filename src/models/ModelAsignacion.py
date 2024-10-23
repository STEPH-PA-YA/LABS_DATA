class ModelAsignacion:
    @classmethod
    def get_asignaciones(cls, db):
        try:
            cursor = db.connection.cursor()
            sql = """
                SELECT aa.id, a.fullname as asistente_nombre, 
                       l.nombre as laboratorio_nombre,
                       aa.asistente_id, aa.laboratorio_id
                FROM AsignacionesAsistente aa
                JOIN Asistentes a ON aa.asistente_id = a.id
                JOIN Laboratorios l ON aa.laboratorio_id = l.id
            """
            cursor.execute(sql)
            asignaciones = cursor.fetchall()
            return asignaciones
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def agregar_asignacion(cls, db, asistente_id, laboratorio_id):
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO AsignacionesAsistente 
                     (asistente_id, laboratorio_id) 
                     VALUES (%s, %s)"""
            cursor.execute(sql, (asistente_id, laboratorio_id))
            db.connection.commit()
            return True
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def editar_asignacion(cls, db, id, asistente_id, laboratorio_id):
        try:
            cursor = db.connection.cursor()
            sql = """UPDATE AsignacionesAsistente 
                     SET asistente_id = %s, laboratorio_id = %s 
                     WHERE id = %s"""
            cursor.execute(sql, (asistente_id, laboratorio_id, id))
            db.connection.commit()
            return True
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def eliminar_asignacion(cls, db, id):
        try:
            cursor = db.connection.cursor()
            sql = "DELETE FROM AsignacionesAsistente WHERE id = %s"
            cursor.execute(sql, (id,))
            db.connection.commit()
            return True
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def obtener_asignacion(cls, db, id):
        try:
            cursor = db.connection.cursor()
            sql = """
                SELECT id, asistente_id, laboratorio_id
                FROM AsignacionesAsistente
                WHERE id = %s
            """
            cursor.execute(sql, (id,))
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()