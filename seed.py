from datetime import date, timedelta
from database.connection import engine, Base, init_db, SessionLocal
from database.models import Categoria, Cliente, Equipo, Arriendo
from services.categoria_service import CategoriaService
from services.equipo_service import EquipoService
from services.cliente_service import ClienteService
from services.arriendo_service import ArriendoService


def poblar_base_datos():
    Base.metadata.drop_all(bind=engine)
    init_db()

    print("Iniciando carga de datos de ejemplo...")

    # 1. Crear Categorías
    CategoriaService.crear_categoria(
        "Ciclismo", "Bicicletas de montaña, ruta y cascos"
    )
    CategoriaService.crear_categoria(
        "Deportes Acuáticos", "Kayaks, tablas SUP y chalecos salvavidas"
    )
    CategoriaService.crear_categoria(
        "Camping y Montaña", "Carpas, sacos de dormir y bastones de trekking"
    )

    # 2. Crear Clientes
    ClienteService.crear_cliente(
        "Camila Morales", "camila.morales@correo.cl", "912345678"
    )
    ClienteService.crear_cliente(
        "Matías Valenzuela", "matias.v@correo.cl", "987654321"
    )
    ClienteService.crear_cliente(
        "Sofía Riquelme", "sofia.riquelme@correo.cl", "955443322"
    )

    # 3. Consultar IDs reales desde SQLite
    session = SessionLocal()
    try:
        cat_ciclismo = session.query(Categoria).filter_by(nombre="Ciclismo").first().id
        cat_acuatico = session.query(Categoria).filter_by(nombre="Deportes Acuáticos").first().id
        cat_camping = session.query(Categoria).filter_by(nombre="Camping y Montaña").first().id

        c1_id = session.query(Cliente).filter_by(correo="camila.morales@correo.cl").first().id
        c2_id = session.query(Cliente).filter_by(correo="matias.v@correo.cl").first().id
        c3_id = session.query(Cliente).filter_by(correo="sofia.riquelme@correo.cl").first().id
    finally:
        session.close()

    # 4. Crear Equipos (utiliza EquipoFactory internamente)
    EquipoService.crear_equipo(
        nombre="Bicicleta MTB Aro 29",
        categoria_id=cat_ciclismo,
        precio_diario=15000,
        stock_total=6,
    )
    EquipoService.crear_equipo(
        nombre="Bicicleta de Ruta Carbono",
        categoria_id=cat_ciclismo,
        precio_diario=22000,
        stock_total=3,
    )
    EquipoService.crear_equipo(
        nombre="Kayak Individual",
        categoria_id=cat_acuatico,
        precio_diario=20000,
        stock_total=4,
    )
    EquipoService.crear_equipo(
        nombre="Tabla Paddle Surf (SUP)",
        categoria_id=cat_acuatico,
        precio_diario=18000,
        stock_total=5,
    )
    EquipoService.crear_equipo(
        nombre="Carpa Alta Montaña 4P",
        categoria_id=cat_camping,
        precio_diario=12000,
        stock_total=7,
    )

    # 5. Obtener IDs de los equipos creados
    session = SessionLocal()
    try:
        bici_mtb_id = session.query(Equipo).filter_by(nombre="Bicicleta MTB Aro 29").first().id
        bici_ruta_id = session.query(Equipo).filter_by(nombre="Bicicleta de Ruta Carbono").first().id
        kayak_id = session.query(Equipo).filter_by(nombre="Kayak Individual").first().id
        tabla_sup_id = session.query(Equipo).filter_by(nombre="Tabla Paddle Surf (SUP)").first().id
        carpa_id = session.query(Equipo).filter_by(nombre="Carpa Alta Montaña 4P").first().id
    finally:
        session.close()

    hoy = date.today()

    # 6. Registrar Arriendos (devueltos y activos para poblar estadísticas)
    ArriendoService.registrar_arriendo(
        equipo_id=bici_mtb_id,
        cliente_id=c1_id,
        fecha_inicio=hoy - timedelta(days=10),
        fecha_fin_prevista=hoy - timedelta(days=7),
        cantidad=2,
    )
    ArriendoService.registrar_arriendo(
        equipo_id=bici_mtb_id,
        cliente_id=c2_id,
        fecha_inicio=hoy - timedelta(days=6),
        fecha_fin_prevista=hoy - timedelta(days=4),
        cantidad=1,
    )
    ArriendoService.registrar_arriendo(
        equipo_id=kayak_id,
        cliente_id=c3_id,
        fecha_inicio=hoy - timedelta(days=5),
        fecha_fin_prevista=hoy - timedelta(days=3),
        cantidad=2,
    )

    # Devolver los 3 primeros arriendos para generar historial
    session = SessionLocal()
    try:
        primeros_arriendos = session.query(Arriendo).order_by(Arriendo.id).limit(3).all()
        ids_devolver = [a.id for a in primeros_arriendos]
    finally:
        session.close()

    for arriendo_id in ids_devolver:
        ArriendoService.registrar_devolucion(arriendo_id)

    # Registrar arriendos activos
    ArriendoService.registrar_arriendo(
        equipo_id=bici_mtb_id,
        cliente_id=c3_id,
        fecha_inicio=hoy,
        fecha_fin_prevista=hoy + timedelta(days=3),
        cantidad=2,
    )
    ArriendoService.registrar_arriendo(
        equipo_id=bici_ruta_id,
        cliente_id=c1_id,
        fecha_inicio=hoy,
        fecha_fin_prevista=hoy + timedelta(days=2),
        cantidad=1,
    )
    ArriendoService.registrar_arriendo(
        equipo_id=tabla_sup_id,
        cliente_id=c2_id,
        fecha_inicio=hoy,
        fecha_fin_prevista=hoy + timedelta(days=4),
        cantidad=2,
    )
    ArriendoService.registrar_arriendo(
        equipo_id=carpa_id,
        cliente_id=c1_id,
        fecha_inicio=hoy,
        fecha_fin_prevista=hoy + timedelta(days=5),
        cantidad=1,
    )

    print("¡Base de datos poblada exitosamente con datos de ejemplo!")


if __name__ == "__main__":
    poblar_base_datos()