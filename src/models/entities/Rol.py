class Rol:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def __repr__(self):
        return f"Rol(id={self.id}, nombre='{self.nombre}')"

    @classmethod
    def from_db(cls, row):
        return cls(row[0], row[1])