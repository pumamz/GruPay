"""
GruPay V3 - Aplicación de Escritorio
Gestor de Gastos Compartidos (Tkinter Desktop)
Versión 3: Arquitectura Refactorizada, CRUD Directo con Auto-Save, Administrador Único,
Control de Cambios sin Guardar (isDirty), Validaciones Estrictas y Tabla de División Específica.
Ejecutable directamente en Thonny con F5 o: python3 v3/src/app.py
"""

from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Optional

from core import (
    GestorMultiGruposV3,
    Grupo,
    sanitizar_nombre_archivo,
    sanitizar_texto,
    validar_fecha,
    validar_importe,
)


class GruPayAppV3(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("GruPay Desktop V3 - Gestor de Gastos Compartidos")
        self.geometry("1100x750")
        self.minsize(980, 650)

        # Directorio de grupos
        ruta_base = os.path.dirname(os.path.abspath(__file__))
        self.dir_grupos = os.path.join(os.path.dirname(ruta_base), "datos", "grupos_guardados")
        os.makedirs(self.dir_grupos, exist_ok=True)
        self.gestor_multi = GestorMultiGruposV3(self.dir_grupos)

        # FASE 1: Inicialización ESTRICTAMENTE EN BLANCO (sin datos mock precargados)
        self.grupo = Grupo("Nuevo Grupo")
        self.ruta_archivo_actual: Optional[str] = None

        # Variables reactivas para división y control de cambios pendientes (isDirty)
        self.check_vars: Dict[str, tk.BooleanVar] = {}
        self._bloqueando_evento_tab = False

        self._configurar_estilos()
        self._construir_ui()
        self._actualizar_selector_grupos()
        self._actualizar_tab_participantes()

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
        style.configure("Treeview", font=("Inter", 9), rowheight=25, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Inter", 9, "bold"), background="#f1f5f9", foreground="#0f172a")

    def _construir_ui(self):
        # 1. Cabecera superior
        header = tk.Frame(self, bg="#ffffff", height=54, bd=1, relief="solid")
        header.pack(fill="x", side="top")

        lbl_logo = tk.Label(
            header,
            text="👥 GruPay V3",
            font=("Inter", 14, "bold"),
            bg="#ffffff",
            fg="#4f46e5",
            padx=16,
        )
        lbl_logo.pack(side="left")

        # Selector de grupos guardados
        tk.Label(header, text="Cambiar de Grupo:", font=("Inter", 9, "bold"), bg="#ffffff", fg="#475569").pack(side="left", padx=4)
        self.cmb_grupos = ttk.Combobox(header, state="readonly", width=28)
        self.cmb_grupos.pack(side="left", padx=4)
        self.cmb_grupos.bind("<<ComboboxSelected>>", self._al_seleccionar_grupo_selector)

        btn_refrescar = ttk.Button(header, text="🔄", width=3, command=self._actualizar_selector_grupos)
        btn_refrescar.pack(side="left", padx=2)

        self.lbl_estado_sincro = tk.Label(
            header,
            text="● Estado: Grupo en blanco",
            font=("Inter", 9),
            bg="#ffffff",
            fg="#64748b",
            padx=16,
        )
        self.lbl_estado_sincro.pack(side="right")

        # 2. Contenedor de Pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=8)

        # Tab 1: Grupos y Participantes
        self.tab_part = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_part, text="  1. Participantes y Grupo  ")
        self._construir_tab_participantes()

        # Tab 2: Registro de Gastos
        self.tab_gastos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gastos, text="  2. Registro de Gastos  ")
        self._construir_tab_gastos()

        # Tab 3: Saldos y División Específica (Fase 5)
        self.tab_saldos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_saldos, text="  3. Saldos y Desglose Específico  ")
        self._construir_tab_saldos()

        self.notebook.bind("<<NotebookTabChanged>>", self._al_intentar_cambiar_tab)

        # 3. Barra de Pie Global (Fase 4: Reubicación del botón Guardar en esquina inferior derecha)
        footer_global = tk.Frame(self, bg="#ffffff", height=46, bd=1, relief="solid")
        footer_global.pack(fill="x", side="bottom")

        self.lbl_footer_info = tk.Label(
            footer_global,
            text="GruPay V3 • Modo de Sincronización Automática Activo",
            font=("Inter", 9),
            bg="#ffffff",
            fg="#64748b",
            padx=16,
        )
        self.lbl_footer_info.pack(side="left")

        # FASE 4: Botón Guardar en la esquina inferior derecha
        self.btn_guardar_global = ttk.Button(
            footer_global,
            text="💾 Guardar Grupo Completo",
            style="Success.TButton",
            command=self._guardar_grupo_completo,
        )
        self.btn_guardar_global.pack(side="right", padx=16, pady=6)

    # -------------------------------------------------------------
    # TAB 1: PARTICIPANTES Y GRUPO (FASES 1, 2, 3, 4)
    # -------------------------------------------------------------
    def _construir_tab_participantes(self):
        # Sección A: Configuración del Grupo
        frame_grp = ttk.LabelFrame(self.tab_part, text=" Nombre del Grupo Activo ", padding=12)
        frame_grp.pack(fill="x", padx=8, pady=4)

        ttk.Label(frame_grp, text="Nombre:").pack(side="left", padx=4)
        self.var_nombre_grupo = tk.StringVar(value=self.grupo.nombre)
        self.ent_nombre_grupo = ttk.Entry(frame_grp, textvariable=self.var_nombre_grupo, width=32, font=("Inter", 10))
        self.ent_nombre_grupo.pack(side="left", padx=6)
        self.var_nombre_grupo.trace_add("write", self._al_escribir_nombre_grupo)

        ttk.Button(frame_grp, text="+ Nuevo Grupo en Blanco", command=self._crear_nuevo_grupo_en_blanco).pack(side="left", padx=8)

        # Sección B: Gestión de Participantes
        frame_parts = ttk.LabelFrame(self.tab_part, text=" Participantes (CRUD Directo con Auto-Save y Admin Único) ", padding=12)
        frame_parts.pack(fill="both", expand=True, padx=8, pady=4)

        # Formulario de alta
        f_add = ttk.Frame(frame_parts)
        f_add.pack(fill="x", pady=4)

        ttk.Label(f_add, text="Nombre:").pack(side="left", padx=4)
        self.ent_nuevo_part = ttk.Entry(f_add, width=22, font=("Inter", 10))
        self.ent_nuevo_part.pack(side="left", padx=4)
        self.ent_nuevo_part.bind("<Return>", lambda e: self._agregar_participante_crud())

        ttk.Label(f_add, text="Rol:").pack(side="left", padx=6)
        self.cmb_nuevo_rol = ttk.Combobox(f_add, values=["Miembro", "Organizador"], state="readonly", width=14)
        self.cmb_nuevo_rol.current(0)
        self.cmb_nuevo_rol.pack(side="left", padx=4)

        self.btn_add_part = ttk.Button(
            f_add,
            text="+ Agregar Participante",
            style="Primary.TButton",
            command=self._agregar_participante_crud,
        )
        self.btn_add_part.pack(side="left", padx=8)

        # Tabla de participantes
        cols = ("#", "Nombre", "Rol (Admin Único)", "Gastos Pagados", "En Divisiones")
        self.tree_parts = ttk.Treeview(frame_parts, columns=cols, show="headings", height=8)
        self.tree_parts.heading("#", text="#")
        self.tree_parts.heading("Nombre", text="Nombre del Participante")
        self.tree_parts.heading("Rol (Admin Único)", text="Rol Asignado")
        self.tree_parts.heading("Gastos Pagados", text="Total Pagado ($)")
        self.tree_parts.heading("En Divisiones", text="En Divisiones")

        self.tree_parts.column("#", width=50, anchor="center")
        self.tree_parts.column("Nombre", width=280)
        self.tree_parts.column("Rol (Admin Único)", width=170, anchor="center")
        self.tree_parts.column("Gastos Pagados", width=140, anchor="e")
        self.tree_parts.column("En Divisiones", width=130, anchor="center")

        self.tree_parts.pack(fill="both", expand=True, pady=6)

        # Barra de acciones de la tabla
        f_acc = ttk.Frame(frame_parts)
        f_acc.pack(fill="x", pady=4)

        ttk.Button(f_acc, text="✏️ Editar Participante", style="Primary.TButton", command=self._editar_participante_modal).pack(side="left", padx=4)
        ttk.Button(f_acc, text="🗑️ Eliminar Participante", style="Danger.TButton", command=self._eliminar_participante_crud).pack(side="left", padx=6)

        # FASE 4: Bloqueo de avance por cambios pendientes
        self.btn_ir_gastos = ttk.Button(
            f_acc,
            text="Continuar a Gastos →",
            style="Primary.TButton",
            command=self._continuar_a_gastos_con_validacion,
        )
        self.btn_ir_gastos.pack(side="right", padx=4)

    # -------------------------------------------------------------
    # TAB 2: REGISTRO DE GASTOS (FASES 3 Y 4)
    # -------------------------------------------------------------
    def _construir_tab_gastos(self):
        frame_form = ttk.LabelFrame(self.tab_gastos, text=" Registrar Nuevo Gasto (Validaciones Estrictas) ", padding=12)
        frame_form.pack(fill="x", padx=8, pady=4)

        f_in = ttk.Frame(frame_form)
        f_in.pack(fill="x", pady=4)

        ttk.Label(f_in, text="Concepto:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.ent_concepto = ttk.Entry(f_in, width=28, font=("Inter", 10))
        self.ent_concepto.grid(row=0, column=1, padx=6, pady=2)

        ttk.Label(f_in, text="Importe ($):").grid(row=0, column=2, sticky="w", padx=6, pady=2)
        self.ent_importe = ttk.Entry(f_in, width=12, font=("Inter", 10))
        self.ent_importe.grid(row=0, column=3, padx=6, pady=2)
        self.ent_importe.bind("<KeyRelease>", lambda e: self._recalcular_cuota_dinamica())

        ttk.Label(f_in, text="Fecha (DD/MM/AAAA):").grid(row=0, column=4, sticky="w", padx=6, pady=2)
        self.ent_fecha = ttk.Entry(f_in, width=14, font=("Inter", 10))
        self.ent_fecha.insert(0, datetime.today().strftime("%d/%m/%Y"))
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

        f_cuota = ttk.Frame(frame_form)
        f_cuota.pack(fill="x", pady=6)

        self.lbl_cuota_formula = ttk.Label(
            f_cuota,
            text="Fórmula: $0.00 / 0 personas = $0.00 c/u",
            font=("Inter", 10, "bold"),
            foreground="#4f46e5",
        )
        self.lbl_cuota_formula.pack(side="left", padx=4)

        ttk.Button(
            f_cuota,
            text="+ Registrar Gasto",
            style="Primary.TButton",
            command=self._registrar_gasto_en_tiempo_real,
        ).pack(side="right", padx=6)

        ttk.Button(f_cuota, text="Limpiar Formulario", style="Secondary.TButton", command=self._limpiar_form_gasto).pack(side="right", padx=4)

        # Historial de Gastos con reflejo en tiempo real
        frame_tabla = ttk.LabelFrame(self.tab_gastos, text=" Gastos Registrados (Reflejo en Tiempo Real) ", padding=12)
        frame_tabla.pack(fill="both", expand=True, padx=8, pady=4)

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
        self.tree_gastos.column("Fecha", width=100, anchor="center")
        self.tree_gastos.column("Concepto", width=250)
        self.tree_gastos.column("Importe ($)", width=110, anchor="e")
        self.tree_gastos.column("Pagado Por", width=140)
        self.tree_gastos.column("Participantes", width=240)
        self.tree_gastos.column("Cuota c/u", width=95, anchor="e")

        self.tree_gastos.pack(fill="both", expand=True, pady=6)

        f_acc_g = ttk.Frame(frame_tabla)
        f_acc_g.pack(fill="x", pady=4)

        self.lbl_total_acum = ttk.Label(f_acc_g, text="Total: $0.00", font=("Inter", 10, "bold"))
        self.lbl_total_acum.pack(side="left", padx=4)

        ttk.Button(f_acc_g, text="🗑️ Eliminar Gasto", style="Danger.TButton", command=self._eliminar_gasto_en_tiempo_real).pack(side="left", padx=16)
        ttk.Button(f_acc_g, text="Continuar a Saldos →", style="Primary.TButton", command=lambda: self.notebook.select(2)).pack(side="right", padx=4)

    # -------------------------------------------------------------
    # TAB 3: SALDOS Y TABLA DE DIVISIÓN ESPECÍFICA (FASE 5)
    # -------------------------------------------------------------
    def _construir_tab_saldos(self):
        # A. FASE 5: Tabla de División Específica y Desglose Equitativo
        frame_desglose = ttk.LabelFrame(
            self.tab_saldos,
            text=" 🔍 Tabla de División Específica y Transparencia (Fase 5) ",
            padding=10,
        )
        frame_desglose.pack(fill="x", padx=8, pady=4)

        cols_d = ("Fecha", "Concepto", "Monto", "Pagó", "Beneficiarios", "Cuota", "Desglose Transparente")
        self.tree_desglose = ttk.Treeview(frame_desglose, columns=cols_d, show="headings", height=5)
        self.tree_desglose.heading("Fecha", text="Fecha")
        self.tree_desglose.heading("Concepto", text="Concepto")
        self.tree_desglose.heading("Monto", text="Monto ($)")
        self.tree_desglose.heading("Pagó", text="Pagó")
        self.tree_desglose.heading("Beneficiarios", text="Involucrados")
        self.tree_desglose.heading("Cuota", text="Cuota c/u")
        self.tree_desglose.heading("Desglose Transparente", text="Explicación del Cómputo")

        self.tree_desglose.column("Fecha", width=95, anchor="center")
        self.tree_desglose.column("Concepto", width=140)
        self.tree_desglose.column("Monto", width=85, anchor="e")
        self.tree_desglose.column("Pagó", width=110)
        self.tree_desglose.column("Beneficiarios", width=160)
        self.tree_desglose.column("Cuota", width=85, anchor="e")
        self.tree_desglose.column("Desglose Transparente", width=360)

        self.tree_desglose.pack(fill="x", expand=True, pady=4)

        # B. Balances Netos
        frame_bal = ttk.LabelFrame(self.tab_saldos, text=" Resumen de Saldos Individuales ", padding=10)
        frame_bal.pack(fill="both", expand=True, padx=8, pady=4)

        cols_b = ("Participante", "Total Pagado", "Cuota Consumida", "Saldo Neto", "Situación")
        self.tree_saldos = ttk.Treeview(frame_bal, columns=cols_b, show="headings", height=4)
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

        # C. Propuesta de Transferencias
        frame_trans = ttk.LabelFrame(self.tab_saldos, text=" Transferencias Óptimas Sugeridas para Cancelar Deudas ", padding=10)
        frame_trans.pack(fill="both", expand=True, padx=8, pady=4)

        cols_t = ("Deudor (Quién Paga)", "Acreedor (Quién Recibe)", "Monto ($)", "Estado")
        self.tree_trans = ttk.Treeview(frame_trans, columns=cols_t, show="headings", height=4)
        self.tree_trans.heading("Deudor (Quién Paga)", text="Deudor (Quién Paga)")
        self.tree_trans.heading("Acreedor (Quién Recibe)", text="Acreedor (Quién Recibe)")
        self.tree_trans.heading("Monto ($)", text="Monto ($)")
        self.tree_trans.heading("Estado", text="Estado")

        self.tree_trans.column("Deudor (Quién Paga)", width=220)
        self.tree_trans.column("Acreedor (Quién Recibe)", width=220)
        self.tree_trans.column("Monto ($)", width=140, anchor="e")
        self.tree_trans.column("Estado", width=160, anchor="center")

        self.tree_trans.pack(fill="both", expand=True, pady=4)

    # -------------------------------------------------------------
    # CONTROL DE CAMBIOS PENDIENTES (isDirty) Y NAVEGACIÓN
    # -------------------------------------------------------------
    def _tiene_datos_en_formulario_gasto(self) -> bool:
        """Determina si hay un gasto a medio cargar en los inputs."""
        c = self.ent_concepto.get().strip()
        m = self.ent_importe.get().strip()
        return bool(c or m)

    def _tiene_datos_en_formulario_participante(self) -> bool:
        """Determina si hay un nombre escrito en el input de nuevo participante."""
        return bool(self.ent_nuevo_part.get().strip())

    def _al_intentar_cambiar_tab(self, event):
        if self._bloqueando_evento_tab:
            return

        # Si viene desde la pestaña 2 con gasto a medio cargar
        if self._tiene_datos_en_formulario_gasto():
            resp = messagebox.askyesnocancel(
                "Cambios sin Guardar (isDirty)",
                "Tienes datos sin registrar en el formulario de gastos.\n\n"
                "¿Deseas descartar estos datos y continuar?\n"
                "• Sí: Descartar datos y cambiar de pestaña.\n"
                "• No: Permanecer en la pestaña para registrar el gasto.",
            )
            if resp:  # Descartar
                self._limpiar_form_gasto()
            else:  # Cancelar o No
                self._bloqueando_evento_tab = True
                self.notebook.select(1)
                self._bloqueando_evento_tab = False
                return

        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            self._actualizar_tab_participantes()
        elif idx == 1:
            self._actualizar_tab_gastos()
        elif idx == 2:
            self._actualizar_tab_saldos()

    def _continuar_a_gastos_con_validacion(self):
        # FASE 4: Bloqueo de avance si hay nombre sin agregar
        if self._tiene_datos_en_formulario_participante():
            messagebox.showwarning(
                "Acción Pendiente",
                "Tienes un nombre escrito en el campo de participante que no ha sido agregado.\n"
                "Haz clic en '+ Agregar Participante' o limpia el campo antes de continuar.",
            )
            return
        if len(self.grupo.participantes) == 0:
            messagebox.showwarning(
                "Sin Participantes",
                "Agrega al menos un participante al grupo antes de continuar a la pestaña de Gastos.",
            )
            return
        self.notebook.select(1)

    # -------------------------------------------------------------
    # FASE 1: AUTO-SAVE DIRECTO Y PERSISTENCIA DE GRUPO
    # -------------------------------------------------------------
    def _al_escribir_nombre_grupo(self, *args):
        val = self.var_nombre_grupo.get().strip()
        if val:
            try:
                self.grupo.cambiar_nombre(val)
                self.title(f"GruPay Desktop V3 - {self.grupo.nombre}")
            except ValueError:
                pass

    def _auto_guardar_json_si_corresponde(self):
        """Auto-save directo tras cada acción CRUD de participantes (Fase 1)."""
        try:
            nombre_arch = sanitizar_nombre_archivo(self.grupo.nombre)
            ruta = os.path.join(self.dir_grupos, nombre_arch)
            self.grupo.guardar_en_archivo(ruta)
            self.ruta_archivo_actual = ruta
            self.lbl_estado_sincro.config(text=f"✓ Auto-guardado: {nombre_arch}", fg="#059669")
            self._actualizar_selector_grupos()
        except Exception as e:
            self.lbl_estado_sincro.config(text=f"⚠️ Error auto-guardado: {str(e)}", fg="#dc2626")

    def _guardar_grupo_completo(self):
        """Guardado explícito invocado por el botón reubicado en la esquina inferior derecha."""
        try:
            self.grupo.cambiar_nombre(self.var_nombre_grupo.get())
            nombre_arch = sanitizar_nombre_archivo(self.grupo.nombre)
            ruta = os.path.join(self.dir_grupos, nombre_arch)
            self.grupo.guardar_en_archivo(ruta)
            self.ruta_archivo_actual = ruta
            self.lbl_estado_sincro.config(text=f"✓ Guardado: {nombre_arch}", fg="#059669")
            self._actualizar_selector_grupos()
            messagebox.showinfo("Guardado Exitoso", f"El grupo se guardó correctamente como:\n{nombre_arch}")
        except Exception as e:
            messagebox.showerror("Error al Guardar", str(e))

    def _crear_nuevo_grupo_en_blanco(self):
        if messagebox.askyesno("Nuevo Grupo", "¿Crear un nuevo grupo limpio en blanco?"):
            self.grupo.reiniciar_en_blanco("Nuevo Grupo")
            self.ruta_archivo_actual = None
            self.var_nombre_grupo.set(self.grupo.nombre)
            self.title(f"GruPay Desktop V3 - {self.grupo.nombre}")
            self.lbl_estado_sincro.config(text="● Grupo en blanco (Sin guardar)", fg="#64748b")
            self._actualizar_tab_participantes()
            self._actualizar_tab_gastos()
            self._actualizar_tab_saldos()
            self._actualizar_selector_grupos()

    def _actualizar_selector_grupos(self):
        grupos = self.gestor_multi.listar_grupos()
        nombres = [f"{g['nombre']} ({g['cant_participantes']} pers)" for g in grupos]
        self.cmb_grupos["values"] = nombres
        for idx, g in enumerate(grupos):
            if g["nombre"] == self.grupo.nombre:
                self.cmb_grupos.current(idx)
                break

    def _al_seleccionar_grupo_selector(self, event):
        idx = self.cmb_grupos.current()
        if idx >= 0:
            grupos = self.gestor_multi.listar_grupos()
            if idx < len(grupos):
                ruta = grupos[idx]["ruta"]
                try:
                    # Limpieza total e hidratación pura (Fase 1)
                    self.grupo.cargar_desde_archivo(ruta)
                    self.ruta_archivo_actual = ruta
                    self.var_nombre_grupo.set(self.grupo.nombre)
                    self.title(f"GruPay Desktop V3 - {self.grupo.nombre}")
                    nom_arch = os.path.basename(ruta)
                    self.lbl_estado_sincro.config(text=f"✓ Cargado: {nom_arch}", fg="#059669")
                    self._actualizar_tab_participantes()
                    self._actualizar_tab_gastos()
                    self._actualizar_tab_saldos()
                except Exception as err:
                    messagebox.showerror("Error al Cargar", str(err))

    # -------------------------------------------------------------
    # FASE 2: CRUD DE PARTICIPANTES (AUTO-SAVE Y ADMIN ÚNICO)
    # -------------------------------------------------------------
    def _agregar_participante_crud(self):
        nom = self.ent_nuevo_part.get().strip()
        rol = self.cmb_nuevo_rol.get().strip()

        # Validación estricta de no vacíos (Fase 3)
        if not nom:
            messagebox.showwarning("Campo Vacío", "El nombre del participante no puede estar vacío.")
            return

        try:
            self.grupo.agregar_participante(nom, rol)
            self.ent_nuevo_part.delete(0, tk.END)
            self._actualizar_tab_participantes()
            # FASE 1: Sincronización CRUD directa
            self._auto_guardar_json_si_corresponde()
        except ValueError as err:
            messagebox.showerror("Validación", str(err))

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
        modal.geometry("380x180")
        modal.transient(self)
        modal.grab_set()

        ttk.Label(modal, text=f"Editar datos de '{nom_actual}':", font=("Inter", 10, "bold")).pack(padx=12, pady=6)

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

        def guardar():
            nuevo_n = ent_nom.get().strip()
            nuevo_r = cmb_r.get().strip()
            if not nuevo_n:
                messagebox.showerror("Campo Vacío", "El nombre no puede estar vacío.")
                return

            try:
                self.grupo.editar_participante(nom_actual, nuevo_n, nuevo_r)
                modal.destroy()
                self._actualizar_tab_participantes()
                # FASE 1: Sincronización CRUD directa
                self._auto_guardar_json_si_corresponde()
                messagebox.showinfo("Éxito", f"Participante '{nom_actual}' actualizado.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(modal, text="Guardar Cambios", style="Primary.TButton", command=guardar).pack(pady=10)

    def _eliminar_participante_crud(self):
        sel = self.tree_parts.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un participante para eliminar.")
            return

        nom = self.tree_parts.item(sel[0], "values")[1]
        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar a '{nom}'?"):
            try:
                # FASE 2: Regla de integridad
                self.grupo.eliminar_participante(nom)
                self._actualizar_tab_participantes()
                # FASE 1: Sincronización CRUD directa
                self._auto_guardar_json_si_corresponde()
                messagebox.showinfo("Eliminado", f"Participante '{nom}' eliminado.")
            except ValueError as err:
                messagebox.showerror("Regla de Integridad", str(err))

    def _actualizar_tab_participantes(self):
        self.tree_parts.delete(*self.tree_parts.get_children())
        saldos = self.grupo.calcular_saldos_individuales()

        for idx, p in enumerate(self.grupo.participantes, start=1):
            nom = p["nombre"]
            rol = p.get("rol", "Miembro")
            total_pag = f"${saldos[nom]['pagado']:.2f}"
            asoc = sum(1 for g in self.grupo.gastos if nom in g.divididos)
            self.tree_parts.insert("", "end", values=(idx, nom, rol, total_pag, f"{asoc} gastos"))

    # -------------------------------------------------------------
    # FASES 3 Y 4: MÓDULO DE GASTOS CON REFLEJO EN TIEMPO REAL
    # -------------------------------------------------------------
    def _actualizar_tab_gastos(self):
        self.cmb_pagador["values"] = self.grupo.nombres_participantes
        if self.grupo.nombres_participantes and not self.cmb_pagador.get():
            self.cmb_pagador.current(0)
        elif self.cmb_pagador.get() not in self.grupo.nombres_participantes:
            if self.grupo.nombres_participantes:
                self.cmb_pagador.current(0)
            else:
                self.cmb_pagador.set("")

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
        txt = self.ent_importe.get().strip().replace("$", "")
        sel_count = sum(1 for v in self.check_vars.values() if v.get())

        if not txt:
            self.lbl_cuota_formula.config(text=f"Fórmula: $0.00 / {sel_count} personas = $0.00 c/u", foreground="#64748b")
            return

        try:
            monto = validar_importe(txt)
            if sel_count == 0:
                self.lbl_cuota_formula.config(text="⚠️ Selecciona al menos un participante para dividir", foreground="#dc2626")
                return

            cuota = monto / sel_count
            self.lbl_cuota_formula.config(
                text=f"Fórmula: ${monto:.2f} / {sel_count} pers = ${cuota:.2f} c/u",
                foreground="#059669",
            )
        except ValueError:
            self.lbl_cuota_formula.config(text="⚠️ Importe inválido (positivo, máx 2 decimales)", foreground="#dc2626")

    def _registrar_gasto_en_tiempo_real(self):
        concepto = self.ent_concepto.get().strip()
        importe_txt = self.ent_importe.get().strip()
        fecha_txt = self.ent_fecha.get().strip()
        pagador = self.cmb_pagador.get().strip()

        # Validación estricta Fase 3
        if not concepto:
            messagebox.showerror("Validación", "El concepto del gasto no puede estar vacío.")
            return

        try:
            importe = validar_importe(importe_txt)
        except ValueError as err:
            messagebox.showerror("Validación de Importe", str(err))
            return

        try:
            fecha_valida = validar_fecha(fecha_txt)
        except ValueError as err:
            messagebox.showerror("Validación de Fecha", str(err))
            return

        if not pagador:
            messagebox.showerror("Validación", "Debes seleccionar quién pagó el gasto.")
            return

        divididos = [nom for nom, v in self.check_vars.items() if v.get()]
        if not divididos:
            messagebox.showerror("Validación", "Debes seleccionar al menos un participante para dividir el gasto.")
            return

        try:
            # FASE 4: Registro y reflejo en tiempo real inmediato
            self.grupo.registrar_gasto(concepto, importe, fecha_valida, pagador, divididos)
            self._limpiar_form_gasto()
            self._refrescar_tabla_gastos()
            self._auto_guardar_json_si_corresponde()
            messagebox.showinfo("Gasto Registrado", f"Gasto '{concepto}' agregado exitosamente.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _limpiar_form_gasto(self):
        self.ent_concepto.delete(0, tk.END)
        self.ent_importe.delete(0, tk.END)
        self.ent_fecha.delete(0, tk.END)
        self.ent_fecha.insert(0, datetime.today().strftime("%d/%m/%Y"))
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

    def _eliminar_gasto_en_tiempo_real(self):
        sel = self.tree_gastos.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un gasto de la tabla para eliminar.")
            return

        id_gasto = int(self.tree_gastos.item(sel[0], "values")[0])
        if messagebox.askyesno("Confirmar", f"¿Eliminar el gasto #{id_gasto}?"):
            try:
                self.grupo.eliminar_gasto(id_gasto)
                self._refrescar_tabla_gastos()
                self._auto_guardar_json_si_corresponde()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    # -------------------------------------------------------------
    # FASE 5: TABLA DE DIVISIÓN ESPECÍFICA Y SALDOS
    # -------------------------------------------------------------
    def _actualizar_tab_saldos(self):
        # 1. Tabla de División Específica (Fase 5)
        self.tree_desglose.delete(*self.tree_desglose.get_children())
        desglose = self.grupo.obtener_desglose_division_especifica()

        for d in desglose:
            self.tree_desglose.insert(
                "",
                "end",
                values=(
                    d["fecha"],
                    d["concepto"],
                    f"${d['importe']:.2f}",
                    d["pagador"],
                    d["participantes"],
                    f"${d['cuota_individual']:.2f}",
                    d["texto_desglose"],
                ),
            )

        # 2. Resumen de Saldos Individuales
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

        # 3. Transferencias sugeridas
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


if __name__ == "__main__":
    app = GruPayAppV3()
    app.mainloop()
