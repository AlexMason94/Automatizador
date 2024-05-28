import tkinter as tk
import subprocess
from tkinter import messagebox, filedialog
import os
from utils import procesar_kml, detectar_repetidos, detectar_saltos, reasignar_numeros_secuenciales, validar_y_preparar_postes, actualizar_nombres_placemarks, registrar_cambios, verificar_consistencia, guardar_cambios_kml
from config import ns, script_dir, data_dir, data_dir_new

def seleccionar_archivo_y_procesar():
    tk_root = tk.Tk()
    tk_root.withdraw()  # Ocultar la ventana principal de Tkinter

    # Asegurar que los directorios existen
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(data_dir_new, exist_ok=True)

    
    file_path = filedialog.askopenfilename(filetypes=[("KML files", "*.kml;*.kmz")])
    if not file_path:
        messagebox.showinfo("Información", "No se seleccionó ningún archivo.")
        tk_root.destroy()
        return
    

     # Verificar la extensión del archivo seleccionado
    if not file_path.lower().endswith('.kml'):
        messagebox.showerror("Error de Formato", "Solo se aceptan archivos de tipo KML.")
        tk_root.destroy()  # Asegurarse de destruir la ventana de Tkinter
        return
    
    procesar_archivo(file_path, tk_root)

def procesar_archivo(file_path, tk_root):
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(data_dir_new, exist_ok=True)

    postes, root, tree = procesar_kml(file_path, ns)
    print("Postes procesados:", postes)  # Depuración
    postes_ordenados = sorted(postes, key=lambda x: x[1])
    
    repetidos = detectar_repetidos(postes_ordenados)
    print("Postes repetidos:", repetidos)  # Depuración
    saltos = detectar_saltos(postes_ordenados)
    print("Saltos detectados:", saltos)  # Depuración

     
   # Guardar y procesar información
    if not repetidos and not saltos:
        # Si no hay repetidos ni saltos, mostrar un mensaje indicando que todo está correcto
        messagebox.showinfo("Procesamiento Completado", "No se encontraron números repetidos ni saltos en la secuencia de números de poste.")

    
    with open(os.path.join(data_dir, 'resultado_inicial.txt'), 'w', encoding='utf-8') as file:
        for poste in postes_ordenados:
            file.write(f"{poste[0]}, {poste[1]}\n")

    with open(os.path.join(data_dir, 'repetidos.txt'), 'w', encoding='utf-8') as file:
        for numero, nombres in repetidos.items():
            line = f"Número repetido {numero}: {'; '.join(nombres)}\n"
            print("Escribiendo en 'repetidos.txt':", line.strip())  # Depuración
            file.write(line)

    with open(os.path.join(data_dir, 'saltos.txt'), 'w', encoding='utf-8') as file:
        for salto in saltos:
            line = f"Salto detectado entre {salto[0]} y {salto[1]}\n"
            print("Escribiendo en 'saltos.txt':", line.strip())  # Depuración
            file.write(line)

    
    postes_ordenados, cambios = reasignar_numeros_secuenciales(postes_ordenados)
    registrar_cambios(cambios, os.path.join(data_dir, 'registro_de_cambios.txt'))

    archivo_log = os.path.join(data_dir, 'registro_de_cambios.txt')
    registrar_cambios(cambios, archivo_log)
    # Registrar cambios en la vista previa de reasignaciones
    archivo_vista_previa = os.path.join(data_dir, 'vista_previa_reasignaciones.txt')
    with open(archivo_vista_previa, 'w', encoding='utf-8') as file:
        for nombre, numero_original, numero_nuevo in cambios:
            file.write(f"Cambio: {nombre} de número {numero_original} a {numero_nuevo}\n")
            
    errores = verificar_consistencia(postes_ordenados)
    if errores:
        with open(os.path.join(data_dir, 'errores.txt'), 'w', encoding='utf-8') as file:
            for error in errores:
                file.write(error + '\n')
    else:
        print("No se encontraron errores de consistencia.")

    actualizar_nombres_placemarks(root, postes_ordenados, ns)
    kml_file_path_nuevo = os.path.join(data_dir_new, 'modificado.kml')
    guardar_cambios_kml(tree, kml_file_path_nuevo)
    
    print(f"Procesamiento completado. Archivo guardado en: {kml_file_path_nuevo}")
    # Abrir la carpeta donde se guardan los archivos de texto
    subprocess.run(f'explorer "{data_dir}"', shell=True)
    # Abrir la carpeta donde se guarda el archivo KML modificado
    subprocess.run(f'explorer /select,"{kml_file_path_nuevo}"', shell=True)
    
     # Mostrar mensaje modal de confirmación
    tk_root.deiconify()  # Mostrar la ventana principal de Tkinter
    if repetidos or saltos:
        messagebox.showwarning("Advertencia", "Se detectaron saltos o repeticiones")
    else:
        messagebox.showinfo("Procesamiento Completado", "El archivo KML ha sido procesado exitosamente y no se detectaron errores.")
    tk_root.destroy()  # Cerrar la ventana de Tkinter después de cerrar el mensaje
if __name__ == "__main__":
    seleccionar_archivo_y_procesar()
