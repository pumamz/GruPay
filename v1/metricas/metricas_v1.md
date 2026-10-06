# Métricas de Calidad y Validación - GruPay Versión 1 (V1)

> **Taller de Desarrollo con IA — Sesión 1**  
> **Fecha de Validación:** 06/10/2026  
> **Estado de la Versión 1:** ✅ 100% Completa y Aprobada

---

## 1. Cobertura de Requisitos Funcionales

| Requisito Funcional | Estado | Módulo / Método Responsable | Validación |
| :--- | :---: | :--- | :---: |
| **RF1.** Crear un grupo de participantes | ✅ Cumplido | `Grupo.__init__()`, `Grupo.reiniciar_grupo()` | `test_rf1_crear_grupo` (OK) |
| **RF2.** Agregar, editar y eliminar participantes | ✅ Cumplido | `agregar_participante()`, `editar_participante()`, `eliminar_participante()` | `test_rf2_agregar_editar_eliminar_participante` (OK) |
| **RF3.** Registrar gastos con concepto, importe y fecha | ✅ Cumplido | `Gasto.__init__()`, `Grupo.registrar_gasto()` | `test_rf3_registrar_gastos` (OK) |
| **RF4.** Indicar quién pagó cada gasto | ✅ Cumplido | `Grupo.registrar_gasto(pagador=...)` | `test_rf4_indicar_quien_pago` (OK) |
| **RF5.** Seleccionar entre quiénes se divide | ✅ Cumplido | `Grupo.registrar_gasto(divididos=...)` | `test_rf5_seleccionar_entre_quienes_se_divide` (OK) |
| **RF6.** Dividir el importe en partes iguales | ✅ Cumplido | `Gasto.cuota_individual` ($M / N$) | `test_rf6_dividir_importe_partes_iguales` (OK) |
| **RF7.** Mostrar cuánto pagó cada persona | ✅ Cumplido | `Grupo.calcular_totales_pagados()` | `test_rf7_mostrar_cuanto_pago_cada_persona` (OK) |
| **RF8.** Calcular los saldos individuales | ✅ Cumplido | `Grupo.calcular_saldos_individuales()` | `test_rf8_calcular_saldos_individuales` (OK) |
| **RF9.** Proponer transferencias para cancelar deudas | ✅ Cumplido | `Grupo.calcular_transferencias()` | `test_rf9_proponer_transferencias_cancelar_deudas` (OK) |
| **RF10.** Guardar y recuperar la información del grupo | ✅ Cumplido | `guardar_en_archivo()`, `cargar_desde_archivo()` | `test_rf10_guardar_y_recuperar_informacion` (OK) |

**Porcentaje de cumplimiento de requisitos funcionales:** **100% (10 de 10)**

---

## 2. Resultados de Pruebas Automatizadas

* **Framework de pruebas:** `unittest` (Estándar de Python).
* **Total de casos de prueba ejecutados:** 10
* **Casos de prueba exitosos:** 10 (100%)
* **Casos fallidos o con error:** 0 (0%)
* **Tiempo total de ejecución de la suite:** 0.001 segundos
* **Comando de ejecución:** `PYTHONPATH=v1/src python3 -m unittest v1/pruebas/test_v1.py`

---

## 3. Métricas de Código (Lines of Code - LOC)

| Archivo | Rol | Líneas de Código (LOC) |
| :--- | :--- | :---: |
| `v1/src/core.py` | Lógica de negocio y algoritmos de balance | 305 |
| `v1/src/app.py` | Interfaz gráfica de escritorio (Tkinter / ttk) | 707 |
| `v1/pruebas/test_v1.py` | Suite de pruebas unitarias automatizadas | 237 |
| **Total V1** | | **1,249** |

---

## 4. Verificación de Compatibilidad en Thonny IDE

* **Dependencias externas:** 0 (Usa 100% biblioteca estándar de Python: `tkinter`, `json`, `datetime`, `unittest`).
* **Tiempo de arranque de la GUI:** < 0.2 segundos.
* **Compatibilidad de ejecución con F5 en Thonny:** ✅ Verificada.
* **Persistencia local:** Archivos formato `.json` legibles y portables.
