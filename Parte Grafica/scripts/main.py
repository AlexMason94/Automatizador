import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
import os
from PIL import Image, ImageTk  # Importar Image y ImageTk
import subprocess  # Importa subprocess para abrir exploradores de archivos
import webbrowser
from config import root_dir
from utils import procesar_kml, detectar_repetidos, detectar_saltos, reasignar_numeros_secuenciales, validar_y_preparar_postes, actualizar_nombres_placemarks, registrar_cambios, verificar_consistencia, guardar_cambios_kml
from config import ns, script_dir, data_dir, data_dir_new

def abrir_github():
    webbrowser.open("https://github.com/AlexMason94")  
def seleccionar_archivo():
    file_path = filedialog.askopenfilename(filetypes=[("KML files", "*.kml;*.kmz")])
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

def iniciar_renumeracion():
    file_path = entry_file_path.get()
    if not file_path:
        messagebox.showwarning("Advertencia", "Por favor, seleccione un archivo antes de continuar.")
        return
     # Asegurar que los directorios existen
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(data_dir_new, exist_ok=True)

     # Verificar la extensión del archivo seleccionado
    if not file_path.lower().endswith('.kml'):
        messagebox.showerror("Error de Formato", "Solo se aceptan archivos de tipo KML.")
        return

    postes, root, tree = procesar_kml(file_path, ns)
    postes_ordenados = sorted(postes, key=lambda x: x[1])
    
    repetidos = detectar_repetidos(postes_ordenados)
    saltos = detectar_saltos(postes_ordenados)
    
    
    with open(os.path.join(data_dir, 'resultado_inicial.txt'), 'w', encoding='utf-8') as file:
        for poste in postes_ordenados:
            file.write(f"{poste[0]}, {poste[1]}\n")
    
    if repetidos:
        with open(os.path.join(data_dir, 'repetidos.txt'), 'w', encoding='utf-8') as file:
            for numero, nombres in repetidos.items():
                file.write(f"Número repetido {numero}: {'; '.join(nombres)}\n")

    if saltos:
        with open(os.path.join(data_dir, 'saltos.txt'), 'w', encoding='utf-8') as file:
            for salto in saltos:
                file.write(f"Salto detectado entre {salto[0]} y {salto[1]}\n")
    
    postes_ordenados, cambios = reasignar_numeros_secuenciales(postes_ordenados)
    registrar_cambios(cambios, os.path.join(data_dir, 'registro_de_cambios.txt'))

    errores = verificar_consistencia(postes_ordenados)
    if errores:
        with open(os.path.join(data_dir, 'errores.txt'), 'w', encoding='utf-8') as file:
            for error in errores:
                file.write(error + '\n')

    # Guardar y procesar información
    actualizar_nombres_placemarks(root, postes_ordenados, ns)
    kml_file_path_nuevo = os.path.join(data_dir_new, 'modificado.kml')
    guardar_cambios_kml(tree, kml_file_path_nuevo)

    # Abrir la carpeta donde se guardan los archivos de texto
    subprocess.run(f'explorer "{data_dir}"', shell=True)
    # Abrir la carpeta donde se guarda el archivo KML modificado
    subprocess.run(f'explorer /select,"{kml_file_path_nuevo}"', shell=True)

    if repetidos or saltos:
        messagebox.showwarning("Advertencia", "Se detectaron saltos o repeticiones.")
    else:
        messagebox.showinfo("Procesamiento Completado", "El archivo KML ha sido procesado exitosamente y no se detectaron errores.")


main_window = tk.Tk()
main_window.title("Responsive-Reasignador de Postes")


# Ruta a la imagen, asegurándote de que el camino sea dinámico
image_path = root_dir / 'images' / 'responsive.png'

# Cargar el logo de la empresa
original_image  = Image.open(image_path)  # Asegúrate de usar el camino correcto al archivo PNG
resized_image = original_image.resize((150, 70), Image.Resampling.LANCZOS)  # Ajusta estos valores según tus necesidades
logo_image = ImageTk.PhotoImage(resized_image)

logo_label = tk.Label(main_window, image=logo_image)
logo_label.pack(pady=(10, 0))

titulo = tk.Label(main_window, text="Reasignador de Postes", font=("Arial", 16), fg="#173A67")
titulo.pack(pady=10)

frame = tk.Frame(main_window)
frame.pack(padx=10, pady=10)

label_file_path = tk.Label(frame, text="Archivo seleccionado:", fg="#173A67")
label_file_path.pack(anchor="w")

entry_file_path = tk.Entry(frame, width=50)
entry_file_path.pack(fill=tk.X, padx=5, pady=5)

button_select_file = tk.Button(frame, text="Seleccionar Archivo", command=seleccionar_archivo, bg="#B61917", fg="white")
button_select_file.pack(fill=tk.X)

button_renumerar = tk.Button(frame, text="Renumerar Postes", command=iniciar_renumeracion, bg="#B61917", fg="white")
button_renumerar.pack(fill=tk.X, pady=10)

github_link = tk.Label(main_window, text="Desarrollado por: Alejandro M. Barrios Vallejos", fg="#173A67", cursor="hand2")
github_link.pack(pady=10)
github_link.bind("<Button-1>", lambda e: abrir_github())

main_window.mainloop()