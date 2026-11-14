from database.connection import Base, engine
import database.models  # noqa: F401 - Registra los modelos en Base.metadata
from ui.app import AppArriendoDeportivo
from ui.theme import aplicar_tema


def inicializar_bd():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    inicializar_bd()
    app = AppArriendoDeportivo()
    aplicar_tema(app)
    app.mainloop()
