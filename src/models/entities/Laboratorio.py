class Laboratorio:
    def __init__(self,codigo, nombre, ubicacion, carrera_id) -> None:
        self.codigo = codigo
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.carrera_id = carrera_id

    @classmethod
    def from_tuple(cls, tuple_data):
        return cls(*tuple_data)

