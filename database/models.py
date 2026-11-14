from datetime import date
from sqlalchemy import Integer, String, Float, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    equipos: Mapped[list["Equipo"]] = relationship(
        back_populates="categoria",
        cascade="save-update, merge"
    )

    def __repr__(self) -> str:
        return f"<Categoria(id={self.id}, nombre='{self.nombre}')>"


class Equipo(Base):
    __tablename__ = "equipos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"),
        nullable=False
    )
    precio_diario: Mapped[float] = mapped_column(Float, nullable=False)
    stock_total: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_disponible: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_equipamiento: Mapped[str] = mapped_column(String(50), default="General", nullable=False)

    __table_args__ = (
        CheckConstraint("precio_diario > 0", name="check_precio_positivo"),
        CheckConstraint("stock_total >= 0", name="check_stock_total_no_negativo"),
        CheckConstraint("stock_disponible >= 0", name="check_stock_disp_no_negativo"),
        CheckConstraint("stock_disponible <= stock_total", name="check_stock_disp_menor_igual_total"),
    )

    categoria: Mapped["Categoria"] = relationship(back_populates="equipos")
    arriendos: Mapped[list["Arriendo"]] = relationship(
        back_populates="equipo",
        cascade="save-update, merge"
    )

    def __repr__(self) -> str:
        return f"<Equipo(id={self.id}, nombre='{self.nombre}', disp={self.stock_disponible}/{self.stock_total})>"


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)

    arriendos: Mapped[list["Arriendo"]] = relationship(
        back_populates="cliente",
        cascade="save-update, merge"
    )

    def __repr__(self) -> str:
        return f"<Cliente(id={self.id}, nombre='{self.nombre}', correo='{self.correo}')>"


class Arriendo(Base):
    __tablename__ = "arriendos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipo_id: Mapped[int] = mapped_column(
        ForeignKey("equipos.id", ondelete="RESTRICT"),
        nullable=False
    )
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"),
        nullable=False
    )
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin_prevista: Mapped[date] = mapped_column(Date, nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVO", nullable=False)

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="check_cantidad_positiva"),
        CheckConstraint("fecha_fin_prevista >= fecha_inicio", name="check_fechas_validas"),
        CheckConstraint("estado IN ('ACTIVO', 'DEVUELTO')", name="check_estado_valido"),
    )

    equipo: Mapped["Equipo"] = relationship(back_populates="arriendos")
    cliente: Mapped["Cliente"] = relationship(back_populates="arriendos")

    def __repr__(self) -> str:
        return f"<Arriendo(id={self.id}, equipo_id={self.equipo_id}, cant={self.cantidad}, estado='{self.estado}')>"