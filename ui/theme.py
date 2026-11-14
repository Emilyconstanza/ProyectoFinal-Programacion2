import tkinter as tk
from tkinter import ttk


def aplicar_tema(root: tk.Tk):
    style = ttk.Style(root)
    style.theme_use("clam")

    # Paleta Azul Moderno / Sky & Sapphire
    BG_PRINCIPAL = "#F4F8FB"     # Azul hielo muy suave (fondo general)
    BG_CARD = "#E8F1FA"          # Celeste pastel limpio (formularios)
    AZUL_PRIMARIO = "#2563EB"    # Azul zafiro moderno (botones y cabeceras)
    AZUL_HOVER = "#1D4ED8"       # Azul cobalto profundo (hover y títulos)
    AZUL_SUAVE = "#DBEAFE"       # Celeste claro (pestañas inactivas y selección)
    BORDE_AZUL = "#BFDBFE"       # Borde celeste sutil
    TEXTO_OSCURO = "#1E293B"     # Azul pizarra oscuro (alta legibilidad)
    BLANCO = "#FFFFFF"

    root.configure(bg=BG_PRINCIPAL)

    # Tipografía moderna
    fuente_base = ("Segoe UI", 10)
    fuente_bold = ("Segoe UI", 10, "bold")
    fuente_titulo = ("Segoe UI", 11, "bold")

    style.configure(".", background=BG_PRINCIPAL, foreground=TEXTO_OSCURO, font=fuente_base)

    # Contenedores y marcos
    style.configure("TFrame", background=BG_PRINCIPAL)
    style.configure(
        "TLabelframe",
        background=BG_CARD,
        bordercolor=BORDE_AZUL,
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label",
        background=BG_PRINCIPAL,
        foreground=AZUL_HOVER,
        font=fuente_titulo,
    )
    style.configure("TLabel", background=BG_CARD, foreground=TEXTO_OSCURO, font=fuente_base)
    style.configure("TCheckbutton", background=BG_CARD, foreground=TEXTO_OSCURO, font=fuente_base)

    # Pestañas (Notebook)
    style.configure("TNotebook", background=BG_PRINCIPAL, borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=AZUL_SUAVE,
        foreground=TEXTO_OSCURO,
        padding=[14, 6],
        font=fuente_bold,
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", AZUL_PRIMARIO), ("active", BORDE_AZUL)],
        foreground=[("selected", BLANCO)],
    )

    # Botones (padding ajustado para que no se corte el texto)
    style.configure(
        "TButton",
        background=AZUL_PRIMARIO,
        foreground=BLANCO,
        font=fuente_bold,
        padding=[9, 5],
        borderwidth=0,
    )
    style.map(
        "TButton",
        background=[("active", AZUL_HOVER), ("pressed", AZUL_HOVER)],
        foreground=[("active", BLANCO)],
    )

    # Inputs (Entry y Combobox)
    style.configure(
        "TEntry",
        fieldbackground=BLANCO,
        foreground=TEXTO_OSCURO,
        bordercolor=BORDE_AZUL,
        lightcolor=AZUL_PRIMARIO,
        padding=4,
    )
    style.configure(
        "TCombobox",
        fieldbackground=BLANCO,
        background=AZUL_SUAVE,
        foreground=TEXTO_OSCURO,
        bordercolor=BORDE_AZUL,
        padding=4,
    )

    # Tablas (Treeview)
    style.configure(
        "Treeview",
        background=BLANCO,
        foreground=TEXTO_OSCURO,
        fieldbackground=BLANCO,
        rowheight=28,
        bordercolor=BORDE_AZUL,
        font=fuente_base,
    )
    style.configure(
        "Treeview.Heading",
        background=AZUL_PRIMARIO,
        foreground=BLANCO,
        font=fuente_bold,
        padding=[6, 6],
        borderwidth=0,
    )
    style.map(
        "Treeview.Heading",
        background=[("active", AZUL_HOVER)],
    )
    style.map(
        "Treeview",
        background=[("selected", AZUL_SUAVE)],
        foreground=[("selected", TEXTO_OSCURO)],
    )