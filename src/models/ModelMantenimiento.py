from datetime import datetime

class ModelMantenimiento:
    @staticmethod
    def get_tipos_mantenimiento(db):
        """Obtener todos los tipos de mantenimiento para el dropdown"""
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id, nombre 
                    FROM TiposMantenimiento 
                    ORDER BY nombre"""
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [(row[0], row[1]) for row in rows]  # Convertir a lista de tuplas (id, nombre)
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def programar_mantenimiento(db, equipo_id, tipo_mantenimiento_id, anio, mes):
        """Crear una programación de mantenimiento y su registro inicial"""
        try:
            cursor = db.connection.cursor()
            
            # Primero insertamos en ProgramacionMantenimiento
            sql_programacion = """
                INSERT INTO ProgramacionMantenimiento 
                (equipo_id, tipo_mantenimiento_id, anio, mes)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_programacion, (equipo_id, tipo_mantenimiento_id, anio, mes))
            
            # Obtenemos el ID de la programación recién creada
            programacion_id = cursor.lastrowid
            
            # Creamos el registro inicial en RegistroMantenimiento
            sql_registro = """
                INSERT INTO RegistroMantenimiento 
                (programacion_id, estado)
                VALUES (%s, 'PROGRAMADO')
            """
            cursor.execute(sql_registro, (programacion_id,))
            
            db.connection.commit()
            return True
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def get_programacion_mantenimiento(db, user_id, user_rol):
        """Obtener la programación de mantenimiento según el rol del usuario"""
        try:
            cursor = db.connection.cursor()
            
            if user_rol == 1:  # Administrador
                sql = """
                    SELECT 
                        pm.id,
                        e.nombre as equipo_nombre,
                        tm.nombre as tipo_mantenimiento,
                        pm.anio,
                        pm.mes,
                        rm.estado,
                        rm.fecha_realizado,
                        a.fullname as realizado_por
                    FROM ProgramacionMantenimiento pm
                    JOIN Equipos e ON pm.equipo_id = e.id
                    JOIN TiposMantenimiento tm ON pm.tipo_mantenimiento_id = tm.id
                    LEFT JOIN RegistroMantenimiento rm ON pm.id = rm.programacion_id
                    LEFT JOIN Asistentes a ON rm.realizado_por = a.id
                    ORDER BY pm.anio, pm.mes
                """
                cursor.execute(sql)
            else:  # Asistente
                sql = """
                    SELECT 
                        pm.id,
                        e.nombre as equipo_nombre,
                        tm.nombre as tipo_mantenimiento,
                        pm.anio,
                        pm.mes,
                        rm.estado,
                        rm.fecha_realizado,
                        a.fullname as realizado_por
                    FROM ProgramacionMantenimiento pm
                    JOIN Equipos e ON pm.equipo_id = e.id
                    JOIN TiposMantenimiento tm ON pm.tipo_mantenimiento_id = tm.id
                    LEFT JOIN RegistroMantenimiento rm ON pm.id = rm.programacion_id
                    LEFT JOIN Asistentes a ON rm.realizado_por = a.id
                    JOIN Laboratorios l ON e.laboratorio_id = l.id
                    JOIN AsignacionesAsistente aa ON l.id = aa.laboratorio_id
                    WHERE aa.asistente_id = %s
                    ORDER BY pm.anio, pm.mes
                """
                cursor.execute(sql, (user_id,))
            
            # Obtener los nombres de las columnas
            columns = [desc[0] for desc in cursor.description]
            # Convertir los resultados en una lista de diccionarios
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def registrar_mantenimiento_realizado(db, programacion_id, user_id):
        """Registrar un mantenimiento como realizado"""
        try:
            cursor = db.connection.cursor()
            
            sql = """
                UPDATE RegistroMantenimiento 
                SET estado = 'REALIZADO',
                    fecha_realizado = CURRENT_DATE,
                    realizado_por = %s
                WHERE programacion_id = %s
            """
            cursor.execute(sql, (user_id, programacion_id))
            db.connection.commit()
            return True
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def eliminar_programacion(db, programacion_id, user_id, user_rol):
        """Eliminar una programación de mantenimiento"""
        try:
            cursor = db.connection.cursor()
            
            # Verificar permisos
            if user_rol != 1:  # Si no es admin, verificar que el equipo pertenezca a sus laboratorios
                sql_verify = """
                    SELECT 1
                    FROM ProgramacionMantenimiento pm
                    JOIN Equipos e ON pm.equipo_id = e.id
                    JOIN Laboratorios l ON e.laboratorio_id = l.id
                    JOIN AsignacionesAsistente aa ON l.id = aa.laboratorio_id
                    WHERE pm.id = %s AND aa.asistente_id = %s
                """
                cursor.execute(sql_verify, (programacion_id, user_id))
                if not cursor.fetchone():
                    raise Exception("No tienes permiso para eliminar esta programación")
            
            # Eliminar la programación (el registro se eliminará en cascada)
            sql_delete = "DELETE FROM ProgramacionMantenimiento WHERE id = %s"
            cursor.execute(sql_delete, (programacion_id,))
            
            db.connection.commit()
            return True
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()