"""
Suite de Pruebas Unitarias Automatizadas - GruPay V2
Valida estrictamente los Criterios de Aceptación de la Fase 4 y Mejoras de V2:
1. Prueba de Grupo: "Prueba 2026" mantiene su nombre sin volver a "Nuevo Grupo".
2. Prueba de Cálculos: $100 entre 4 personas = exactamente $25.00 c/u.
3. Prueba de Balances: Persona A +$75.00, las otras tres -$25.00.
4. Prueba de Archivos: Saneamiento de "Viaje a la playa / 2026??" a "Viaje_a_la_playa_2026.json".
5. Prueba de Edición: Cambio de nombre con gastos asociados actualiza saldos sin perder deudas.
6. Pruebas de Saneamiento y Validación con Regex.
7. Prueba de Gestión de Múltiples Grupos (GestorMultiGrupos).
"""

import os
import shutil
import tempfile
import unittest

from core import (
    GestorMultiGrupos,
    Grupo,
    sanitizar_nombre_archivo,
    sanitizar_texto,
)


class TestGruPayV2(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # --- CRITERIO 1: PRUEBA DE GRUPO ---
    def test_criterio_1_nombre_grupo_persiste(self):
        """Crear grupo 'Prueba 2026' y verificar que al guardar y recargar el nombre se mantenga."""
        grupo = Grupo("Prueba 2026")
        grupo.agregar_participante("Ana")
        self.assertEqual(grupo.nombre, "Prueba 2026")

        ruta_guardado = grupo.guardar_en_directorio(self.temp_dir)
        self.assertTrue(os.path.exists(ruta_guardado))

        # Recargar en una nueva instancia
        grupo_cargado = Grupo("Nuevo Grupo")
        grupo_cargado.cargar_desde_archivo(ruta_guardado)

        # Verificar que NO vuelve a "Nuevo Grupo"
        self.assertEqual(grupo_cargado.nombre, "Prueba 2026")
        self.assertNotEqual(grupo_cargado.nombre, "Nuevo Grupo")

    # --- CRITERIO 2: PRUEBA DE CÁLCULOS ---
    def test_criterio_2_calculo_cuota_equitativa(self):
        """Gasto de $100 pagado por Persona A, dividido entre 4 personas -> cuota exactamente $25 c/u."""
        grupo = Grupo("Grupo Cálculo")
        for p in ["Persona A", "Persona B", "Persona C", "Persona D"]:
            grupo.agregar_participante(p)

        gasto = grupo.registrar_gasto(
            concepto="Almuerzo",
            importe=100.0,
            fecha="2026-10-06",
            pagador="Persona A",
            divididos=["Persona A", "Persona B", "Persona C", "Persona D"],
        )

        self.assertEqual(gasto.cuota_individual, 25.0)

    # --- CRITERIO 3: PRUEBA DE BALANCES ---
    def test_criterio_3_balances_exactos(self):
        """Persona A: saldo neto +$75.00; Persona B, C, D: saldo neto -$25.00 cada uno."""
        grupo = Grupo("Grupo Balance")
        for p in ["Persona A", "Persona B", "Persona C", "Persona D"]:
            grupo.agregar_participante(p)

        grupo.registrar_gasto(
            concepto="Almuerzo",
            importe=100.0,
            fecha="2026-10-06",
            pagador="Persona A",
            divididos=["Persona A", "Persona B", "Persona C", "Persona D"],
        )

        saldos = grupo.calcular_saldos_individuales()

        # Persona A (Pagó 100, consumió 25 -> Saldo +75)
        self.assertEqual(saldos["Persona A"]["pagado"], 100.0)
        self.assertEqual(saldos["Persona A"]["consumido"], 25.0)
        self.assertEqual(saldos["Persona A"]["saldo"], 75.0)

        # Personas B, C, D (Pagaron 0, consumieron 25 -> Saldo -25)
        for p in ["Persona B", "Persona C", "Persona D"]:
            self.assertEqual(saldos[p]["pagado"], 0.0)
            self.assertEqual(saldos[p]["consumido"], 25.0)
            self.assertEqual(saldos[p]["saldo"], -25.0)

        # Suma neta debe ser exactamente 0
        total_saldos = sum(d["saldo"] for d in saldos.values())
        self.assertAlmostEqual(total_saldos, 0.0, places=2)

    # --- CRITERIO 4: PRUEBA DE ARCHIVOS (SANEAMIENTO) ---
    def test_criterio_4_saneamiento_nombre_archivo(self):
        """Guardar grupo 'Viaje a la playa / 2026??' sanea el nombre a 'Viaje_a_la_playa_2026.json'."""
        nombre_original = "Viaje a la playa / 2026??"
        nombre_archivo = sanitizar_nombre_archivo(nombre_original)
        self.assertEqual(nombre_archivo, "Viaje_a_la_playa_2026.json")

        grupo = Grupo(nombre_original)
        grupo.agregar_participante("Carlos")
        ruta = grupo.guardar_en_directorio(self.temp_dir)

        self.assertTrue(os.path.exists(ruta))
        self.assertTrue(ruta.endswith("Viaje_a_la_playa_2026.json"))

    # --- CRITERIO 5: PRUEBA DE EDICIÓN EN CASCADA ---
    def test_criterio_5_edicion_participante_en_cascada(self):
        """Cambiar nombre de un participante con gastos actualiza saldos sin perder deudas."""
        grupo = Grupo("Grupo Edición")
        grupo.agregar_participante("Carlos")
        grupo.agregar_participante("Sofía")

        # Carlos paga 100 dividido entre Carlos y Sofía ($50 c/u)
        grupo.registrar_gasto("Cena", 100.0, "2026-10-06", "Carlos", ["Carlos", "Sofía"])

        # Editar Carlos -> Carlos Gómez
        grupo.editar_participante("Carlos", "Carlos Gómez", nuevo_rol="Organizador")

        # Verificar lista de participantes
        self.assertIn("Carlos Gómez", grupo.nombres_participantes)
        self.assertNotIn("Carlos", grupo.nombres_participantes)

        # Verificar actualización en cascada en el gasto
        gasto = grupo.gastos[0]
        self.assertEqual(gasto.pagador, "Carlos Gómez")
        self.assertIn("Carlos Gómez", gasto.divididos)
        self.assertNotIn("Carlos", gasto.divididos)

        # Verificar saldos
        saldos = grupo.calcular_saldos_individuales()
        self.assertIn("Carlos Gómez", saldos)
        self.assertEqual(saldos["Carlos Gómez"]["saldo"], 50.0)
        self.assertEqual(saldos["Sofía"]["saldo"], -50.0)

    # --- VALIDACIONES Y SANEAMIENTO REGEX ---
    def test_saneamiento_caracteres_especiales(self):
        """Verifica que sanitizar_texto bloquee o elimine caracteres < > { } [ ]."""
        texto_inseguro = "Cena <script> {importante} [vip]"
        texto_limpio = sanitizar_texto(texto_inseguro)
        self.assertEqual(texto_limpio, "Cena script importante vip")

        with self.assertRaises(ValueError):
            sanitizar_texto("<>{}[ ]")

    def test_validaciones_estrictas_campos_obligatorios(self):
        """Importes <= 0 o divididos vacíos deben lanzar error."""
        grupo = Grupo("Validaciones")
        grupo.agregar_participante("Lucas")

        # Importe 0 o negativo
        with self.assertRaises(ValueError):
            grupo.registrar_gasto("Gasto 0", 0.0, "2026-10-06", "Lucas", ["Lucas"])
        with self.assertRaises(ValueError):
            grupo.registrar_gasto("Gasto Negativo", -50.0, "2026-10-06", "Lucas", ["Lucas"])

        # Sin beneficiarios
        with self.assertRaises(ValueError):
            grupo.registrar_gasto("Gasto Vacio", 50.0, "2026-10-06", "Lucas", [])

    # --- GESTIÓN DE MÚLTIPLES GRUPOS ---
    def test_gestor_multi_grupos(self):
        """Comprueba el escaneo y listado de múltiples grupos en el directorio."""
        g1 = Grupo("Grupo Vacaciones")
        g1.agregar_participante("Ana")
        g1.guardar_en_directorio(self.temp_dir)

        g2 = Grupo("Piso Compartido")
        g2.agregar_participante("Bruno")
        g2.guardar_en_directorio(self.temp_dir)

        gestor = GestorMultiGrupos(self.temp_dir)
        lista = gestor.listar_grupos()
        self.assertEqual(len(lista), 2)
        nombres = [item["nombre"] for item in lista]
        self.assertIn("Grupo Vacaciones", nombres)
        self.assertIn("Piso Compartido", nombres)

    # --- AUDITORÍA DE PAGOS REALES ---
    def test_auditoria_pagos_individuales(self):
        grupo = Grupo("Auditoría")
        grupo.agregar_participante("Mario")
        grupo.agregar_participante("Luigi")

        grupo.registrar_gasto("Gasto 1", 30.0, "2026-10-01", "Mario", ["Mario", "Luigi"])
        grupo.registrar_gasto("Gasto 2", 70.0, "2026-10-02", "Mario", ["Mario", "Luigi"])

        auditoria = grupo.obtener_auditoria_pagos()
        self.assertEqual(auditoria["Mario"]["total_pagado"], 100.0)
        self.assertEqual(auditoria["Mario"]["cantidad_gastos_pagados"], 2)
        self.assertEqual(auditoria["Luigi"]["total_pagado"], 0.0)


if __name__ == "__main__":
    unittest.main()
