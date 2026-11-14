from database.connection import SessionLocal
from database.models import Categoria, Equipo, Arriendo
from patterns.equipment_factory import EquipoFactory


class EquipoGenericoFactory(EquipoFactory):
    """Fábrica concreta compatible con EquipoFactory para crear instancias persistentes."""

    def crear_equipo(
        self,
        nombre: str,
        categoria_id: int,
        precio_diario: float,
        stock_total: int,
    ) -> Equipo:
        self._validar_datos_base(nombre, precio_diario, stock_total)
        return Equipo(
            nombre=nombre.strip(),
            categoria_id=categoria_id,
            precio_diario=float(precio_diario),
            stock_total=int(stock_total),
            stock_disponible=int(stock_total),
        )


class EquipoService:
    @staticmethod
    def crear_equipo(
        nombre: str,
        categoria_id: int,
        precio_diario: float,
        stock_total: int,
        factory: EquipoFactory | None = None,
    ) -> Equipo:
        fabrica = factory or EquipoGenericoFactory()

        with SessionLocal() as session:
            categoria = session.get(Categoria, categoria_id)
            if not categoria:
                raise ValueError("La categoría seleccionada no existe.")

            equipo = fabrica.crear_equipo(
                nombre=nombre,
                categoria_id=categoria_id,
                precio_diario=precio_diario,
                stock_total=stock_total,
            )
            session.add(equipo)
            session.commit()
            session.refresh(equipo)
            return equipo

    @staticmethod
    def listar_equipos(solo_disponibles: bool = False) -> list[Equipo]:
        with SessionLocal() as session:
            query = session.query(Equipo)
            if solo_disponibles:
                query = query.filter(Equipo.stock_disponible > 0)
            return query.order_by(Equipo.id).all()

    @staticmethod
    def actualizar_equipo(
        equipo_id: int,
        nombre: str,
        categoria_id: int,
        precio_diario: float,
        stock_total: int,
    ) -> Equipo:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del equipo no puede estar vacío.")
        if precio_diario <= 0:
            raise ValueError("El precio diario debe ser mayor a 0.")
        if stock_total < 0:
            raise ValueError("El stock total no puede ser negativo.")

        with SessionLocal() as session:
            equipo = session.get(Equipo, equipo_id)
            if not equipo:
                raise ValueError("El equipo seleccionado no existe.")

            categoria = session.get(Categoria, categoria_id)
            if not categoria:
                raise ValueError("La categoría seleccionada no existe.")

            unidades_arrendadas = equipo.stock_total - equipo.stock_disponible
            if stock_total < unidades_arrendadas:
                raise ValueError(
                    f"El stock total ({stock_total}) no puede ser menor a las unidades actualmente arrendadas ({unidades_arrendadas})."
                )

            equipo.nombre = nombre.strip()
            equipo.categoria_id = categoria_id
            equipo.precio_diario = float(precio_diario)
            equipo.stock_total = int(stock_total)
            equipo.stock_disponible = int(stock_total) - unidades_arrendadas

            session.commit()
            session.refresh(equipo)
            return equipo

    @staticmethod
    def eliminar_equipo(equipo_id: int) -> None:
        with SessionLocal() as session:
            equipo = session.get(Equipo, equipo_id)
            if not equipo:
                raise ValueError("El equipo seleccionado no existe.")

            arriendos_count = session.query(Arriendo).filter_by(equipo_id=equipo_id).count()
            if arriendos_count > 0:
                raise ValueError(
                    "No se puede eliminar el equipo porque tiene arriendos registrados en el historial."
                )

            session.delete(equipo)
            session.commit()
