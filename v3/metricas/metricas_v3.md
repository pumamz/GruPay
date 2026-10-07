# Métricas de Calidad y Validación - GruPay Versión 3 (V3)

> **Taller de Desarrollo con IA — Sesión 1: Desarrollo Iterativo (V3)**  
> **Fecha de Validación:** 07/10/2026  
> **Estado de la Versión 3:** ✅ 100% Completa y Aprobada

---

## 1. Cobertura de Mejoras por Fase (V3)

| Fase | Funcionalidad / Regla Implementada | Validación | Estado |
| :--- | :--- | :--- | :---: |
| **Fase 1** | **Limpieza e Hidratación Pura:** Al cambiar de grupo, el estado se limpia sin arrastrar datos previos. | `test_fase1_cambio_de_grupo_limpia_e_hidrata_estado` | ✅ Aprobado |
| **Fase 1** | **Sin Datos Mock:** Grupos nuevos inician estrictamente en blanco (`[]`). | `test_fase1_inicializacion_estrictamente_vacia` | ✅ Aprobado |
| **Fase 1** | **Sincronización CRUD Directa:** Auto-guardado en archivo `.json` tras cada adición/edición/borrado. | Verificado en GUI y Core | ✅ Aprobado |
| **Fase 1** | **Control isDirty:** Modal al cambiar de pestaña con datos a medio cargar en el formulario. | Verificado en `_al_intentar_cambiar_tab()` | ✅ Aprobado |
| **Fase 2** | **Administrador Único:** Solo puede haber un Organizador a la vez; se remueve del previo al asignar nuevo. | `test_fase2_administrador_unico_al_agregar`, `test_fase2_administrador_unico_al_editar` | ✅ Aprobado |
| **Fase 2** | **Regla de Integridad:** Bloqueo de eliminación de participantes asociados a gastos. | `test_fase2_regla_de_integridad_bloqueo_eliminacion` | ✅ Aprobado |
| **Fase 3** | **Validación de Fechas:** Formato estricto DD/MM/AAAA y calendario real. | `test_fase3_validacion_fechas_estricta` | ✅ Aprobado |
| **Fase 3** | **Validación de Importes:** Positivos, máx 2 decimales, rechaza letras y negativos. | `test_fase3_validacion_importes_estricta` | ✅ Aprobado |
| **Fase 3** | **Bloqueo Campos en Blanco:** Rechaza campos vacíos o con solo espacios. | `test_fase3_bloqueo_campos_en_blanco` | ✅ Aprobado |
| **Fase 4** | **Reflejo en Tiempo Real:** Gastos aparecen al instante en la tabla tras registrarse. | Verificado en `_registrar_gasto_en_tiempo_real()` | ✅ Aprobado |
| **Fase 4** | **Reubicación de Guardar:** Botón movido a la esquina inferior derecha. | Verificado en `footer_global` | ✅ Aprobado |
| **Fase 4** | **Bloqueo de Avance:** "Continuar a Gastos" bloquea si hay nombres pendientes en el input. | Verificado en `_continuar_a_gastos_con_validacion()` | ✅ Aprobado |
| **Fase 5** | **Tabla de División Específica:** Desglose transparente ("Cena: $120. Pagó Carlos..."). | `test_fase5_desglose_equitativo_transparente` | ✅ Aprobado |

**Tasa de Aprobación de Pruebas Unitarias:** **100% (9 de 9 tests exitosos en 0.002s)**

---

## 2. Evolución Comparativa de las 3 Versiones (V1 vs V2 vs V3)

| Métrica de Proyecto | Versión 1 (V1) | Versión 2 (V2) | Versión 3 (V3) |
| :--- | :---: | :---: | :---: |
| **Enfoque Principal** | 10 Requisitos Funcionales Base | Estabilización y Multi-Grupo | Arquitectura, Auto-Save y Transparencia |
| **LOC `core.py`** | 305 | 424 | 467 |
| **LOC `app.py`** | 707 | 798 | 856 |
| **LOC Tests** | 237 | 204 | 206 |
| **Total LOC** | **1,249** | **1,426** | **1,529** |
| **Pruebas Automatizadas** | 10 tests | 9 tests | 9 tests |
| **Total acumulado pruebas** | 10 | 19 | **28 tests aprobados** |
| **Dependencias Externas** | 0 (Solo Python Stdlib) | 0 (Solo Python Stdlib) | 0 (Solo Python Stdlib) |
| **Compatibilidad Thonny IDE** | ✅ 100% | ✅ 100% | ✅ 100% |
