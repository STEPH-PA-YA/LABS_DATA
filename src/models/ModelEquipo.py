from .entities.Equipo import Equipo

class ModelEquipo:
    @staticmethod
    def get_equipos(db, user_id, user_rol):
        """Obtener todos los equipos según el rol del usuario"""
        try:
            cursor = db.connection.cursor()
            if user_rol == 1:  # Rol administrador
                sql = """
                    SELECT 
                        e.id,
                        e.codigo,
                        e.nombre,
                        e.marca,
                        e.modelo,
                        e.serie,
                        e.laboratorio_id,
                        l.nombre as laboratorio_nombre
                    FROM 
                        Equipos e
                    LEFT JOIN 
                        Laboratorios l ON e.laboratorio_id = l.id
                    ORDER BY 
                        e.nombre
                """
                cursor.execute(sql)
            else:
                # Para asistentes, solo mostrar equipos de sus laboratorios asignados
                sql = """
                    SELECT 
                        e.id,
                        e.codigo,
                        e.nombre,
                        e.marca,
                        e.modelo,
                        e.serie,
                        e.laboratorio_id,
                        l.nombre as laboratorio_nombre
                    FROM 
                        Equipos e
                    INNER JOIN 
                        Laboratorios l ON e.laboratorio_id = l.id
                    INNER JOIN 
                        AsignacionesAsistente aa ON l.id = aa.laboratorio_id
                    WHERE 
                        aa.asistente_id = %s
                    ORDER BY 
                        e.nombre
                """
                cursor.execute(sql, (user_id,))

            # Para depuración
            results = cursor.fetchall()
            print("Datos obtenidos:", results)  # Para ver qué datos estamos recibiendo

            equipos = [Equipo.from_tuple(row) for row in results]
            
            # Para depuración
            if equipos:
                print("Primer equipo:", vars(equipos[0]))  # Para ver cómo quedó construido el objeto
                
            return equipos
        except Exception as ex:
            print("Error:", str(ex))  # Para depuración
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def get_laboratorios_disponibles(db, user_id, user_rol):
        """Obtener laboratorios disponibles para el dropdown según el rol del usuario"""
        try:
            cursor = db.connection.cursor()
            if user_rol == 1:  # Administrador ve todos los laboratorios
                sql = """SELECT id, nombre 
                        FROM Laboratorios 
                        ORDER BY nombre"""
                cursor.execute(sql)
            else:
                # Asistentes solo ven sus laboratorios asignados
                sql = """SELECT l.id, l.nombre 
                        FROM Laboratorios l
                        JOIN AsignacionesAsistente aa ON l.id = aa.laboratorio_id
                        WHERE aa.asistente_id = %s
                        ORDER BY l.nombre"""
                cursor.execute(sql, (user_id,))
            
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def agregar_equipo(cls, db, equipo, user_id, user_rol):
        """Agregar un nuevo equipo verificando permisos"""
        try:
            # Verificar si el usuario tiene permiso para agregar equipos en este laboratorio
            if not cls._verificar_permiso_laboratorio(db, user_id, user_rol, equipo.laboratorio_id):
                raise Exception("No tienes permiso para agregar equipos en este laboratorio")

            cursor = db.connection.cursor()
            sql = """INSERT INTO Equipos (codigo, nombre, marca, modelo, 
                                        serie, laboratorio_id) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (equipo.codigo, equipo.nombre, equipo.marca,
                               equipo.modelo, equipo.serie, equipo.laboratorio_id))
            db.connection.commit()
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def editar_equipo(cls, db, equipo, user_id, user_rol):
        """Editar un equipo existente verificando permisos"""
        try:
            # Verificar si el usuario tiene permiso para editar equipos en este laboratorio
            if not cls._verificar_permiso_laboratorio(db, user_id, user_rol, equipo.laboratorio_id):
                raise Exception("No tienes permiso para editar equipos en este laboratorio")

            cursor = db.connection.cursor()
            sql = """UPDATE Equipos 
                     SET codigo = %s, nombre = %s, marca = %s, 
                         modelo = %s, serie = %s, laboratorio_id = %s 
                     WHERE id = %s"""
            
            if equipo.laboratorio_id is None:
                raise ValueError("laboratorio_id no puede ser None")
            
            cursor.execute(sql, (equipo.codigo, equipo.nombre, equipo.marca,
                               equipo.modelo, equipo.serie, equipo.laboratorio_id,
                               equipo.id))
            db.connection.commit()
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def eliminar_equipo(cls, db, equipo_id, user_id, user_rol):
        """Eliminar un equipo verificando permisos"""
        try:
            # Primero obtener el laboratorio_id del equipo
            cursor = db.connection.cursor()
            sql = "SELECT laboratorio_id FROM Equipos WHERE id = %s"
            cursor.execute(sql, (equipo_id,))
            result = cursor.fetchone()
            
            if not result:
                raise Exception("Equipo no encontrado")
                
            laboratorio_id = result[0]
            
            # Verificar si el usuario tiene permiso para eliminar equipos en este laboratorio
            if not cls._verificar_permiso_laboratorio(db, user_id, user_rol, laboratorio_id):
                raise Exception("No tienes permiso para eliminar equipos en este laboratorio")

            sql = "DELETE FROM Equipos WHERE id = %s"
            cursor.execute(sql, (equipo_id,))
            db.connection.commit()
        except Exception as ex:
            db.connection.rollback()
            raise Exception(ex)
        finally:
            cursor.close()

    @classmethod
    def obtener_equipo(cls, db, id, user_id, user_rol):
        """Obtener un equipo específico verificando permisos"""
        try:
            cursor = db.connection.cursor()
            if user_rol == 1:  # Administrador
                sql = """SELECT e.id, e.codigo, e.nombre, e.marca, e.modelo, 
                               e.serie, e.laboratorio_id
                        FROM Equipos e
                        WHERE e.id = %s"""
                cursor.execute(sql, (id,))
            else:
                # Para asistentes, verificar que el equipo pertenezca a sus laboratorios
                sql = """SELECT e.id, e.codigo, e.nombre, e.marca, e.modelo, 
                               e.serie, e.laboratorio_id
                        FROM Equipos e
                        JOIN Laboratorios l ON e.laboratorio_id = l.id
                        JOIN AsignacionesAsistente aa ON l.id = aa.laboratorio_id
                        WHERE e.id = %s AND aa.asistente_id = %s"""
                cursor.execute(sql, (id, user_id))

            result = cursor.fetchone()
            if result:
                return Equipo.from_tuple(result)
            return None
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()

    @staticmethod
    def _verificar_permiso_laboratorio(db, user_id, user_rol, laboratorio_id):
        """Verifica si un usuario tiene permiso para gestionar equipos en un laboratorio"""
        try:
            cursor = db.connection.cursor()
            if user_rol == 1:  # Administrador tiene permiso en todos los laboratorios
                return True
            
            # Para asistentes, verificar si tienen asignación al laboratorio
            sql = """SELECT 1 FROM AsignacionesAsistente 
                    WHERE asistente_id = %s AND laboratorio_id = %s"""
            cursor.execute(sql, (user_id, laboratorio_id))
            return cursor.fetchone() is not None
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()