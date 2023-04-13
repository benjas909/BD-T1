import pyodbc as odbc

try:
    LOOP = True
    while LOOP:
        usr = int(
            input(
                "¿Quién está usando el programa?\n(1)Pipes \n(2)Benjas\n(3)Otro (UNTESTED)"
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


def initializeDB():
    cursor.execute("SELECT name FROM master.dbo.sysdatabases")
    rowAux = cursor.fetchall()
    row = [item for i in rowAux for item in i]
    if "spotUSM" not in row:
        cursor.execute("CREATE DATABASE spotUSM")
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
    cursor.execute("USE spotUSM")
    return


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


def startMenu():
    print("Menu:")
    print(
        """\t1)Mostrar canciones reproducidas.\n\t2)Mostrar canciones favoritas.\n\t3)Buscar canción.\n\t4)Escuchadas en los ultimos dias.\n\t5)TOP 15 TEST.\n\t6)posicion peak \n\t7)promedio streams"""
    )
    choice = input("Ingrese una opción: ")
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
                    "¿Qué desea hacer?\n\t1)Reproducir.\n\t2)Agregar/Quitar de favoritos."
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
            days = input("Cuantos dias? ")
            showSongLastDays(days)
        case "5":
            searchTop15()
        case "6":
            name = input("Nombre artista ")
            searchPeakPos(name)
        case "7":
            name = input("Nombre artista ")
            searchAvgPlays(name)


def showPlays():
    print("1) Ordenar por fecha")
    print("2) Ordenar por reproducciones")

    songChoice = input("Opción: ")
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

    print("Acciones Rápidas: 1)Buscar en la lista  2)Volver al menú principal")
    choice = input("Acción")
    match choice:
        case "1":
            Name = input("Nombre de la canción: ")
            searchSongInPlays(Name)
        case "2":
            startMenu()


def showFav():
    cursor.execute("""SELECT * FROM lista_favoritos""")
    rows = cursor.fetchall()
    if len(rows) > 0:
        print("Canciones favoritas: ")
        for row in rows:
            print(row)
    else:
        print("No tienes ninguna cancion favorita")


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
        rem = input("1)Sí, 2)No\n>")
        if rem == 1:
            removeFav(songID)
        else:
            print("No hubo cambios.")
    startMenu()


def removeFav(songID):
    cursor.execute("""SELECT * FROM lista_favoritos WHERE id=?""", songID)
    print("Estás apunto de eliminar de tus favoritos la cancion:")
    print(cursor.fetchone())

    selection = input("Para confirmar escriba SI ")
    match selection:
        case "SI":
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
        case _:
            print("La cancion no ha sido eliminada.")


def playSong(songID):
    # name = input("Nombre de la canción: ")
    # cursor.execute("""SELECT * FROM repositorio_musica WHERE song_name=?""", name)
    # songs = cursor.fetchall()
    # if len(songs) != 0:

    #     if len(songs) > 1:
    #         print("hay mas de una cancion con ese nombre")
    #         i = 1
    #         for song in songs:
    #             # print(song)
    #             print(str(i) + ')', song[2], '-', song[3])
    #             i += 1
    #         songnum = int(input("Escriba el numero de la canción: ")) - 1
    #     else:
    #         songnum = 0

    #     songID = songs[songnum][0]
    cursor.execute("""SELECT id FROM reproduccion WHERE id=?""", songID)
    aux = cursor.fetchone()
    # print(aux, 'hola')

    if not aux:
        cursor.execute("""SELECT * FROM repositorio_musica WHERE id=?""", songID)
        # print(songs[songnum])
        song = cursor.fetchone()
        song_name = song[3]
        artist_name = song[2]
        # print(artist_name)
        reprod = 1
        cursor.execute("""SELECT id FROM lista_favoritos WHERE id=?""", songID)
        aux2 = cursor.fetchone()
        # print('buenas', aux2)
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
    choice = input("Acción: ")
    match choice:
        case "1":
            makeFav(songID)
        case "2":
            startMenu()


# else:
#     print("cancion no encontrada")


def searchSong():
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
                else:
                    songnum = 0
                songID = songs[songnum][0]
            else:
                print("No se encuentra la cancion.")
                songID = searchSong()

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
                songID = songs[songnum][0]

                print("Canción seleccionada.")

            else:
                print("No se encuentra el artista.")
                songID = searchSong()
    return songID


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
        # print("Acciones Rápidas: 1)Agregar a favoritos  2)Volver al menú principal")
        # choice = input("Acción: ")
        # match choice:
        #     case '1':

        #     case '2':
        #         startMenu()
    else:
        print("No se encuentra esa cancion.")


def showSongLastDays(Days):
    cursor.execute(
        """SELECT * FROM reproduccion WHERE fecha_reproduccion >= DATEADD(day, -?, GETDATE())""",
        int(Days),
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


def searchTop15():
    cursor.execute(
        """CREATE VIEW sumtop10 AS SELECT artist_name,SUM(top_10) as timesintop10 FROM repositorio_musica GROUP BY artist_name"""
    )
    cursor.execute("""SELECT TOP 15 * FROM sumtop10 ORDER By timesintop10 DESC""")
    top = cursor.fetchall()
    i = 1
    for artist in top:
        print(str(i) + ")", artist[0], "-", artist[1])
        i += 1


def searchPeakPos(name):
    # CHECKEAR SI EL NOMBRE EXISTE
    cursor.execute(
        """SELECT MIN(peak_position), artist_name FROM repositorio_musica WHERE artist_name=? GROUP BY artist_name""",
        name,
    )
    print(cursor.fetchall())


def searchAvgPlays(name):
    cursor.execute(
        """SELECT AVG(CAST (total_streams AS BIGINT)), artist_name FROM repositorio_musica WHERE artist_name=? GROUP BY artist_name""",
        name,
    )
    print(cursor.fetchall())


def main():
    initializeDB()
    print("Bienvenido a spotUSM!")
    # print("Inicializando...")
    # loadIntoDB()
    startMenu()
    # playSong()
    # cancion = input("buscar: ")
    # searchSongInPlays(cancion)


if __name__ == "__main__":
    main()
