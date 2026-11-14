# Sistema de Gestión de Arriendo de Equipamiento Deportivo

Aplicación de escritorio desarrollada en **Python 3** para administrar categorías, equipamiento deportivo, clientes, arriendos y devoluciones, con persistencia en **SQLite** mediante **SQLAlchemy ORM**, interfaz gráfica en **Tkinter**, visualización estadística con **Matplotlib** e implementación del patrón de diseño **Factory Method**.

---

## 1. Requisitos e Instalación

### Requisitos previos
* Python 3.10 o superior
* `pip` (gestor de paquetes de Python)

### Instalación y ejecución

1. Clonar el repositorio o descomprimir el proyecto:
```bash
git clone [https://github.com/Emilyconstanza/ProyectoFinal-Programacion2.git](https://github.com/Emilyconstanza/ProyectoFinal-Programacion2.git)
cd ProyectoFinal-Programacion2
```

2. Crear y activar un entorno virtual (opcional, recomendado):
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate
```

3. Instalar las dependencias del proyecto:
```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación:
```bash
python main.py
```

> **Nota sobre la base de datos:** Al ejecutar `main.py` por primera vez, el sistema crea automáticamente el archivo de base de datos SQLite y sus tablas mediante SQLAlchemy, conservando todos los registros entre sesiones.

---

## 2. Arquitectura del Proyecto

```text
ProyectoFinal-Programacion2/
├── database/
│   ├── connection.py          # Configuración del motor SQLite y sesiones SQLAlchemy
│   └── models.py              # Definición de entidades ORM y relaciones
├── patterns/
│   └── equipment_factory.py   # Implementación del patrón Factory Method
├── services/
│   ├── categoria_service.py   # Lógica CRUD y validaciones de categorías
│   ├── equipo_service.py      # Lógica CRUD de equipos (integrado con Factory Method)
│   ├── cliente_service.py     # Lógica CRUD y validaciones de clientes
│   └── arriendo_service.py    # Gestión de arriendos, devoluciones y datos para gráficos
├── ui/
│   └── app.py                 # Interfaz gráfica en Tkinter y gráficos Matplotlib
├── main.py                    # Punto de entrada de la aplicación
└── requirements.txt           # Dependencias (SQLAlchemy, Matplotlib)
```

---

## 3. Modelo de Datos

El modelo relacional se implementa con **SQLAlchemy ORM** sobre **SQLite**, compuesto por cuatro entidades principales:

* **Categoria (`categorias`):**
  * `id` (PK), `nombre` (único, obligatorio), `descripcion`.
  * **Relación:** Una categoría agrupa muchos equipos (`1:N`).
* **Equipo (`equipos`):**
  * `id` (PK), `nombre`, `categoria_id` (FK), `precio_diario` (> 0), `stock_total` (>= 0), `stock_disponible` (>= 0).
  * **Relación:** Pertenece a una categoría y puede estar asociado a múltiples arriendos.
* **Cliente (`clientes`):**
  * `id` (PK), `nombre`, `correo` (único), `telefono`.
  * **Relación:** Un cliente puede registrar múltiples arriendos (`1:N`).
* **Arriendo (`arriendos`):**
  * `id` (PK), `equipo_id` (FK), `cliente_id` (FK), `fecha_inicio`, `fecha_fin_prevista`, `cantidad` (> 0), `estado` (`ACTIVO` o `DEVUELTO`).
  * **Relación:** Vincula un equipo y un cliente en una operación de arriendo.

---

## 4. Patrón de Diseño: Factory Method

### Justificación e integración
El patrón **Factory Method** (`patterns/equipment_factory.py`) se utiliza para encapsular y desacoplar la creación de instancias de `Equipo` respecto a la capa de servicios y la interfaz gráfica:

* **Clase creadora abstracta (`EquipoFactory`):** Define el método fábrica `crear_equipo(...)` y centraliza las reglas de validación iniciales (nombre no vacío, precio diario positivo y stock inicial válido).
* **Creador concreto (`EquipoGenericoFactory`):** Implementa la instanciación concreta del modelo persistente `Equipo`, inicializando automáticamente `stock_disponible = stock_total`.
* **Integración con SQLAlchemy:** En `EquipoService.crear_equipo()`, el servicio delega la construcción y validación del objeto a la fábrica antes de persistirlo en la sesión de SQLAlchemy (`session.add()` y `session.commit()`). Esto permite extender fácilmente el sistema en el futuro con fábricas especializadas (por ejemplo, equipamiento con depósito de garantía o mantenimiento obligatorio) sin modificar la lógica de persistencia ni las vistas.

---

## 5. Pruebas Mínimas de Demostración

Se ejecutó y verificó el flujo completo de pruebas exigido:

| Paso | Acción realizada | Resultado esperado | Estado |
| :--- | :--- | :--- | :---: |
| **1** | Crear categoría (ej. *Ciclismo*) y equipo (ej. *Bicicleta MTB*) con `stock_total = 5`. | Equipo registrado con `stock_disponible = 5`. | ✅ Verificado |
| **2** | Crear cliente y registrar arriendo de `2` unidades. | `stock_disponible` pasa a `3`; estado del arriendo `ACTIVO`. | ✅ Verificado |
| **3** | Intentar arrendar `4` unidades adicionales del mismo equipo. | Operación rechazada con mensaje de error; `stock_disponible` se mantiene en `3`. | ✅ Verificado |
| **4** | Registrar devolución del arriendo de `2` unidades. | `stock_disponible` vuelve a `5`; estado cambia a `DEVUELTO`. | ✅ Verificado |
| **5** | Intentar devolver nuevamente el mismo arriendo ya devuelto. | Operación rechazada; se impide devolución duplicada y stock sigue en `5`. | ✅ Verificado |
| **6** | Cerrar y reabrir la aplicación; consultar pestaña de reportes. | Datos conservados en SQLite y gráficos generados con datos reales. | ✅ Verificado |

---

## 6. Capturas de Pantalla

*(Reemplazar estas rutas con las capturas tomadas al ejecutar la aplicación localmente)*

* **Gestión de Categorías, Equipos y Clientes:**
  `![CRUD Equipos](docs/captura_equipos.png)`
* **Registro de Arriendos y Devoluciones:**
  `![Arriendos y Devoluciones](docs/captura_arriendos.png)`
* **Reportes y Gráficos Matplotlib (Arriendos por categoría y Top equipos):**
  `![Gráficos Matplotlib](docs/captura_graficos.png)`

---

## 7. Fuentes Consultadas

* **SQLAlchemy ORM:** Documentación oficial de SQLAlchemy 2.0 — *Declarative Mapping, Relationships & Session Basics* (https://docs.sqlalchemy.org/).
* **Tkinter:** Documentación oficial de Python — *Graphical User Interfaces with Tk (`tkinter` y `tkinter.ttk`)* (https://docs.python.org/3/library/tkinter.html).
* **Matplotlib:** Documentación oficial de Matplotlib — *Embedding in Tk (`FigureCanvasTkAgg`) y Bar Charts* (https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html).
* **Patrón Factory Method:** Refactoring Guru — *Factory Method Design Pattern in Python* (https://refactoring.guru/design-patterns/factory-method/python/example).
