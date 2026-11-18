import glob
import re

reemplazos_paginas = {
    "index.html": "/",
    "login.html": "/login",
    "seccion-inicio.html": "/inicio",
    "mentorias.html": "/mentorias",
    "oportunidades.html": "/oportunidades",
    "perfil.html": "/perfil",
    "proyectos.html": "/proyectos",
}

for ruta in glob.glob("templates/*.html"):
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Pasa CSS e imágenes a /static/ sin duplicar si ya lo tienen
    contenido = re.sub(
        r'(href|src)=["\'](?!http|/static/)\.?/?((?:css/|img/|imagenes/|index\.css)[^"\']*)["\']',
        r'\1="/static/\2"',
        contenido,
    )

    # Cambia enlaces entre archivos .html por las rutas de Flask
    for archivo, url_flask in reemplazos_paginas.items():
        contenido = re.sub(
            rf'href=["\']\.?/?{re.escape(archivo)}["\']',
            f'href="{url_flask}"',
            contenido,
        )

    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)

    print(f"Listo: {ruta}")
    