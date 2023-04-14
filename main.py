import pyodbc as odbc

try:
    LOOP = True
    while LOOP:
        usr = int(
            input(
                "¿Quién está usando el programa?\n(1)Pipes \n(2)Benjas\n(3)Otro (UNTESTED)\n> "
            )
        )
        if usr == 1:
            LOOP = False
            USR_STR = "pipe\SQLEXPRESS01"
        elif usr == 2:
            LOOP = False
            USR_STR = "Benjas\SQLEXPRESS"
        elif usr == 3:
            LOOP = False
            USR_STR = input("Ingrese el nombre de su server:")
        else:
            print("Opción inválida.")

    connection = odbc.connect(
        f"DRIVER={{SQL SERVER}};SERVER={USR_STR};Trusted_Connection=yes",
        autocommit=True,
    )

    cursor = connection.cursor()
except Exception() as ex:
    print(ex)


# listo
def initializeDB():
    # Query para obtener los nombres de las bases de datos existentes
    cursor.execute("SELECT name FROM master.dbo.sysdatabases")
    rowAux = cursor.fetchall()
    row = [item for i in rowAux for item in i]

    # Si spotUSM no existe, se crea ella y sus tablas, para finalmente cargar los datos a repositorio_musica
    if "spotUSM" not in row:
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
                id INT NOT NULL PRIMARY KEY,
                song_name VARCHAR(50),
                artist_name VARCHAR(50),
                fecha_reproduccion DATE,
                veces_reproducida INT,
                favorito BIT
            )"""
        )

        cursor.execute(
            """CREATE TABLE lista_favoritos (
                id INT NOT NULL PRIMARY KEY,
                song_name VARCHAR(50),
                artist_name VARCHAR(50),
                fecha_agregada DATE
            )"""
        )
        loadIntoDB()

        # cursor.execute(
        #     """CREATE FUNCTION peakPosInt(@peak_position_time VARCHAR(6))
        #     RETURNS INT
        #     AS
        #     BEGIN
        #         DECLARE @posStr VARCHAR(3)
        #         SET @posStr = TRIM(')(x' FROM @peak_position_time);
        #         DECLARE @posInt INT
        #         SET @posInt = CONVERT(INT, @posStr)
        #         RETURN @posInt
        #     END"""
        # )
        cursor.execute(
            """CREATE VIEW totalTop10 AS SELECT artist_name, SUM(top_10) AS timesInTop10 FROM repositorio_musica GROUP BY artist_name"""
        )

    cursor.execute("USE spotUSM")

    return


# listo
def loadIntoDB():
    inFile = open("song.csv", "r", encoding="utf-8")
    songID = 0

    cursor.execute("SET QUOTED_IDENTIFIER OFF")

    for line in inFile:
        if songID == 0:
            songID += 1
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
        VALUES ({songID}, "{position}", "{artist_name[:-1]}", "{song_name}", {days}, {top_10}, "{peak_position}", "{peak_position_time}", {peak_streams}, {total_streams});"""
        # print(insert)
        cursor.execute(insert)
        songID += 1

    inFile.close()
    return


# listo
def startMenu():
    while True:
        print("Menu:")
        print(
            """\t1)Mostrar canciones reproducidas.\n\t2)Mostrar canciones favoritas.\n\t3)Buscar canción.\n\t4)Escuchadas en los ultimos dias.\n\t5)TOP 15 TEST.\n\t6)posicion peak \n\t7)promedio streams \n\t8)Salir"""
        )
        choice = input("> ")
        match choice:
            case "1":
                showPlays()
            case "2":
                showFav()
            case "3":
                songID = searchSong()
                loop = True
                while loop:
                    inp = input(
                        "¿Qué desea hacer?\n\t1)Reproducir.\n\t2)Agregar/Quitar de favoritos.\n> "
                    )
                    match inp:
                        case "1":
                            loop = False
                            playSong(songID)
                        case "2":
                            loop = False
                            makeFav(songID)
                        case other:
                            print("Opción inválida.")

            case "4":
                date = input("Ingrese una fecha: ")
                showSongLastDays(date)
            case "5":
                searchTop15()
            case "6":
                name = input("Nombre artista ")
                searchPeakPos(name)
            case "7":
                name = input("Nombre artista ")
                searchAvgPlays(name)
            case "8":
                while True:
                    close = input("\t¿Cerrar Sesión?\n\t[Y/N]\n")
                    if close == "Y" or close == "y":
                        return
                    elif close == "N" or close == "n":
                        break
                    else:
                        continue
            case other:
                print("Opción Inválida.")
                continue
    return


# listo
def showPlays():
    print("1) Ordenar por fecha")
    print("2) Ordenar por reproducciones")

    songChoice = input("> ")
    i = 1

    match songChoice:
        case "1":
            cursor.execute(
                """SELECT * FROM reproduccion ORDER BY fecha_reproduccion DESC"""
            )
            songs = cursor.fetchall()
            for song in songs:
                print(str(i) + ")", song[1], "-", song[2], "-", song[3])
        case "2":
            cursor.execute(
                """SELECT * FROM reproduccion ORDER BY veces_reproducida DESC"""
            )
            songs = cursor.fetchall()
            for song in songs:
                print(str(i) + ")", song[1], "-", song[2], "-", song[4])

    if not songs:
        print("Lista vacía.")

    while True:
        print("Acciones Rápidas: 1)Buscar en la lista  2)Volver al menú principal")
        choice = input("> ")
        match choice:
            case "1":
                Name = input("Nombre de la canción: ")
                searchSongInPlays(Name)
                break
            case "2":
                startMenu()
                break
            case other:
                continue
    return


# listo
def showFav():
    cursor.execute("""SELECT * FROM lista_favoritos""")
    rows = cursor.fetchall()
    if len(rows) > 0:
        print("Canciones favoritas: ")
        for row in rows:
            print("\t", row[2], "-", row[1])
    else:
        print("No tienes ninguna cancion favorita")
    print("Acciones Rápidas: 1)Buscar una canción  2)Volver al menú principal")
    choice = input("> ")
    match choice:
        case "1":
            searchSong()
        case "2":
            return
    return


# listo
def makeFav(songID):
    cursor.execute("""SELECT id FROM lista_favoritos WHERE id=?""", songID)
    select = cursor.fetchone()

    if not select:
        cursor.execute(
            """INSERT INTO lista_favoritos (id, song_name, artist_name, fecha_agregada) SELECT id, song_name, artist_name, GETDATE() FROM repositorio_musica WHERE id=?""",
            songID,
        )
        print("Cancion agregada a favoritos.")

        ##buscar en reproduccion y updatear
        cursor.execute("""SELECT id FROM reproduccion WHERE id=?""", songID)
        select2 = cursor.fetchone()
        if not select2:
            print("TEST la cancion no está en reproducciones.")
        else:
            cursor.execute("""UPDATE reproduccion SET favorito=1 WHERE id=?""", songID)

    else:
        print("La cancion ya esta en favoritos. ¿Desea quitarla?")
        rem = input("1)Sí, 2)No\n> ")
        if rem == "1":
            removeFav(songID)
        else:
            print("No hubo cambios.")
    return


# listo
def removeFav(songID):
    cursor.execute("""SELECT * FROM lista_favoritos WHERE id=?""", songID)
    print("Estás apunto de eliminar de tus favoritos la cancion:")
    print(cursor.fetchone())

    while True:
        selection = input("¿Confirmar?\n\t1)Sí\n\t2)No\n> ")
        match selection:
            case "1":
                cursor.execute("""DELETE FROM lista_favoritos WHERE id=?""", songID)
                print("Cancion eliminada de favoritos")

                cursor.execute("""SELECT id FROM reproduccion WHERE id=?""", songID)
                select2 = cursor.fetchone()
                if not select2:
                    print("TEST la cancion no está en reproducciones")
                else:
                    cursor.execute(
                        """UPDATE reproduccion SET favorito=0 WHERE id=?""", songID
                    )
                break
            case "2":
                print("La cancion no ha sido eliminada.")
    return


# listo
def playSong(songID):
    cursor.execute("""SELECT id FROM reproduccion WHERE id=?""", songID)
    aux = cursor.fetchone()

    if not aux:
        cursor.execute("""SELECT * FROM repositorio_musica WHERE id=?""", songID)
        song = cursor.fetchone()
        song_name = song[3]
        artist_name = song[2]
        reprod = 1
        cursor.execute("""SELECT id FROM lista_favoritos WHERE id=?""", songID)
        aux2 = cursor.fetchone()
        if aux2 is None:
            favorito = 0
        else:
            favorito = 1

        cursor.execute(
            """INSERT INTO reproduccion(id, song_name, artist_name, fecha_reproduccion, veces_reproducida, favorito) VALUES (?,?,?,GETDATE(),?,?)""",
            songID,
            song_name,
            artist_name,
            reprod,
            favorito,
        )
    else:
        cursor.execute(
            """UPDATE reproduccion SET veces_reproducida=veces_reproducida + 1 WHERE id=?""",
            songID,
        )

    print("Reproduciendo...")

    print("Acciones Rápidas: 1)Agregar a favoritos  2)Volver al menú principal")
    choice = input("> ")
    match choice:
        case "1":
            makeFav(songID)
        case "2":
            return
    return


# listo
def searchSong():
    loop = True
    while True:
        mode = input(
            "1)Buscar por nombre de canción.\n2)Buscar por artista.\nIngrese una opción: "
        )
        match mode:
            case "1":
                name = input("Nombre de la canción: ")
                cursor.execute(
                    """SELECT * FROM repositorio_musica WHERE song_name=?""", name
                )
                songs = cursor.fetchall()
                if len(songs) != 0:
                    if len(songs) > 1:
                        print("hay mas de una cancion con ese nombre")
                        i = 1
                        for song in songs:
                            # print(song)
                            print(str(i) + ")", song[2], "-", song[3])
                            i += 1
                        songnum = int(input("Escriba el numero de la canción: ")) - 1
                        print(
                            "Canción seleccionada:",
                            songs[songnum][2],
                            "-",
                            songs[songnum][3],
                        )

                    else:
                        songnum = 0
                    return songs[songnum][0]

                else:
                    print("No se encuentra la cancion.")

            case "2":
                artist = input("Nombre del artista: ")
                cursor.execute(
                    """SELECT * FROM repositorio_musica WHERE artist_name=?""", artist
                )
                songs = cursor.fetchall()
                if len(songs):
                    i = 1
                    for song in songs:
                        print(str(i) + ")", song[2], "-", song[3])
                        i += 1
                    songnum = int(input("Escriba el numero de la canción: ")) - 1
                    print(
                        "Canción seleccionada:",
                        songs[songnum][2],
                        "-",
                        songs[songnum][3],
                    )
                    return songs[songnum][0]
                else:
                    print("No se encuentra el artista.")
    return


# listo?
def searchSongInPlays(Name):
    cursor.execute("""SELECT * FROM reproduccion WHERE song_name=?""", Name)
    songs = cursor.fetchall()
    if songs:
        i = 1
        print(
            "   Nombre   |   Artista   |   Fecha primera rep.   |   Veces reproducida   |"
        )
        for song in songs:
            print(str(i) + ")", song[1], "|", song[2], "|", song[3], "|", song[4])
            i += 1

    else:
        print("No se encuentra esa cancion.")
    return


def showSongLastDays(date):
    cursor.execute(
        """SELECT * FROM reproduccion WHERE fecha_reproduccion >= ?""",
        date,
    )
    songs = cursor.fetchall()
    if len(songs) >= 1:
        i = 1
        print(
            "   Nombre   |   Artista   |   Fecha primera rep.   |   Veces reproducida   |"
        )
        for song in songs:
            print(str(i) + ")", song[1], "|", song[2], "|", song[3], "|", song[4])
            i += 1
    else:
        print("no hay cansione lol douu")
    return


def searchTop15():
    cursor.execute("""SELECT TOP 15 * FROM totalTop10 ORDER By timesInTop10 DESC""")
    top = cursor.fetchall()
    i = 1
    for artist in top:
        print(str(i) + ")", artist[0], "-", artist[1])
        i += 1

    print("Acciones Rápidas: 1)Volver al menú principal")
    choice = input("> ")
    match choice:
        case "1":
            startMenu()
    return


def searchPeakPos(name):
    # CHECKEAR SI EL NOMBRE EXISTE
    cursor.execute(
        """SELECT MIN(peak_position), artist_name FROM repositorio_musica WHERE artist_name=? GROUP BY artist_name""",
        name,
    )
    print(cursor.fetchall())
    return


def searchAvgPlays(name):
    cursor.execute(
        """SELECT AVG(CAST (total_streams AS BIGINT)), artist_name FROM repositorio_musica WHERE artist_name=? GROUP BY artist_name""",
        name,
    )
    print(cursor.fetchall())
    return


def main():
    initializeDB()
    print("Bienvenido a spotUSM!")
    startMenu()
    return


if __name__ == "__main__":
    main()
