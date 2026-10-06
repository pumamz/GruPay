# Registro de Prompts - GruPay Versión 2 (V2)

> **Taller de Desarrollo con IA — Sesión 1: Desarrollo Iterativo (V2)**  
> **Objetivo:** Estabilización del sistema, corrección de errores críticos en cálculos y estado, validaciones estrictas y administración multi-grupo.

---

## Prompt 1: Fase 1 - Corrección de Errores Críticos (Bug Fixes)

```text
Actúa como un ingeniero de software principal. En el proyecto GruPay, corrige los siguientes fallos críticos:
1. Corrección del Nombre del Grupo:
   - Problema: El estado guardaba siempre 'Nuevo Grupo'.
   - Solución: Vincular el evento de escritura del input (StringVar / onChange) directamente al estado del grupo para sobrescribir en tiempo real el valor antes de guardar.
2. Reparación de la División Equitativa:
   - Problema: Desincronización en la cuota al tildar/destildar participantes.
   - Solución: Vincular el cálculo (Importe / Cantidad de seleccionados) de manera reactiva tanto al evento de modificación del importe como a cada cambio en los checkboxes de participantes.
3. Cálculo Exacto de Saldos Individuales:
   - Problema: Discrepancias en consolidación de balances.
   - Solución: Implementar la fórmula estricta: Saldo Neto = Total Pagado por el usuario - Cuota Consumida por el usuario en todos los gastos. Garantizar que la sumatoria total de saldos del grupo sea siempre 0.00.
```

---

## Prompt 2: Fase 2 - Nuevas Funcionalidades (Multi-Grupo, Edición y Auditoría)

```text
Añade las siguientes funcionalidades a GruPay V2:
1. Listado de Grupos Vinculados (Dashboard / Selector):
   - Crear un componente GestorMultiGrupos que escanee el directorio de datos 'grupos_guardados/' y exponga los grupos disponibles en un selector para alternar entre grupos fácilmente.
2. Edición de Participantes con Actualización en Cascada:
   - Incorporar modal de edición para modificar nombre y rol del participante.
   - Actualizar en cascada todas las referencias en los gastos existentes (pagador y divididos) sin perder el historial ni alterar las deudas pasadas.
3. Visualización y Auditoría de Pagos Individuales:
   - Añadir una tabla de auditoría en la pestaña de Saldos que muestre el monto total real que pagó cada miembro, el número de desembolsos realizados y su porcentaje respecto al gasto total del grupo.
```

---

## Prompt 3: Fase 3 - Validaciones Estrictas y Seguridad de Datos

```text
Implementa mecanismos de sanitización y validación estricta:
1. Saneamiento con Regex:
   - Diseñar la función sanitizar_texto() que elimine caracteres conflictivos (< > { } [ ] \\) para prevenir inyecciones o rupturas en el formato JSON.
2. Bloqueo de Campos Obligatorios:
   - Rechazar gastos con importe <= 0, sin concepto o sin pagador.
   - Impedir la creación de gastos sin al menos un participante beneficiario en la división.
3. Saneamiento de Nombre de Archivo:
   - Diseñar la función sanitizar_nombre_archivo() que convierta nombres con caracteres prohibidos de sistemas operativos (\\ / : * ? " < > |) y espacios en nombres válidos como 'Viaje_a_la_playa_2026.json'.
```

---

## Prompt 4: Fase 4 - Suite de Pruebas Automatizadas

```text
Genera la suite test_v2.py con unittest para validar al 100% los 5 criterios de aceptación de la Fase 4:
1. Prueba de Grupo: Crear 'Prueba 2026', guardar y recargar comprobando que no vuelva a 'Nuevo Grupo'.
2. Prueba de Cálculos: $100 entre 4 personas = exactamente $25.00 c/u.
3. Prueba de Balances: Persona A +$75.00 y las otras 3 -$25.00 cada una.
4. Prueba de Archivos: 'Viaje a la playa / 2026??' guardado como 'Viaje_a_la_playa_2026.json'.
5. Prueba de Edición: Modificar participante con gastos y verificar que saldos se mantengan exactos.
```
