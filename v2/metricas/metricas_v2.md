# Métricas de Calidad y Validación - GruPay Versión 2 (V2)

> **Taller de Desarrollo con IA — Sesión 1: Desarrollo Iterativo (V2)**  
> **Fecha de Validación:** 06/10/2026  
> **Estado de la Versión 2:** ✅ 100% Completa y Aprobada

---

## 1. Cumplimiento de Criterios de Aceptación (Fase 4)

| ID | Criterio de Aceptación (Fase 4) | Método / Prueba | Resultado |
| :--- | :--- | :--- | :---: |
| **C1** | **Prueba de Grupo:** Crear "Prueba 2026", guardar y recargar manteniendo el nombre sin revertir a "Nuevo Grupo". | `test_criterio_1_nombre_grupo_persiste` | ✅ Aprobado |
| **C2** | **Prueba de Cálculos:** Gasto de $100 pagado por Persona A, dividido entre 4 personas $\rightarrow$ cuota exacta de $25.00 c/u. | `test_criterio_2_calculo_cuota_equitativa` | ✅ Aprobado |
| **C3** | **Prueba de Balances:** Persona A con saldo neto +$75.00 y las otras 3 personas con -$25.00 cada una. | `test_criterio_3_balances_exactos` | ✅ Aprobado |
| **C4** | **Prueba de Archivos:** Saneamiento de "Viaje a la playa / 2026??" a "Viaje_a_la_playa_2026.json". | `test_criterio_4_saneamiento_nombre_archivo` | ✅ Aprobado |
| **C5** | **Prueba de Edición:** Edición en cascada de participante con gastos asociados manteniendo balances sin pérdida de datos. | `test_criterio_5_edicion_participante_en_cascada` | ✅ Aprobado |
| **C6** | **Seguridad Regex:** Saneamiento de `< > { } [ ] \\`. | `test_saneamiento_caracteres_especiales` | ✅ Aprobado |
| **C7** | **Validaciones Estrictas:** Bloqueo de importes $\le 0$ y beneficiarios vacíos. | `test_validaciones_estrictas_campos_obligatorios` | ✅ Aprobado |
| **C8** | **Multi-Grupos:** Escaneo, listado y cambio dinámico entre múltiples grupos. | `test_gestor_multi_grupos` | ✅ Aprobado |
| **C9** | **Auditoría de Pagos:** Desglose del monto real desembolsado por cada miembro. | `test_auditoria_pagos_individuales` | ✅ Aprobado |

**Tasa de Aprobación de Criterios de Aceptación:** **100% (9 de 9 pruebas exitosas)**

---

## 2. Resultados de la Suite Automatizada

* **Comando:** `PYTHONPATH=v2/src python3 -m unittest v2/pruebas/test_v2.py`
* **Pruebas ejecutadas:** 9
* **Pruebas aprobadas:** 9 (100%)
* **Errores / Fallos:** 0 (0%)
* **Tiempo de ejecución:** 0.001 segundos

---

## 3. Comparativa de Métricas de Código (V1 vs V2)

| Métrica | Versión 1 (V1) | Versión 2 (V2) | Incremento / Delta |
| :--- | :---: | :---: | :---: |
| **LOC `core.py`** | 305 | 424 | +119 (+39.0%) |
| **LOC `app.py`** | 707 | 798 | +91 (+12.8%) |
| **LOC Tests** | 237 | 204 | Tests focalizados Fase 4 |
| **Total Líneas de Código** | 1,249 | 1,426 | +177 líneas |
| **Funcionalidades Nuevas** | RF1-RF10 base | Multi-Grupo, Auditoría, Regex | +3 capacidades mayores |
| **Tiempo de Cómputo** | < 1 ms | < 1 ms | Constante |
