# Registro de Prompts - GruPay Versión 4 (V4)

> **Taller de Desarrollo con IA — Sesión 1: Desarrollo Iterativo (V4)**  
> **Objetivo:** Cumplir los 5 Requerimientos No Funcionales (RNF): Estabilidad, Rapidez y Claridad Visual sin sobrecarga tecnológica.

---

## Prompt 1: Fase 1 - Motor de Persistencia y Seguridad de Datos (RNF4)

```text
Diseña el módulo de persistencia segura para GruPay V4:
1. Exportación: Empaquetar el estado completo de la memoria (participantes, gastos y saldos) en un JSON estructurado y forzar la descarga/guardado en el dispositivo del usuario.
2. Importación Protegida ante Corrupción: Inspeccionar el archivo JSON antes de renderizar nada en pantalla para validar que contenga las listas requeridas de participantes y gastos con tipos correctos.
3. Protección del Sistema: Si el archivo cargado no cumple con el esquema requerido o está corrupto, abortar inmediatamente el proceso, mantener intactos los datos que el usuario estaba viendo y desplegar una advertencia clara.
```

---

## Prompt 2: Fase 2 - Validaciones Estrictas en Formularios (RNF1 y RNF2)

```text
Implementa las validaciones estrictas de entrada para evitar que ingrese 'basura' al sistema:
1. Bloqueo de Registros Incompletos (RNF2):
   - El botón de guardar gasto debe permanecer desactivado (disabled) por defecto.
   - Evaluar constantemente el formulario y solo habilitar el botón cuando: el concepto no esté vacío ni tenga solo espacios, la fecha tenga formato válido DD/MM/AAAA, el importe sea numérico > 0, haya un pagador definido y exista al menos una persona seleccionada para dividir.
2. Control de Teclado del Campo de Dinero (RNF1):
   - Bloquear activamente al escribir signos negativos, letras y caracteres no numéricos.
3. Auto-formato Decimal onBlur (RNF1):
   - En el evento de pérdida de foco, tomar el número ingresado y completarlo con dos decimales exactos ('15' -> '15.00', '50' -> '50.00').
```

---

## Prompt 3: Fase 3 - Optimización de Rendimiento y Cálculos (RNF3)

```text
Optimiza el motor de cálculo para procesar operaciones masivas (100 participantes y 1000 gastos) en menos de un segundo:
1. Estrategia de Cálculo Directo:
   - Crear un directorio hash temporal en memoria con los saldos de todos los miembros en cero.
2. Recorrido Único O(N):
   - Leer el historial completo de gastos una única vez de principio a fin, acumulando el monto al pagador y descontando la cuota en los participantes involucrados.
3. Memoria de Resultados (Memoization):
   - Almacenar en caché el resultado de los balances. Los simples cambios visuales (como cambiar de pestaña) no deben detonar un recálculo a menos que se agregue, edite o elimine un gasto o participante real.
```

---

## Prompt 4: Fase 4 - Semántica Visual y Estados Financieros (RNF1 y RNF5)

```text
Implementa la semántica visual y financiera:
1. Estandarización de Moneda (RNF1):
   - Formatear siempre con símbolo monetario, separador de miles y dos decimales ($ 1,250.00).
2. Interpretación Visual de Saldos (RNF5):
   - Saldo positivo: Color verde, texto 'Recibe dinero', ícono '▲ (+)', cifra positiva.
   - Saldo negativo: Color rojo, texto 'Debe dinero', ícono '▼ (-)', omitiendo el signo menos en el número para no confundir ($ 25.00).
   - Saldo cero: Tono gris, texto 'Cuentas saldadas', ícono '✓'.
```

---

## Prompt 5: Pruebas y Criterios de Aceptación (Checklist)

```text
Crea la suite test_v4.py que valide los 5 criterios del checklist:
1. Bloqueo de caracteres no numéricos y autoformato de '15' a '15.00'.
2. Imposibilidad de guardar tickets incompletos.
3. Benchmark de 100 participantes y 1000 gastos completado en menos de 1 segundo sin congelar.
4. Protección del sistema ante archivos corruptos abortando y preservando datos.
5. Verificación de los 3 estados semánticos visuales (verde, rojo y gris).
```
