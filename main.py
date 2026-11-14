from database.connection import Base, engine
import database.models  # noqa: F401 - Registra los modelos en Base.metadata
from ui.app import AppArriendoDeportivo


def inicializar_bd():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    inicializar_bd()
    app = AppArriendoDeportivo()
    app.mainloop()
