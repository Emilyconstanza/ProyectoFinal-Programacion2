from sqlalchemy.exc import IntegrityError
from database.connection import SessionLocal
from database.models import Cliente, Arriendo


class ClienteService:
    @staticmethod
    def crear_cliente(nombre: str, correo: str, telefono: str = "") -> Cliente:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del cliente no puede estar vacío.")
        if not correo or "@" not in correo:
            raise ValueError("Debe ingresar un correo electrónico válido.")

        with SessionLocal() as session:
            try:
                cliente = Cliente(
                    nombre=nombre.strip(),
                    correo=correo.strip().lower(),
                    telefono=telefono.strip() if telefono else None,
                )
                session.add(cliente)
                session.commit()
                session.refresh(cliente)
                return cliente
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Ya existe un cliente registrado con el correo '{correo.strip()}'.")

    @staticmethod
    def listar_clientes() -> list[Cliente]:
        with SessionLocal() as session:
            return session.query(Cliente).order_by(Cliente.id).all()

    @staticmethod
    def actualizar_cliente(cliente_id: int, nombre: str, correo: str, telefono: str = "") -> Cliente:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del cliente no puede estar vacío.")
        if not correo or "@" not in correo:
            raise ValueError("Debe ingresar un correo electrónico válido.")

        with SessionLocal() as session:
            cliente = session.get(Cliente, cliente_id)
            if not cliente:
                raise ValueError("El cliente seleccionado no existe.")

            try:
                cliente.nombre = nombre.strip()
                cliente.correo = correo.strip().lower()
                cliente.telefono = telefono.strip() if telefono else None
                session.commit()
                session.refresh(cliente)
                return cliente
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Otro cliente ya utiliza el correo '{correo.strip()}'.")

    @staticmethod
    def eliminar_cliente(cliente_id: int) -> None:
        with SessionLocal() as session:
            cliente = session.get(Cliente, cliente_id)
            if not cliente:
                raise ValueError("El cliente seleccionado no existe.")

            arriendos_count = session.query(Arriendo).filter_by(cliente_id=cliente_id).count()
            if arriendos_count > 0:
                raise ValueError(
                    "No se puede eliminar el cliente porque tiene arriendos asociados."
                )

            session.delete(cliente)
            session.commit()
