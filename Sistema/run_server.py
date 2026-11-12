"""Punto de entrada para iniciar el servidor web de Clínica Odontológica Sonrisa Sana."""

import uvicorn


def main() -> None:
    """Inicia el servidor Uvicorn en http://127.0.0.1:8000."""
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
