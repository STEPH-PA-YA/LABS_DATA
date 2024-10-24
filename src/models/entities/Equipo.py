class Equipo:
    def __init__(self, id=None, codigo=None, nombre=None, marca=None, modelo=None, serie=None, laboratorio_id=None, laboratorio_nombre=None):
        self.id = id
        self.codigo = codigo
        self.nombre = nombre
        self.marca = marca
        self.modelo = modelo
        self.serie = serie
        self.laboratorio_id = laboratorio_id
        self.laboratorio_nombre = laboratorio_nombre

    @classmethod
    def from_tuple(cls, row):
        # Crear instancia con los campos básicos
        equipo = cls(
            id=row[0],
            codigo=row[1],
            nombre=row[2],
            marca=row[3],
            modelo=row[4],
            serie=row[5],
            laboratorio_id=row[6]
        )
        # Si hay un nombre de laboratorio en la tupla (índice 7), agregarlo
        if len(row) > 7:
            equipo.laboratorio_nombre = row[7]
        return equipo