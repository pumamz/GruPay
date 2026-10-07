"""
Suite de Pruebas Unitarias Automatizadas - GruPay V3
Valida exhaustivamente las Fases 1 a 5 de la Versión 3:
1. Inicio en blanco sin datos mock.
2. Cambio de grupo con limpieza e hidratación total de estado.
3. Regla de Administrador Único (exclusividad de rol).
4. Regla de Integridad en eliminación de participantes.
5. Validación estricta de fechas (DD/MM/AAAA).
6. Formateador numérico estricto de importes (positivos, máx 2 decimales).
7. Desglose equitativo específico por gasto para máxima transparencia.
8. Persistencia y sincronización directa JSON.
"""

import os
import shutil
import tempfile
import unittest

from core import (
    GestorMultiGruposV3,
    Grupo,
    sanitizar_texto,
    validar_fecha,
    validar_importe,
)


class TestGruPayV3(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # --- FASE 1: INICIALIZACIÓN EN BLANCO Y CAMBIO DE GRUPO LIMPIO ---
    def test_fase1_inicializacion_estrictamente_vacia(self):
        """Verifica que un grupo nuevo inicie 100% en blanco sin datos mock o precargados."""
        grupo = Grupo("Grupo Limpio")
        self.assertEqual(len(grupo.participantes), 0)
        self.assertEqual(len(grupo.gastos), 0)
        self.assertEqual(grupo.nombres_participantes, [])

    def test_fase1_cambio_de_grupo_limpia_e_hidrata_estado(self):
        """Al cargar un grupo nuevo, el estado previo se limpia totalmente sin arrastrar datos."""
        # Grupo 1 con 2 personas y 1 gasto
        g1 = Grupo("Grupo 1")
        g1.agregar_participante("Ana", "Organizador")
        g1.agregar_participante("Beto", "Miembro")
        g1.registrar_gasto("Gasto 1", 50.0, "01/10/2026", "Ana", ["Ana", "Beto"])
        ruta1 = os.path.join(self.temp_dir, "grupo1.json")
        g1.guardar_en_archivo(ruta1)

        # Grupo 2 con 1 persona y 0 gastos
        g2 = Grupo("Grupo 2")
        g2.agregar_participante("Carlos", "Organizador")
        ruta2 = os.path.join(self.temp_dir, "grupo2.json")
        g2.guardar_en_archivo(ruta2)

        # Instancia activa que carga Grupo 1 y luego cambia a Grupo 2
        app_grupo = Grupo()
        app_grupo.cargar_desde_archivo(ruta1)
        self.assertEqual(app_grupo.nombre, "Grupo 1")
        self.assertEqual(len(app_grupo.participantes), 2)
        self.assertEqual(len(app_grupo.gastos), 1)

        # Cambiar a Grupo 2: debe limpiarse completamente
        app_grupo.cargar_desde_archivo(ruta2)
        self.assertEqual(app_grupo.nombre, "Grupo 2")
        self.assertEqual(len(app_grupo.participantes), 1)
        self.assertEqual(app_grupo.nombres_participantes, ["Carlos"])
        self.assertEqual(len(app_grupo.gastos), 0)
        self.assertNotIn("Ana", app_grupo.nombres_participantes)

    # --- FASE 2: ADMINISTRADOR ÚNICO Y REGLA DE INTEGRIDAD ---
    def test_fase2_administrador_unico_al_agregar(self):
        """Al asignar el rol Organizador a un nuevo miembro, se le quita al que lo tenía previamente."""
        grupo = Grupo("Regla Admin")
        grupo.agregar_participante("Carlos", "Organizador")
        self.assertEqual(grupo.participantes[0]["rol"], "Organizador")

        # Agregar a Sofía como Organizador -> Carlos debe pasar a Miembro
        grupo.agregar_participante("Sofía", "Organizador")
        roles = {p["nombre"]: p["rol"] for p in grupo.participantes}
        self.assertEqual(roles["Sofía"], "Organizador")
        self.assertEqual(roles["Carlos"], "Miembro")

        # Verificar que solo hay 1 Organizador
        total_admins = sum(1 for p in grupo.participantes if p["rol"] == "Organizador")
        self.assertEqual(total_admins, 1)

    def test_fase2_administrador_unico_al_editar(self):
        """Al editar un miembro y volverlo Organizador, el administrador anterior pasa a Miembro."""
        grupo = Grupo("Regla Admin Edit")
        grupo.agregar_participante("Carlos", "Organizador")
        grupo.agregar_participante("Mateo", "Miembro")

        grupo.editar_participante("Mateo", "Mateo", nuevo_rol="Organizador")
        roles = {p["nombre"]: p["rol"] for p in grupo.participantes}
        self.assertEqual(roles["Mateo"], "Organizador")
        self.assertEqual(roles["Carlos"], "Miembro")

    def test_fase2_regla_de_integridad_bloqueo_eliminacion(self):
        """No permite eliminar un participante si tiene gastos asociados (como pagador o en divididos)."""
        grupo = Grupo("Integridad")
        grupo.agregar_participante("Carlos")
        grupo.agregar_participante("Sofía")
        grupo.agregar_participante("Lucas")  # Lucas no tiene gastos

        grupo.registrar_gasto("Cena", 60.0, "06/10/2026", "Carlos", ["Carlos", "Sofía"])

        # Intentar eliminar a Carlos (pagador) -> Bloqueado
        with self.assertRaises(ValueError) as ctx:
            grupo.eliminar_participante("Carlos")
        self.assertIn("Integridad Bloqueada", str(ctx.exception))

        # Intentar eliminar a Sofía (beneficiaria) -> Bloqueado
        with self.assertRaises(ValueError) as ctx:
            grupo.eliminar_participante("Sofía")
        self.assertIn("Integridad Bloqueada", str(ctx.exception))

        # Eliminar a Lucas (sin gastos) -> Permitido
        grupo.eliminar_participante("Lucas")
        self.assertNotIn("Lucas", grupo.nombres_participantes)

    # --- FASE 3: VALIDACIONES ESTRICTAS DE FECHA, IMPORTE Y CAMPOS VACÍOS ---
    def test_fase3_validacion_fechas_estricta(self):
        """Valida que la fecha requiera formato DD/MM/AAAA y calendario real."""
        # Válidas
        self.assertEqual(validar_fecha("06/10/2026"), "06/10/2026")
        self.assertEqual(validar_fecha("01/01/2025"), "01/01/2025")
        self.assertEqual(validar_fecha("28-02-2024"), "28/02/2024")

        # Inválidas
        with self.assertRaises(ValueError):
            validar_fecha("")
        with self.assertRaises(ValueError):
            validar_fecha("2026-10-06")  # Formato incorrecto AAAA-MM-DD
        with self.assertRaises(ValueError):
            validar_fecha("32/01/2026")  # Día imposible
        with self.assertRaises(ValueError):
            validar_fecha("15/13/2026")  # Mes imposible
        with self.assertRaises(ValueError):
            validar_fecha("fecha_invalida")

    def test_fase3_validacion_importes_estricta(self):
        """Solo valores numéricos positivos, máx 2 decimales, sin negativos ni caracteres alfabéticos."""
        # Válidos
        self.assertEqual(validar_importe("100"), 100.0)
        self.assertEqual(validar_importe("100.50"), 100.5)
        self.assertEqual(validar_importe("$45.99"), 45.99)
        self.assertEqual(validar_importe(120), 120.0)

        # Inválidos
        with self.assertRaises(ValueError):
            validar_importe("0")  # Cero no permitido
        with self.assertRaises(ValueError):
            validar_importe("-50")  # Negativos bloqueados
        with self.assertRaises(ValueError):
            validar_importe("100.555")  # Más de dos decimales
        with self.assertRaises(ValueError):
            validar_importe("abc")  # Letras
        with self.assertRaises(ValueError):
            validar_importe("")  # Vacío

    def test_fase3_bloqueo_campos_en_blanco(self):
        """Bloquea campos que contengan solo espacios en blanco o nulos."""
        with self.assertRaises(ValueError):
            sanitizar_texto("    ")
        with self.assertRaises(ValueError):
            sanitizar_texto("")

    # --- FASE 5: TABLA DE DIVISIÓN ESPECÍFICA Y DESGLOSE EQUITATIVO ---
    def test_fase5_desglose_equitativo_transparente(self):
        """Verifica la generación explícita del desglose de división por gasto."""
        grupo = Grupo("Desglose Específico")
        grupo.agregar_participante("Carlos")
        grupo.agregar_participante("Sofía")
        grupo.agregar_participante("Mateo")

        # Gasto de 120 pagado por Carlos entre Carlos, Sofía y Mateo a $40 c/u
        gasto = grupo.registrar_gasto(
            concepto="Cena",
            importe="120.00",
            fecha="06/10/2026",
            pagador="Carlos",
            divididos=["Carlos", "Sofía", "Mateo"],
        )

        desglose = grupo.obtener_desglose_division_especifica()
        self.assertEqual(len(desglose), 1)

        item = desglose[0]
        self.assertEqual(item["concepto"], "Cena")
        self.assertEqual(item["importe"], 120.0)
        self.assertEqual(item["pagador"], "Carlos")
        self.assertEqual(item["cant_participantes"], 3)
        self.assertEqual(item["cuota_individual"], 40.0)

        texto_esperado = "Cena: $120.00. Pagó Carlos. Dividido entre 3 personas (Carlos, Sofía, Mateo) a $40.00 c/u."
        self.assertEqual(item["texto_desglose"], texto_esperado)


if __name__ == "__main__":
    unittest.main()
