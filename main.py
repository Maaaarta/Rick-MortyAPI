# 1)importa las librerias
import requests #esta para hacer llamadas a la api
import pandas as pd #esta para manejar los dataframes
import os #esta para manejar carpetas y archivos
#creamos una carpeta para guardar las imagenes de los personajes
os.makedirs("imagenes", exist_ok=True)  #si ya existe no pasa nada, por eso el exist_ok

# 2)traer todos los personajes de la api
#lista que va guaradando todos los personajes
todos_los_personajes = []  #aquí se irán metiendo todos los personajes
# url de la api de los personajes
url = "https://rickandmortyapi.com/api/character"
#bucle para recorrer todas las paginas de la api
while url:  #mientras haya una siguiente página va a seguir
    response = requests.get(url).json()  #hace request a la api y se convierte en json
    todos_los_personajes.extend(response['results']) #guarda los personajes en la lista
    url = response['info']['next']  # lleva ala siguiente pagina
#crea dataframe con todos los personajes de la lista
df = pd.DataFrame(todos_los_personajes)  #aquí ya tenemos toda la info en formato tabla
#selecciona las columnas necesarias para el dataframe
df = df[['id', 'name', 'status', 'species', 'gender', 'episode', 'image']]

# 3) modificar el dataframe y usar 'id' como indice del dataframe
df.set_index('id', inplace=True)

# 4) guardar y leer csv
#guardda el csv en UTF-8 i evita errors amb accents i caracters especials
df.to_csv("rick_and_morty.csv", encoding="utf-8") #aquí se guarda todo en un archivo csv
#lee el CSV para continuar trabajando sin hacer otra llamada a la api
df_csv = pd.read_csv("rick_and_morty.csv", index_col='id')  #lo leemos de nuevo para comprobar que va bien
#comprovar que se lee bien el csv
print(df_csv.head())  #muestra las primeras filas con head
print(df_csv.info())  #muestra info del dataframe (tipos, columnas, ...)

# 5) busca los personajes y guarda sus imagenes para meterlas en una carpeta 
personajes_especiales = ["Mel Gibson", "Johnny Depp", "Pickle Rick"]  #los personajes que queremos buscar

for nombre in personajes_especiales:
    # filtra el dataframe por nombre de personaje
    p = df[df['name'] == nombre]  #busca si el nombre coincide exactamente
    if not p.empty:  #si existe ese personaje en la tabla
        url_img = p['image'].values[0] #pillamos ña url de la imagen
        #guarda las imagenes localmente en una carpeta independiente que va a crear automaticamente llamada /imagenes/
        img_data = requests.get(url_img).content  #descarga la imagen
        with open(f"imagenes/{nombre.replace(' ', '_')}.jpeg", "wb") as f:
            f.write(img_data)  #guarda la imagen en el archivo

# 6) cuenta las apariciones de los personajes estelares
personajes_estelares = ["Birdperson", "Squanchy", "Mr. Meeseeks"]  #personajes que aparecen en varios caps

for nombre in personajes_estelares:
    df_personaje = df[df['name'].str.contains(nombre, case=False)]  #busca aunque no sea exactamente igual
    if not df_personaje.empty:
        # explode separa los episodios que están en listas
        episodios = df_personaje['episode'].explode()  #convierte la lista de episodios en filas
        # xxtrae solo el id del episodio de la url
        episodios_ids = episodios.apply(lambda x: x.split('/')[-1])  #saca solo el número del episodio(con lambda)
        print(f"{nombre} aparece en los episodios: {list(episodios_ids)}")  #imprime los episodios

# 7) crea el csv de las apariciones de personajes estelares
lista_apariciones = []  #aquí se guardará cada aparición como registro independiente

for nombre in personajes_estelares:
    df_personaje = df[df['name'].str.contains(nombre, case=False)]  #buscamos el personaje
    if not df_personaje.empty:
        episodios = df_personaje['episode'].explode()  #separamos los episodios
        for ep in episodios:  #recorremos cada episodio
            lista_apariciones.append({"personaje": nombre, "episode_id": ep.split('/')[-1]})
            #cada aparición se guarda como diccionario con personaje + id del episodio

df_apariciones = pd.DataFrame(lista_apariciones)  #convertimos la lista en dataframe
#guarda el csv con las apariciones de los personajes
df_apariciones.to_csv("apariciones_estelares.csv", index=False, encoding='utf-8')  #guardamos el csv final
