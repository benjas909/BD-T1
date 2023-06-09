import pyodbc as odbc
from datetime import datetime

# Conexión inicial con SQL SERVER
try:
    LOOP = True
    while LOOP:
        usr = int(
            input("¿Quién está usando el programa?\n(1)Pipes \n(2)Benjas\n(3)Otro\n> ")
        )
        if usr == 1:
            LOOP = False
            USR_STR = "pipe\SQLEXPRESS01"
        elif usr == 2:
            LOOP = False
            USR_STR = "Benjas\SQLEXPRESS"
        elif usr == 3:
            LOOP = False
            USR_STR = input("Ingrese el nombre de su server: ")
        else:
            print("Opción inválida.")

    connection = odbc.connect(
        f"DRIVER={{SQL SERVER}};SERVER={USR_STR};Trusted_Connection=yes",
        autocommit=True,
    )

    cursor = connection.cursor()
except Exception() as ex:
    print(ex)


def isValidDate(date):
    """
    Verifica si la fecha ingresada es válida.

    Verifica si el formato es correcto, si el año, mes y día son correctos y además, si la fecha es en el futuro.

    Returns
    -------
    res : bool
        Retorna True si la fecha es válida, False si no lo es.

    """
    format = "%Y-%m-%d"
    res = True
    now = datetime.now()
    try:
        res = bool(
            bool(datetime.strptime(date, format))
            and (datetime.strptime(date, "%Y-%m-%d")) <= now
        )
    except ValueError:
        res = False

    return res


# listo
def initializeDB():
    """
    Inicializa la base de datos.

    Si la base no existe, se crean ella, sus tablas, funciones y views, en caso contrario, solo se usa.
    """

    # Query para obtener los nombres de las bases de datos existentes
    cursor.execute("SELECT name FROM master.dbo.sysdatabases")
    rowAux = cursor.fetchall()
    row = [item for i in rowAux for item in i]

    # Si spotUSM no existe, se crea ella y sus tablas, para finalmente cargar los datos a repositorio_musica
    if "spotUSM" not in row:
        print("Inicializando Base de Datos...")
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

        # Se llama a la función para cargar los datos a la base
        loadIntoDB()

        # Creación de la view para uso en la función top15
        cursor.execute(
            """CREATE VIEW totalTop10 AS SELECT artist_name, SUM(top_10) AS timesInTop10 FROM repositorio_musica GROUP BY artist_name"""
        )

        # Función SQL que revisa si la canción está en favoritos y retorna un 1 si es así, o un 0 si no
        cursor.execute(
            """CREATE FUNCTION dbo.checkFavs (@id INT)
                RETURNS INT
                AS
                BEGIN
                    DECLARE @result INT
                    SET @result = 0
                    
                    IF EXISTS(SELECT id FROM lista_favoritos WHERE id = @id)
                        SET @result = 1
        
                    RETURN @result
                END"""
        )

    cursor.execute("USE spotUSM")

    return


# listo
def loadIntoDB():
    """
    Carga los datos leídos desde el csv hacia la base de datos.

    Se lee, manipula y carga linea por linea (o canción por canción) el archivo csv.
    """

    inFile = open("song.csv", "r", encoding="utf-8")
    songID = 0

    # Se cambia este ajuste para poder usar comillas dobles y evitar confusión del programa con apóstrofes
    cursor.execute("SET QUOTED_IDENTIFIER OFF")

    # Lectura, manipulación e inserción a la base de datos de cada fila de datos en el archivo csv
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

        cursor.execute(insert)
        songID += 1

    inFile.close()
    return


# listo
def startMenu():
    """
    Menú principal del programa.

    Permite navegar a las diferentes opciones que se ofrecen ingresando el número de opción.
    """

    while True:
        print("Menu:")
        print(
            """\t1)Mostrar canciones reproducidas.\n\t2)Mostrar canciones favoritas.\n\t3)Buscar canción (Reproducir/Agregar/Quitar Favorito)\n\t4)Escuchadas en los ultimos dias.\n\t5)TOP 15.\n\t6)Posición peak \n\t7)Promedio streams \n\t8)Salir"""
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
                showSongLastDays()
            case "5":
                searchTop15()
            case "6":
                searchPeakPos()
            case "7":
                searchAvgPlays()
            case "8":
                while True:
                    close = input("\t¿Cerrar Sesión?\n\t[Y/N]\n> ")
                    if close == "Y" or close == "y":
                        print("Cerrando Sesión...")
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
    """
    Muestra la lista de canciones reproducidas por el usuario.

    Permite ordenar la lista por fecha o cantidad de reproducciones, y de manera ascendiente o descendiente.
    """

    while True:
        print("\t1) Ordenar por fecha")
        print("\t2) Ordenar por reproducciones")

        songChoice = input("> ")
        i = 1

        match songChoice:
            case "1":
                while True:
                    order = input("\t1)Orden ascendente\n\t2)Orden descendente\n> ")
                    match order:
                        case "1":
                            order = "ASC"
                            break
                        case "2":
                            order = "DESC"
                            break
                        case other:
                            print("Opción inválida.")
                            continue

                cursor.execute(
                    f"""SELECT * FROM reproduccion ORDER BY fecha_reproduccion {order}"""
                )
                songs = cursor.fetchall()
                if not songs:
                    print("Lista vacía.")
                    return

                for song in songs:
                    if song[5]:
                        favStr = "Está en favoritos."
                    else:
                        favStr = "No está en favoritos."

                    print(
                        f"\t{str(i)}) {song[1]} - {song[2]} | Primera reproducción: {song[3]} | Veces reproducida: {song[4]} | {favStr}"
                    )
                    i += 1
                break

            case "2":
                while True:
                    order = input("\t1)Orden ascendente\n\t2)Orden descendente\n> ")
                    match order:
                        case "1":
                            order = "ASC"
                            break
                        case "2":
                            order = "DESC"
                            break
                        case other:
                            print("Opción inválida.")
                            continue
                cursor.execute(
                    f"""SELECT * FROM reproduccion ORDER BY veces_reproducida {order}"""
                )
                songs = cursor.fetchall()
                if not songs:
                    print("Lista vacía.")
                    return

                for song in songs:
                    if song[5]:
                        favStr = "Está en favoritos."
                    else:
                        favStr = "No está en favoritos."

                    print(
                        f"\t{str(i)}) {song[1]} - {song[2]} | Primera reproducción: {song[3]} | Veces reproducida: {song[4]} | {favStr}"
                    )
                    i += 1
                break

            case other:
                print("Opción inválida.")
                continue

    while True:
        print("Acciones Rápidas: 1)Buscar en la lista  2)Volver al menú principal")
        choice = input("> ")
        match choice:
            case "1":
                Name = input("Nombre de la canción: ")
                searchSongInPlays(Name)
                break
            case "2":
                return
            case other:
                continue
    return


# listo
def showFav():
    """
    Muestra las canciones favoritas del usuario.
    """
    cursor.execute("""SELECT * FROM lista_favoritos""")
    rows = cursor.fetchall()
    if len(rows) > 0:
        print("Canciones favoritas: ")
        for row in rows:
            print("\t", row[2], "-", row[1])
    else:
        print("No tienes ninguna cancion favorita")

    while True:
        print("Acciones Rápidas: 1)Buscar una canción  2)Volver al menú principal")
        choice = input("> ")
        match choice:
            case "1":
                searchSong()
                return
            case "2":
                return
            case other:
                print("Opción inválida.")
                continue


# listo
def makeFav(songID):
    """
    Permite agregar una canción a la lista de favoritos.

    En caso de que la canción ya esté en la lista, da la opción de quitarla. Además, actualiza la tabla reproducciones.

    Parameters
    ----------
    songID : int
        ID de la canción a agregar.

    """
    cursor.execute("""SELECT dbo.checkFavs(?)""", songID)
    favorito = cursor.fetchone()[0]

    if not favorito:
        cursor.execute(
            """INSERT INTO lista_favoritos (id, song_name, artist_name, fecha_agregada) SELECT id, song_name, artist_name, GETDATE() FROM repositorio_musica WHERE id=?""",
            songID,
        )
        print("Cancion agregada a favoritos.")

        ##buscar en reproduccion y updatear
        cursor.execute("""SELECT id FROM reproduccion WHERE id=?""", songID)
        select2 = cursor.fetchone()
        if select2:
            cursor.execute("""UPDATE reproduccion SET favorito=1 WHERE id=?""", songID)

    else:
        print("La cancion ya esta en favoritos. ¿Desea quitarla?")
        rem = input("\t1)Sí\n\t2)No\n> ")
        if rem == "1":
            removeFav(songID)
        else:
            print("No hubo cambios.")
    return


# listo
def removeFav(songID):
    """
    Quita la canción indicada de la lista de favoritos.

    Además, actualiza su estado en la lista reproducciones.

    Parameters
    ----------
    songID : int
        ID de la canción a agregar.

    """
    cursor.execute("""SELECT * FROM lista_favoritos WHERE id=?""", songID)
    print("Estás a punto de eliminar de tus favoritos la cancion:")
    song = cursor.fetchone()
    print("\t" + song[2] + " - " + song[1])

    while True:
        selection = input("¿Confirmar?\n\t1)Sí\n\t2)No\n> ")
        match selection:
            case "1":
                cursor.execute("""DELETE FROM lista_favoritos WHERE id=?""", songID)
                print("Cancion eliminada de favoritos")

                cursor.execute("""SELECT id FROM reproduccion WHERE id=?""", songID)
                select2 = cursor.fetchone()
                if select2:
                    cursor.execute(
                        """UPDATE reproduccion SET favorito=0 WHERE id=?""", songID
                    )
                break
            case "2":
                print("La cancion no ha sido eliminada.")
    return


# listo
def playSong(songID):
    """
    "Reproduce" la canción dada.

    Actualiza todos los valores necesarios, además de dar la opción de agregar o quitar la canción de favoritos.

    Parameters
    ----------
    songID : int
        ID de la canción a agregar.

    """
    # se busca si la canción ya ha sido reproducida antes
    cursor.execute("""SELECT id FROM reproduccion WHERE id=?""", songID)
    aux = cursor.fetchone()

    if not aux:
        # si la cancion no ha sido reproducida antes, hay que buscar los datos de la canción en el repositorio
        cursor.execute("""SELECT * FROM repositorio_musica WHERE id=?""", songID)
        song = cursor.fetchone()
        song_name = song[3]
        artist_name = song[2]
        reprod = 1

        # busca si la cancion está en la tabla favoritos, retorna 0 si no
        cursor.execute("""SELECT dbo.checkFavs(?)""", songID)
        favorito = cursor.fetchone()[0]

        cursor.execute(
            """INSERT INTO reproduccion(id, song_name, artist_name, fecha_reproduccion, veces_reproducida, favorito) VALUES (?,?,?,GETDATE(),?,?)""",
            songID,
            song_name,
            artist_name,
            reprod,
            favorito,
        )
    else:
        # Si la canción ya estaba en reproduccion, solo se aumenta el numero de reproducciones
        cursor.execute(
            """UPDATE reproduccion SET veces_reproducida=veces_reproducida + 1 WHERE id=?""",
            songID,
        )
    cursor.execute(
        """UPDATE repositorio_musica SET total_streams = total_streams + 1 WHERE id=?""",
        songID,
    )

    print("Reproduciendo...")

    while True:
        print("Acciones Rápidas: 1)Agregar a favoritos  2)Volver al menú principal")
        choice = input("> ")
        match choice:
            case "1":
                makeFav(songID)
                return
            case "2":
                return
            case other:
                print("Opción inválida.")
                continue


# listo
def searchSong():
    """
    Permite buscar canciones en el repositorio.

    Permite buscar por nombre de canción y nombre de artista y seleccionar la canción deseada.

    Returns
    -------
    songID :
        ID de la canción seleccionada.

    """
    loop = True
    while True:
        mode = input("\t1)Buscar por nombre de canción.\n\t2)Buscar por artista.\n> ")
        match mode:
            case "1":
                name = input("Nombre de la canción: ")
                cursor.execute(
                    """SELECT * FROM repositorio_musica WHERE song_name=?""", name
                )
                songs = cursor.fetchall()
                if len(songs) != 0:
                    if len(songs) > 1:
                        print("Hay más de una cancion con ese nombre.")
                        i = 1
                        for song in songs:
                            # print(song)
                            print("\t" + str(i) + ")", song[2], "-", song[3])
                            i += 1

                        while True:
                            songnum = (
                                int(input("Escriba el numero de la canción: ")) - 1
                            )
                            if songnum not in range(i - 1):
                                print("Opción inválida.")
                                continue
                            else:
                                break

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
                        print("\t" + str(i) + ")", song[2], "-", song[3])
                        i += 1

                    while True:
                        songnum = int(input("Escriba el numero de la canción: ")) - 1
                        if songnum not in range(i - 1):
                            print("Opción inválida.")
                            continue
                        else:
                            break

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


def searchSongInPlays(Name):
    """
    Permite buscar canciones en la lista de reproducciones del usuario.

    Muestra las canciones y sus datos.

    Parameters
    ----------
    Name : str
        Nombre de la canción a buscar.

    """
    cursor.execute("""SELECT * FROM reproduccion WHERE song_name=?""", Name)
    songs = cursor.fetchall()
    if songs:
        i = 1
        for song in songs:
            if song[5]:
                favStr = "Está en favoritos."
            else:
                favStr = "No está en favoritos."

            print(
                f"\t {str(i)}) {song[1]} - {song[2]} | Primera reproducción: {song[3]} | Veces reproducida: {song[4]} | {favStr}"
            )
            i += 1

    else:
        print("No se encuentra esa cancion.")

    while True:
        print("Acciones Rápidas: 1)Volver al menú principal")
        choice = input("> ")
        match choice:
            case "1":
                return
            case other:
                print("Opción inválida,")
                continue


def showSongLastDays():
    """
    Muestra las canciones reproducidas desde la fecha dada.

    Muestra las canciones y sus datos.

    """
    now = datetime.now()

    while True:
        date = input("Ingrese una fecha (AAAA-MM-DD): ")

        if isValidDate(date):
            break
        else:
            print("Fecha inválida.")

    cursor.execute(
        """SELECT * FROM reproduccion WHERE fecha_reproduccion >= ?""",
        date,
    )
    songs = cursor.fetchall()
    if len(songs) >= 1:
        i = 1
        for song in songs:
            if song[5]:
                favStr = "Está en favoritos."
            else:
                favStr = "No está en favoritos."

            print(
                f"{str(i)}) {song[1]} - {song[2]} | Primera reproducción: {song[3]} | Veces reproducida: {song[4]} | {favStr}"
            )
            i += 1
    else:
        print("No has reproducido canciones desde ese día.")

    while True:
        print("Acciones Rápidas: 1)Volver al menú principal")
        choice = input("> ")
        match choice:
            case "1":
                return
            case other:
                print("Opción inválida,")
                continue


def searchTop15():
    """
    Muestra el top 15 de artistas con mayor cantidad total de veces en que sus canciones han estado en el top 10.

    Muestra cada artista y la cantidad de veces que ha estado en el top.

    """
    cursor.execute("""SELECT TOP 15 * FROM totalTop10 ORDER By timesInTop10 DESC""")
    top = cursor.fetchall()
    i = 1
    for artist in top:
        print("\t" + str(i) + ")", artist[0], "-", artist[1])
        i += 1

    while True:
        print("Acciones Rápidas: 1)Volver al menú principal")
        choice = input("> ")
        match choice:
            case "1":
                return
            case other:
                print("Opción inválida,")
                continue


def searchPeakPos():
    """
    Muestra la posición más alta que ha alcanzado el artista en el top.

    En caso de no encontrar el artista, sigue preguntando.

    """
    while True:
        name = input("Nombre artista: ")
        # CHECKEAR SI EL NOMBRE EXISTE
        cursor.execute(
            """SELECT artist_name FROM repositorio_musica WHERE artist_name=?""", name
        )
        row = cursor.fetchone()

        if row:
            cursor.execute(
                """SELECT MIN(peak_position), artist_name FROM repositorio_musica WHERE artist_name=? GROUP BY artist_name""",
                name,
            )
            output = cursor.fetchone()
            print(f"{output[1]} - Posición más alta: {output[0]}")

            while True:
                print("Acciones Rápidas: 1)Volver al menú principal")
                choice = input("> ")
                match choice:
                    case "1":
                        return
                    case other:
                        continue

        else:
            print("No se encuentra el artista.")
            continue


def searchAvgPlays():
    """
    Muestra el promedio de streams del artista.

    En caso de no encontrar el artista, sigue preguntando.

    """
    while True:
        name = input("Nombre artista: ")

        cursor.execute(
            """SELECT artist_name FROM repositorio_musica WHERE artist_name=?""", name
        )
        row = cursor.fetchone()

        if row:
            cursor.execute(
                """SELECT AVG(CAST (total_streams AS BIGINT)), artist_name FROM repositorio_musica WHERE artist_name=? GROUP BY artist_name""",
                name,
            )
            output = cursor.fetchone()
            print(f"{output[1]} - Promedio de streams: {output[0]}")
            while True:
                print("Acciones Rápidas: 1)Volver al menú principal")
                choice = input("> ")
                match choice:
                    case "1":
                        return
                    case other:
                        print("Opción inválida,")
                        continue

        else:
            print("No se encuentra el artista.")
            continue


def main():
    initializeDB()
    print("Bienvenido a spotUSM!")
    startMenu()
    return


if __name__ == "__main__":
    main()
