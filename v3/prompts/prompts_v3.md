# Registro de Prompts - GruPay Versión 3 (V3)

> **Taller de Desarrollo con IA — Sesión 1: Desarrollo Iterativo (V3)**  
> **Objetivo:** Reestructuración arquitectónica, persistencia CRUD directa con auto-save, administrador único, control de cambios pendientes (`isDirty`), validación estricta de importes/fechas y tabla de división específica.

---

## Prompt 1: Fase 1 - Motor de Persistencia y Estados

```text
Actúa como un arquitecto de software senior en Python. Refactoriza el motor de persistencia y estado de GruPay:
1. Corrección de Cambio de Grupo: Modificar el flujo de carga para que al seleccionar un grupo diferente, el estado global se limpie por completo y se hidrate instantáneamente con los datos parseados del nuevo archivo .json.
2. Sincronización CRUD Directa (Participantes): Configurar los métodos de adición, edición y eliminación en la tabla de Participantes para que escriban y sobrescriban automáticamente el archivo .json local tras cada acción, eliminando la necesidad de un botón de guardado manual para estas acciones.
3. Control de Cambios sin Guardar (isDirty): Implementar un sistema de rastreo de estado. Si el usuario intenta cambiar de pestaña teniendo modificaciones pendientes en el formulario de gasto o participantes, el sistema desplegará un modal con las opciones de Descartar Cambios o Cancelar.
4. Limpieza de Datos Precargados: Eliminar cualquier estructura de datos "mock" o de prueba en el código fuente. La función de Crear Grupo debe inicializar participantes y gastos estrictamente como arrays vacíos [], garantizando que la interfaz inicie en blanco.
```

---

## Prompt 2: Fase 2 - Módulo de Participantes y Reglas de Negocio

```text
Implementa las siguientes reglas de negocio en GruPay V3:
1. Regla de Integridad Estricta: Solo se podrá eliminar un participante si no tiene gastos asociados (ni como pagador ni en la lista de beneficiarios divididos). Si los tiene, el sistema bloqueará la eliminación con un mensaje de error explícito.
2. Validación de Administrador Único: Refactorizar la lógica de asignación de roles. Al marcar a un participante como Administrador/Organizador, el sistema recorrerá la lista, removerá dicho rol del usuario que lo poseía anteriormente y se lo asignará exclusivamente al nuevo seleccionado. Solo puede haber un administrador a la vez.
```

---

## Prompt 3: Fase 3 - Validaciones Estrictas de Interfaz

```text
Diseña funciones de validación estricta:
1. Bloqueo de Campos en Blanco: Rechazar y advertir visualmente si los campos de texto están vacíos o contienen únicamente espacios.
2. Validación Numérica Estricta de Importes: Implementar validar_importe(). Solo permitir números positivos con máximo 2 decimales, bloqueando signos negativos, letras o valores <= 0.
3. Validación Estricta de Fechas: Implementar validar_fecha(). Asegurar que la fecha requiera formato DD/MM/AAAA y pertenezca al calendario gregoriano real.
```

---

## Prompt 4: Fase 4 - Módulo de Gastos y UX General

```text
En la interfaz de escritorio de Tkinter (app.py):
1. Reflejo en Tiempo Real: Asegurar que al registrar un nuevo gasto, la tabla del historial se recargue inmediatamente en el mismo ciclo de eventos.
2. Reubicación de Controles: Mover el botón general de "Guardar Grupo Completo" a la esquina inferior derecha de la pantalla.
3. Bloqueo de Avance por Cambios Pendientes: El botón "Continuar a Gastos" debe verificar si hay nombres pendientes en el campo de entrada sin haber presionado "+ Agregar". Si los hay, bloquear el avance con una advertencia.
```

---

## Prompt 5: Fase 5 - Auditoría y Tabla de División Específica

```text
En la pestaña de Saldos y Deudas:
1. Integrar una nueva tabla de detalle: 'Tabla de División Específica y Transparencia'.
2. Por cada gasto registrado, mostrar el desglose explícito de cómo se dividió el importe en partes iguales entre las personas involucradas (ej. "Cena: $120.00. Pagó Carlos. Dividido entre 3 personas (Carlos, Sofía, Mateo) a $40.00 c/u.").
```
