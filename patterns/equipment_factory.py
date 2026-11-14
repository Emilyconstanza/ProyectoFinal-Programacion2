from abc import ABC, abstractmethod
from database.models import Equipo


class EquipoFactory(ABC):
      #Creador abstracto (Creator) para instanciar objetos Equipo según su tipo

    @abstractmethod
    def crear_equipo(
        self,
        nombre: str,
        categoria_id: int,
        precio_diario: float,
        stock_total: int,
    ) -> Equipo:
        pass

    def _validar_datos_base(self, nombre: str, precio_diario: float, stock_total: int) -> None:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del equipo no puede estar vacío.")
        if precio_diario <= 0:
            raise ValueError("El precio diario debe ser mayor a 0.")
        if stock_total < 0:
            raise ValueError("El stock total no puede ser negativo.")


class EquipoGeneralFactory(EquipoFactory):
     # Fábrica para equipamiento deportivo estándar sin recargos adicionales

    def crear_equipo(self, nombre: str, categoria_id: int, precio_diario: float, stock_total: int) -> Equipo:
        self._validar_datos_base(nombre, precio_diario, stock_total)
        return Equipo(
            nombre=nombre.strip(),
            categoria_id=categoria_id,
            precio_diario=round(precio_diario, 2),
            stock_total=stock_total,
            stock_disponible=stock_total,
            tipo_equipamiento="General",
        )


class EquipoAcuaticoFactory(EquipoFactory):
    # Fábrica para equipamiento acuático 

    def crear_equipo(self, nombre: str, categoria_id: int, precio_diario: float, stock_total: int) -> Equipo:
        self._validar_datos_base(nombre, precio_diario, stock_total)
        precio_ajustado = round(precio_diario * 1.15, 2)
        return Equipo(
            nombre=nombre.strip(),
            categoria_id=categoria_id,
            precio_diario=precio_ajustado,
            stock_total=stock_total,
            stock_disponible=stock_total,
            tipo_equipamiento="Acuático",
        )


class EquipoMontanaFactory(EquipoFactory):
    # Fábrica para equipamiento de montaña/outdoor 

    def crear_equipo(self, nombre: str, categoria_id: int, precio_diario: float, stock_total: int) -> Equipo:
        self._validar_datos_base(nombre, precio_diario, stock_total)
        precio_ajustado = round(precio_diario * 1.10, 2)
        return Equipo(
            nombre=nombre.strip(),
            categoria_id=categoria_id,
            precio_diario=precio_ajustado,
            stock_total=stock_total,
            stock_disponible=stock_total,
            tipo_equipamiento="Montaña",
        )


def obtener_fabrica_equipo(tipo: str) -> EquipoFactory:
     # Selector de fábrica concreta según el tipo de equipamiento elegido en la UI
    fabricas: dict[str, EquipoFactory] = {
        "General": EquipoGeneralFactory(),
        "Acuático": EquipoAcuaticoFactory(),
        "Montaña": EquipoMontanaFactory(),
    }
    fabrica = fabricas.get(tipo)
    if not fabrica:
        raise ValueError(f"Tipo de equipamiento no soportado: '{tipo}'.")
    return fabrica