from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from reactpy.backend.fastapi import configure
from reactpy import html
from backend import app as backend_app
from frontend import SudokuApp
from bootstrap import BootstrapCSS
from reactpy import config
from fastapi.middleware.cors import CORSMiddleware

config.REACTPY_DEBUG_MODE.current = True

# Crear instancia principal de la aplicación FastAPI
app = FastAPI()

# Agregar Middleware de CORS si estás trabajando con diferentes orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto según tus necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar la aplicación de backend
app.mount("/api", backend_app)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar FastAPI con el componente ReactPy
configure(
    app, 
    component=lambda: html.div(
        html.link({"rel": "stylesheet", "href": "/static/style.css"}), 
        BootstrapCSS(), 
        SudokuApp()
    )
)