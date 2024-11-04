class ProgramacionMantenimiento:
    def __init__(self, id=None, equipo_id=None, fecha_inicio=None, fecha_fin=None, 
                 tipo_mantenimiento=None, descripcion=None, estado='ACTIVO'):
        self.id = id
        self.equipo_id = equipo_id
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.tipo_mantenimiento = tipo_mantenimiento
        self.descripcion = descripcion
        self.estado = estado

    @classmethod
    def from_tuple(cls, row):
        return cls(
            id=row[0],
            equipo_id=row[1],
            fecha_inicio=row[2],
            fecha_fin=row[3],
            tipo_mantenimiento=row[4],
            descripcion=row[5],
            estado=row[6]
        )

class RegistroMantenimiento:
    def __init__(self, id=None, programacion_id=None, fecha_programada=None, 
                 estado='PROGRAMADO', observaciones=None, fecha_realizado=None):
        self.id = id
        self.programacion_id = programacion_id
        self.fecha_programada = fecha_programada
        self.estado = estado
        self.observaciones = observaciones
        self.fecha_realizado = fecha_realizado

    @classmethod
    def from_tuple(cls, row):
        return cls(
            id=row[0],
            programacion_id=row[1],
            fecha_programada=row[2],
            estado=row[3],
            observaciones=row[4],
            fecha_realizado=row[5]
        )