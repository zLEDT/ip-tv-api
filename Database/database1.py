import mysql.connector
def conectar():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            database="ip-tv"
        )
class dbase:
    connector = mysql.connector.connect(host="localhost",user="root",database="ip-tv")
    
    def __init__(self):
        # self.connector = self.conectar()
        self.stream_mode = self.read("configuration","*",{"name":"streaming_mode"})[0].get("value")

    def conectar(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            database="ip-tv"
        )

    def create(self, table, data):
        """Inserta un nuevo registro en la tabla especificada."""
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        with self.connector.cursor(dictionary=True) as cursor:
            cursor.execute(sql, tuple(data.values()))
            self.connector.commit()
            return cursor.lastrowid

    # def read(self, table, conditions=None):
    #     """Obtiene registros de la tabla especificada con condiciones opcionales."""
    #     sql = f"SELECT * FROM {table}"
    #     if conditions:
    #         placeholders = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
    #         sql += f" WHERE {placeholders}"
    #     with self.connector.cursor(dictionary=True) as cursor:
    #         if conditions:
    #             cursor.execute(sql, tuple(conditions.values()))
    #         else:
    #             cursor.execute(sql)
    #         return cursor.fetchall()
        
    def read(self, table, columns='*', conditions=None):
        """Obtiene registros de la tabla especificada con columnas y condiciones opcionales."""
        if isinstance(columns, (list, tuple)):
            columns = ', '.join(columns)  # Convertir lista/tupla a cadena separada por comas
        
        sql = f"SELECT {columns} FROM {table}"
        
        if conditions:
            placeholders = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
            sql += f" WHERE {placeholders}"
        
        with self.connector.cursor(dictionary=True) as cursor:
            if conditions:
                cursor.execute(sql, tuple(conditions.values()))
            else:
                cursor.execute(sql)
            return cursor.fetchall()

    def update(self, table, data, conditions):
        """Actualiza registros en la tabla especificada con condiciones dadas."""
        set_clause = ', '.join([f"{col} = %s" for col in data.keys()])
        where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        with self.connector.cursor(dictionary=True) as cursor:
            cursor.execute(sql, tuple(data.values()) + tuple(conditions.values()))
            self.connector.commit()
            return cursor.rowcount

    def delete(self, table, conditions):
        """Elimina registros de la tabla especificada con condiciones dadas."""
        where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause}"
        with self.connector.cursor(dictionary=True) as cursor:
            cursor.execute(sql, tuple(conditions.values()))
            self.connector.commit()
            return cursor.rowcount

    def close(self):
        """Cierra la conexión con la base de datos."""
        self.connector.close()

    # def __del__(self):
    #     """Asegura que la conexión se cierre automáticamente al destruir el objeto."""
    #     self.close()

# Ejemplo de uso
if __name__ == "__main__":
    db = dbase()
    
    # Insertar un nuevo registro
    new_id = db.create("channel", {"name": "Juan"})
    print(f"Nuevo ID insertado: {new_id}")
    
    # Leer registros
    users = db.read("channel","*", {"name": "juan"})
    print("Usuarios con 30 años:", users)
    
    # Actualizar registros
    # updated_rows = db.update("usuarios", {"edad": 31}, {"nombre": "Juan"})
    # print(f"Registros actualizados: {updated_rows}")
    
    # # Eliminar registros
    # deleted_rows = db.delete("usuarios", {"nombre": "Juan"})
    # print(f"Registros eliminados: {deleted_rows}")
