Benjamín Aguilera - 202173507-0
Felipe Nuñez - 202173568-2

    - Para el correcto funcionamiento del programa, DEBE ejecutarse en Python 3.10 o superior.
    - Al principio de la ejecución, el programa pregunta quién está usando el mismo, en caso de elegir "otro", se debe ingresar
      el nombre de servidor de quién lo ejecute.
    - No todas las opciones mencionadas en el pdf están disponibles directamente en el menú principal, algunas de ellas están 
      dentro de otro menú, como la opción para reproducir y agregar a favoritos, que están dentro de la opción de buscar canción.
    - Debido a una ambigüedad en el punto 7, hicimos la suposición de que se le debe preguntar al usuario la fecha desde la cual 
      quiere saber las canciones que ha escuchado.
    - Al reproducir una canción, también se actualiza la columna total_streams de la misma en la tabla repositorio_musica
    - Se usó una view para el punto 9, el cuál consistía en mostrar el top 15 de artistas que han estado más veces en el top 10
    - La función SQL se usó en un par de puntos a lo largo del programa, y consiste en revisar si la canción dada por el id, está
      en favoritos, y retorna un 1 en ese caso, y un 0 en el caso contrario.