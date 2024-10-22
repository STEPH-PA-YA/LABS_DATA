class Laboratorio:
    def __init__(self, id, nombre, ubicacion, carrera_id):
        self.id = id
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.carrera_id = carrera_id

    @classmethod
    def from_tuple(cls, tuple_data):
        return cls(*tuple_data)

