# 👥 GruPay - Gestor de Gastos Compartidos (Desktop)

> **Taller de Prototipos de Software y Desarrollo Iterativo con IA**  
> Repositorio Oficial: [https://github.com/pumamz/GruPay](https://github.com/pumamz/GruPay)  
> Autor: **@pumamz**

Aplicación de escritorio en Python construida iterativamente con Inteligencia Artificial para dividir gastos de viajes, eventos o convivencia compartida.

---

## 📌 Requisitos Funcionales Cumplidos (RF1 a RF10)

| Requisito | Descripción | Estado V1 |
| :--- | :--- | :---: |
| **RF1** | Crear un grupo de participantes | ✅ |
| **RF2** | Agregar, editar y eliminar participantes | ✅ |
| **RF3** | Registrar gastos con concepto, importe y fecha | ✅ |
| **RF4** | Indicar quién pagó cada gasto | ✅ |
| **RF5** | Seleccionar entre quiénes se divide | ✅ |
| **RF6** | Dividir el importe en partes iguales | ✅ |
| **RF7** | Mostrar cuánto pagó cada persona | ✅ |
| **RF8** | Calcular los saldos individuales (Saldo = Pagado - Consumido) | ✅ |
| **RF9** | Proponer transferencias mínimas para cancelar deudas | ✅ |
| **RF10**| Guardar y recuperar la información del grupo en JSON local | ✅ |

---

## 🚀 Cómo Ejecutar en Thonny IDE (o Terminal)

El proyecto utiliza **100% biblioteca estándar de Python (`tkinter`, `json`, `datetime`, `unittest`)**, por lo que **no requiere instalar dependencias con pip** y funciona inmediatamente al abrir y pulsar `F5` en Thonny.

### Ejecución de la Versión 1 (V1):
```bash
# Desde la raíz del repositorio:
python3 v1/src/app.py
```
*O en Thonny: Abrir `v1/src/app.py` y pulsar F5.*

### Ejecución de la Versión 2 (V2):
```bash
# Desde la raíz del repositorio:
python3 v2/src/app.py
```
*O en Thonny: Abrir `v2/src/app.py` y pulsar F5.*

### Ejecución de la Versión 3 (V3):
```bash
# Desde la raíz del repositorio:
python3 v3/src/app.py
```
*O en Thonny: Abrir `v3/src/app.py` y pulsar F5.*

### Ejecución de la Versión 4 (V4 - RNF Engine):
```bash
# Versión de Escritorio en Python (Thonny F5):
python3 v4/src/app.py

# Versión Web Nativa Standalone (Abrir en cualquier navegador):
xdg-open v4/src/index.html  # o doble clic en el archivo
```

### Ejecución de Pruebas Unitarias Automatizadas:
```bash
# Pruebas V1 (10 Requisitos Funcionales):
PYTHONPATH=v1/src python3 -m unittest v1/pruebas/test_v1.py

# Pruebas V2 (Criterios de Aceptación Fase 4):
PYTHONPATH=v2/src python3 -m unittest v2/pruebas/test_v2.py

# Pruebas V3 (Arquitectura, Auto-Save, Admin Único y División Específica):
PYTHONPATH=v3/src python3 -m unittest v3/pruebas/test_v3.py

# Pruebas V4 (RNF1-RNF5, Stress Test 1000 gastos < 1s, Validación de Esquema):
PYTHONPATH=v4/src python3 -m unittest v4/pruebas/test_v4.py
```

---

## 📂 Estructura del Repositorio por Versiones

```text
GruPay/
├── ENTREGABLE_SESION_1.md    # Especificación de requisitos y prototipo
├── README.md                 # Guía general del proyecto
│
├── v1/                       # Versión 1 (RF1-RF10 Base - 100% Validada)
│   ├── src/ (core.py, app.py)
│   ├── pruebas/ (test_v1.py - 10/10 tests OK)
│   ├── datos/
│   ├── prompts/ (prompts_v1.md)
│   └── metricas/ (metricas_v1.md)
│
├── v2/                       # Versión 2 (Estabilización, Multi-Grupo, Auditoría, Regex)
│   ├── src/ (core.py, app.py)
│   ├── pruebas/ (test_v2.py - 9/9 tests OK)
│   ├── datos/grupos_guardados/
│   ├── prompts/ (prompts_v2.md)
│   └── metricas/ (metricas_v2.md)
│
├── v3/                       # Versión 3 (Auto-Save, Admin Único, isDirty, Transparencia)
│   ├── src/ (core.py, app.py)
│   ├── pruebas/ (test_v3.py - 9/9 tests OK)
│   ├── datos/
│   ├── prompts/ (prompts_v3.md)
│   └── metricas/ (metricas_v3.md)
│
└── v4/                       # Versión 4 (RNF Engine: O(N) 1000 gastos en 27ms, RNF1-RNF5)
    ├── src/ (core.py, app.py, index.html)
    ├── pruebas/ (test_v4.py - 8/8 tests OK con benchmark)
    ├── datos/ (stress_test_1000_gastos.json, archivos corruptos y válidos)
    ├── prompts/ (prompts_v4.md)
    └── metricas/ (metricas_v4.md)
```

---

## 🏷️ Versiones y Tags en Git
* **`v1.0.0`**: Versión 1 completa con los 10 requerimientos funcionales validados con 10/10 pruebas unitarias y aplicación de escritorio operativa en Thonny.
* **`v2.0.0`**: Versión 2 estabilizada con corrección de errores críticos, multi-grupo, saneamiento de archivos y auditoría de pagos (9/9 pruebas aprobadas).
* **`v3.0.0`**: Versión 3 con reestructuración arquitectónica, persistencia CRUD directa con auto-save, administrador único, control isDirty, validaciones estrictas y tabla de división específica (9/9 pruebas aprobadas).
* **`v4.0.0`**: Versión 4 con cumplimiento total de los 5 Requerimientos No Funcionales (RNF1 a RNF5): motor O(N) de 1000 gastos en 27ms con memoización, validación y formateo onBlur, botones disabled por defecto, protección estricta contra archivos corruptos y semántica visual financiera (8/8 pruebas con benchmark aprobadas).



