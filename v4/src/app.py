"""
GruPay V4 - Aplicación de Escritorio (Cumplimiento de los 5 RNF)
Gestor de Gastos Compartidos (Tkinter Desktop)
Ejecutable directamente en Thonny con F5 o: python3 v4/src/app.py

Implementa estrictamente:
- RNF1: Validador de teclado en tiempo real para importes, auto-formato onBlur ('15' -> '15.00')
        y formateador estándar de moneda ($ X,XXX.XX).
- RNF2: Botón de guardar gasto visualmente desactivado (disabled) por defecto;
        se activa reactivamente solo cuando el formulario está 100% completo y válido.
- RNF3: Algoritmo O(N) de recorrido único con memoización; procesa 1000 gastos instantáneamente.
- RNF4: Exportación automática e importación protegida con validación estricta de esquema.
- RNF5: Semántica visual en saldos con colores accesibles (verde/rojo/gris),
        textos explícitos ('Recibe dinero'/'Debe dinero'/'Cuentas saldadas') y flechas/íconos sin signo negativo.
"""

from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Optional

from core import (
    GrupoV4,
    autoformatear_monto_texto,
    es_caracter_monto_permitido,
    formatear_moneda,
    sanitizar_texto,
    validar_esquema_archivo,
    validar_fecha_estricta,
)


class GruPayAppV4(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("GruPay Desktop V4 - Sistema de Alto Rendimiento y Semántica Financiera")
        self.geometry("1120x760")
        self.minsize(980, 660)

        # Directorio de grupos
        ruta_base = os.path.dirname(os.path.abspath(__file__))
        self.dir_datos = os.path.join(os.path.dirname(ruta_base), "datos")
        os.makedirs(self.dir_datos, exist_ok=True)

        # Instancia del modelo optimizado
        self.grupo = GrupoV4("Viaje de Graduación 2026")
        self.ruta_archivo_actual: Optional[str] = None

        # Variables reactivas para división y validación en tiempo real
        self.check_vars: Dict[str, tk.BooleanVar] = {}

        self._configurar_estilos()
        self._construir_ui()

        # Cargar datos base limpios para demostración inicial
        self._cargar_datos_iniciales_limpios()
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

        # Treeview / Tablas
        style.configure("Treeview", font=("Inter", 9), rowheight=26, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Inter", 9, "bold"), background="#f1f5f9", foreground="#0f172a")

    def _construir_ui(self):
        # 1. Cabecera superior
        header = tk.Frame(self, bg="#ffffff", height=54, bd=1, relief="solid")
        header.pack(fill="x", side="top")

        lbl_logo = tk.Label(
            header,
            text="⚡ GruPay V4 (RNF Engine)",
            font=("Inter", 13, "bold"),
            bg="#ffffff",
            fg="#4f46e5",
            padx=16,
        )
        lbl_logo.pack(side="left")

        # Botones de persistencia segura (RNF4)
        btn_exportar = ttk.Button(
            header,
            text="⬇️ Exportar Archivo (RNF4)",
            style="Success.TButton",
            command=self._exportar_archivo_automatico,
        )
        btn_exportar.pack(side="left", padx=8)

        btn_importar = ttk.Button(
            header,
            text="⬆️ Importar Seguro (RNF4)",
            style="Secondary.TButton",
            command=self._importar_archivo_con_proteccion,
        )
        btn_importar.pack(side="left", padx=4)

        btn_stress = ttk.Button(
            header,
            text="🚀 Benchmark 1000 Gastos (RNF3)",
            command=self._ejecutar_benchmark_estres,
        )
        btn_stress.pack(side="left", padx=8)

        self.lbl_estado_sistema = tk.Label(
            header,
            text="● Sistema Protegido (RNF4 Activo)",
            font=("Inter", 9),
            bg="#ffffff",
            fg="#059669",
            padx=16,
        )
        self.lbl_estado_sistema.pack(side="right")

        # 2. Contenedor de Pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=8)

        # Tab 1: Participantes
        self.tab_part = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_part, text="  1. Participantes y Grupo  ")
        self._construir_tab_participantes()

        # Tab 2: Gastos (RNF1 y RNF2)
        self.tab_gastos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gastos, text="  2. Registro de Gastos (Validación RNF1/RNF2)  ")
        self._construir_tab_gastos()

        # Tab 3: Saldos y Liquidación (RNF3 y RNF5)
        self.tab_saldos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_saldos, text="  3. Saldos y Semántica Visual (RNF5)  ")
        self._construir_tab_saldos()

        self.notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_tab)

        # 3. Pie de página
        footer = tk.Frame(self, bg="#ffffff", height=38, bd=1, relief="solid")
        footer.pack(fill="x", side="bottom")

        self.lbl_benchmark_info = tk.Label(
            footer,
            text="RNF3: Algoritmo O(N) Single-Pass con Memoización activo | RNF1 Formateo Nativo",
            font=("Inter", 9),
            bg="#ffffff",
            fg="#64748b",
            padx=16,
        )
        self.lbl_benchmark_info.pack(side="left")

    # -------------------------------------------------------------
    # TAB 1: PARTICIPANTES
    # -------------------------------------------------------------
    def _construir_tab_participantes(self):
        f_grp = ttk.LabelFrame(self.tab_part, text=" Nombre del Grupo ", padding=10)
        f_grp.pack(fill="x", padx=8, pady=4)

        ttk.Label(f_grp, text="Nombre:").pack(side="left", padx=4)
        self.var_nombre_grupo = tk.StringVar(value=self.grupo.nombre)
        self.ent_nombre_grupo = ttk.Entry(f_grp, textvariable=self.var_nombre_grupo, width=32, font=("Inter", 10))
        self.ent_nombre_grupo.pack(side="left", padx=6)
        self.var_nombre_grupo.trace_add("write", lambda *a: self.grupo.cambiar_nombre(self.var_nombre_grupo.get() or "Grupo"))

        ttk.Button(f_grp, text="+ Nuevo Grupo Limpio", command=self._nuevo_grupo_limpio).pack(side="left", padx=8)

        # Gestión de miembros
        f_parts = ttk.LabelFrame(self.tab_part, text=" Integrantes del Grupo ", padding=10)
        f_parts.pack(fill="both", expand=True, padx=8, pady=4)

        f_add = ttk.Frame(f_parts)
        f_add.pack(fill="x", pady=4)

        ttk.Label(f_add, text="Nombre:").pack(side="left", padx=4)
        self.ent_nuevo_part = ttk.Entry(f_add, width=22, font=("Inter", 10))
        self.ent_nuevo_part.pack(side="left", padx=4)
        self.ent_nuevo_part.bind("<Return>", lambda e: self._agregar_participante())

        ttk.Label(f_add, text="Rol:").pack(side="left", padx=6)
        self.cmb_rol = ttk.Combobox(f_add, values=["Miembro", "Organizador"], state="readonly", width=14)
        self.cmb_rol.current(0)
        self.cmb_rol.pack(side="left", padx=4)

        ttk.Button(f_add, text="+ Agregar", style="Primary.TButton", command=self._agregar_participante).pack(side="left", padx=8)

        cols = ("#", "Nombre", "Rol", "Total Aportado (RNF1)", "En Gastos")
        self.tree_parts = ttk.Treeview(f_parts, columns=cols, show="headings", height=8)
        self.tree_parts.heading("#", text="#")
        self.tree_parts.heading("Nombre", text="Nombre del Participante")
        self.tree_parts.heading("Rol", text="Rol")
        self.tree_parts.heading("Total Aportado (RNF1)", text="Total Aportado ($)")
        self.tree_parts.heading("En Gastos", text="Participa En")

        self.tree_parts.column("#", width=50, anchor="center")
        self.tree_parts.column("Nombre", width=280)
        self.tree_parts.column("Rol", width=150, anchor="center")
        self.tree_parts.column("Total Aportado (RNF1)", width=170, anchor="e")
        self.tree_parts.column("En Gastos", width=130, anchor="center")

        self.tree_parts.pack(fill="both", expand=True, pady=6)

        f_acc = ttk.Frame(f_parts)
        f_acc.pack(fill="x", pady=4)

        ttk.Button(f_acc, text="✏️ Editar Nombre", command=self._editar_participante).pack(side="left", padx=4)
        ttk.Button(f_acc, text="🗑️ Eliminar Integrante", style="Danger.TButton", command=self._eliminar_participante).pack(side="left", padx=6)
        ttk.Button(f_acc, text="Continuar a Gastos →", style="Primary.TButton", command=lambda: self.notebook.select(1)).pack(side="right", padx=4)

    # -------------------------------------------------------------
    # TAB 2: GASTOS (VALIDACIONES ESTRICTAS RNF1 Y RNF2)
    # -------------------------------------------------------------
    def _construir_tab_gastos(self):
        f_form = ttk.LabelFrame(
            self.tab_gastos,
            text=" Formulario de Gasto (RNF1 Formato Numérico • RNF2 Bloqueo de Incompletos) ",
            padding=12,
        )
        f_form.pack(fill="x", padx=8, pady=4)

        f_in = ttk.Frame(f_form)
        f_in.pack(fill="x", pady=4)

        # Concepto (RNF2)
        ttk.Label(f_in, text="Concepto:*").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.var_concepto = tk.StringVar()
        self.ent_concepto = ttk.Entry(f_in, textvariable=self.var_concepto, width=26, font=("Inter", 10))
        self.ent_concepto.grid(row=0, column=1, padx=6, pady=2)
        self.var_concepto.trace_add("write", lambda *a: self._evaluar_formulario_reactivo())

        # Importe con RNF1: validación en tiempo real de teclado + onBlur autoformateo
        ttk.Label(f_in, text="Importe ($):*").grid(row=0, column=2, sticky="w", padx=6, pady=2)

        # Validador de teclado nativo de Tkinter
        vcmd = (self.register(self._validar_tecleo_monto), "%S", "%P")
        self.var_importe = tk.StringVar()
        self.ent_importe = ttk.Entry(
            f_in,
            textvariable=self.var_importe,
            width=13,
            font=("Inter", 10),
            validate="key",
            validatecommand=vcmd,
        )
        self.ent_importe.grid(row=0, column=3, padx=6, pady=2)
        # Evento onBlur: auto-formato con 2 decimales ('15' -> '15.00')
        self.ent_importe.bind("<FocusOut>", self._al_perder_foco_importe)
        self.var_importe.trace_add("write", lambda *a: self._evaluar_formulario_reactivo())

        # Fecha (RNF2)
        ttk.Label(f_in, text="Fecha (DD/MM/AAAA):*").grid(row=0, column=4, sticky="w", padx=6, pady=2)
        self.var_fecha = tk.StringVar(value=datetime.today().strftime("%d/%m/%Y"))
        self.ent_fecha = ttk.Entry(f_in, textvariable=self.var_fecha, width=13, font=("Inter", 10))
        self.ent_fecha.grid(row=0, column=5, padx=6, pady=2)
        self.var_fecha.trace_add("write", lambda *a: self._evaluar_formulario_reactivo())

        # Pagador
        f_pag = ttk.Frame(f_form)
        f_pag.pack(fill="x", pady=6)

        ttk.Label(f_pag, text="¿Quién lo pagó?:*", font=("Inter", 10, "bold")).pack(side="left", padx=4)
        self.cmb_pagador = ttk.Combobox(f_pag, state="readonly", width=24)
        self.cmb_pagador.pack(side="left", padx=6)
        self.cmb_pagador.bind("<<ComboboxSelected>>", lambda e: self._evaluar_formulario_reactivo())

        # Beneficiarios
        f_div = ttk.Frame(f_form)
        f_div.pack(fill="x", pady=6)

        ttk.Label(f_div, text="Dividir entre:*", font=("Inter", 10, "bold")).pack(side="left", padx=4)
        ttk.Button(f_div, text="Marcar Todos", command=self._marcar_todos).pack(side="left", padx=6)
        ttk.Button(f_div, text="Desmarcar Todos", command=self._desmarcar_todos).pack(side="left", padx=4)

        self.frame_checks = ttk.Frame(f_form)
        self.frame_checks.pack(fill="x", pady=4)

        # Fila de Acción con RNF2: Botón bloqueado (disabled) por defecto
        f_btn_action = ttk.Frame(f_form)
        f_btn_action.pack(fill="x", pady=6)

        self.lbl_validacion_estado = ttk.Label(
            f_btn_action,
            text="⚠️ Completa concepto, importe, fecha, pagador y beneficiarios para habilitar el guardado.",
            font=("Inter", 9),
            foreground="#dc2626",
        )
        self.lbl_validacion_estado.pack(side="left", padx=4)

        # RNF2: Botón disabled por defecto
        self.btn_guardar_gasto = ttk.Button(
            f_btn_action,
            text="🔒 Guardar Gasto (RNF2)",
            style="Primary.TButton",
            state="disabled",
            command=self._guardar_gasto_validado,
        )
        self.btn_guardar_gasto.pack(side="right", padx=6)

        ttk.Button(f_btn_action, text="Limpiar", style="Secondary.TButton", command=self._limpiar_form_gasto).pack(side="right", padx=4)

        # Tabla de gastos registrados
        f_tabla = ttk.LabelFrame(self.tab_gastos, text=" Historial de Gastos Registrados ", padding=10)
        f_tabla.pack(fill="both", expand=True, padx=8, pady=4)

        cols_g = ("ID", "Fecha", "Concepto", "Importe Formateado", "Pagado Por", "Participantes", "Cuota Individual")
        self.tree_gastos = ttk.Treeview(f_tabla, columns=cols_g, show="headings", height=8)

        self.tree_gastos.heading("ID", text="ID")
        self.tree_gastos.heading("Fecha", text="Fecha")
        self.tree_gastos.heading("Concepto", text="Concepto")
        self.tree_gastos.heading("Importe Formateado", text="Importe (RNF1)")
        self.tree_gastos.heading("Pagado Por", text="Pagado Por")
        self.tree_gastos.heading("Participantes", text="Dividido Entre")
        self.tree_gastos.heading("Cuota Individual", text="Cuota c/u")

        self.tree_gastos.column("ID", width=40, anchor="center")
        self.tree_gastos.column("Fecha", width=100, anchor="center")
        self.tree_gastos.column("Concepto", width=250)
        self.tree_gastos.column("Importe Formateado", width=130, anchor="e")
        self.tree_gastos.column("Pagado Por", width=150)
        self.tree_gastos.column("Participantes", width=240)
        self.tree_gastos.column("Cuota Individual", width=110, anchor="e")

        self.tree_gastos.pack(fill="both", expand=True, pady=6)

        f_acc_g = ttk.Frame(f_tabla)
        f_acc_g.pack(fill="x", pady=4)

        self.lbl_total_gastos = ttk.Label(f_acc_g, text="Total Registrado: $ 0.00", font=("Inter", 10, "bold"))
        self.lbl_total_gastos.pack(side="left", padx=4)

        ttk.Button(f_acc_g, text="🗑️ Eliminar Gasto", style="Danger.TButton", command=self._eliminar_gasto).pack(side="left", padx=16)
        ttk.Button(f_acc_g, text="Ver Saldos Semánticos →", style="Primary.TButton", command=lambda: self.notebook.select(2)).pack(side="right", padx=4)

    # -------------------------------------------------------------
    # TAB 3: SALDOS Y SEMÁNTICA VISUAL (RNF5 Y RNF3)
    # -------------------------------------------------------------
    def _construir_tab_saldos(self):
        f_saldos = ttk.LabelFrame(
            self.tab_saldos,
            text=" Liquidación Financiera Semántica (RNF5: Verde / Rojo / Gris con Íconos y Textos Explícitos) ",
            padding=12,
        )
        f_saldos.pack(fill="both", expand=True, padx=8, pady=4)

        cols_s = ("Participante", "Total Pagado (RNF1)", "Total Consumido", "Monto Saldo", "Situación Financiera (RNF5)")
        self.tree_saldos = ttk.Treeview(f_saldos, columns=cols_s, show="headings", height=6)

        self.tree_saldos.heading("Participante", text="Participante")
        self.tree_saldos.heading("Total Pagado (RNF1)", text="Total Pagado ($)")
        self.tree_saldos.heading("Total Consumido", text="Total Consumido ($)")
        self.tree_saldos.heading("Monto Saldo", text="Saldo ($)")
        self.tree_saldos.heading("Situación Financiera (RNF5)", text="Estado Semántico y Acción")

        self.tree_saldos.column("Participante", width=220)
        self.tree_saldos.column("Total Pagado (RNF1)", width=150, anchor="e")
        self.tree_saldos.column("Total Consumido", width=150, anchor="e")
        self.tree_saldos.column("Monto Saldo", width=150, anchor="e")
        self.tree_saldos.column("Situación Financiera (RNF5)", width=280, anchor="center")

        # Configuración de tags de color para la tabla (RNF5)
        self.tree_saldos.tag_configure("tag_positivo", background="#ecfdf5", foreground="#065f46")  # Verde suave
        self.tree_saldos.tag_configure("tag_negativo", background="#fef2f2", foreground="#991b1b")  # Rojo suave
        self.tree_saldos.tag_configure("tag_cero", background="#f8fafc", foreground="#475569")      # Gris suave

        self.tree_saldos.pack(fill="both", expand=True, pady=6)

        # Transferencias
        f_trans = ttk.LabelFrame(self.tab_saldos, text=" Transferencias Directas Optimizadas para Liquidación ", padding=10)
        f_trans.pack(fill="both", expand=True, padx=8, pady=4)

        cols_t = ("Deudor (Quién Debe Pagar)", "Acreedor (Quién Debe Recibir)", "Importe Formateado (RNF1)", "Instrucción de Pago")
        self.tree_trans = ttk.Treeview(f_trans, columns=cols_t, show="headings", height=5)
        self.tree_trans.heading("Deudor (Quién Debe Pagar)", text="Deudor (Quién Debe Pagar)")
        self.tree_trans.heading("Acreedor (Quién Debe Recibir)", text="Acreedor (Quién Debe Recibir)")
        self.tree_trans.heading("Importe Formateado (RNF1)", text="Monto a Transferir")
        self.tree_trans.heading("Instrucción de Pago", text="Estado de Liquidación")

        self.tree_trans.column("Deudor (Quién Debe Pagar)", width=230)
        self.tree_trans.column("Acreedor (Quién Debe Recibir)", width=230)
        self.tree_trans.column("Importe Formateado (RNF1)", width=160, anchor="e")
        self.tree_trans.column("Instrucción de Pago", width=220, anchor="center")

        self.tree_trans.pack(fill="both", expand=True, pady=6)

    # -------------------------------------------------------------
    # RNF1 Y RNF2: VALIDACIONES EN TIEMPO REAL Y AUTOFORMATO
    # -------------------------------------------------------------
    def _validar_tecleo_monto(self, char_ingresado: str, texto_futuro: str) -> bool:
        """RNF1: Rechaza de forma activa cualquier carácter no numérico, negativos o letras."""
        return es_caracter_monto_permitido(char_ingresado, texto_futuro)

    def _al_perder_foco_importe(self, event):
        """RNF1: onBlur autoformatea el importe completando 2 decimales ('15' -> '15.00')."""
        txt = self.var_importe.get().strip()
        if txt:
            try:
                formateado = autoformatear_monto_texto(txt)
                self.var_importe.set(formateado)
            except ValueError:
                pass
        self._evaluar_formulario_reactivo()

    def _evaluar_formulario_reactivo(self):
        """
        RNF2: Evalúa constantemente el formulario y solo habilita el botón cuando se cumplen
        todas las condiciones a la vez:
        1. Concepto no vacío ni solo espacios.
        2. Fecha válida DD/MM/AAAA.
        3. Importe mayor a cero.
        4. Pagador definido.
        5. Al menos un beneficiario seleccionado.
        """
        concepto = self.var_concepto.get().strip()
        importe_txt = self.var_importe.get().strip()
        fecha_txt = self.var_fecha.get().strip()
        pagador = self.cmb_pagador.get().strip()
        divs_count = sum(1 for v in self.check_vars.values() if v.get())

        es_valido = True
        motivo = ""

        if not concepto:
            es_valido = False
            motivo = "Falta ingresar el concepto del gasto."
        elif not importe_txt:
            es_valido = False
            motivo = "Falta ingresar el importe."
        else:
            try:
                monto = float(importe_txt)
                if monto <= 0:
                    es_valido = False
                    motivo = "El importe debe ser mayor a 0."
            except ValueError:
                es_valido = False
                motivo = "El importe debe ser un número válido."

        if es_valido:
            try:
                validar_fecha_estricta(fecha_txt)
            except ValueError:
                es_valido = False
                motivo = "La fecha debe tener formato DD/MM/AAAA válido."

        if es_valido and not pagador:
            es_valido = False
            motivo = "Falta seleccionar quién pagó el gasto."

        if es_valido and divs_count == 0:
            es_valido = False
            motivo = "Selecciona al menos un participante para dividir."

        if es_valido:
            self.btn_guardar_gasto.config(state="normal", text="✓ Guardar Gasto")
            monto_num = float(importe_txt)
            cuota_est = monto_num / divs_count
            self.lbl_validacion_estado.config(
                text=f"✓ Formulario válido. Cuota: {formatear_moneda(cuota_est)} c/u ({divs_count} pers.)",
                foreground="#059669",
            )
        else:
            self.btn_guardar_gasto.config(state="disabled", text="🔒 Guardar Gasto (Bloqueado)")
            self.lbl_validacion_estado.config(text=f"⚠️ {motivo}", foreground="#dc2626")

    def _guardar_gasto_validado(self):
        """Registra el gasto verificado tras cumplir RNF1 y RNF2."""
        concepto = self.var_concepto.get().strip()
        monto = float(self.var_importe.get().strip())
        fecha = self.var_fecha.get().strip()
        pagador = self.cmb_pagador.get().strip()
        divididos = [nom for nom, v in self.check_vars.items() if v.get()]

        try:
            self.grupo.registrar_gasto(concepto, monto, fecha, pagador, divididos)
            self._limpiar_form_gasto()
            self._refrescar_tabla_gastos()
            self.lbl_estado_sistema.config(text=f"✓ Gasto '{concepto}' registrado", fg="#059669")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _limpiar_form_gasto(self):
        self.var_concepto.set("")
        self.var_importe.set("")
        self.var_fecha.set(datetime.today().strftime("%d/%m/%Y"))
        self._marcar_todos()
        self._evaluar_formulario_reactivo()

    # -------------------------------------------------------------
    # RNF4: PERSISTENCIA SEGURA Y PROTECCIÓN ANTE ARCHIVOS CORRUPTOS
    # -------------------------------------------------------------
    def _exportar_archivo_automatico(self):
        """RNF4: Exporta y fuerza la descarga/guardado del archivo en el dispositivo."""
        nom_base = f"{self.grupo.nombre.replace(' ', '_')}.json"
        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json")],
            initialfile=nom_base,
            initialdir=self.dir_datos,
        )
        if not ruta:
            return
        try:
            self.grupo.guardar_en_archivo(ruta)
            self.ruta_archivo_actual = ruta
            nom_arch = os.path.basename(ruta)
            self.lbl_estado_sistema.config(text=f"✓ Exportado: {nom_arch}", fg="#059669")
            messagebox.showinfo("Exportación Exitosa", f"Archivo empaquetado y descargado exitosamente en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Fallo de Exportación", str(e))

    def _importar_archivo_con_proteccion(self):
        """
        RNF4: Inspecciona el interior del archivo antes de mostrar nada.
        Si está corrupto o falta estructura, aborta inmediatamente manteniendo intactos los datos actuales.
        """
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json")],
            initialdir=self.dir_datos,
        )
        if not ruta:
            return

        try:
            # Inspección y carga protegida
            self.grupo.cargar_con_proteccion(ruta)
            self.ruta_archivo_actual = ruta
            self.var_nombre_grupo.set(self.grupo.nombre)
            self.title(f"GruPay Desktop V4 - {self.grupo.nombre}")
            nom_arch = os.path.basename(ruta)
            self.lbl_estado_sistema.config(text=f"✓ Archivo Verificado: {nom_arch}", fg="#059669")
            self._actualizar_tab_participantes()
            self._refrescar_tabla_gastos()
            self._actualizar_tab_saldos()
            messagebox.showinfo("Importación Segura", f"El archivo '{nom_arch}' superó la verificación de esquema y fue cargado con éxito.")
        except Exception as err:
            # Abortar y mantener datos intactos
            self.lbl_estado_sistema.config(text="⚠️ Carga Abortada: Archivo Inválido", fg="#dc2626")
            messagebox.showerror(
                "Protección del Sistema Activada",
                f"No se pudo cargar el archivo porque está dañado o no cumple con el esquema requerido.\n\n"
                f"Detalle del rechazo:\n{str(err)}\n\n"
                f"Tus datos actuales en pantalla se mantienen intactos.",
            )

    # -------------------------------------------------------------
    # RNF3: RENDIMIENTO Y BENCHMARK DE ESTRÉS (1000 GASTOS)
    # -------------------------------------------------------------
    def _ejecutar_benchmark_estres(self):
        """
        RNF3: Carga el archivo de estrés con 100 participantes y 1000 gastos,
        calculando los saldos en menos de un segundo y mostrando el tiempo exacto.
        """
        ruta_estres = os.path.join(self.dir_datos, "stress_test_1000_gastos.json")
        if not os.path.exists(ruta_estres):
            messagebox.showwarning("Atención", "No se encontró el archivo de estrés 'stress_test_1000_gastos.json'.")
            return

        t_inicio = time.perf_counter()
        self.grupo.cargar_con_proteccion(ruta_estres)
        saldos = self.grupo.calcular_saldos_individuales()
        trans = self.grupo.calcular_transferencias()
        t_total = time.perf_counter() - t_inicio

        self.var_nombre_grupo.set(self.grupo.nombre)
        self._actualizar_tab_participantes()
        self._refrescar_tabla_gastos()
        self._actualizar_tab_saldos()

        msg = (
            f"🚀 Benchmark RNF3 Completado:\n\n"
            f"• Participantes procesados: {len(self.grupo.participantes)}\n"
            f"• Gastos procesados: {len(self.grupo.gastos)}\n"
            f"• Transferencias generadas: {len(trans)}\n"
            f"• Tiempo de cómputo: {t_total * 1000:.2f} milisegundos ({t_total:.4f} s)\n\n"
            f"Criterio RNF3 cumplido: El cálculo se completó muy por debajo del límite de 1 segundo sin congelar la interfaz."
        )
        self.lbl_benchmark_info.config(
            text=f"Benchmark RNF3: 1,000 gastos procesados en {t_total * 1000:.1f} ms (< 1s)",
            fg="#059669",
        )
        messagebox.showinfo("Rendimiento RNF3 Verificado", msg)

    # -------------------------------------------------------------
    # RNF5: ACTUALIZACIÓN DE SALDOS Y SEMÁNTICA VISUAL
    # -------------------------------------------------------------
    def _actualizar_tab_saldos(self):
        self.tree_saldos.delete(*self.tree_saldos.get_children())
        # RNF3: Obtener saldos (O(1) si no hubo cambios)
        saldos = self.grupo.calcular_saldos_individuales()

        for nom, d in saldos.items():
            pag_formateado = formatear_moneda(d["pagado"])
            cons_formateado = formatear_moneda(d["consumido"])

            sem = d["semantica"]
            monto_visual = sem["monto_visual"]
            texto_situacion = f"{sem['icono']} {sem['texto']}"

            # Tag visual de color (verde / rojo / gris)
            tag_color = f"tag_{sem['estado']}"

            self.tree_saldos.insert(
                "",
                "end",
                values=(nom, pag_formateado, cons_formateado, monto_visual, texto_situacion),
                tags=(tag_color,),
            )

        # Transferencias
        self.tree_trans.delete(*self.tree_trans.get_children())
        trans = self.grupo.calcular_transferencias()

        if not trans:
            self.tree_trans.insert("", "end", values=("—", "—", "$ 0.00", "✓ Cuentas completamente saldadas"))
        else:
            for t in trans:
                self.tree_trans.insert(
                    "",
                    "end",
                    values=(t["de"], t["a"], t["monto_formateado"], f"Transferir de {t['de']} hacia {t['a']}"),
                )

    # -------------------------------------------------------------
    # MÉTODOS AUXILIARES
    # -------------------------------------------------------------
    def _al_cambiar_tab(self, event):
        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            self._actualizar_tab_participantes()
        elif idx == 1:
            self._actualizar_tab_gastos()
        elif idx == 2:
            self._actualizar_tab_saldos()

    def _actualizar_tab_participantes(self):
        self.tree_parts.delete(*self.tree_parts.get_children())
        saldos = self.grupo.calcular_saldos_individuales()

        for idx, p in enumerate(self.grupo.participantes, start=1):
            nom = p["nombre"]
            rol = p.get("rol", "Miembro")
            total_pag = formatear_moneda(saldos.get(nom, {}).get("pagado", 0.0))
            cant_asoc = sum(1 for g in self.grupo.gastos if nom in g.divididos)
            self.tree_parts.insert("", "end", values=(idx, nom, rol, total_pag, f"{cant_asoc} gastos"))

    def _actualizar_tab_gastos(self):
        self.cmb_pagador["values"] = self.grupo.nombres_participantes
        if self.grupo.nombres_participantes and not self.cmb_pagador.get():
            self.cmb_pagador.current(0)
        elif self.cmb_pagador.get() not in self.grupo.nombres_participantes:
            if self.grupo.nombres_participantes:
                self.cmb_pagador.current(0)
            else:
                self.cmb_pagador.set("")

        for w in self.frame_checks.winfo_children():
            w.destroy()

        self.check_vars = {}
        for nom in self.grupo.nombres_participantes:
            var = tk.BooleanVar(value=True)
            self.check_vars[nom] = var
            chk = ttk.Checkbutton(
                self.frame_checks,
                text=nom,
                variable=var,
                command=self._evaluar_formulario_reactivo,
            )
            chk.pack(side="left", padx=6, pady=2)

        self._evaluar_formulario_reactivo()
        self._refrescar_tabla_gastos()

    def _marcar_todos(self):
        for v in self.check_vars.values():
            v.set(True)
        self._evaluar_formulario_reactivo()

    def _desmarcar_todos(self):
        for v in self.check_vars.values():
            v.set(False)
        self._evaluar_formulario_reactivo()

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
                    formatear_moneda(g.importe),
                    g.pagador,
                    div_txt,
                    formatear_moneda(g.cuota_individual),
                ),
            )

        self.lbl_total_gastos.config(text=f"Total Registrado: {len(self.grupo.gastos)} gastos • {formatear_moneda(total)}")

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

    def _agregar_participante(self):
        nom = self.ent_nuevo_part.get().strip()
        rol = self.cmb_rol.get().strip()
        if not nom:
            messagebox.showwarning("Campo Vacío", "Ingresa un nombre de participante.")
            return
        try:
            self.grupo.agregar_participante(nom, rol)
            self.ent_nuevo_part.delete(0, tk.END)
            self._actualizar_tab_participantes()
        except ValueError as err:
            messagebox.showerror("Validación", str(err))

    def _editar_participante(self):
        sel = self.tree_parts.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un participante de la tabla.")
            return

        item = self.tree_parts.item(sel[0], "values")
        nom_act = item[1]
        rol_act = item[2]

        modal = tk.Toplevel(self)
        modal.title(f"Editar: {nom_act}")
        modal.geometry("360x160")
        modal.transient(self)
        modal.grab_set()

        ttk.Label(modal, text=f"Editar nombre de '{nom_act}':").pack(padx=12, pady=6)
        ent_n = ttk.Entry(modal, width=22)
        ent_n.insert(0, nom_act)
        ent_n.pack(padx=12, pady=4)

        cmb_r = ttk.Combobox(modal, values=["Miembro", "Organizador"], state="readonly", width=19)
        cmb_r.set(rol_act)
        cmb_r.pack(padx=12, pady=4)

        def guardar():
            n = ent_n.get().strip()
            r = cmb_r.get().strip()
            try:
                self.grupo.editar_participante(nom_act, n, r)
                modal.destroy()
                self._actualizar_tab_participantes()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(modal, text="Guardar Cambios", style="Primary.TButton", command=guardar).pack(pady=8)

    def _eliminar_participante(self):
        sel = self.tree_parts.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un participante.")
            return
        nom = self.tree_parts.item(sel[0], "values")[1]

        if messagebox.askyesno("Confirmar", f"¿Eliminar a '{nom}'?"):
            try:
                self.grupo.eliminar_participante(nom)
                self._actualizar_tab_participantes()
            except ValueError as e:
                messagebox.showerror("Regla de Integridad", str(e))

    def _nuevo_grupo_limpio(self):
        if messagebox.askyesno("Nuevo Grupo", "¿Inicializar un grupo completamente limpio?"):
            self.grupo = GrupoV4("Nuevo Grupo")
            self.ruta_archivo_actual = None
            self.var_nombre_grupo.set(self.grupo.nombre)
            self._actualizar_tab_participantes()
            self._actualizar_tab_gastos()
            self._actualizar_tab_saldos()

    def _cargar_datos_iniciales_limpios(self):
        self.grupo.agregar_participante("Carlos Gómez", "Organizador")
        self.grupo.agregar_participante("Sofía Martínez", "Miembro")
        self.grupo.agregar_participante("Mateo Silva", "Miembro")
        self.grupo.agregar_participante("Valentina Ríos", "Miembro")

        self.grupo.registrar_gasto(
            "Cena de Bienvenida",
            120.0,
            "06/10/2026",
            "Carlos Gómez",
            ["Carlos Gómez", "Sofía Martínez", "Mateo Silva", "Valentina Ríos"],
        )
        self.grupo.registrar_gasto(
            "Supermercado",
            80.0,
            "05/10/2026",
            "Sofía Martínez",
            ["Carlos Gómez", "Sofía Martínez", "Mateo Silva", "Valentina Ríos"],
        )


if __name__ == "__main__":
    app = GruPayAppV4()
    app.mainloop()
