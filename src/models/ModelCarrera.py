class ModelCarrera:
    @classmethod
    def get_carreras_for_dropdown(cls, db):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, nombre FROM Carreras"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [(row[0], row[1]) for row in rows]
        except Exception as ex:
            raise Exception(ex)
        finally:
            cursor.close()