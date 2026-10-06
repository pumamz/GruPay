"""
Suite de Pruebas Unitarias Automatizadas - GruPay V1
Valida estrictamente los Requisitos Funcionales del 1 al 10 (RF1 a RF10).
"""

import os
import tempfile
import unittest

from core import Grupo, Gasto


class TestGruPayV1(unittest.TestCase):

    def setUp(self):
        """Inicializa un grupo fresco con datos base para cada prueba."""
        self.grupo = Grupo("Viaje a la Playa")
        self.grupo.agregar_participante("Carlos")
        self.grupo.agregar_participante("Sofía")
        self.grupo.agregar_participante("Mateo")
        self.grupo.agregar_participante("Valentina")

    # RF1: Crear un grupo de participantes
    def test_rf1_crear_grupo(self):
        g = Grupo("Casa Compartida")
        self.assertEqual(g.nombre, "Casa Compartida")
        self.assertEqual(len(g.participantes), 0)
        self.assertEqual(len(g.gastos), 0)

        # Reiniciar grupo
        g.reiniciar_grupo("Vacaciones 2026")
        self.assertEqual(g.nombre, "Vacaciones 2026")

        # Nombre no válido
        with self.assertRaises(ValueError):
            g.reiniciar_grupo("")

    # RF2: Agregar, editar y eliminar participantes
    def test_rf2_agregar_editar_eliminar_participante(self):
        # Agregar
        self.grupo.agregar_participante("Lucas")
        self.assertIn("Lucas", self.grupo.participantes)

        # No permitir duplicados
        with self.assertRaises(ValueError):
            self.grupo.agregar_participante("Carlos")

        # No permitir nombres vacíos
        with self.assertRaises(ValueError):
            self.grupo.agregar_participante("   ")

        # Editar participante
        self.grupo.editar_participante("Lucas", "Lucas Gómez")
        self.assertIn("Lucas Gómez", self.grupo.participantes)
        self.assertNotIn("Lucas", self.grupo.participantes)

        # Eliminar participante sin gastos
        self.grupo.eliminar_participante("Lucas Gómez")
        self.assertNotIn("Lucas Gómez", self.grupo.participantes)

        # Registrar gasto y probar que no se puede eliminar si tiene gastos
        self.grupo.registrar_gasto("Cena", 100.0, "2026-10-06", "Carlos", ["Carlos", "Sofía"])
        with self.assertRaises(ValueError):
            self.grupo.eliminar_participante("Carlos")
        with self.assertRaises(ValueError):
            self.grupo.eliminar_participante("Sofía")

    # RF3: Registrar gastos con concepto, importe y fecha
    def test_rf3_registrar_gastos(self):
        gasto = self.grupo.registrar_gasto(
            concepto="Alquiler Cabaña",
            importe=400.0,
            fecha="2026-10-01",
            pagador="Carlos",
            divididos=["Carlos", "Sofía", "Mateo", "Valentina"],
        )
        self.assertEqual(gasto.concepto, "Alquiler Cabaña")
        self.assertEqual(gasto.importe, 400.0)
        self.assertEqual(gasto.fecha, "2026-10-01")
        self.assertEqual(len(self.grupo.gastos), 1)

        # Validaciones de error
        with self.assertRaises(ValueError):
            self.grupo.registrar_gasto("", 50.0, "2026-10-01", "Carlos", ["Carlos"])
        with self.assertRaises(ValueError):
            self.grupo.registrar_gasto("Peaje", -10.0, "2026-10-01", "Carlos", ["Carlos"])
        with self.assertRaises(ValueError):
            self.grupo.registrar_gasto("Peaje", 0.0, "2026-10-01", "Carlos", ["Carlos"])

    # RF4: Indicar quién pagó cada gasto
    def test_rf4_indicar_quien_pago(self):
        gasto = self.grupo.registrar_gasto("Supermercado", 80.0, "2026-10-02", "Sofía", ["Sofía", "Mateo"])
        self.assertEqual(gasto.pagador, "Sofía")

        # Pagador inexistente
        with self.assertRaises(ValueError):
            self.grupo.registrar_gasto("Bebidas", 20.0, "2026-10-02", "Pedro", ["Sofía"])

    # RF5: Seleccionar entre quiénes se divide
    def test_rf5_seleccionar_entre_quienes_se_divide(self):
        gasto = self.grupo.registrar_gasto(
            concepto="Actividad Acuática",
            importe=60.0,
            fecha="2026-10-03",
            pagador="Valentina",
            divididos=["Mateo", "Valentina"],
        )
        self.assertEqual(set(gasto.divididos), {"Mateo", "Valentina"})
        self.assertNotIn("Carlos", gasto.divididos)
        self.assertNotIn("Sofía", gasto.divididos)

        # Participante inexistente en divididos
        with self.assertRaises(ValueError):
            self.grupo.registrar_gasto("Snacks", 10.0, "2026-10-03", "Valentina", ["Carlos", "Fantasma"])

    # RF6: Dividir el importe en partes iguales
    def test_rf6_dividir_importe_partes_iguales(self):
        gasto = self.grupo.registrar_gasto(
            concepto="Cena Pizza",
            importe=120.0,
            fecha="2026-10-04",
            pagador="Carlos",
            divididos=["Carlos", "Sofía", "Mateo", "Valentina"],
        )
        # 120 / 4 = 30.00
        self.assertEqual(gasto.cuota_individual, 30.0)

        gasto2 = self.grupo.registrar_gasto(
            concepto="Taxis",
            importe=50.0,
            fecha="2026-10-04",
            pagador="Sofía",
            divididos=["Sofía", "Valentina"],
        )
        # 50 / 2 = 25.00
        self.assertEqual(gasto2.cuota_individual, 25.0)

    # RF7: Mostrar cuánto pagó cada persona
    def test_rf7_mostrar_cuanto_pago_cada_persona(self):
        self.grupo.registrar_gasto("Gasto 1", 100.0, "2026-10-01", "Carlos", ["Carlos", "Sofía"])
        self.grupo.registrar_gasto("Gasto 2", 80.0, "2026-10-02", "Carlos", ["Mateo", "Valentina"])
        self.grupo.registrar_gasto("Gasto 3", 50.0, "2026-10-03", "Sofía", ["Sofía", "Valentina"])

        totales = self.grupo.calcular_totales_pagados()
        self.assertEqual(totales["Carlos"], 180.0)
        self.assertEqual(totales["Sofía"], 50.0)
        self.assertEqual(totales["Mateo"], 0.0)
        self.assertEqual(totales["Valentina"], 0.0)

    # RF8: Calcular los saldos individuales
    def test_rf8_calcular_saldos_individuales(self):
        # Carlos paga 120 para los 4 (cuota 30 c/u)
        self.grupo.registrar_gasto("Cena", 120.0, "2026-10-01", "Carlos", ["Carlos", "Sofía", "Mateo", "Valentina"])
        # Sofía paga 80 para los 4 (cuota 20 c/u)
        self.grupo.registrar_gasto("Súper", 80.0, "2026-10-02", "Sofía", ["Carlos", "Sofía", "Mateo", "Valentina"])
        # Valentina paga 60 para los 4 (cuota 15 c/u)
        self.grupo.registrar_gasto("Peajes", 60.0, "2026-10-03", "Valentina", ["Carlos", "Sofía", "Mateo", "Valentina"])
        # Mateo no pagó nada

        # Cuota total por persona: 30 + 20 + 15 = 65.0
        # Carlos: pagó 120, debe 65 -> saldo +55.0
        # Sofía: pagó 80, debe 65 -> saldo +15.0
        # Valentina: pagó 60, debe 65 -> saldo -5.0
        # Mateo: pagó 0, debe 65 -> saldo -65.0
        saldos = self.grupo.calcular_saldos_individuales()

        self.assertEqual(saldos["Carlos"]["pagado"], 120.0)
        self.assertEqual(saldos["Carlos"]["consumido"], 65.0)
        self.assertEqual(saldos["Carlos"]["saldo"], 55.0)

        self.assertEqual(saldos["Sofía"]["pagado"], 80.0)
        self.assertEqual(saldos["Sofía"]["consumido"], 65.0)
        self.assertEqual(saldos["Sofía"]["saldo"], 15.0)

        self.assertEqual(saldos["Valentina"]["pagado"], 60.0)
        self.assertEqual(saldos["Valentina"]["consumido"], 65.0)
        self.assertEqual(saldos["Valentina"]["saldo"], -5.0)

        self.assertEqual(saldos["Mateo"]["pagado"], 0.0)
        self.assertEqual(saldos["Mateo"]["consumido"], 65.0)
        self.assertEqual(saldos["Mateo"]["saldo"], -65.0)

        # Regla fundamental: suma de saldos netos = 0
        suma_saldos = sum(d["saldo"] for d in saldos.values())
        self.assertAlmostEqual(suma_saldos, 0.0, places=2)

    # RF9: Proponer transferencias para cancelar deudas
    def test_rf9_proponer_transferencias_cancelar_deudas(self):
        # Carlos pagó 120 (a favor +55)
        self.grupo.registrar_gasto("Cena", 120.0, "2026-10-01", "Carlos", ["Carlos", "Sofía", "Mateo", "Valentina"])
        # Sofía pagó 80 (a favor +15)
        self.grupo.registrar_gasto("Súper", 80.0, "2026-10-02", "Sofía", ["Carlos", "Sofía", "Mateo", "Valentina"])
        # Valentina pagó 60 (en contra -5)
        self.grupo.registrar_gasto("Peajes", 60.0, "2026-10-03", "Valentina", ["Carlos", "Sofía", "Mateo", "Valentina"])
        # Mateo pagó 0 (en contra -65)

        transferencias = self.grupo.calcular_transferencias()
        self.assertTrue(len(transferencias) > 0)

        # Validar que las transferencias compensan exactamente las deudas
        balances_simulados = {p: saldos["saldo"] for p, saldos in self.grupo.calcular_saldos_individuales().items()}
        for t in transferencias:
            balances_simulados[t["de"]] += t["monto"]
            balances_simulados[t["a"]] -= t["monto"]

        for persona, balance in balances_simulados.items():
            self.assertAlmostEqual(balance, 0.0, places=2, msg=f"El balance de {persona} no quedó en 0.")

    # RF10: Guardar y recuperar la información del grupo
    def test_rf10_guardar_y_recuperar_informacion(self):
        self.grupo.registrar_gasto("Gasto Prueba", 150.0, "2026-10-05", "Carlos", ["Carlos", "Sofía"])

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Guardar
            self.grupo.guardar_en_archivo(tmp_path)
            self.assertTrue(os.path.exists(tmp_path))

            # Recuperar en un nuevo grupo
            nuevo_grupo = Grupo("Temp")
            nuevo_grupo.cargar_desde_archivo(tmp_path)

            self.assertEqual(nuevo_grupo.nombre, "Viaje a la Playa")
            self.assertEqual(len(nuevo_grupo.participantes), 4)
            self.assertEqual(len(nuevo_grupo.gastos), 1)
            self.assertEqual(nuevo_grupo.gastos[0].concepto, "Gasto Prueba")
            self.assertEqual(nuevo_grupo.gastos[0].importe, 150.0)
            self.assertEqual(nuevo_grupo.gastos[0].pagador, "Carlos")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
