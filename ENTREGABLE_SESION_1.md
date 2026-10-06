# Prototipo Sencillo de Escritorio: GruPay (3 Pantallas)

> **Taller Práctico de Software con IA — Sesión 1: Definición del Prototipo**  
> Enfoque: **Minimalista, directo y funcional.** Sin pantallas sobrecargadas ni funciones innecesarias; 3 vistas de escritorio simples que cubren exactamente los 10 requisitos funcionales.

---

## 📌 Mapeo Directo: 3 Pantallas vs 10 Requisitos Funcionales

### Pantalla 1: `Grupos y Participantes`
* **RF1:** Crear un grupo de participantes (Campo *Nombre del Grupo* + botón *Crear*).
* **RF2:** Agregar, editar y eliminar participantes (Input para nombre + tabla con botón *Eliminar*).
* **RF10:** Guardar y recuperar la información (Botones *Guardar* y *Cargar* archivo local).
* 📁 Archivo HTML: [`pantalla1_participantes.html`](./pantalla1_participantes.html)
* 🖼️ Imagen: [`pantalla1_participantes.png`](./pantalla1_participantes.png)

---

### Pantalla 2: `Registro de Gastos`
* **RF3:** Registrar gastos con concepto, importe y fecha (Campos del formulario).
* **RF4:** Indicar quién pagó cada gasto (Selector desplegable *¿Quién lo pagó?*).
* **RF5:** Seleccionar entre quiénes se divide (Checkboxes de integrantes).
* **RF6:** Dividir el importe en partes iguales (Cálculo automático visible: *Cuota igual por persona*).
* Tabla con historial de gastos y acción para eliminar.
* 📁 Archivo HTML: [`pantalla2_gastos.html`](./pantalla2_gastos.html)
* 🖼️ Imagen: [`pantalla2_gastos.png`](./pantalla2_gastos.png)

---

### Pantalla 3: `Saldos y Deudas (Liquidación)`
* **RF7:** Mostrar cuánto pagó cada persona (Columna *Total Pagado*).
* **RF8:** Calcular los saldos individuales (Columna *Saldo Neto*: verde a favor, rojo en contra).
* **RF9:** Proponer transferencias para cancelar deudas (Lista simple de pagos directos sugeridos: *X le paga a Y $Z* con botón *Marcar Pagado*).
* 📁 Archivo HTML: [`pantalla3_saldos.html`](./pantalla3_saldos.html)
* 🖼️ Imagen: [`pantalla3_saldos.png`](./pantalla3_saldos.png)

---

## 🎯 Resumen para Validar con el Docente

| Elemento | Definición Concreta y Simple |
| :--- | :--- |
| **Problema** | División de gastos compartidos en grupos de amigos o viajes sin enredos ni cálculos manuales. |
| **Usuarios** | Integrantes de un grupo: el que anota/administra, los que pagan y los que consumen. |
| **Estructura de Datos** | • **Grupo:** nombre.<br>• **Participantes:** lista de nombres.<br>• **Gastos:** concepto, monto, fecha, pagador, lista de involucrados. |
| **Cálculo de Saldos** | `Saldo Neto = Total Pagado - Total Consumido`. La suma de todos los saldos siempre da $0.00. |
| **Cancelación de Deudas** | Emparejar deudores con acreedores para saldar con el menor número de transferencias. |
| **Almacenamiento** | Guardar y cargar en un archivo JSON local. |
