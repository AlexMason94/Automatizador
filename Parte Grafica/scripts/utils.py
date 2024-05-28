import os
import xml.etree.ElementTree as ET
import re
from collections import defaultdict
from config import data_dir, data_dir_new
def validar_y_preparar_postes(postes):
    postes_unicos = []
    numeros_vistos = set()
    for poste in postes:
        nombre, numero = poste
        if numero not in numeros_vistos:
            postes_unicos.append(poste)
            numeros_vistos.add(numero)
    return postes_unicos

def procesar_kml(kml_file_path, ns):
    tree = ET.parse(kml_file_path)
    root = tree.getroot()
    postes = []
    regex_poste = r'\b(PMa|PMe|PC|PM|P|PRFV)[ -]*(\d*)'
    for placemark in root.findall('.//kml:Placemark', ns):
        nombre = placemark.find('kml:name', ns)
        if nombre is not None:
            match = re.search(regex_poste, nombre.text)
            if match:
                numero = int(match.group(2)) if match.group(2) else None
                if numero is not None:
                    postes.append((nombre.text, numero))
    return postes, root, tree

def detectar_repetidos(postes):
    conteo_numeros = defaultdict(list)
    for nombre, numero in postes:
        conteo_numeros[numero].append(nombre)
    repetidos = {numero: nombres for numero, nombres in conteo_numeros.items() if len(nombres) > 1}
    return repetidos

def detectar_saltos(postes_ordenados):
    saltos_detectados = []
    for i in range(len(postes_ordenados) - 1):
        diferencia = postes_ordenados[i + 1][1] - postes_ordenados[i][1]
        if diferencia > 1:
            saltos_detectados.append((postes_ordenados[i][0], postes_ordenados[i + 1][0]))
    return saltos_detectados

def reasignar_numeros_secuenciales(postes_ordenados):
    cambios = []
    if not postes_ordenados:
        return postes_ordenados, cambios

    numero_actual = postes_ordenados[0][1]
    for i in range(1, len(postes_ordenados)):
        nombre_actual, numero_actual_poste = postes_ordenados[i]
        nombre_anterior, numero_anterior_poste = postes_ordenados[i-1]

        # Incrementar el número actual si es necesario
        if numero_actual_poste <= numero_anterior_poste:
            numero_actual = numero_anterior_poste + 1
        else:
            numero_actual = numero_actual_poste

        # Guardar el cambio si el número ha sido ajustado
        if numero_actual != numero_actual_poste:
            cambios.append((nombre_actual, numero_actual_poste, numero_actual))
            postes_ordenados[i] = (nombre_actual, numero_actual)

    return postes_ordenados, cambios


def verificar_consistencia(postes_ordenados):
    errores = []
    for i in range(1, len(postes_ordenados)):
        if postes_ordenados[i][1] <= postes_ordenados[i-1][1]:
            errores.append(f"Error de secuencia en {postes_ordenados[i][0]}: {postes_ordenados[i-1][1]} seguido de {postes_ordenados[i][1]}")
    return errores

def registrar_cambios(cambios, archivo_log):
    with open(archivo_log, 'w', encoding='utf-8') as file:
        for cambio in cambios:
            file.write(f"Poste: {cambio[0]}, Número original: {cambio[1]}, Número reasignado: {cambio[2]}\n")


def actualizar_nombres_placemarks(root, postes_actualizados, ns):
    for placemark in root.findall('.//kml:Placemark', ns):
        nombre_element = placemark.find('.//kml:name', ns)
        if nombre_element is not None:
            nombre_actual = nombre_element.text
            for nombre_poste, nuevo_numero in postes_actualizados:
                if nombre_actual.startswith(nombre_poste.rsplit(' ', 1)[0]):
                    match = re.match(r"([a-zA-Z-]+)(\d+)", nombre_actual)
                    if match:
                        prefijo = match.group(1)
                        resto = nombre_actual[match.end(2):]
                        nombre_actualizado = f"{prefijo}{nuevo_numero}{resto}"
                        nombre_element.text = nombre_actualizado
                        break

def guardar_cambios_kml(tree, filename):
    file_path_nuevo = os.path.join(data_dir_new, filename)
    tree.write(file_path_nuevo, encoding='utf-8', xml_declaration=True)