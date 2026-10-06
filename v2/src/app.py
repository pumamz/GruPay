"""
GruPay V2 - Aplicación de Escritorio
Gestor de Gastos Compartidos (Tkinter Desktop)
Versión 2: Estabilización, Corrección de Errores, Validaciones Estrictas y Multi-Grupo.
Ejecutable directamente en Thonny con F5 o: python3 v2/src/app.py
"""

from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Optional

from core import (
    GestorMultiGrupos,
    Grupo,
    sanitizar_nombre_archivo,
    sanitizar_texto,
)


class GruPayAppV2(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("GruPay Desktop V2 - Gestor de Gastos Compartidos")
        self.geometry("1060x720")
        self.minsize(940, 620)

        # Directorio de grupos para la gestión multi-grupo (Fase 2)
        ruta_base = os.path.dirname(os.path.abspath(__file__))
        self.dir_grupos = os.path.join(os.path.dirname(ruta_base), "datos", "grupos_guardados")
        os.makedirs(self.dir_grupos, exist_ok=True)
        self.gestor_multi = GestorMultiGrupos(self.dir_grupos)

        # Instancia del grupo activo
        self.grupo = Grupo("Viaje a la Playa")
        self.ruta_archivo_actual: Optional[str] = None

        # Variables reactivas para división equitativa dinámica
        self.check_vars: Dict[str, tk.BooleanVar] = {}

        self._configurar_estilos()
        self._construir_ui()

        # Cargar grupos demo en el directorio si está vacío
        self._inicializar_datos_demo()
        self._actualizar_selector_grupos()

    def _configurar_estilos(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        bg_main = "#f8f9fc"
        primary = "#4f46e5"

        self.configure(bg=bg_main)

        style.configure("TFrame", background=bg_main)
        style.configure("TLabelframe", background=bg_main)
        style.configure("TLabelframe.Label", font=("Inter", 10, "bold"), foreground="#1e293b", background=bg_main)
        style.configure("TLabel", background=bg_main, font=("Inter", 10), foreground="#1e293b")

        # Botones
        style.configure("Primary.TButton", font=("Inter", 9, "bold"), background=primary, foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#4338ca")])

        style.configure("Success.TButton", font=("Inter", 9, "bold"), background="#059669", foreground="#ffffff")
        style.map("Success.TButton", background=[("active", "#047857")])

        style.configure("Secondary.TButton", font=("Inter", 9), background="#e2e8f0", foreground="#1e293b")
        style.map("Secondary.TButton", background=[("active", "#cbd5e1")])

        style.configure("Danger.TButton", font=("Inter", 9), background="#fee2e2", foreground="#991b1b")
        style.map("Danger.TButton", background=[("active", "#fecaca")])

        # Pestañas
        style.configure("TNotebook", background=bg_main)
        style.configure("TNotebook.Tab", font=("Inter", 10, "bold"), padding=[18, 9])
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", primary)])

        # Tablas
        style.configure("Treeview", font=("Inter", 9), rowheight=26, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Inter", 9, "bold"), background="#f1f5f9", foreground="#0f172a")

    def _construir_ui(self):
        # 1. Barra superior nativa
        header = tk.Frame(self, bg="#ffffff", height=54, bd=1, relief="solid")
        header.pack(fill="x", side="top")

        lbl_logo = tk.Label(
            header,
            text="👥 GruPay Desktop V2",
            font=("Inter", 14, "bold"),
            bg="#ffffff",
            fg="#4f46e5",
            padx=16,
        )
        lbl_logo.pack(side="left")

        # Selector rápido de grupos vinculados en el encabezado (Fase 2)
        tk.Label(header, text="Grupo Activo:", font=("Inter", 10, "bold"), bg="#ffffff", fg="#475569").pack(side="left", padx=4)
        self.cmb_grupos_vinculados = ttk.Combobox(header, state="readonly", width=26)
        self.cmb_grupos_vinculados.pack(side="left", padx=6)
        self.cmb_grupos_vinculados.bind("<<ComboboxSelected>>", self._al_seleccionar_grupo_vinculado)

        btn_refrescar_grupos = ttk.Button(header, text="🔄", width=3, command=self._actualizar_selector_grupos)
        btn_refrescar_grupos.pack(side="left", padx=2)

        self.lbl_estado_archivo = tk.Label(
            header,
            text="● Estado: Grupo sincronizado",
            font=("Inter", 9),
            bg="#ffffff",
            fg="#059669",
            padx=16,
        )
        self.lbl_estado_archivo.pack(side="right")

        # 2. Contenedor de Pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=10)

        # Tab 1: Grupos y Participantes
        self.tab_part = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_part, text="  1. Grupos y Participantes  ")
        self._construir_tab_participantes()

        # Tab 2: Registro de Gastos
        self.tab_gastos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gastos, text="  2. Registro de Gastos  ")
        self._construir_tab_gastos()

        # Tab 3: Saldos y Liquidación (con Auditoría de pagos de Fase 2)
        self.tab_saldos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_saldos, text="  3. Saldos, Auditoría y Deudas  ")
        self._construir_tab_saldos()

        self.notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_tab)

    # -------------------------------------------------------------
    # TAB 1: GRUPOS Y PARTICIPANTES (FASE 1, 2, 3)
    # -------------------------------------------------------------
    def _construir_tab_participantes(self):
        # A. Nombre del grupo y persistencia segura
        frame_grp = ttk.LabelFrame(self.tab_part, text=" Configuración y Guardado Seguro de Grupo ", padding=12)
        frame_grp.pack(fill="x", padx=8, pady=6)

        ttk.Label(frame_grp, text="Nombre del Grupo:").grid(row=0, column=0, sticky="w", padx=4, pady=4)

        # FASE 1: Vinculación reactiva del input onChange/KeyRelease
        self.var_nombre_grupo = tk.StringVar(value=self.grupo.nombre)
        self.ent_nombre_grupo = ttk.Entry(frame_grp, textvariable=self.var_nombre_grupo, width=32, font=("Inter", 10))
        self.ent_nombre_grupo.grid(row=0, column=1, padx=6, pady=4)
        self.var_nombre_grupo.trace_add("write", self._al_escribir_nombre_grupo)

        btn_nuevo = ttk.Button(frame_grp, text="+ Nuevo Grupo", command=self._crear_nuevo_grupo)
        btn_nuevo.grid(row=0, column=2, padx=4, pady=4)

        btn_guardar_auto = ttk.Button(frame_grp, text="💾 Guardar (Saneado)", style="Success.TButton", command=self._guardar_grupo_saneado)
        btn_guardar_auto.grid(row=0, column=3, padx=6, pady=4)

        btn_guardar_como = ttk.Button(frame_grp, text="Exportar Como...", style="Secondary.TButton", command=self._exportar_como)
        btn_guardar_como.grid(row=0, column=4, padx=4, pady=4)

        btn_cargar = ttk.Button(frame_grp, text="📂 Abrir Archivo", style="Secondary.TButton", command=self._cargar_archivo_dialogo)
        btn_cargar.grid(row=0, column=5, padx=4, pady=4)

        # B. Gestión y Edición de Participantes (Fase 2)
        frame_parts = ttk.LabelFrame(self.tab_part, text=" Gestión de Participantes ", padding=12)
        frame_parts.pack(fill="both", expand=True, padx=8, pady=6)

        # Entrada rápida
        frame_add = ttk.Frame(frame_parts)
        frame_add.pack(fill="x", pady=6)

        ttk.Label(frame_add, text="Nombre:").pack(side="left", padx=4)
        self.ent_nuevo_part = ttk.Entry(frame_add, width=22, font=("Inter", 10))
        self.ent_nuevo_part.pack(side="left", padx=4)
        self.ent_nuevo_part.bind("<Return>", lambda e: self._agregar_participante())

        ttk.Label(frame_add, text="Rol:").pack(side="left", padx=6)
        self.cmb_rol = ttk.Combobox(frame_add, values=["Miembro", "Organizador"], state="readonly", width=12)
        self.cmb_rol.current(0)
        self.cmb_rol.pack(side="left", padx=4)

        btn_add_p = ttk.Button(frame_add, text="+ Agregar", style="Primary.TButton", command=self._agregar_participante)
        btn_add_p.pack(side="left", padx=8)

        # Tabla de participantes con roles
        cols = ("#", "Nombre", "Rol", "Total Aportado", "Gastos Involucrado")
        self.tree_parts = ttk.Treeview(frame_parts, columns=cols, show="headings", height=8)
        self.tree_parts.heading("#", text="#")
        self.tree_parts.heading("Nombre", text="Nombre del Participante")
        self.tree_parts.heading("Rol", text="Rol")
        self.tree_parts.heading("Total Aportado", text="Total Pagado ($)")
        self.tree_parts.heading("Gastos Involucrado", text="En Divisiones")

        self.tree_parts.column("#", width=50, anchor="center")
        self.tree_parts.column("Nombre", width=280)
        self.tree_parts.column("Rol", width=130, anchor="center")
        self.tree_parts.column("Total Aportado", width=140, anchor="e")
        self.tree_parts.column("Gastos Involucrado", width=140, anchor="center")

        self.tree_parts.pack(fill="both", expand=True, pady=6)

        # Acciones: Editar (Fase 2) y Eliminar
        f_acc = ttk.Frame(frame_parts)
        f_acc.pack(fill="x", pady=4)

        btn_edit = ttk.Button(f_acc, text="✏️ Editar Participante", style="Primary.TButton", command=self._editar_participante_modal)
        btn_edit.pack(side="left", padx=4)

        btn_del = ttk.Button(f_acc, text="🗑️ Eliminar Participante", style="Danger.TButton", command=self._eliminar_participante)
        btn_del.pack(side="left", padx=6)

        btn_ir_g = ttk.Button(f_acc, text="Continuar a Gastos →", style="Primary.TButton", command=lambda: self.notebook.select(1))
        btn_ir_g.pack(side="right", padx=4)

    # -------------------------------------------------------------
    # TAB 2: REGISTRO DE GASTOS (FASE 1 & FASE 3)
    # -------------------------------------------------------------
    def _construir_tab_gastos(self):
        frame_form = ttk.LabelFrame(self.tab_gastos, text=" Nuevo Gasto (Cálculo Equitativo Dinámico) ", padding=12)
        frame_form.pack(fill="x", padx=8, pady=6)

        f_in = ttk.Frame(frame_form)
        f_in.pack(fill="x", pady=4)

        ttk.Label(f_in, text="Concepto:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.ent_concepto = ttk.Entry(f_in, width=28, font=("Inter", 10))
        self.ent_concepto.grid(row=0, column=1, padx=6, pady=2)

        ttk.Label(f_in, text="Importe ($):").grid(row=0, column=2, sticky="w", padx=6, pady=2)
        self.ent_importe = ttk.Entry(f_in, width=12, font=("Inter", 10))
        self.ent_importe.grid(row=0, column=3, padx=6, pady=2)
        self.ent_importe.bind("<KeyRelease>", lambda e: self._recalcular_cuota_dinamica())

        ttk.Label(f_in, text="Fecha:").grid(row=0, column=4, sticky="w", padx=6, pady=2)
        self.ent_fecha = ttk.Entry(f_in, width=12, font=("Inter", 10))
        self.ent_fecha.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.ent_fecha.grid(row=0, column=5, padx=6, pady=2)

        f_pag = ttk.Frame(frame_form)
        f_pag.pack(fill="x", pady=6)

        ttk.Label(f_pag, text="¿Quién lo pagó?:", font=("Inter", 10, "bold")).pack(side="left", padx=4)
        self.cmb_pagador = ttk.Combobox(f_pag, state="readonly", width=24)
        self.cmb_pagador.pack(side="left", padx=6)

        f_div = ttk.Frame(frame_form)
        f_div.pack(fill="x", pady=6)

        ttk.Label(f_div, text="Dividir equitativamente entre:", font=("Inter", 10, "bold")).pack(side="left", padx=4)
        ttk.Button(f_div, text="Marcar Todos", command=self._marcar_todos).pack(side="left", padx=6)
        ttk.Button(f_div, text="Desmarcar Todos", command=self._desmarcar_todos).pack(side="left", padx=4)

        self.frame_checks_container = ttk.Frame(frame_form)
        self.frame_checks_container.pack(fill="x", pady=4)

        # FASE 1: Indicador visible de la fórmula en tiempo real
        f_cuota = ttk.Frame(frame_form)
        f_cuota.pack(fill="x", pady=6)

        self.lbl_cuota_formula = ttk.Label(
            f_cuota,
            text="Fórmula: $0.00 / 0 personas = $0.00 c/u",
            font=("Inter", 10, "bold"),
            foreground="#4f46e5",
        )
        self.lbl_cuota_formula.pack(side="left", padx=4)

        self.btn_guardar_gasto = ttk.Button(
            f_cuota,
            text="+ Registrar Gasto",
            style="Primary.TButton",
            command=self._registrar_gasto,
        )
        self.btn_guardar_gasto.pack(side="right", padx=6)

        ttk.Button(f_cuota, text="Limpiar", style="Secondary.TButton", command=self._limpiar_form_gasto).pack(side="right", padx=4)

        # Tabla de gastos registrados
        frame_tabla = ttk.LabelFrame(self.tab_gastos, text=" Historial de Gastos del Grupo ", padding=12)
        frame_tabla.pack(fill="both", expand=True, padx=8, pady=6)

        cols_g = ("ID", "Fecha", "Concepto", "Importe ($)", "Pagado Por", "Participantes", "Cuota c/u")
        self.tree_gastos = ttk.Treeview(frame_tabla, columns=cols_g, show="headings", height=8)

        self.tree_gastos.heading("ID", text="ID")
        self.tree_gastos.heading("Fecha", text="Fecha")
        self.tree_gastos.heading("Concepto", text="Concepto")
        self.tree_gastos.heading("Importe ($)", text="Importe ($)")
        self.tree_gastos.heading("Pagado Por", text="Pagado Por")
        self.tree_gastos.heading("Participantes", text="Dividido Entre")
        self.tree_gastos.heading("Cuota c/u", text="Cuota c/u")

        self.tree_gastos.column("ID", width=40, anchor="center")
        self.tree_gastos.column("Fecha", width=95, anchor="center")
        self.tree_gastos.column("Concepto", width=240)
        self.tree_gastos.column("Importe ($)", width=105, anchor="e")
        self.tree_gastos.column("Pagado Por", width=140)
        self.tree_gastos.column("Participantes", width=220)
        self.tree_gastos.column("Cuota c/u", width=95, anchor="e")

        self.tree_gastos.pack(fill="both", expand=True, pady=6)

        f_acc_g = ttk.Frame(frame_tabla)
        f_acc_g.pack(fill="x", pady=4)

        self.lbl_total_acum = ttk.Label(f_acc_g, text="Total: $0.00", font=("Inter", 10, "bold"))
        self.lbl_total_acum.pack(side="left", padx=4)

        ttk.Button(f_acc_g, text="🗑️ Eliminar Gasto", style="Danger.TButton", command=self._eliminar_gasto).pack(side="left", padx=16)
        ttk.Button(f_acc_g, text="Continuar a Saldos →", style="Primary.TButton", command=lambda: self.notebook.select(2)).pack(side="right", padx=4)

    # -------------------------------------------------------------
    # TAB 3: SALDOS, AUDITORÍA DE PAGOS Y DEUDAS (FASE 1 & 2)
    # -------------------------------------------------------------
    def _construir_tab_saldos(self):
        # A. FASE 2: Auditoría y Desglose de Pagos Reales
        frame_audit = ttk.LabelFrame(self.tab_saldos, text=" Auditoría de Pagos Reales por Miembro (Fase 2) ", padding=10)
        frame_audit.pack(fill="x", padx=8, pady=4)

        cols_a = ("Miembro", "Monto Total que Pagó ($)", "Cantidad de Pagos", "Aporte en el Total (%)")
        self.tree_audit = ttk.Treeview(frame_audit, columns=cols_a, show="headings", height=4)
        self.tree_audit.heading("Miembro", text="Miembro")
        self.tree_audit.heading("Monto Total que Pagó ($)", text="Monto Total Pagado ($)")
        self.tree_audit.heading("Cantidad de Pagos", text="N° de Gastos Abonados")
        self.tree_audit.heading("Aporte en el Total (%)", text="% del Gasto Grupal")

        self.tree_audit.column("Miembro", width=220)
        self.tree_audit.column("Monto Total que Pagó ($)", width=180, anchor="e")
        self.tree_audit.column("Cantidad de Pagos", width=160, anchor="center")
        self.tree_audit.column("Aporte en el Total (%)", width=160, anchor="center")

        self.tree_audit.pack(fill="x", expand=True, pady=4)

        # B. FASE 1: Balances Exactos
        frame_bal = ttk.LabelFrame(self.tab_saldos, text=" Cálculo de Saldos Individuales (Saldo Neto = Pagado - Consumido) ", padding=10)
        frame_bal.pack(fill="both", expand=True, padx=8, pady=4)

        cols_b = ("Participante", "Total Pagado", "Cuota Consumida", "Saldo Neto", "Situación")
        self.tree_saldos = ttk.Treeview(frame_bal, columns=cols_b, show="headings", height=5)
        self.tree_saldos.heading("Participante", text="Participante")
        self.tree_saldos.heading("Total Pagado", text="Total Pagado ($)")
        self.tree_saldos.heading("Cuota Consumida", text="Total Consumido ($)")
        self.tree_saldos.heading("Saldo Neto", text="Saldo Neto ($)")
        self.tree_saldos.heading("Situación", text="Estado de Cuenta")

        self.tree_saldos.column("Participante", width=220)
        self.tree_saldos.column("Total Pagado", width=140, anchor="e")
        self.tree_saldos.column("Cuota Consumida", width=140, anchor="e")
        self.tree_saldos.column("Saldo Neto", width=140, anchor="e")
        self.tree_saldos.column("Situación", width=180, anchor="center")

        self.tree_saldos.pack(fill="both", expand=True, pady=4)

        # C. Liquidación de Deudas
        frame_trans = ttk.LabelFrame(self.tab_saldos, text=" Transferencias Mínimas para Saldar Deudas ", padding=10)
        frame_trans.pack(fill="both", expand=True, padx=8, pady=4)

        cols_t = ("Deudor (Paga)", "Acreedor (Recibe)", "Monto ($)", "Acción")
        self.tree_trans = ttk.Treeview(frame_trans, columns=cols_t, show="headings", height=4)
        self.tree_trans.heading("Deudor (Paga)", text="Deudor (Quién Paga)")
        self.tree_trans.heading("Acreedor (Recibe)", text="Acreedor (Quién Recibe)")
        self.tree_trans.heading("Monto ($)", text="Monto ($)")
        self.tree_trans.heading("Acción", text="Acción")

        self.tree_trans.column("Deudor (Paga)", width=220)
        self.tree_trans.column("Acreedor (Recibe)", width=220)
        self.tree_trans.column("Monto ($)", width=140, anchor="e")
        self.tree_trans.column("Acción", width=160, anchor="center")

        self.tree_trans.pack(fill="both", expand=True, pady=4)

        f_pie = ttk.Frame(self.tab_saldos)
        f_pie.pack(fill="x", padx=8, pady=4)

        ttk.Button(f_pie, text="← Volver a Gastos", command=lambda: self.notebook.select(1)).pack(side="left", padx=4)
        ttk.Button(f_pie, text="🔄 Recalcular Todo", style="Primary.TButton", command=self._actualizar_tab_saldos).pack(side="right", padx=4)

    # -------------------------------------------------------------
    # CONTROLADORES Y LÓGICA REACTIVA
    # -------------------------------------------------------------
    def _al_cambiar_tab(self, event):
        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            self._actualizar_tab_participantes()
        elif idx == 1:
            self._actualizar_tab_gastos()
        elif idx == 2:
            self._actualizar_tab_saldos()

    # --- FASE 1: EVENTO DE CAMBIO DEL NOMBRE DEL GRUPO ---
    def _al_escribir_nombre_grupo(self, *args):
        val = self.var_nombre_grupo.get().strip()
        if val:
            try:
                self.grupo.cambiar_nombre(val)
                self.title(f"GruPay Desktop V2 - {self.grupo.nombre}")
                self.lbl_estado_archivo.config(text=f"● Grupo: {self.grupo.nombre} (Modificado)", fg="#d97706")
            except ValueError:
                pass

    def _crear_nuevo_grupo(self):
        if messagebox.askyesno("Nuevo Grupo", "¿Crear un nuevo grupo limpio?"):
            self.grupo = Grupo("Nuevo Grupo")
            self.ruta_archivo_actual = None
            self.var_nombre_grupo.set(self.grupo.nombre)
            self._actualizar_tab_participantes()
            self._actualizar_selector_grupos()
            self.lbl_estado_archivo.config(text="● Nuevo grupo sin guardar", fg="#64748b")

    # --- FASE 2 & 3: PERSISTENCIA SANEADA Y GESTIÓN MULTI-GRUPO ---
    def _guardar_grupo_saneado(self):
        try:
            # Asegurar nombre saneado
            self.grupo.cambiar_nombre(self.var_nombre_grupo.get())
            ruta = self.grupo.guardar_en_directorio(self.dir_grupos)
            self.ruta_archivo_actual = ruta
            nom_arch = os.path.basename(ruta)
            self.lbl_estado_archivo.config(text=f"✓ Guardado: {nom_arch}", fg="#059669")
            self._actualizar_selector_grupos()
            messagebox.showinfo("Guardado Exitoso", f"El grupo se guardó de forma segura como:\n{nom_arch}")
        except Exception as e:
            messagebox.showerror("Error al Guardar", str(e))

    def _exportar_como(self):
        nom_propuesto = sanitizar_nombre_archivo(self.grupo.nombre)
        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json")],
            initialfile=nom_propuesto,
        )
        if not ruta:
            return
        try:
            self.grupo.guardar_en_directorio(os.path.dirname(ruta))
            messagebox.showinfo("Exportado", f"Archivo exportado con éxito a:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _cargar_archivo_dialogo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if not ruta:
            return
        self._cargar_desde_ruta(ruta)

    def _cargar_desde_ruta(self, ruta: str):
        try:
            self.grupo.cargar_desde_archivo(ruta)
            self.ruta_archivo_actual = ruta
            self.var_nombre_grupo.set(self.grupo.nombre)
            self.title(f"GruPay Desktop V2 - {self.grupo.nombre}")
            nom_arch = os.path.basename(ruta)
            self.lbl_estado_archivo.config(text=f"✓ Cargado: {nom_arch}", fg="#059669")
            self._actualizar_tab_participantes()
            self._actualizar_selector_grupos()
            messagebox.showinfo("Grupo Cargado", f"Se cargó con éxito el grupo '{self.grupo.nombre}'.")
        except Exception as e:
            messagebox.showerror("Error al Cargar", str(e))

    def _actualizar_selector_grupos(self):
        grupos = self.gestor_multi.listar_grupos()
        nombres = [f"{g['nombre']} ({g['cant_participantes']} pers)" for g in grupos]
        self.cmb_grupos_vinculados["values"] = nombres
        for idx, g in enumerate(grupos):
            if g["nombre"] == self.grupo.nombre:
                self.cmb_grupos_vinculados.current(idx)
                break

    def _al_seleccionar_grupo_vinculado(self, event):
        idx = self.cmb_grupos_vinculados.current()
        if idx >= 0:
            grupos = self.gestor_multi.listar_grupos()
            if idx < len(grupos):
                self._cargar_desde_ruta(grupos[idx]["ruta"])

    # --- FASE 2: GESTIÓN Y EDICIÓN DE PARTICIPANTES ---
    def _agregar_participante(self):
        nom = self.ent_nuevo_part.get().strip()
        rol = self.cmb_rol.get().strip()
        try:
            self.grupo.agregar_participante(nom, rol)
            self.ent_nuevo_part.delete(0, tk.END)
            self._actualizar_tab_participantes()
        except ValueError as e:
            messagebox.showerror("Validación", str(e))

    def _editar_participante_modal(self):
        sel = self.tree_parts.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un participante de la tabla para editar.")
            return

        item = self.tree_parts.item(sel[0], "values")
        nom_actual = item[1]
        rol_actual = item[2]

        modal = tk.Toplevel(self)
        modal.title(f"Editar: {nom_actual}")
        modal.geometry("360x170")
        modal.transient(self)
        modal.grab_set()

        ttk.Label(modal, text=f"Modificar datos de '{nom_actual}':", font=("Inter", 10, "bold")).pack(padx=12, pady=6)

        f_nom = ttk.Frame(modal)
        f_nom.pack(fill="x", padx=12, pady=4)
        ttk.Label(f_nom, text="Nombre:").pack(side="left")
        ent_nom = ttk.Entry(f_nom, width=22)
        ent_nom.insert(0, nom_actual)
        ent_nom.pack(side="right")

        f_rol = ttk.Frame(modal)
        f_rol.pack(fill="x", padx=12, pady=4)
        ttk.Label(f_rol, text="Rol:").pack(side="left")
        cmb_r = ttk.Combobox(f_rol, values=["Miembro", "Organizador"], state="readonly", width=19)
        cmb_r.set(rol_actual)
        cmb_r.pack(side="right")

        def guardar_cambios():
            nuevo_n = ent_nom.get().strip()
            nuevo_r = cmb_r.get().strip()
            try:
                self.grupo.editar_participante(nom_actual, nuevo_n, nuevo_r)
                modal.destroy()
                self._actualizar_tab_participantes()
                messagebox.showinfo("Éxito", f"Participante '{nom_actual}' actualizado a '{nuevo_n}'.")
            except ValueError as err:
                messagebox.showerror("Error", str(err))

        ttk.Button(modal, text="Guardar Cambios", style="Primary.TButton", command=guardar_cambios).pack(pady=10)

    def _eliminar_participante(self):
        sel = self.tree_parts.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un participante para eliminar.")
            return

        nom = self.tree_parts.item(sel[0], "values")[1]
        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar a '{nom}'?"):
            try:
                self.grupo.eliminar_participante(nom)
                self._actualizar_tab_participantes()
                messagebox.showinfo("Eliminado", f"Participante '{nom}' eliminado del grupo.")
            except ValueError as err:
                messagebox.showerror("Bloqueo de Seguridad", str(err))

    def _actualizar_tab_participantes(self):
        self.tree_parts.delete(*self.tree_parts.get_children())
        auditoria = self.grupo.obtener_auditoria_pagos()

        for idx, p in enumerate(self.grupo.participantes, start=1):
            nom = p["nombre"]
            rol = p.get("rol", "Miembro")
            total_pag = f"${auditoria[nom]['total_pagado']:.2f}"
            asoc = sum(1 for g in self.grupo.gastos if nom in g.divididos)
            self.tree_parts.insert("", "end", values=(idx, nom, rol, total_pag, f"{asoc} gastos"))

    # --- FASE 1: DIVISIÓN EQUITATIVA DINÁMICA ---
    def _actualizar_tab_gastos(self):
        # Actualizar lista de pagador
        self.cmb_pagador["values"] = self.grupo.nombres_participantes
        if self.grupo.nombres_participantes and not self.cmb_pagador.get():
            self.cmb_pagador.current(0)
        elif self.cmb_pagador.get() not in self.grupo.nombres_participantes:
            if self.grupo.nombres_participantes:
                self.cmb_pagador.current(0)
            else:
                self.cmb_pagador.set("")

        # Reconstruir checkboxes
        for w in self.frame_checks_container.winfo_children():
            w.destroy()

        self.check_vars = {}
        for nom in self.grupo.nombres_participantes:
            var = tk.BooleanVar(value=True)
            self.check_vars[nom] = var
            chk = ttk.Checkbutton(
                self.frame_checks_container,
                text=nom,
                variable=var,
                command=self._recalcular_cuota_dinamica,
            )
            chk.pack(side="left", padx=6, pady=2)

        self._recalcular_cuota_dinamica()
        self._refrescar_tabla_gastos()

    def _marcar_todos(self):
        for v in self.check_vars.values():
            v.set(True)
        self._recalcular_cuota_dinamica()

    def _desmarcar_todos(self):
        for v in self.check_vars.values():
            v.set(False)
        self._recalcular_cuota_dinamica()

    def _recalcular_cuota_dinamica(self):
        """Calcula estrictamente (Importe / Cantidad de participantes seleccionados)."""
        txt = self.ent_importe.get().strip().replace("$", "")
        sel_count = sum(1 for v in self.check_vars.values() if v.get())

        if not txt:
            self.lbl_cuota_formula.config(text=f"Fórmula: $0.00 / {sel_count} personas = $0.00 c/u", foreground="#64748b")
            return

        try:
            monto = float(txt)
            if monto <= 0:
                self.lbl_cuota_formula.config(text="⚠️ El importe debe ser mayor a $0.00", foreground="#ba1a1a")
                return

            if sel_count == 0:
                self.lbl_cuota_formula.config(text="⚠️ Selecciona al menos un participante para dividir", foreground="#ba1a1a")
                return

            cuota = monto / sel_count
            self.lbl_cuota_formula.config(
                text=f"Fórmula Exacta: ${monto:.2f} / {sel_count} pers = ${cuota:.2f} por persona",
                foreground="#059669",
            )
        except ValueError:
            self.lbl_cuota_formula.config(text="⚠️ Importe numérico inválido", foreground="#ba1a1a")

    def _registrar_gasto(self):
        concepto = self.ent_concepto.get().strip()
        importe_txt = self.ent_importe.get().strip().replace("$", "")
        fecha = self.ent_fecha.get().strip()
        pagador = self.cmb_pagador.get().strip()

        # Validación estricta Fase 3
        if not concepto:
            messagebox.showerror("Campo Obligatorio", "El concepto del gasto no puede estar vacío.")
            return

        try:
            importe = float(importe_txt)
            if importe <= 0:
                messagebox.showerror("Importe Inválido", "El importe debe ser estrictamente mayor a $0.00.")
                return
        except ValueError:
            messagebox.showerror("Importe Inválido", "Ingresa un número válido para el importe.")
            return

        if not pagador:
            messagebox.showerror("Campo Obligatorio", "Debes seleccionar quién pagó el gasto.")
            return

        divididos = [nom for nom, v in self.check_vars.items() if v.get()]
        if not divididos:
            messagebox.showerror("Beneficiarios Obligatorios", "Debes seleccionar al menos un participante para dividir el gasto.")
            return

        try:
            self.grupo.registrar_gasto(concepto, importe, fecha, pagador, divididos)
            self._limpiar_form_gasto()
            self._refrescar_tabla_gastos()
            messagebox.showinfo("Gasto Guardado", f"Gasto '{concepto}' por ${importe:.2f} registrado exitosamente.")
        except ValueError as err:
            messagebox.showerror("Error", str(err))

    def _limpiar_form_gasto(self):
        self.ent_concepto.delete(0, tk.END)
        self.ent_importe.delete(0, tk.END)
        self.ent_fecha.delete(0, tk.END)
        self.ent_fecha.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self._marcar_todos()

    def _refrescar_tabla_gastos(self):
        self.tree_gastos.delete(*self.tree_gastos.get_children())
        total = 0.0

        for g in self.grupo.gastos:
            total += g.importe
            div_txt = f"{len(g.divididos)} pers ({', '.join(g.divididos)})"
            self.tree_gastos.insert(
                "",
                "end",
                values=(
                    g.id_gasto,
                    g.fecha,
                    g.concepto,
                    f"${g.importe:.2f}",
                    g.pagador,
                    div_txt,
                    f"${g.cuota_individual:.2f}",
                ),
            )

        self.lbl_total_acum.config(text=f"Total Registrado: {len(self.grupo.gastos)} gastos • ${total:.2f}")

    def _eliminar_gasto(self):
        sel = self.tree_gastos.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un gasto de la tabla para eliminar.")
            return

        id_gasto = int(self.tree_gastos.item(sel[0], "values")[0])
        if messagebox.askyesno("Confirmar", f"¿Eliminar el gasto #{id_gasto}?"):
            try:
                self.grupo.eliminar_gasto(id_gasto)
                self._refrescar_tabla_gastos()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    # --- FASE 1 & 2: SALDOS EXACTOS Y AUDITORÍA ---
    def _actualizar_tab_saldos(self):
        # 1. Auditoría de Pagos Reales (Fase 2)
        self.tree_audit.delete(*self.tree_audit.get_children())
        auditoria = self.grupo.obtener_auditoria_pagos()
        total_grupal = sum(g.importe for g in self.grupo.gastos)

        for nom, datos in auditoria.items():
            pag = datos["total_pagado"]
            pct = f"{(pag / total_grupal * 100):.1f}%" if total_grupal > 0 else "0.0%"
            self.tree_audit.insert(
                "",
                "end",
                values=(nom, f"${pag:.2f}", f"{datos['cantidad_gastos_pagados']} pagos", pct),
            )

        # 2. Saldos Individuales (Fase 1)
        self.tree_saldos.delete(*self.tree_saldos.get_children())
        saldos = self.grupo.calcular_saldos_individuales()

        for nom, d in saldos.items():
            pag = f"${d['pagado']:.2f}"
            cons = f"${d['consumido']:.2f}"
            s = d["saldo"]

            if s > 0.009:
                s_str = f"+${s:.2f}"
                sit = "🟢 A favor (Recibe)"
            elif s < -0.009:
                s_str = f"-${abs(s):.2f}"
                sit = "🔴 En deuda (Paga)"
            else:
                s_str = "$0.00"
                sit = "⚪ Equilibrado"

            self.tree_saldos.insert("", "end", values=(nom, pag, cons, s_str, sit))

        # 3. Transferencias para saldar deudas
        self.tree_trans.delete(*self.tree_trans.get_children())
        trans = self.grupo.calcular_transferencias()

        if not trans:
            self.tree_trans.insert("", "end", values=("—", "—", "$0.00", "Cuentas saldadas"))
        else:
            for t in trans:
                self.tree_trans.insert(
                    "",
                    "end",
                    values=(t["de"], t["a"], f"${t['monto']:.2f}", "Pendiente transferir"),
                )

    def _inicializar_datos_demo(self):
        """Crea el grupo de demostración y lo guarda en el almacén de grupos."""
        self.grupo.agregar_participante("Carlos Gómez", "Organizador")
        self.grupo.agregar_participante("Sofía Martínez", "Miembro")
        self.grupo.agregar_participante("Mateo Silva", "Miembro")
        self.grupo.agregar_participante("Valentina Ríos", "Miembro")

        self.grupo.registrar_gasto(
            "Cena Restaurante",
            120.0,
            "2026-10-06",
            "Carlos Gómez",
            ["Carlos Gómez", "Sofía Martínez", "Mateo Silva", "Valentina Ríos"],
        )
        self.grupo.registrar_gasto(
            "Supermercado",
            80.0,
            "2026-10-05",
            "Sofía Martínez",
            ["Carlos Gómez", "Sofía Martínez", "Mateo Silva", "Valentina Ríos"],
        )
        self.grupo.registrar_gasto(
            "Combustible",
            40.0,
            "2026-10-04",
            "Valentina Ríos",
            ["Carlos Gómez", "Sofía Martínez", "Mateo Silva", "Valentina Ríos"],
        )

        # Guardar automáticamente como grupo vinculado demo
        self.grupo.guardar_en_directorio(self.dir_grupos)
        self._actualizar_tab_participantes()


if __name__ == "__main__":
    app = GruPayAppV2()
    app.mainloop()
