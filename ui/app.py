from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from services.categoria_service import CategoriaService
from services.equipo_service import EquipoService
from services.cliente_service import ClienteService
from services.arriendo_service import ArriendoService


class AppArriendoDeportivo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Arriendo de Equipamiento Deportivo")
        self.geometry("1100x700")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_categorias = ttk.Frame(self.notebook)
        self.tab_equipos = ttk.Frame(self.notebook)
        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_arriendos = ttk.Frame(self.notebook)
        self.tab_graficos = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_categorias, text="Categorías")
        self.notebook.add(self.tab_equipos, text="Equipos")
        self.notebook.add(self.tab_clientes, text="Clientes")
        self.notebook.add(self.tab_arriendos, text="Arriendos y Devoluciones")
        self.notebook.add(self.tab_graficos, text="Reportes y Gráficos")

        self._build_categorias_tab()
        self._build_equipos_tab()
        self._build_clientes_tab()
        self._build_arriendos_tab()
        self._build_graficos_tab()

        self.refrescar_todo()

    def refrescar_todo(self):
        self.cargar_categorias()
        self.cargar_equipos()
        self.cargar_clientes()
        self.cargar_arriendos()
        self.actualizar_graficos()

    # ---------------- TAB CATEGORÍAS ----------------
    def _build_categorias_tab(self):
        form = ttk.LabelFrame(self.tab_categorias, text="Gestión de Categorías", padding=10)
        form.pack(fill="x", padx=10, pady=5)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.cat_nombre = ttk.Entry(form, width=30)
        self.cat_nombre.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Descripción:").grid(row=0, column=2, padx=5, pady=5)
        self.cat_desc = ttk.Entry(form, width=40)
        self.cat_desc.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(form, text="Agregar", command=self.agregar_categoria).grid(row=0, column=4, padx=5)
        ttk.Button(form, text="Actualizar Seleccionada", command=self.editar_categoria).grid(row=0, column=5, padx=5)
        ttk.Button(form, text="Eliminar Seleccionada", command=self.eliminar_categoria).grid(row=0, column=6, padx=5)

        self.tree_cat = ttk.Treeview(self.tab_categorias, columns=("ID", "Nombre", "Descripción"), show="headings")
        for col in ("ID", "Nombre", "Descripción"):
            self.tree_cat.heading(col, text=col)
        self.tree_cat.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree_cat.bind("<<TreeviewSelect>>", self._on_select_cat)

    def _on_select_cat(self, _):
        sel = self.tree_cat.selection()
        if sel:
            vals = self.tree_cat.item(sel[0], "values")
            self.cat_nombre.delete(0, tk.END)
            self.cat_nombre.insert(0, vals[1])
            self.cat_desc.delete(0, tk.END)
            self.cat_desc.insert(0, vals[2] if vals[2] != "None" else "")

    def cargar_categorias(self):
        for item in self.tree_cat.get_children():
            self.tree_cat.delete(item)
        categorias = CategoriaService.listar_categorias()
        for c in categorias:
            self.tree_cat.insert("", tk.END, values=(c.id, c.nombre, c.descripcion or ""))
        self.cat_map = {f"{c.id} - {c.nombre}": c.id for c in categorias}
        if hasattr(self, "eq_cat_combo"):
            self.eq_cat_combo["values"] = list(self.cat_map.keys())

    def agregar_categoria(self):
        try:
            CategoriaService.crear_categoria(self.cat_nombre.get(), self.cat_desc.get())
            self.cat_nombre.delete(0, tk.END)
            self.cat_desc.delete(0, tk.END)
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Categoría creada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_categoria(self):
        sel = self.tree_cat.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una categoría de la tabla.")
            return
        cat_id = int(self.tree_cat.item(sel[0], "values")[0])
        try:
            CategoriaService.actualizar_categoria(cat_id, self.cat_nombre.get(), self.cat_desc.get())
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Categoría actualizada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_categoria(self):
        sel = self.tree_cat.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una categoría de la tabla.")
            return
        cat_id = int(self.tree_cat.item(sel[0], "values")[0])
        try:
            CategoriaService.eliminar_categoria(cat_id)
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Categoría eliminada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- TAB EQUIPOS ----------------
    def _build_equipos_tab(self):
        form = ttk.LabelFrame(self.tab_equipos, text="Gestión de Equipos (Factory Method)", padding=10)
        form.pack(fill="x", padx=10, pady=5)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.eq_nombre = ttk.Entry(form, width=25)
        self.eq_nombre.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Categoría:").grid(row=0, column=2, padx=5, pady=5)
        self.eq_cat_combo = ttk.Combobox(form, state="readonly", width=22)
        self.eq_cat_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Precio Diario:").grid(row=1, column=0, padx=5, pady=5)
        self.eq_precio = ttk.Entry(form, width=15)
        self.eq_precio.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Stock Total:").grid(row=1, column=2, padx=5, pady=5)
        self.eq_stock = ttk.Entry(form, width=15)
        self.eq_stock.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ttk.Button(form, text="Crear Equipo", command=self.agregar_equipo).grid(row=0, column=4, padx=5)
        ttk.Button(form, text="Actualizar", command=self.editar_equipo).grid(row=0, column=5, padx=5)
        ttk.Button(form, text="Eliminar", command=self.eliminar_equipo).grid(row=1, column=4, padx=5)

        self.solo_disp_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            form,
            text="Mostrar solo con stock disponible",
            variable=self.solo_disp_var,
            command=self.cargar_equipos,
        ).grid(row=1, column=5, padx=5)

        cols = ("ID", "Nombre", "Categoría ID", "Precio Diario", "Stock Total", "Stock Disponible")
        self.tree_eq = ttk.Treeview(self.tab_equipos, columns=cols, show="headings")
        for col in cols:
            self.tree_eq.heading(col, text=col)
        self.tree_eq.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree_eq.bind("<<TreeviewSelect>>", self._on_select_eq)

    def _on_select_eq(self, _):
        sel = self.tree_eq.selection()
        if sel:
            vals = self.tree_eq.item(sel[0], "values")
            self.eq_nombre.delete(0, tk.END)
            self.eq_nombre.insert(0, vals[1])
            self.eq_precio.delete(0, tk.END)
            self.eq_precio.insert(0, vals[3])
            self.eq_stock.delete(0, tk.END)
            self.eq_stock.insert(0, vals[4])

    def cargar_equipos(self):
        for item in self.tree_eq.get_children():
            self.tree_eq.delete(item)
        equipos = EquipoService.listar_equipos(solo_disponibles=self.solo_disp_var.get())
        for e in equipos:
            self.tree_eq.insert(
                "",
                tk.END,
                values=(e.id, e.nombre, e.categoria_id, e.precio_diario, e.stock_total, e.stock_disponible),
            )
        todos = EquipoService.listar_equipos(solo_disponibles=False)
        self.eq_map = {f"{e.id} - {e.nombre} (Disp: {e.stock_disponible})": e.id for e in todos}
        if hasattr(self, "arr_eq_combo"):
            self.arr_eq_combo["values"] = list(self.eq_map.keys())

    def agregar_equipo(self):
        try:
            cat_key = self.eq_cat_combo.get()
            if not cat_key:
                raise ValueError("Seleccione una categoría.")
            EquipoService.crear_equipo(
                nombre=self.eq_nombre.get(),
                categoria_id=self.cat_map[cat_key],
                precio_diario=float(self.eq_precio.get()),
                stock_total=int(self.eq_stock.get()),
            )
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Equipo creado mediante Factory Method.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_equipo(self):
        sel = self.tree_eq.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un equipo.")
            return
        eq_id = int(self.tree_eq.item(sel[0], "values")[0])
        try:
            cat_key = self.eq_cat_combo.get()
            if not cat_key:
                raise ValueError("Seleccione una categoría.")
            EquipoService.actualizar_equipo(
                equipo_id=eq_id,
                nombre=self.eq_nombre.get(),
                categoria_id=self.cat_map[cat_key],
                precio_diario=float(self.eq_precio.get()),
                stock_total=int(self.eq_stock.get()),
            )
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Equipo actualizado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_equipo(self):
        sel = self.tree_eq.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un equipo.")
            return
        eq_id = int(self.tree_eq.item(sel[0], "values")[0])
        try:
            EquipoService.eliminar_equipo(eq_id)
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Equipo eliminado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- TAB CLIENTES ----------------
    def _build_clientes_tab(self):
        form = ttk.LabelFrame(self.tab_clientes, text="Gestión de Clientes", padding=10)
        form.pack(fill="x", padx=10, pady=5)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.cli_nombre = ttk.Entry(form, width=25)
        self.cli_nombre.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Correo:").grid(row=0, column=2, padx=5, pady=5)
        self.cli_correo = ttk.Entry(form, width=25)
        self.cli_correo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Teléfono:").grid(row=0, column=4, padx=5, pady=5)
        self.cli_tel = ttk.Entry(form, width=18)
        self.cli_tel.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(form, text="Registrar", command=self.agregar_cliente).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(form, text="Actualizar", command=self.editar_cliente).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(form, text="Eliminar", command=self.eliminar_cliente).grid(row=1, column=3, padx=5, pady=5)

        cols = ("ID", "Nombre", "Correo", "Teléfono")
        self.tree_cli = ttk.Treeview(self.tab_clientes, columns=cols, show="headings")
        for col in cols:
            self.tree_cli.heading(col, text=col)
        self.tree_cli.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree_cli.bind("<<TreeviewSelect>>", self._on_select_cli)

    def _on_select_cli(self, _):
        sel = self.tree_cli.selection()
        if sel:
            vals = self.tree_cli.item(sel[0], "values")
            self.cli_nombre.delete(0, tk.END)
            self.cli_nombre.insert(0, vals[1])
            self.cli_correo.delete(0, tk.END)
            self.cli_correo.insert(0, vals[2])
            self.cli_tel.delete(0, tk.END)
            self.cli_tel.insert(0, vals[3] if vals[3] != "None" else "")

    def cargar_clientes(self):
        for item in self.tree_cli.get_children():
            self.tree_cli.delete(item)
        clientes = ClienteService.listar_clientes()
        for c in clientes:
            self.tree_cli.insert("", tk.END, values=(c.id, c.nombre, c.correo, c.telefono or ""))
        self.cli_map = {f"{c.id} - {c.nombre} ({c.correo})": c.id for c in clientes}
        if hasattr(self, "arr_cli_combo"):
            self.arr_cli_combo["values"] = list(self.cli_map.keys())

    def agregar_cliente(self):
        try:
            ClienteService.crear_cliente(self.cli_nombre.get(), self.cli_correo.get(), self.cli_tel.get())
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Cliente registrado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_cliente(self):
        sel = self.tree_cli.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un cliente.")
            return
        cli_id = int(self.tree_cli.item(sel[0], "values")[0])
        try:
            ClienteService.actualizar_cliente(cli_id, self.cli_nombre.get(), self.cli_correo.get(), self.cli_tel.get())
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Cliente actualizado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_cliente(self):
        sel = self.tree_cli.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un cliente.")
            return
        cli_id = int(self.tree_cli.item(sel[0], "values")[0])
        try:
            ClienteService.eliminar_cliente(cli_id)
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Cliente eliminado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- TAB ARRIENDOS ----------------
    def _build_arriendos_tab(self):
        form = ttk.LabelFrame(self.tab_arriendos, text="Registrar Nuevo Arriendo / Procesar Devolución", padding=10)
        form.pack(fill="x", padx=10, pady=5)

        ttk.Label(form, text="Equipo:").grid(row=0, column=0, padx=5, pady=5)
        self.arr_eq_combo = ttk.Combobox(form, state="readonly", width=32)
        self.arr_eq_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Cliente:").grid(row=0, column=2, padx=5, pady=5)
        self.arr_cli_combo = ttk.Combobox(form, state="readonly", width=32)
        self.arr_cli_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5)
        self.arr_cant = ttk.Entry(form, width=10)
        self.arr_cant.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Inicio (YYYY-MM-DD):").grid(row=1, column=2, padx=5, pady=5)
        self.arr_inicio = ttk.Entry(form, width=15)
        self.arr_inicio.insert(0, date.today().isoformat())
        self.arr_inicio.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Fin Prevista (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.arr_fin = ttk.Entry(form, width=15)
        self.arr_fin.insert(0, date.today().isoformat())
        self.arr_fin.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(form, text="Registrar Arriendo", command=self.crear_arriendo).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(form, text="Devolver Arriendo Seleccionado", command=self.devolver_arriendo).grid(row=2, column=3, padx=5, pady=5)

        self.solo_activos_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            form,
            text="Ver solo arriendos ACTIVOS",
            variable=self.solo_activos_var,
            command=self.cargar_arriendos,
        ).grid(row=2, column=4, padx=5)

        cols = ("ID", "Equipo", "Cliente", "Fecha Inicio", "Fin Prevista", "Cantidad", "Estado")
        self.tree_arr = ttk.Treeview(self.tab_arriendos, columns=cols, show="headings")
        for col in cols:
            self.tree_arr.heading(col, text=col)
        self.tree_arr.pack(fill="both", expand=True, padx=10, pady=5)

    def cargar_arriendos(self):
        for item in self.tree_arr.get_children():
            self.tree_arr.delete(item)
        arriendos = ArriendoService.listar_arriendos(solo_activos=self.solo_activos_var.get())
        for a in arriendos:
            self.tree_arr.insert(
                "",
                tk.END,
                values=(
                    a["id"],
                    a["equipo"],
                    a["cliente"],
                    a["fecha_inicio"],
                    a["fecha_fin_prevista"],
                    a["cantidad"],
                    a["estado"],
                ),
            )

    def crear_arriendo(self):
        try:
            eq_key = self.arr_eq_combo.get()
            cli_key = self.arr_cli_combo.get()
            if not eq_key or not cli_key:
                raise ValueError("Debe seleccionar un equipo y un cliente.")

            ArriendoService.registrar_arriendo(
                equipo_id=self.eq_map[eq_key],
                cliente_id=self.cli_map[cli_key],
                fecha_inicio=date.fromisoformat(self.arr_inicio.get().strip()),
                fecha_fin_prevista=date.fromisoformat(self.arr_fin.get().strip()),
                cantidad=int(self.arr_cant.get()),
            )
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Arriendo registrado y stock descontado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def devolver_arriendo(self):
        sel = self.tree_arr.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un arriendo de la tabla.")
            return
        arr_id = int(self.tree_arr.item(sel[0], "values")[0])
        try:
            ArriendoService.registrar_devolucion(arr_id)
            self.refrescar_todo()
            messagebox.showinfo("Éxito", "Devolución procesada y stock restituido.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- TAB GRÁFICOS MATPLOTLIB ----------------
    def _build_graficos_tab(self):
        top = ttk.Frame(self.tab_graficos)
        top.pack(fill="x", padx=10, pady=5)
        ttk.Button(top, text="Actualizar Gráficos desde BD", command=self.actualizar_graficos).pack(side="left")

        self.fig = Figure(figsize=(10, 4.8), dpi=100)
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_graficos)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def actualizar_graficos(self):
        self.ax1.clear()
        self.ax2.clear()

        cat_data = ArriendoService.datos_arriendos_por_categoria()
        if cat_data:
            nombres_cat = [x[0] for x in cat_data]
            conteo_cat = [x[1] for x in cat_data]
            self.ax1.bar(nombres_cat, conteo_cat, color="#2b7bba")
            self.ax1.set_title("Arriendos por Categoría (Operaciones)")
            self.ax1.set_ylabel("Cantidad de Arriendos")
            self.ax1.tick_params(axis="x", rotation=25)
        else:
            self.ax1.set_title("Arriendos por Categoría (Sin datos)")

        eq_data = ArriendoService.datos_equipos_mas_arrendados()
        if eq_data:
            nombres_eq = [x[0] for x in eq_data]
            conteo_eq = [x[1] for x in eq_data]
            self.ax2.bar(nombres_eq, conteo_eq, color="#3caea3")
            self.ax2.set_title("Equipos con Mayor N° de Arriendos")
            self.ax2.set_ylabel("Cantidad de Arriendos")
            self.ax2.tick_params(axis="x", rotation=25)
        else:
            self.ax2.set_title("Equipos Más Arrendados (Sin datos)")

        self.fig.tight_layout()
        self.canvas.draw()
