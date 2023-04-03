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
        position VARCHAR(6),
        artist_name VARCHAR(50),
        song_name VARCHAR(100),
        days INT,
        top_10 INT,
        peak_position INT,
        peak_position_time VARCHAR(6),
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


def loadIntoDB():
    inFile = open("song.csv", "r", encoding="utf-8")
    id = 0

    cursor.execute("SET QUOTED_IDENTIFIER OFF")

    for line in inFile:
        if id == 0:
            id += 1
            continue
        line = line.strip()
        (
            position,
            artist_name,
            song_name,
            days,
            top_10,
            peak_position,
            peak_position_time,
            peak_streams,
            total_streams,
        ) = line.split(";")

        insert = f"""INSERT INTO repositorio_musica (id, position, artist_name, song_name, days, top_10, peak_position, peak_position_time, peak_streams, total_streams)
        VALUES ({id}, "{position}", "{artist_name[:-1]}", "{song_name}", {days}, {top_10}, "{peak_position}", "{peak_position_time}", {peak_streams}, {total_streams});"""
        # print(insert)
        cursor.execute(insert)
        id += 1

    inFile.close()
    return


def main():
    initializeDB()
    loadIntoDB()


if __name__ == "__main__":
    main()
