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
*O en Thonny: Abrir `v1/src/app.py` y pulsar el botón verde de Ejecutar (F5).*

### Ejecución de Pruebas Unitarias Automatizadas (V1):
```bash
PYTHONPATH=v1/src python3 -m unittest v1/pruebas/test_v1.py
```

---

## 📂 Estructura del Repositorio

```text
GruPay/
├── ENTREGABLE_SESION_1.md    # Especificación de requisitos y prototipo
├── index.html                # Prototipo web exportado de Stitch
├── pantalla1_participantes.* # Vistas de diseño de Stitch
├── pantalla2_gastos.*
├── pantalla3_saldos.*
│
├── v1/                       # Versión 1 (100% Funcional y Validada)
│   ├── src/
│   │   ├── core.py           # Lógica desacoplada y algoritmos de saldos
│   │   └── app.py            # GUI Tkinter desktop para Thonny
│   ├── pruebas/
│   │   └── test_v1.py        # 10 tests automatizados (100% pasando)
│   ├── datos/
│   │   ├── ejemplo_viaje.json
│   │   └── ejemplo_roommates.json
│   ├── prompts/
│   │   └── prompts_v1.md     # Registro de prompts de generación
│   └── metricas/
│       └── metricas_v1.md    # Métricas de calidad, LOC y tiempos
│
├── v2/                       # En desarrollo iterativo
└── v3/                       # En desarrollo iterativo
```

---

## 🏷️ Versiones y Tags en Git
* **`v1.0.0`**: Versión 1 completa con los 10 requerimientos funcionales validados con 10/10 pruebas unitarias y aplicación de escritorio operativa en Thonny.
