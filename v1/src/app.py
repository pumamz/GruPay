"""
GruPay V1 - Aplicación de Escritorio
Gestor de Gastos Compartidos (Tkinter Desktop)
Ejecutable directamente en Thonny o terminal: python3 app.py
Cumple con los 10 requisitos funcionales (RF1 a RF10).
"""

from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict

from core import Grupo


class GruPayApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("GruPay Desktop - Gestor de Gastos Compartidos (V1)")
        self.geometry("960x680")
        self.minsize(880, 580)

        # Instancia central del modelo
        self.grupo = Grupo("Viaje a la Playa")
        self.archivo_actual = None

        # Variables para división dinámica con checkboxes
        self.check_vars: Dict[str, tk.BooleanVar] = {}

        # Configurar estilos visuales sobrios de escritorio
        self._configurar_estilos()

        # Construir interfaz gráfica
        self._construir_ui()

        # Cargar datos iniciales de ejemplo para facilidad de prueba
        self._cargar_datos_demo()

    def _configurar_estilos(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Colores del tema
        bg_main = "#f8f9fc"
        primary = "#4f46e5"

        self.configure(bg=bg_main)

        style.configure("TFrame", background=bg_main)
        style.configure("TLabelframe", background=bg_main)
        style.configure("TLabelframe.Label", font=("Inter", 10, "bold"), foreground="#1e293b", background=bg_main)
        style.configure("TLabel", background=bg_main, font=("Inter", 10), foreground="#1e293b")
        style.configure("Header.TLabel", font=("Inter", 13, "bold"), foreground="#0f172a")

        # Botones
        style.configure("Primary.TButton", font=("Inter", 9, "bold"), background=primary, foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#4338ca")])

        style.configure("Secondary.TButton", font=("Inter", 9), background="#e2e8f0", foreground="#1e293b")
        style.map("Secondary.TButton", background=[("active", "#cbd5e1")])

        style.configure("Danger.TButton", font=("Inter", 9), background="#fee2e2", foreground="#991b1b")
        style.map("Danger.TButton", background=[("active", "#fecaca")])

        # Pestañas
        style.configure("TNotebook", background=bg_main)
        style.configure("TNotebook.Tab", font=("Inter", 10, "bold"), padding=[16, 8])
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", primary)])

        # Treeview / Tablas
        style.configure("Treeview", font=("Inter", 9), rowheight=26, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Inter", 9, "bold"), background="#f1f5f9", foreground="#0f172a")

    def _construir_ui(self):
        # 1. Barra de Título / Header superior de la ventana
        header_frame = tk.Frame(self, bg="#ffffff", height=50, bd=1, relief="solid")
        header_frame.pack(fill="x", side="top")

        lbl_logo = tk.Label(
            header_frame,
            text="👥 GruPay",
            font=("Inter", 14, "bold"),
            bg="#ffffff",
            fg="#4f46e5",
            padx=16,
        )
        lbl_logo.pack(side="left")

        lbl_sub = tk.Label(
            header_frame,
            text="• Gestor de Gastos Compartidos (V1)",
            font=("Inter", 10),
            bg="#ffffff",
            fg="#64748b",
        )
        lbl_sub.pack(side="left")

        self.lbl_archivo = tk.Label(
            header_frame,
            text="Archivo: No guardado",
            font=("Inter", 9),
            bg="#ffffff",
            fg="#64748b",
            padx=16,
        )
        self.lbl_archivo.pack(side="right")

        # 2. Contenedor de Pestañas (3 Pantallas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=12)

        # Pantalla 1: Grupos y Participantes
        self.tab_participantes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_participantes, text="  1. Grupos y Participantes  ")
        self._construir_tab_participantes()

        # Pantalla 2: Registro de Gastos
        self.tab_gastos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gastos, text="  2. Registro de Gastos  ")
        self._construir_tab_gastos()

        # Pantalla 3: Saldos y Liquidación
        self.tab_saldos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_saldos, text="  3. Saldos y Deudas  ")
        self._construir_tab_saldos()

        # Evento al cambiar de pestaña para refrescar datos
        self.notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_pestana)

    # -------------------------------------------------------------
    # PANTALLA 1: GRUPOS Y PARTICIPANTES (RF1, RF2, RF10)
    # -------------------------------------------------------------
    def _construir_tab_participantes(self):
        # Subsección A: Configuración del Grupo (RF1, RF10)
        frame_grupo = ttk.LabelFrame(self.tab_participantes, text=" Configuración del Grupo (RF1, RF10) ", padding=12)
        frame_grupo.pack(fill="x", padx=8, pady=8)

        lbl_nombre = ttk.Label(frame_grupo, text="Nombre del Grupo:")
        lbl_nombre.grid(row=0, column=0, sticky="w", padx=4, pady=4)

        self.ent_nombre_grupo = ttk.Entry(frame_grupo, width=28, font=("Inter", 10))
        self.ent_nombre_grupo.insert(0, self.grupo.nombre)
        self.ent_nombre_grupo.grid(row=0, column=1, padx=6, pady=4)

        btn_renombrar = ttk.Button(frame_grupo, text="Actualizar Nombre", command=self._actualizar_nombre_grupo)
        btn_renombrar.grid(row=0, column=2, padx=4, pady=4)

        btn_nuevo = ttk.Button(frame_grupo, text="+ Nuevo Grupo", command=self._nuevo_grupo)
        btn_nuevo.grid(row=0, column=3, padx=4, pady=4)

        btn_guardar = ttk.Button(frame_grupo, text="💾 Guardar Grupo", style="Primary.TButton", command=self._guardar_grupo)
        btn_guardar.grid(row=0, column=4, padx=6, pady=4)

        btn_cargar = ttk.Button(frame_grupo, text="📂 Cargar Grupo", style="Secondary.TButton", command=self._cargar_grupo)
        btn_cargar.grid(row=0, column=5, padx=4, pady=4)

        # Subsección B: Gestión de Participantes (RF2)
        frame_parts = ttk.LabelFrame(self.tab_participantes, text=" Gestión de Participantes (RF2) ", padding=12)
        frame_parts.pack(fill="both", expand=True, padx=8, pady=8)

        # Entrada de nuevo participante
        frame_add = ttk.Frame(frame_parts)
        frame_add.pack(fill="x", pady=6)

        ttk.Label(frame_add, text="Nombre de Persona:").pack(side="left", padx=4)
        self.ent_nuevo_part = ttk.Entry(frame_add, width=24, font=("Inter", 10))
        self.ent_nuevo_part.pack(side="left", padx=6)
        self.ent_nuevo_part.bind("<Return>", lambda e: self._agregar_participante())

        btn_add_part = ttk.Button(frame_add, text="+ Agregar Participante", style="Primary.TButton", command=self._agregar_participante)
        btn_add_part.pack(side="left", padx=4)

        # Tabla de participantes
        cols = ("#", "Nombre", "Gastos Pagados", "Gastos Asociados")
        self.tree_parts = ttk.Treeview(frame_parts, columns=cols, show="headings", height=8)
        self.tree_parts.heading("#", text="#")
        self.tree_parts.heading("Nombre", text="Nombre del Participante")
        self.tree_parts.heading("Gastos Pagados", text="Total Pagado")
        self.tree_parts.heading("Gastos Asociados", text="En Divisiones")

        self.tree_parts.column("#", width=50, anchor="center")
        self.tree_parts.column("Nombre", width=300)
        self.tree_parts.column("Gastos Pagados", width=140, anchor="e")
        self.tree_parts.column("Gastos Asociados", width=140, anchor="center")

        self.tree_parts.pack(fill="both", expand=True, pady=6)

        # Botones de acción para participante seleccionado
        frame_acc_parts = ttk.Frame(frame_parts)
        frame_acc_parts.pack(fill="x", pady=4)

        btn_edit_part = ttk.Button(frame_acc_parts, text="✏️ Editar Nombre", command=self._editar_participante)
        btn_edit_part.pack(side="left", padx=4)

        btn_del_part = ttk.Button(frame_acc_parts, text="🗑️ Eliminar Seleccionado", style="Danger.TButton", command=self._eliminar_participante)
        btn_del_part.pack(side="left", padx=4)

        btn_ir_gastos = ttk.Button(frame_acc_parts, text="Continuar a Gastos →", style="Primary.TButton", command=lambda: self.notebook.select(1))
        btn_ir_gastos.pack(side="right", padx=4)

    # -------------------------------------------------------------
    # PANTALLA 2: REGISTRO DE GASTOS (RF3, RF4, RF5, RF6)
    # -------------------------------------------------------------
    def _construir_tab_gastos(self):
        # Subsección A: Formulario de Nuevo Gasto
        frame_form = ttk.LabelFrame(self.tab_gastos, text=" Registrar Nuevo Gasto (RF3, RF4, RF5, RF6) ", padding=12)
        frame_form.pack(fill="x", padx=8, pady=8)

        # Fila 1: Concepto, Importe, Fecha
        f_inputs = ttk.Frame(frame_form)
        f_inputs.pack(fill="x", pady=4)

        ttk.Label(f_inputs, text="Concepto:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.ent_concepto = ttk.Entry(f_inputs, width=28, font=("Inter", 10))
        self.ent_concepto.grid(row=0, column=1, padx=6, pady=2)

        ttk.Label(f_inputs, text="Importe ($):").grid(row=0, column=2, sticky="w", padx=6, pady=2)
        self.ent_importe = ttk.Entry(f_inputs, width=12, font=("Inter", 10))
        self.ent_importe.grid(row=0, column=3, padx=6, pady=2)
        self.ent_importe.bind("<KeyRelease>", lambda e: self._actualizar_cuota_estimada())

        ttk.Label(f_inputs, text="Fecha (AAAA-MM-DD):").grid(row=0, column=4, sticky="w", padx=6, pady=2)
        self.ent_fecha = ttk.Entry(f_inputs, width=12, font=("Inter", 10))
        self.ent_fecha.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.ent_fecha.grid(row=0, column=5, padx=6, pady=2)

        # Fila 2: Pagador
        f_pagador = ttk.Frame(frame_form)
        f_pagador.pack(fill="x", pady=6)

        ttk.Label(f_pagador, text="¿Quién lo pagó? (RF4):", font=("Inter", 10, "bold")).pack(side="left", padx=4)
        self.cmb_pagador = ttk.Combobox(f_pagador, state="readonly", width=22)
        self.cmb_pagador.pack(side="left", padx=8)

        # Fila 3: División entre participantes (RF5, RF6)
        f_division = ttk.Frame(frame_form)
        f_division.pack(fill="x", pady=6)

        ttk.Label(f_division, text="¿Entre quiénes se divide? (RF5):", font=("Inter", 10, "bold")).pack(side="left", padx=4)

        btn_todos = ttk.Button(f_division, text="Marcar Todos", command=self._marcar_todos_division)
        btn_todos.pack(side="left", padx=4)

        btn_ninguno = ttk.Button(f_division, text="Desmarcar Todos", command=self._desmarcar_todos_division)
        btn_ninguno.pack(side="left", padx=4)

        self.frame_checks = ttk.Frame(frame_form)
        self.frame_checks.pack(fill="x", pady=4)

        # Nota de cuota calculada en tiempo real
        f_cuota = ttk.Frame(frame_form)
        f_cuota.pack(fill="x", pady=4)

        self.lbl_cuota_calculada = ttk.Label(
            f_cuota,
            text="Cuota estimada: $0.00 por persona",
            font=("Inter", 10, "bold"),
            foreground="#4f46e5",
        )
        self.lbl_cuota_calculada.pack(side="left", padx=4)

        btn_guardar_gasto = ttk.Button(
            f_cuota,
            text="+ Agregar Gasto",
            style="Primary.TButton",
            command=self._registrar_gasto,
        )
        btn_guardar_gasto.pack(side="right", padx=6)

        btn_limpiar_gasto = ttk.Button(
            f_cuota,
            text="Limpiar",
            style="Secondary.TButton",
            command=self._limpiar_formulario_gasto,
        )
        btn_limpiar_gasto.pack(side="right", padx=4)

        # Subsección B: Historial de Gastos
        frame_tabla = ttk.LabelFrame(self.tab_gastos, text=" Gastos Registrados ", padding=12)
        frame_tabla.pack(fill="both", expand=True, padx=8, pady=8)

        cols_g = ("ID", "Fecha", "Concepto", "Importe", "Pagado Por", "Dividido Entre", "Cuota c/u")
        self.tree_gastos = ttk.Treeview(frame_tabla, columns=cols_g, show="headings", height=8)

        self.tree_gastos.heading("ID", text="ID")
        self.tree_gastos.heading("Fecha", text="Fecha")
        self.tree_gastos.heading("Concepto", text="Concepto")
        self.tree_gastos.heading("Importe", text="Importe ($)")
        self.tree_gastos.heading("Pagado Por", text="Pagó")
        self.tree_gastos.heading("Dividido Entre", text="Dividido Entre")
        self.tree_gastos.heading("Cuota c/u", text="Cuota c/u")

        self.tree_gastos.column("ID", width=40, anchor="center")
        self.tree_gastos.column("Fecha", width=90, anchor="center")
        self.tree_gastos.column("Concepto", width=220)
        self.tree_gastos.column("Importe", width=100, anchor="e")
        self.tree_gastos.column("Pagado Por", width=130)
        self.tree_gastos.column("Dividido Entre", width=220)
        self.tree_gastos.column("Cuota c/u", width=90, anchor="e")

        self.tree_gastos.pack(fill="both", expand=True, pady=6)

        # Acciones de la tabla
        frame_acc_g = ttk.Frame(frame_tabla)
        frame_acc_g.pack(fill="x", pady=4)

        self.lbl_total_gastos = ttk.Label(frame_acc_g, text="Total acumulado: $0.00", font=("Inter", 10, "bold"))
        self.lbl_total_gastos.pack(side="left", padx=4)

        btn_del_gasto = ttk.Button(frame_acc_g, text="🗑️ Eliminar Gasto", style="Danger.TButton", command=self._eliminar_gasto)
        btn_del_gasto.pack(side="left", padx=12)

        btn_ir_saldos = ttk.Button(frame_acc_g, text="Continuar a Saldos →", style="Primary.TButton", command=lambda: self.notebook.select(2))
        btn_ir_saldos.pack(side="right", padx=4)

    # -------------------------------------------------------------
    # PANTALLA 3: SALDOS Y LIQUIDACIÓN (RF7, RF8, RF9)
    # -------------------------------------------------------------
    def _construir_tab_saldos(self):
        # Subsección A: Resumen de Saldos Individuales (RF7, RF8)
        frame_saldos = ttk.LabelFrame(self.tab_saldos, text=" Resumen y Saldos Individuales (RF7, RF8) ", padding=12)
        frame_saldos.pack(fill="both", expand=True, padx=8, pady=8)

        cols_s = ("Participante", "Total Pagado (RF7)", "Cuota Consumida", "Saldo Neto (RF8)", "Situación")
        self.tree_saldos = ttk.Treeview(frame_saldos, columns=cols_s, show="headings", height=5)

        self.tree_saldos.heading("Participante", text="Participante")
        self.tree_saldos.heading("Total Pagado (RF7)", text="Total Pagado ($)")
        self.tree_saldos.heading("Cuota Consumida", text="Total Consumido ($)")
        self.tree_saldos.heading("Saldo Neto (RF8)", text="Saldo Neto ($)")
        self.tree_saldos.heading("Situación", text="Estado")

        self.tree_saldos.column("Participante", width=200)
        self.tree_saldos.column("Total Pagado (RF7)", width=140, anchor="e")
        self.tree_saldos.column("Cuota Consumida", width=140, anchor="e")
        self.tree_saldos.column("Saldo Neto (RF8)", width=140, anchor="e")
        self.tree_saldos.column("Situación", width=160, anchor="center")

        self.tree_saldos.pack(fill="both", expand=True, pady=6)

        # Subsección B: Propuesta de Transferencias (RF9)
        frame_trans = ttk.LabelFrame(self.tab_saldos, text=" Propuesta de Transferencias para Cancelar Deudas (RF9) ", padding=12)
        frame_trans.pack(fill="both", expand=True, padx=8, pady=8)

        cols_t = ("Deudor (Quién Paga)", "Acreedor (Quién Recibe)", "Monto a Transferir", "Acción")
        self.tree_trans = ttk.Treeview(frame_trans, columns=cols_t, show="headings", height=5)

        self.tree_trans.heading("Deudor (Quién Paga)", text="Deudor (Quién Paga)")
        self.tree_trans.heading("Acreedor (Quién Recibe)", text="Acreedor (Quién Recibe)")
        self.tree_trans.heading("Monto a Transferir", text="Monto ($)")
        self.tree_trans.heading("Acción", text="Estado")

        self.tree_trans.column("Deudor (Quién Paga)", width=220)
        self.tree_trans.column("Acreedor (Quién Recibe)", width=220)
        self.tree_trans.column("Monto a Transferir", width=140, anchor="e")
        self.tree_trans.column("Acción", width=160, anchor="center")

        self.tree_trans.pack(fill="both", expand=True, pady=6)

        # Botones de pie
        frame_pie_saldos = ttk.Frame(self.tab_saldos)
        frame_pie_saldos.pack(fill="x", padx=8, pady=6)

        btn_volver_g = ttk.Button(frame_pie_saldos, text="← Volver a Gastos", command=lambda: self.notebook.select(1))
        btn_volver_g.pack(side="left", padx=4)

        btn_recalcular = ttk.Button(frame_pie_saldos, text="🔄 Recalcular Balances", style="Primary.TButton", command=self._actualizar_pantalla_saldos)
        btn_recalcular.pack(side="right", padx=4)

    # -------------------------------------------------------------
    # MÉTODOS DE CONTROL Y EVENTOS
    # -------------------------------------------------------------
    def _al_cambiar_pestana(self, event):
        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            self._actualizar_pantalla_participantes()
        elif idx == 1:
            self._actualizar_pantalla_gastos()
        elif idx == 2:
            self._actualizar_pantalla_saldos()

    # --- PANTALLA 1 LOGIC ---
    def _actualizar_nombre_grupo(self):
        nuevo_nom = self.ent_nombre_grupo.get().strip()
        if not nuevo_nom:
            messagebox.showwarning("Atención", "El nombre del grupo no puede estar vacío.")
            return
        self.grupo.nombre = nuevo_nom
        self.title(f"GruPay Desktop - {self.grupo.nombre} (V1)")
        messagebox.showinfo("Éxito", f"Nombre actualizado a '{nuevo_nom}'.")

    def _nuevo_grupo(self):
        if messagebox.askyesno("Confirmar", "¿Deseas reiniciar y crear un nuevo grupo en blanco?"):
            self.grupo.reiniciar_grupo("Nuevo Grupo")
            self.archivo_actual = None
            self.lbl_archivo.config(text="Archivo: No guardado")
            self.ent_nombre_grupo.delete(0, tk.END)
            self.ent_nombre_grupo.insert(0, self.grupo.nombre)
            self._actualizar_pantalla_participantes()
            messagebox.showinfo("Nuevo Grupo", "Se ha creado un nuevo grupo limpio.")

    def _agregar_participante(self):
        nombre = self.ent_nuevo_part.get().strip()
        try:
            self.grupo.agregar_participante(nombre)
            self.ent_nuevo_part.delete(0, tk.END)
            self._actualizar_pantalla_participantes()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _editar_participante(self):
        sel = self.tree_parts.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un participante de la tabla para editar.")
            return
        valores = self.tree_parts.item(sel[0], "values")
        nombre_actual = valores[1]

        # Ventana modal simple para editar
        ventana_edit = tk.Toplevel(self)
        ventana_edit.title("Editar Participante")
        ventana_edit.geometry("320x130")
        ventana_edit.transient(self)
        ventana_edit.grab_set()

        ttk.Label(ventana_edit, text=f"Nuevo nombre para '{nombre_actual}':").pack(padx=12, pady=8)
        ent_nuevo = ttk.Entry(ventana_edit, width=24)
        ent_nuevo.insert(0, nombre_actual)
        ent_nuevo.pack(padx=12, pady=4)

        def guardar():
            nuevo_nom = ent_nuevo.get().strip()
            try:
                self.grupo.editar_participante(nombre_actual, nuevo_nom)
                ventana_edit.destroy()
                self._actualizar_pantalla_participantes()
                messagebox.showinfo("Éxito", "Participante modificado correctamente.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(ventana_edit, text="Guardar", style="Primary.TButton", command=guardar).pack(pady=8)

    def _eliminar_participante(self):
        sel = self.tree_parts.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un participante de la tabla para eliminar.")
            return
        nombre = self.tree_parts.item(sel[0], "values")[1]

        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar a '{nombre}'?"):
            try:
                self.grupo.eliminar_participante(nombre)
                self._actualizar_pantalla_participantes()
                messagebox.showinfo("Eliminado", f"Participante '{nombre}' eliminado.")
            except ValueError as e:
                messagebox.showerror("No se puede eliminar", str(e))

    def _actualizar_pantalla_participantes(self):
        self.tree_parts.delete(*self.tree_parts.get_children())
        totales_pagados = self.grupo.calcular_totales_pagados()

        for idx, p in enumerate(self.grupo.participantes, start=1):
            total_pag = f"${totales_pagados.get(p, 0.0):.2f}"
            asoc = sum(1 for g in self.grupo.gastos if p in g.divididos)
            self.tree_parts.insert("", "end", values=(idx, p, total_pag, f"{asoc} gastos"))

    # --- PANTALLA 2 LOGIC ---
    def _actualizar_pantalla_gastos(self):
        # Actualizar combobox de pagador
        self.cmb_pagador["values"] = self.grupo.participantes
        if self.grupo.participantes and not self.cmb_pagador.get():
            self.cmb_pagador.current(0)
        elif self.cmb_pagador.get() not in self.grupo.participantes:
            if self.grupo.participantes:
                self.cmb_pagador.current(0)
            else:
                self.cmb_pagador.set("")

        # Reconstruir checkboxes de división
        for widget in self.frame_checks.winfo_children():
            widget.destroy()

        self.check_vars = {}
        for p in self.grupo.participantes:
            var = tk.BooleanVar(value=True)
            self.check_vars[p] = var
            chk = ttk.Checkbutton(
                self.frame_checks,
                text=p,
                variable=var,
                command=self._actualizar_cuota_estimada,
            )
            chk.pack(side="left", padx=6, pady=2)

        self._actualizar_cuota_estimada()
        self._refrescar_tabla_gastos()

    def _marcar_todos_division(self):
        for var in self.check_vars.values():
            var.set(True)
        self._actualizar_cuota_estimada()

    def _desmarcar_todos_division(self):
        for var in self.check_vars.values():
            var.set(False)
        self._actualizar_cuota_estimada()

    def _actualizar_cuota_estimada(self):
        try:
            importe_txt = self.ent_importe.get().strip().replace("$", "")
            if not importe_txt:
                self.lbl_cuota_calculada.config(text="Cuota estimada: $0.00 por persona")
                return
            monto = float(importe_txt)
            sel_count = sum(1 for var in self.check_vars.values() if var.get())
            if sel_count > 0 and monto > 0:
                cuota = monto / sel_count
                self.lbl_cuota_calculada.config(
                    text=f"Cuota igual (RF6): ${cuota:.2f} c/u entre {sel_count} personas"
                )
            else:
                self.lbl_cuota_calculada.config(text="Selecciona al menos un participante.")
        except ValueError:
            self.lbl_cuota_calculada.config(text="Importe inválido.")

    def _registrar_gasto(self):
        concepto = self.ent_concepto.get().strip()
        importe_txt = self.ent_importe.get().strip().replace("$", "")
        fecha = self.ent_fecha.get().strip()
        pagador = self.cmb_pagador.get().strip()

        try:
            importe = float(importe_txt)
        except ValueError:
            messagebox.showerror("Error", "El importe debe ser un número válido.")
            return

        divididos = [p for p, var in self.check_vars.items() if var.get()]

        try:
            self.grupo.registrar_gasto(concepto, importe, fecha, pagador, divididos)
            self._limpiar_formulario_gasto()
            self._refrescar_tabla_gastos()
            messagebox.showinfo("Gasto Registrado", f"Gasto '{concepto}' agregado correctamente.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _limpiar_formulario_gasto(self):
        self.ent_concepto.delete(0, tk.END)
        self.ent_importe.delete(0, tk.END)
        self.ent_fecha.delete(0, tk.END)
        self.ent_fecha.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self._marcar_todos_division()

    def _refrescar_tabla_gastos(self):
        self.tree_gastos.delete(*self.tree_gastos.get_children())
        total = 0.0

        for g in self.grupo.gastos:
            total += g.importe
            div_str = f"{len(g.divididos)} pers ({', '.join(g.divididos)})"
            self.tree_gastos.insert(
                "",
                "end",
                values=(
                    g.id_gasto,
                    g.fecha,
                    g.concepto,
                    f"${g.importe:.2f}",
                    g.pagador,
                    div_str,
                    f"${g.cuota_individual:.2f}",
                ),
            )

        self.lbl_total_gastos.config(
            text=f"Total registrado: {len(self.grupo.gastos)} gastos • ${total:.2f}"
        )

    def _eliminar_gasto(self):
        sel = self.tree_gastos.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un gasto de la tabla para eliminar.")
            return
        id_gasto = int(self.tree_gastos.item(sel[0], "values")[0])

        if messagebox.askyesno("Confirmar", f"¿Eliminar el gasto ID #{id_gasto}?"):
            try:
                self.grupo.eliminar_gasto(id_gasto)
                self._refrescar_tabla_gastos()
                messagebox.showinfo("Eliminado", "Gasto eliminado correctamente.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    # --- PANTALLA 3 LOGIC ---
    def _actualizar_pantalla_saldos(self):
        # 1. Actualizar tabla de saldos (RF7, RF8)
        self.tree_saldos.delete(*self.tree_saldos.get_children())
        saldos = self.grupo.calcular_saldos_individuales()

        for p, d in saldos.items():
            pag = f"${d['pagado']:.2f}"
            cons = f"${d['consumido']:.2f}"
            saldo_val = d["saldo"]

            if saldo_val > 0.009:
                saldo_str = f"+${saldo_val:.2f}"
                situacion = "🟢 A favor (Recibe)"
            elif saldo_val < -0.009:
                saldo_str = f"-${abs(saldo_val):.2f}"
                situacion = "🔴 En contra (Debe)"
            else:
                saldo_str = "$0.00"
                situacion = "⚪ Al día / Equilibrado"

            self.tree_saldos.insert("", "end", values=(p, pag, cons, saldo_str, situacion))

        # 2. Actualizar tabla de transferencias propuestas (RF9)
        self.tree_trans.delete(*self.tree_trans.get_children())
        trans = self.grupo.calcular_transferencias()

        if not trans:
            self.tree_trans.insert("", "end", values=("—", "—", "$0.00", "Todas las deudas saldadas"))
        else:
            for t in trans:
                self.tree_trans.insert(
                    "",
                    "end",
                    values=(t["de"], t["a"], f"${t['monto']:.2f}", "Pendiente transferir"),
                )

    # --- PERSISTENCIA LOCAL (RF10) ---
    def _guardar_grupo(self):
        if not self.archivo_actual:
            ruta = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Archivos JSON", "*.json")],
                initialfile="grupo_gastos.json",
            )
            if not ruta:
                return
            self.archivo_actual = ruta

        try:
            self.grupo.guardar_en_archivo(self.archivo_actual)
            nom_arch = os.path.basename(self.archivo_actual)
            self.lbl_archivo.config(text=f"Archivo: {nom_arch} (Guardado)")
            messagebox.showinfo("Guardado", f"Grupo guardado exitosamente en '{nom_arch}'.")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    def _cargar_grupo(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json")],
        )
        if not ruta:
            return

        try:
            self.grupo.cargar_desde_archivo(ruta)
            self.archivo_actual = ruta
            nom_arch = os.path.basename(ruta)
            self.lbl_archivo.config(text=f"Archivo: {nom_arch}")
            self.ent_nombre_grupo.delete(0, tk.END)
            self.ent_nombre_grupo.insert(0, self.grupo.nombre)
            self.title(f"GruPay Desktop - {self.grupo.nombre} (V1)")
            self._actualizar_pantalla_participantes()
            messagebox.showinfo("Cargado", f"Grupo cargado con éxito desde '{nom_arch}'.")
        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    def _cargar_datos_demo(self):
        """Carga datos de demostración para probar inmediatamente en Thonny."""
        self.grupo.agregar_participante("Carlos Gómez")
        self.grupo.agregar_participante("Sofía Martínez")
        self.grupo.agregar_participante("Mateo Silva")
        self.grupo.agregar_participante("Valentina Ríos")

        self.grupo.registrar_gasto(
            concepto="Cena Restaurante Mar Azul",
            importe=120.0,
            fecha="2026-10-06",
            pagador="Carlos Gómez",
            divididos=["Carlos Gómez", "Sofía Martínez", "Mateo Silva", "Valentina Ríos"],
        )
        self.grupo.registrar_gasto(
            concepto="Compras Supermercado",
            importe=80.0,
            fecha="2026-10-05",
            pagador="Sofía Martínez",
            divididos=["Carlos Gómez", "Sofía Martínez", "Mateo Silva", "Valentina Ríos"],
        )
        self.grupo.registrar_gasto(
            concepto="Combustible y Peaje",
            importe=40.0,
            fecha="2026-10-04",
            pagador="Valentina Ríos",
            divididos=["Carlos Gómez", "Sofía Martínez", "Mateo Silva", "Valentina Ríos"],
        )
        self._actualizar_pantalla_participantes()


if __name__ == "__main__":
    app = GruPayApp()
    app.mainloop()
