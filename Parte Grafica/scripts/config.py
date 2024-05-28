import os
from pathlib import Path

# Directorio raíz del proyecto, basado en la ubicación de este archivo config.py
root_dir = Path(__file__).parent
# Obtener el directorio del escritorio del usuario actual
desktop_dir = Path.home() / 'Reportes'
ns = {'kml': 'http://www.opengis.net/kml/2.2'}
script_dir = os.path.dirname(__file__)
data_dir = desktop_dir / 'data'
data_dir_new = desktop_dir / 'docs/docs_nuevo'


