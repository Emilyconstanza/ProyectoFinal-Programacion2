from datetime import date
from sqlalchemy import func
from database.connection import SessionLocal
from database.models import Arriendo, Equipo, Cliente, Categoria


class ArriendoService:
    @staticmethod
    def registrar_arriendo(
        equipo_id: int,
        cliente_id: int,
        fecha_inicio: date,
        fecha_fin_prevista: date,
        cantidad: int,
    ) -> Arriendo:
        if cantidad <= 0:
            raise ValueError("La cantidad a arrendar debe ser mayor a 0.")
        if fecha_fin_prevista < fecha_inicio:
            raise ValueError("La fecha de término prevista no puede ser anterior a la fecha de inicio.")

        with SessionLocal() as session:
            equipo = session.get(Equipo, equipo_id)
            if not equipo:
                raise ValueError("El equipo seleccionado no existe.")

            cliente = session.get(Cliente, cliente_id)
            if not cliente:
                raise ValueError("El cliente seleccionado no existe.")

            if cantidad > equipo.stock_disponible:
                raise ValueError(
                    f"Stock insuficiente. Disponible: {equipo.stock_disponible}, solicitado: {cantidad}."
                )

            # Descuento de stock y registro en la misma transacción
            equipo.stock_disponible -= cantidad
            arriendo = Arriendo(
                equipo_id=equipo_id,
                cliente_id=cliente_id,
                fecha_inicio=fecha_inicio,
                fecha_fin_prevista=fecha_fin_prevista,
                cantidad=cantidad,
                estado="ACTIVO",
            )
            session.add(arriendo)
            session.commit()
            session.refresh(arriendo)
            return arriendo

    @staticmethod
    def registrar_devolucion(arriendo_id: int) -> Arriendo:
        with SessionLocal() as session:
            arriendo = session.get(Arriendo, arriendo_id)
            if not arriendo:
                raise ValueError("El arriendo seleccionado no existe.")

            if arriendo.estado != "ACTIVO":
                raise ValueError("Este arriendo ya fue devuelto anteriormente (devolución duplicada rechazada).")

            equipo = session.get(Equipo, arriendo.equipo_id)
            if not equipo:
                raise ValueError("El equipo asociado al arriendo no fue encontrado.")

            nuevo_stock = equipo.stock_disponible + arriendo.cantidad
            if nuevo_stock > equipo.stock_total:
                raise ValueError("Error de integridad: el stock disponible superaría el stock total.")

            # Restitución completa en la misma transacción
            equipo.stock_disponible = nuevo_stock
            arriendo.estado = "DEVUELTO"
            session.commit()
            session.refresh(arriendo)
            return arriendo

    @staticmethod
    def listar_arriendos(solo_activos: bool = False) -> list[dict]:
        with SessionLocal() as session:
            query = (
                session.query(Arriendo, Equipo.nombre, Cliente.nombre)
                .join(Equipo, Arriendo.equipo_id == Equipo.id)
                .join(Cliente, Arriendo.cliente_id == Cliente.id)
            )
            if solo_activos:
                query = query.filter(Arriendo.estado == "ACTIVO")

            resultados = query.order_by(Arriendo.id.desc()).all()
            return [
                {
                    "id": arr.id,
                    "equipo": eq_nombre,
                    "cliente": cli_nombre,
                    "fecha_inicio": arr.fecha_inicio,
                    "fecha_fin_prevista": arr.fecha_fin_prevista,
                    "cantidad": arr.cantidad,
                    "estado": arr.estado,
                }
                for arr, eq_nombre, cli_nombre in resultados
            ]

    @staticmethod
    def datos_arriendos_por_categoria() -> list[tuple[str, int]]:
        """Contabiliza operaciones de arriendo por categoría (no unidades)."""
        with SessionLocal() as session:
            return (
                session.query(Categoria.nombre, func.count(Arriendo.id))
                .join(Equipo, Equipo.categoria_id == Categoria.id)
                .join(Arriendo, Arriendo.equipo_id == Equipo.id)
                .group_by(Categoria.nombre)
                .order_by(func.count(Arriendo.id).desc())
                .all()
            )

    @staticmethod
    def datos_equipos_mas_arrendados() -> list[tuple[str, int]]:
        """Contabiliza operaciones de arriendo por equipo (no unidades)."""
        with SessionLocal() as session:
            return (
                session.query(Equipo.nombre, func.count(Arriendo.id))
                .join(Arriendo, Arriendo.equipo_id == Equipo.id)
                .group_by(Equipo.nombre)
                .order_by(func.count(Arriendo.id).desc())
                .limit(10)
                .all()
            )
