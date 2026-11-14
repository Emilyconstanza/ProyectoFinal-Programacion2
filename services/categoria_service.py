from sqlalchemy.exc import IntegrityError
from database.connection import SessionLocal
from database.models import Categoria, Equipo, Arriendo


class CategoriaService:
    @staticmethod
    def crear_categoria(nombre: str, descripcion: str = "") -> Categoria:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la categoría no puede estar vacío.")

        with SessionLocal() as session:
            try:
                categoria = Categoria(
                    nombre=nombre.strip(),
                    descripcion=descripcion.strip() if descripcion else None,
                )
                session.add(categoria)
                session.commit()
                session.refresh(categoria)
                return categoria
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Ya existe una categoría con el nombre '{nombre.strip()}'.")

    @staticmethod
    def listar_categorias() -> list[Categoria]:
        with SessionLocal() as session:
            return session.query(Categoria).order_by(Categoria.id).all()

    @staticmethod
    def actualizar_categoria(categoria_id: int, nombre: str, descripcion: str = "") -> Categoria:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la categoría no puede estar vacío.")

        with SessionLocal() as session:
            categoria = session.get(Categoria, categoria_id)
            if not categoria:
                raise ValueError("La categoría seleccionada no existe.")

            try:
                categoria.nombre = nombre.strip()
                categoria.descripcion = descripcion.strip() if descripcion else None
                session.commit()
                session.refresh(categoria)
                return categoria
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Ya existe otra categoría llamada '{nombre.strip()}'.")

    @staticmethod
    def eliminar_categoria(categoria_id: int) -> None:
        with SessionLocal() as session:
            categoria = session.get(Categoria, categoria_id)
            if not categoria:
                raise ValueError("La categoría seleccionada no existe.")

            # Verificar si tiene equipos o arriendos asociados
            equipos_ids = [eq.id for eq in session.query(Equipo.id).filter_by(categoria_id=categoria_id).all()]
            if equipos_ids:
                arriendos_count = session.query(Arriendo).filter(Arriendo.equipo_id.in_(equipos_ids)).count()
                if arriendos_count > 0:
                    raise ValueError(
                        "No se puede eliminar la categoría porque tiene equipos vinculados a arriendos."
                    )
                raise ValueError(
                    "No se puede eliminar la categoría porque tiene equipos registrados. Elimínelos primero."
                )

            session.delete(categoria)
            session.commit()
