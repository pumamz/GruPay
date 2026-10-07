"""
Suite de Pruebas Automatizadas - GruPay V4
Valida el cumplimiento estricto de los 5 Requerimientos No Funcionales (RNF):
- RNF1: Autoformato decimal onBlur ('15' -> '15.00') y bloqueo de caracteres no numéricos.
- RNF2: Bloqueo de registros incompletos (sin fecha o concepto).
- RNF3: Rendimiento O(N) con 100 participantes y 1000 gastos en < 1.0 segundo y memoización.
- RNF4: Exportación protegida y aborto inmediato ante archivos corruptos preservando datos actuales.
- RNF5: Semántica visual (Verde: recibe / Rojo: debe sin signo menos / Gris: saldado).
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core import (
    GrupoV4,
    autoformatear_monto_texto,
    es_caracter_monto_permitido,
    formatear_moneda,
    validar_esquema_archivo,
    validar_fecha_estricta,
)


class TestGruPayV4(unittest.TestCase):

    # --- RNF1: FORMATO MONETARIO Y AUTOFORMATO DECIMAL ---
    def test_rnf1_autoformato_decimal(self):
        """Verifica que '15' se convierta en '15.00' y '50' en '50.00'."""
        self.assertEqual(autoformatear_monto_texto("15"), "15.00")
        self.assertEqual(autoformatear_monto_texto("50"), "50.00")
        self.assertEqual(autoformatear_monto_texto("120.5"), "120.50")
        self.assertEqual(autoformatear_monto_texto("$99"), "99.00")

    def test_rnf1_rechazo_letras_y_negativos_en_tiempo_real(self):
        """Bloquea activamente letras y signos negativos al teclear."""
        # Caracteres no permitidos
        self.assertFalse(es_caracter_monto_permitido("-", "-20"))
        self.assertFalse(es_caracter_monto_permitido("a", "15a"))
        self.assertFalse(es_caracter_monto_permitido("+", "+10"))
        self.assertFalse(es_caracter_monto_permitido(" ", " 5"))

        # Caracteres permitidos
        self.assertTrue(es_caracter_monto_permitido("5", "15"))
        self.assertTrue(es_caracter_monto_permitido(".", "15."))
        self.assertTrue(es_caracter_monto_permitido("0", "15.00"))
        self.assertFalse(es_caracter_monto_permitido("5", "15.005"))  # Máximo 2 decimales

    def test_rnf1_formato_monetario_miles(self):
        """Aplica separador de miles y dos decimales obligatorios."""
        self.assertEqual(formatear_moneda(1250.5), "$ 1,250.50")
        self.assertEqual(formatear_moneda(50), "$ 50.00")
        self.assertEqual(formatear_moneda(1000000), "$ 1,000,000.00")

    # --- RNF2: BLOQUEO DE REGISTROS INCOMPLETOS ---
    def test_rnf2_bloqueo_registros_incompletos(self):
        """Es imposible registrar un gasto sin fecha, sin concepto o con importe <= 0."""
        grupo = GrupoV4("Prueba RNF2")
        grupo.agregar_participante("Ana")

        # Sin concepto
        with self.assertRaises(ValueError):
            grupo.registrar_gasto("", 50.0, "06/10/2026", "Ana", ["Ana"])

        # Sin fecha o fecha inválida
        with self.assertRaises(ValueError):
            grupo.registrar_gasto("Cena", 50.0, "", "Ana", ["Ana"])
        with self.assertRaises(ValueError):
            grupo.registrar_gasto("Cena", 50.0, "fecha_invalida", "Ana", ["Ana"])

        # Importe <= 0
        with self.assertRaises(ValueError):
            grupo.registrar_gasto("Cena", 0.0, "06/10/2026", "Ana", ["Ana"])
        with self.assertRaises(ValueError):
            grupo.registrar_gasto("Cena", -20.0, "06/10/2026", "Ana", ["Ana"])

        # Sin personas para dividir
        with self.assertRaises(ValueError):
            grupo.registrar_gasto("Cena", 50.0, "06/10/2026", "Ana", [])

    # --- RNF3: RENDIMIENTO MASIVO (STRESS TEST) Y MEMOIZACIÓN ---
    def test_rnf3_rendimiento_estres_1000_gastos_menor_un_segundo(self):
        """
        Carga el archivo de estrés con 100 participantes y 1000 gastos.
        El cálculo completo de saldos y transferencias debe ejecutarse en MENOS de 1.0 segundo.
        """
        ruta_estres = "v4/datos/stress_test_1000_gastos.json"
        self.assertTrue(os.path.exists(ruta_estres), "No se encontró el archivo de estrés.")

        grupo = GrupoV4()
        t_inicio_carga = time.perf_counter()
        grupo.cargar_con_proteccion(ruta_estres)
        t_fin_carga = time.perf_counter()

        self.assertEqual(len(grupo.participantes), 100)
        self.assertEqual(len(grupo.gastos), 1000)

        # Medir tiempo de cálculo de balances
        t_inicio_calculo = time.perf_counter()
        saldos = grupo.calcular_saldos_individuales()
        transferencias = grupo.calcular_transferencias()
        t_fin_calculo = time.perf_counter()

        duracion_calculo = t_fin_calculo - t_inicio_calculo

        # Criterio RNF3: < 1.0 segundo (suele completarse en < 0.010 s)
        self.assertLess(
            duracion_calculo,
            1.0,
            f"El cálculo de 1000 gastos tardó {duracion_calculo:.4f}s, superando el límite de 1 segundo.",
        )

        # Regla matemática: sumatoria de saldos = 0
        total_balance = sum(d["saldo"] for d in saldos.values())
        self.assertAlmostEqual(total_balance, 0.0, places=1)

    def test_rnf3_memoizacion_cache_sin_recalculo(self):
        """Verifica que llamadas sucesivas a calcular_saldos no recalculen si no hay cambios."""
        grupo = GrupoV4("Cache Test")
        grupo.agregar_participante("Carlos")
        grupo.agregar_participante("Sofía")
        grupo.registrar_gasto("Cena", 100.0, "06/10/2026", "Carlos", ["Carlos", "Sofía"])

        saldos_1 = grupo.calcular_saldos_individuales()
        # Segunda llamada inmediata: debe devolver el mismo objeto de caché en O(1)
        saldos_2 = grupo.calcular_saldos_individuales()
        self.assertIs(saldos_1, saldos_2)

    # --- RNF4: PROTECCIÓN ANTE ARCHIVOS CORRUPTOS ---
    def test_rnf4_proteccion_sistema_archivo_corrupto_abortar(self):
        """
        Si se intenta cargar un archivo corrupto, el sistema aborta inmediatamente,
        mantiene intactos los datos actuales que el usuario estaba viendo y no los corrompe.
        """
        grupo = GrupoV4("Grupo Seguro Actual")
        grupo.agregar_participante("Usuario A")
        grupo.agregar_participante("Usuario B")

        estado_original_nombres = list(grupo.nombres_participantes)
        nombre_original = grupo.nombre

        ruta_corrupta = "v4/datos/archivo_corrupto_prueba.json"
        self.assertTrue(os.path.exists(ruta_corrupta))

        # Debe lanzar ValueError advirtiendo el fallo de esquema
        with self.assertRaises(ValueError) as ctx:
            grupo.cargar_con_proteccion(ruta_corrupta)

        self.assertIn("Protección del Sistema activada", str(ctx.exception))

        # PROTECCIÓN: Los datos que el usuario estaba viendo permanecen 100% INTACTOS
        self.assertEqual(grupo.nombre, nombre_original)
        self.assertEqual(grupo.nombres_participantes, estado_original_nombres)
        self.assertEqual(len(grupo.gastos), 0)

    # --- RNF5: SEMÁNTICA VISUAL Y ESTADOS FINANCIEROS ---
    def test_rnf5_semantica_visual_estados_financieros(self):
        """
        Verifica:
        - Saldo positivo: Color verde, texto 'Recibe dinero', ícono '▲ (+)', cifra positiva.
        - Saldo negativo: Color rojo, texto 'Debe dinero', ícono '▼ (-)', sin signo menos.
        - Saldo cero: Tono gris, texto 'Cuentas saldadas', ícono '✓'.
        """
        # Saldo positivo (+50.00)
        pos = GrupoV4.interpretar_estado_financiero(50.00)
        self.assertEqual(pos["estado"], "positivo")
        self.assertEqual(pos["color"], "#059669")
        self.assertEqual(pos["texto"], "Recibe dinero")
        self.assertEqual(pos["monto_visual"], "$ 50.00")
        self.assertIn("▲", pos["icono"])

        # Saldo negativo (-30.00)
        neg = GrupoV4.interpretar_estado_financiero(-30.00)
        self.assertEqual(neg["estado"], "negativo")
        self.assertEqual(neg["color"], "#dc2626")
        self.assertEqual(neg["texto"], "Debe dinero")
        # Omitir el signo menos en el número para no confundir (RNF5)
        self.assertEqual(neg["monto_visual"], "$ 30.00")
        self.assertNotIn("-", neg["monto_visual"])
        self.assertIn("▼", neg["icono"])

        # Saldo cero (0.00)
        cero = GrupoV4.interpretar_estado_financiero(0.00)
        self.assertEqual(cero["estado"], "cero")
        self.assertEqual(cero["color"], "#64748b")
        self.assertEqual(cero["texto"], "Cuentas saldadas")
        self.assertIn("✓", cero["icono"])


if __name__ == "__main__":
    unittest.main()
