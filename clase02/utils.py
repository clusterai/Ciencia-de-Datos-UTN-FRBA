import os

import pandas as pd


def load_subte_data_old(molientes_path_old):
    """
    Función para cargar y procesar datos antiguos de molinetes del subte.

    Args:
        molientes_path_old (dict): Diccionario con años como claves y rutas de archivos como valores

    Returns:
        pd.DataFrame: DataFrame consolidado con todos los datos procesados
    """
    # Diccionario para almacenar los DataFrames de cada año
    dict_dataframes = {}

    # Lista de columnas que queremos eliminar por no ser útiles para el análisis
    delet_cols = ["periodo", "V1", "ID_ESTACION"]

    # Lista de tuplas para renombrar columnas: (nombre_viejo, nombre_nuevo)
    # Esto nos ayuda a estandarizar los nombres de columnas entre diferentes archivos
    rename_cols = [
        ("fecha", "FECHA"),
        ("desde", "DESDE"),
        ("hasta", "HASTA"),
        ("linea", "LINEA"),
        ("molinete", "MOLINETE"),
        ("estacion", "ESTACION"),
        ("pax_pagos", "PAX_PAGOS"),
        ("pax_pases_pagos", "PAX_PASES_PAGOS"),
        ("pax_franq", "PAX_FREQ"),
        ("total", "TOTAL"),
        ("pax_TOTAL", "TOTAL"),
    ]

    # Iteramos sobre cada año y su archivo correspondiente
    for year, path in molientes_path_old.items():
        print(f"Year: {year}")

        # Cargamos el archivo CSV como DataFrame usando pandas
        # delimiter=',' especifica que las columnas están separadas por comas
        # encoding='latin-1' maneja caracteres especiales del español
        df = pd.read_csv(path, delimiter=",", encoding="latin-1")

        # Eliminamos las columnas innecesarias si existen en el DataFrame
        for col in delet_cols:
            if col in df.columns:
                df = df.drop(columns=[col])

        # Renombramos las columnas para estandarizar los nombres
        for old, new in rename_cols:
            if old in df.columns:
                df = df.rename(columns={old: new})

        # Convertimos la columna FECHA a tipo datetime para poder trabajar con fechas
        # format='mixed' permite detectar automáticamente diferentes formatos de fecha
        df["FECHA"] = pd.to_datetime(df["FECHA"], format="mixed")

        # Guardamos el DataFrame procesado en nuestro diccionario
        dict_dataframes[year] = df

    # Concatenamos todos los DataFrames en uno solo
    # ignore_index=True reinicia el índice para tener una secuencia continua
    df_concat = pd.concat(dict_dataframes.values(), ignore_index=True)
    return df_concat


def load_subte_data_new(molinetes_path_new):
    """
    Función para cargar y procesar datos nuevos de molinetes del subte.
    Esta función maneja archivos más recientes que pueden estar organizados en carpetas.

    Args:
        molinetes_path_new (dict): Diccionario con años como claves y rutas de carpetas como valores

    Returns:
        pd.DataFrame: DataFrame consolidado con todos los datos procesados
    """
    # Diccionario para almacenar los DataFrames de cada año
    dict_of_dataframes_news = {}

    # Lista para almacenar información sobre las columnas (para debugging)
    list_of_colums = []

    # Columnas que queremos eliminar (incluye caracteres especiales por encoding)
    delet_cols = ["Â¿Fuera de rango?", "Ã¹Fuera de rango?", "DIA", "HORA", "TIPO_DIA"]

    # Mapeo para renombrar columnas y estandarizar nombres
    rename_cols = [
        ("fecha", "FECHA"),
        ("desde", "DESDE"),
        ("hasta", "HASTA"),
        ("linea", "LINEA"),
        ("molinete", "MOLINETE"),
        ("estacion", "ESTACION"),
        ("pax_pagos", "PAX_PAGOS"),
        ("pax_pases_pagos", "PAX_PASES_PAGOS"),
        ("pax_franq", "PAX_FREQ"),
        ("total", "TOTAL"),
        ("pax_TOTAL", "TOTAL"),
    ]

    # Iteramos sobre cada año y su carpeta correspondiente
    for year, folder in molinetes_path_new.items():
        print(f"Year: {year}")

        # os.walk() recorre recursivamente todas las subcarpetas
        # root: carpeta actual, dirs: subcarpetas, files: archivos en la carpeta actual
        for root, dirs, files in os.walk(folder):
            # Inicializamos un DataFrame vacío para cada carpeta
            df = pd.DataFrame()

            # Procesamos cada archivo en la carpeta actual
            for file in files:
                # Solo procesamos archivos CSV
                if file.endswith(".csv"):
                    # Cargamos el archivo CSV con configuración específica para archivos nuevos
                    # delimiter=';' porque estos archivos usan punto y coma como separador
                    # engine='python' para mejor manejo de archivos problemáticos
                    current_df = pd.read_csv(
                        os.path.join(root, file),
                        delimiter=";",
                        engine="python",
                        encoding="latin-1",
                    )

                    # Guardamos información de las columnas para debugging
                    list_of_colums.append(df.columns)

                    # Eliminamos columnas innecesarias si existen
                    for col in delet_cols:
                        if col in current_df.columns:
                            current_df = current_df.drop(columns=[col])

                    # Renombramos columnas para estandarizar
                    for old, new in rename_cols:
                        if old in current_df.columns:
                            current_df = current_df.rename(columns={old: new})

                    # Convertimos FECHA a tipo datetime
                    current_df["FECHA"] = pd.to_datetime(
                        current_df["FECHA"], format="mixed"
                    )

                # Concatenamos el DataFrame actual con el DataFrame acumulado del año
                df = pd.concat([df, current_df], ignore_index=True)

            # Guardamos el DataFrame consolidado del año
            dict_of_dataframes_news[year] = df

    # Concatenamos todos los años en un único DataFrame
    df_concat = pd.concat(dict_of_dataframes_news.values(), ignore_index=True)

    return df_concat


def clean_subte_dataframes(df):
    """
    Función para limpiar y estandarizar los datos del subte.
    Realiza múltiples operaciones de limpieza en las columnas LINEA y ESTACION,
    maneja valores nulos y agrega columnas de tiempo útiles para el análisis.

    Args:
        df (pd.DataFrame): DataFrame con datos crudos del subte

    Returns:
        pd.DataFrame: DataFrame limpio y procesado
    """

    # === LIMPIEZA DE LA COLUMNA LINEA ===
    # Removemos la palabra 'Linea' y variaciones para estandarizar los valores
    # El ? hace que la 'a' sea opcional (maneja "Linea" y "Línea")
    df["LINEA"] = df["LINEA"].str.replace(r"Linea?", "", regex=True)
    df["LINEA"] = df["LINEA"].str.replace(r"LINEA_?", "", regex=True)

    # === LIMPIEZA DE LA COLUMNA ESTACION ===
    # Convertimos todos los nombres de estaciones a mayúsculas para consistencia
    df["ESTACION"] = df["ESTACION"].str.upper()

    # Lista de diferentes formas en que aparece "AGÜERO" debido a problemas de encoding
    # Estos caracteres raros aparecen cuando hay problemas con acentos y caracteres especiales
    aguero_replace = [
        "AGÃ¼ERO",
        "AGÃ\x83Â¼ERO",
        "AGÂ\x81ERO",
        "AGÃ\x83Â\x83Ã\x82Â¼ERO",
        "AGÏ¿½ERO",
        "AGÃ\x82Â³ERO",
        "AGÃ¯Â¿Â½ERO",
        "AGÃ\x82Â\x81ERO",
    ]

    # Reemplazamos todas las variaciones problemáticas de "AGÜERO" con la forma estándar
    for a in aguero_replace:
        df["ESTACION"] = df["ESTACION"].str.replace(a, "AGUERO")

    # Estandarizamos otros nombres de estaciones problemáticos
    # .*SAENZ.* captura cualquier variación que contenga "SAENZ"
    df["ESTACION"] = df["ESTACION"].replace(r".*SAENZ .*", "SAENZ PEÑA", regex=True)

    # Removemos sufijos específicos de algunas estaciones (probablemente códigos internos)
    df["ESTACION"] = df["ESTACION"].replace("CALLAO.B", "CALLAO")
    df["ESTACION"] = df["ESTACION"].replace("PUEYRREDON.D", "PUEYRREDON")
    df["ESTACION"] = df["ESTACION"].replace("INDEPENDENCIA.H", "INDEPENDENCIA")
    df["ESTACION"] = df["ESTACION"].replace("RETIRO E", "RETIRO")

    # === ANÁLISIS DE VALORES NULOS ===
    # Calculamos la cantidad de valores nulos por columna, ordenados de mayor a menor
    total = df.isnull().sum().sort_values(ascending=False)

    # Volvemos a calcular lo mismo (código duplicado, posiblemente error)
    total = df.isnull().sum().sort_values(ascending=False)

    # Calculamos el porcentaje que representa cada cantidad de nulos respecto al total
    percent = (df.isnull().sum() / len(df)).sort_values(ascending=False)

    # Creamos una tabla que muestra tanto el total como el porcentaje de nulos
    missing_data = pd.concat([total, percent], axis=1, keys=["Total", "Percent"])
    print(missing_data)

    # === ELIMINACIÓN DE FILAS CON VALORES NULOS ===
    # Eliminamos cualquier fila que tenga al menos un valor nulo
    # how='any' significa que si ANY columna tiene NaN, elimina toda la fila
    # inplace=True modifica el DataFrame original en lugar de crear uno nuevo
    df.dropna(how="any", inplace=True)

    # Mostramos las dimensiones finales del dataset después de la limpieza
    print(
        f"Nos quedamos con un dataframe de {df.shape[0]} filas x {df.shape[1]} columnas"
    )

    # === CREACIÓN DE COLUMNAS TEMPORALES ===
    # Extraemos información temporal de la columna FECHA para análisis posteriores
    # Estas nuevas columnas nos permitirán agrupar y analizar por períodos específicos
    df["MONTH"] = df["FECHA"].dt.month  # Mes (1-12)
    df["YEAR"] = df["FECHA"].dt.year  # Año
    df["DAY"] = df["FECHA"].dt.weekday  # Día de la semana (0=Lunes, 6=Domingo)

    return df


def get_all_data(molientes_path_old, molinetes_path_new):
    """
    Función principal que unifica la carga y limpieza de todos los datos del subte.

    Args:
        molientes_path_old (dict): Diccionario con rutas a archivos de datos antiguos (puede ser None)
        molinetes_path_new (dict): Diccionario con rutas a carpetas de datos nuevos (puede ser None)

    Returns:
        pd.DataFrame: DataFrame consolidado con todos los datos procesados y limpios
    """

    # === PROCESAMIENTO CONDICIONAL DE DATOS ===
    # Solo procesamos datos antiguos si están disponibles
    if molientes_path_old:
        # Cargamos los datos antiguos usando la función específica
        df_old = load_subte_data_old(molientes_path_old)
        # Aplicamos el proceso de limpieza a los datos antiguos
        df_old = clean_subte_dataframes(df_old)

    # Solo procesamos datos nuevos si están disponibles
    if molinetes_path_new:
        # Cargamos los datos nuevos usando la función específica
        df_new = load_subte_data_new(molinetes_path_new)
        # Aplicamos el proceso de limpieza a los datos nuevos
        df_new = clean_subte_dataframes(df_new)

    # === CONSOLIDACIÓN FINAL ===
    # Determinamos qué datos combinar según lo que esté disponible
    if molientes_path_old and molinetes_path_new:
        # Si tenemos ambos tipos de datos, los combinamos
        df = pd.concat([df_old, df_new], ignore_index=True)
    elif molientes_path_old:
        # Si solo tenemos datos antiguos, usamos esos
        df = df_old
    elif molinetes_path_new:
        # Si solo tenemos datos nuevos, usamos esos
        df = df_new

    return df
