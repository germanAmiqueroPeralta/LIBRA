"""
config.py
Configuración central del proyecto.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Base de datos de producción / desarrollo
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")

# Base de datos usada durante las pruebas (en memoria, no toca el archivo real)
TEST_DATABASE_PATH = ":memory:"

DEBUG = True
HOST = "127.0.0.1"
PORT = 5000
