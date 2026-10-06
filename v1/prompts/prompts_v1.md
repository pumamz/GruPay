# Registro de Prompts - GruPay Versión 1 (V1)

> **Taller de Desarrollo con IA — Sesión 1: Desarrollo Iterativo**  
> **Objetivo:** Generación y validación del 100% de los Requisitos Funcionales (RF1 a RF10) mediante prompting estructurado.

---

## Prompt 1: Arquitectura y Lógica de Negocio (Core)

```text
Actúa como un desarrollador senior en Python. Diseña el módulo de lógica de negocio (core.py) para una aplicación de escritorio llamada GruPay (Gestor de Gastos Compartidos). 
Debe cumplir estrictamente los 10 requisitos funcionales del sobre:
RF1. Crear un grupo de participantes.
RF2. Agregar, editar y eliminar participantes.
RF3. Registrar gastos con concepto, importe y fecha.
RF4. Indicar quién pagó cada gasto.
RF5. Seleccionar entre quiénes se divide.
RF6. Dividir el importe en partes iguales.
RF7. Mostrar cuánto pagó cada persona.
RF8. Calcular los saldos individuales (saldo neto = pagado - consumido).
RF9. Proponer transferencias para cancelar deudas (algoritmo óptimo de saldos mínimos).
RF10. Guardar y recuperar la información del grupo en formato JSON local.

Requisitos técnicos:
- Código desacoplado de la GUI para facilitar pruebas unitarias.
- Validaciones robustas de entrada (monto > 0, nombres no vacíos, participantes existentes).
- Compatible con Python estándar (sin librerías externas para ejecutarse sin problemas en Thonny).
```

---

## Prompt 2: Suite de Pruebas Unitarias Automatizadas (Tests)

```text
Genera una suite de pruebas con unittest en Python (test_v1.py) que valide individual y exhaustivamente cada uno de los 10 requisitos funcionales (RF1 al RF10).
Incluye casos de éxito y casos de fallo/borde:
- Creación y reinicio de grupo.
- Prevención de participantes duplicados y bloqueo de eliminación si tienen gastos.
- División equitativa de gastos y división selectiva por subgrupos.
- Verificación matemática de que la suma de saldos individuales es siempre 0.00.
- Algoritmo de transferencias de deuda: verificar que tras aplicar las transferencias propuestas, el saldo de todos los participantes queda exactamente en 0.00.
- Guardado y carga desde archivo JSON temporal comprobando integridad total.
```

---

## Prompt 3: Interfaz Gráfica de Escritorio (Desktop Tkinter)

```text
Crea la aplicación de escritorio en Python utilizando Tkinter y ttk (app.py) para ejecutar en el entorno Thonny.
La aplicación debe estructurarse en 3 pestañas limpias y funcionales que reflejen el prototipo validado:
- Pestaña 1 (Grupos y Participantes): Crear grupo, guardar/cargar archivo local, agregar, editar y eliminar participantes.
- Pestaña 2 (Registro de Gastos): Formulario con concepto, importe, fecha, selector de pagador, checkboxes para seleccionar participantes con cálculo en tiempo real de la cuota individual ($ c/u), y tabla de historial de gastos.
- Pestaña 3 (Saldos y Deudas): Tabla con el total pagado por persona (RF7), saldo individual con badges de color (RF8) y tabla con las transferencias directas sugeridas para saldar deudas (RF9).

Debe incluir datos de demostración pre-cargados al iniciar para que se pueda probar y evaluar de forma inmediata al presionar F5 en Thonny.
```

---

## Prompt 4: Métricas y Validación

```text
Calcula las métricas de software de la Versión 1:
- Cobertura de requerimientos funcionales (RF1-RF10).
- Resultados de la suite de pruebas unitarias (número de tests ejecutados y tiempo).
- Líneas de código (LOC) de core.py, app.py y test_v1.py.
- Complejidad y compatibilidad con Thonny IDE.
```
