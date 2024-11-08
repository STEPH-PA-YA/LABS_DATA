from datetime import datetime
import io 
from flask import make_response


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

#### Nuevas funciones

    @staticmethod
    def get_programacion_by_id(db, programacion_id, user_id, user_rol):
        """Obtener los detalles de una programación de mantenimiento"""
        try:
            cursor = db.connection.cursor()
            
            if user_rol == 1:  # Administrador
                sql = """
                    SELECT 
                        pm.id,
                        e.id AS equipo_id,
                        e.nombre AS equipo_nombre,
                        e.codigo AS equipo_codigo,
                        e.marca AS equipo_marca, 
                        e.serie AS equipo_serie,
                        e.modelo AS equipo_modelo,
                        l.id AS laboratorio_id,
                        l.nombre AS laboratorio_nombre,
                        c.nombre AS carrera_nombre,
                        tm.nombre AS tipo_mantenimiento,
                        pm.anio,
                        pm.mes,
                        COALESCE(rm.estado, 'PROGRAMADO') as estado,
                        rm.fecha_realizado,
                        COALESCE(rm.observaciones, '') as observaciones
                    FROM ProgramacionMantenimiento pm
                    JOIN Equipos e ON pm.equipo_id = e.id
                    JOIN Laboratorios l ON e.laboratorio_id = l.id
                    JOIN Carreras c ON l.carrera_id = c.id
                    JOIN TiposMantenimiento tm ON pm.tipo_mantenimiento_id = tm.id
                    LEFT JOIN RegistroMantenimiento rm ON pm.id = rm.programacion_id
                    WHERE pm.id = %s
                """
                cursor.execute(sql, (programacion_id,))
            else:  # Asistente
                sql = """
                    SELECT 
                        pm.id,
                        e.id AS equipo_id,
                        e.nombre AS equipo_nombre,
                        e.codigo AS equipo_codigo,
                        e.marca AS equipo_marca,
                        e.serie AS equipo_serie,
                        e.modelo AS equipo_modelo,
                        l.id AS laboratorio_id,
                        l.nombre AS laboratorio_nombre,
                        c.nombre AS carrera_nombre,
                        tm.nombre AS tipo_mantenimiento,
                        pm.anio,
                        pm.mes,
                        rm.estado,
                        rm.fecha_realizado,
                        rm.observaciones
                    FROM ProgramacionMantenimiento pm
                    JOIN Equipos e ON pm.equipo_id = e.id
                    JOIN Laboratorios l ON e.laboratorio_id = l.id
                    JOIN Carreras c ON l.carrera_id = c.id
                    JOIN TiposMantenimiento tm ON pm.tipo_mantenimiento_id = tm.id
                    LEFT JOIN RegistroMantenimiento rm ON pm.id = rm.programacion_id
                    JOIN AsignacionesAsistente aa ON l.id = aa.laboratorio_id
                    WHERE pm.id = %s AND aa.asistente_id = %s
                """
                cursor.execute(sql, (programacion_id, user_id))
            
            # Obtener los nombres de las columnas
            columns = [desc[0] for desc in cursor.description]
            # Convertir los resultados en un diccionario
            result = dict(zip(columns, cursor.fetchone()))
            return result
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def get_asistentes_laboratorio(db, laboratorio_id):
        """Obtener los asistentes asignados a un laboratorio"""
        try:
            cursor = db.connection.cursor()
            sql = """
                SELECT a.id, a.fullname
                FROM Asistentes a
                JOIN AsignacionesAsistente aa ON a.id = aa.asistente_id
                WHERE aa.laboratorio_id = %s
            """
            cursor.execute(sql, (laboratorio_id,))
            return [(row[0], row[1]) for row in cursor.fetchall()]
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def registrar_mantenimiento(db, programacion_id, fecha_realizado, realizado_por, observaciones, user_id):
        try:
            cursor = db.connection.cursor()
            
            # Actualizar el registro de mantenimiento
            sql = """
                UPDATE RegistroMantenimiento
                SET estado = 'REALIZADO', fecha_realizado = %s, realizado_por = %s, observaciones = %s
                WHERE programacion_id = %s
            """
            cursor.execute(sql, (fecha_realizado, realizado_por, observaciones, programacion_id))
            
            db.connection.commit()
            return True
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def get_programacion_details(db, programacion_id, user_id, user_rol):
        """Obtener los detalles completos de una programación de mantenimiento"""
        try:
            cursor = db.connection.cursor()
            
            if user_rol == 1:  # Administrador
                sql = """
                    SELECT 
                        pm.id,
                        e.id AS equipo_id,
                        e.nombre AS equipo_nombre,
                        e.codigo AS equipo_codigo,
                        e.marca AS equipo_marca,
                        e.serie AS equipo_serie,
                        e.modelo AS equipo_modelo,
                        l.id AS laboratorio_id,
                        l.nombre AS laboratorio_nombre,
                        c.nombre AS carrera_nombre,
                        tm.nombre AS tipo_mantenimiento,
                        pm.anio,
                        pm.mes,
                        rm.estado,
                        rm.fecha_realizado,
                        rm.observaciones,
                        a.fullname AS realizado_por
                    FROM ProgramacionMantenimiento pm
                    JOIN Equipos e ON pm.equipo_id = e.id
                    JOIN Laboratorios l ON e.laboratorio_id = l.id
                    JOIN Carreras c ON l.carrera_id = c.id
                    JOIN TiposMantenimiento tm ON pm.tipo_mantenimiento_id = tm.id
                    LEFT JOIN RegistroMantenimiento rm ON pm.id = rm.programacion_id
                    LEFT JOIN Asistentes a ON rm.realizado_por = a.id
                    WHERE pm.id = %s
                """
                cursor.execute(sql, (programacion_id,))
            else:  # Asistente
                sql = """
                    SELECT 
                        pm.id,
                        e.id AS equipo_id,
                        e.nombre AS equipo_nombre,
                        e.codigo AS equipo_codigo,
                        e.marca AS equipo_marca,
                        e.serie AS equipo_serie,
                        e.modelo AS equipo_modelo,
                        l.id AS laboratorio_id,
                        l.nombre AS laboratorio_nombre,
                        c.nombre AS carrera_nombre,
                        tm.nombre AS tipo_mantenimiento,
                        pm.anio,
                        pm.mes,
                        rm.estado,
                        rm.fecha_realizado,
                        a.fullname AS realizado_por
                    FROM ProgramacionMantenimiento pm
                    JOIN Equipos e ON pm.equipo_id = e.id
                    JOIN Laboratorios l ON e.laboratorio_id = l.id
                    JOIN Carreras c ON l.carrera_id = c.id
                    JOIN TiposMantenimiento tm ON pm.tipo_mantenimiento_id = tm.id
                    LEFT JOIN RegistroMantenimiento rm ON pm.id = rm.programacion_id
                    LEFT JOIN Asistentes a ON rm.realizado_por = a.id
                    JOIN AsignacionesAsistente aa ON l.id = aa.laboratorio_id
                    WHERE pm.id = %s AND aa.asistente_id = %s
                """
                cursor.execute(sql, (programacion_id, user_id))
            
            # Obtener los nombres de las columnas
            columns = [desc[0] for desc in cursor.description]
            # Convertir los resultados en un diccionario
            result = dict(zip(columns, cursor.fetchone()))
            return result
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    # Problematic code
    @classmethod
    def get_total_mantenimientos_programados(cls,db):
        """
        Obtener el total de mantenimientos programados
        """
        try:
            cursor = db.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM RegistroMantenimiento 
                WHERE estado = 'PROGRAMADO'
            """)
            total = cursor.fetchone()[0]
            return total
        except Exception as ex:
            print(f"Error en get_total_mantenimientos_programados: {ex}")
            return 0
        finally:
            cursor.close()
    @staticmethod
    def get_total_mantenimientos_realizados(db):
        """
        Obtener el total de mantenimientos realizados
        """
        try:
            cursor = db.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM RegistroMantenimiento 
                WHERE estado = 'REALIZADO'
            """)
            total = cursor.fetchone()[0]
            return total
        except Exception as ex:
            print(f"Error en get_total_mantenimientos_realizados: {ex}")
            return 0
        finally:
            cursor.close()