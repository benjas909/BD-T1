import pyodbc as odbc

try:
    connection = odbc.connect(
        "DRIVER={SQL SERVER};SERVER=Benjas\SQLEXPRESS;Trusted_Connection=yes",
        autocommit=True,
    )

    cursor = connection.cursor()
except Exception() as ex:
    print(ex)


def initializeDB():
    cursor.execute("DROP DATABASE IF EXISTS spotUSM")
    cursor.execute("CREATE DATABASE spotUSM")
    cursor.execute("USE spotUSM")
    cursor.execute(
        """CREATE TABLE repositorio_musica (
        id INT NOT NULL PRIMARY KEY,
        position VARCHAR(3),
        artist_name VARCHAR(50),
        song_name VARCHAR(50),
        days INT,
        top_10 INT,
        peak_position INT,
        peak_postition_time VARCHAR(6),
        peak_streams INT,
        total_streams INT
        )"""
    )
    cursor.execute(
        """CREATE TABLE reproduccion (
            id INT FOREIGN KEY REFERENCES repositorio_musica(id),
            song_name VARCHAR(50),
            artist_name VARCHAR(50),
            fecha_reproduccion DATE,
            favorito BIT
        )"""
    )

    cursor.execute(
        """CREATE TABLE lista_favoritos (
            id INT FOREIGN KEY REFERENCES repositorio_musica(id),
            song_name VARCHAR(50),
            artist_name VARCHAR(50),
            fecha_agregada DATE
        )"""
    )
    print("hola")
    return


def main():
    initializeDB()
    inFile = open("song.csv", "r")
    # for line in inFile:
    #     cursor.execute()
    inFile.close()


if __name__ == "__main__":
    main()
