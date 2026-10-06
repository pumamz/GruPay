"""
Lógica del Dominio - GruPay V1
Gestor de Gastos Compartidos para Aplicación de Escritorio
Cumple estrictamente con los 10 requisitos funcionales (RF1 a RF10).
"""

from datetime import datetime
import json
from typing import Any, Dict, List, Optional


class Gasto:
    """Representa un gasto registrado en el grupo."""

    def __init__(
        self,
        id_gasto: int,
        concepto: str,
        importe: float,
        fecha: str,
        pagador: str,
        divididos: List[str],
    ):
        if not concepto or not concepto.strip():
            raise ValueError("El concepto del gasto no puede estar vacío.")
        if importe <= 0:
            raise ValueError("El importe debe ser mayor a cero.")
        if not pagador:
            raise ValueError("Debe indicarse quién pagó el gasto.")
        if not divididos:
            raise ValueError("Debe seleccionarse al menos un participante para dividir el gasto.")

        self.id_gasto = id_gasto
        self.concepto = concepto.strip()
        self.importe = round(float(importe), 2)
        self.fecha = fecha.strip()
        self.pagador = pagador.strip()
        self.divididos = [p.strip() for p in divididos]

    @property
    def cuota_individual(self) -> float:
        """Calcula la cuota en partes iguales entre los participantes seleccionados (RF6)."""
        if not self.divididos:
            return 0.0
        return round(self.importe / len(self.divididos), 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id_gasto,
            "concepto": self.concepto,
            "importe": self.importe,
            "fecha": self.fecha,
            "pagador": self.pagador,
            "divididos": self.divididos,
            "cuota_individual": self.cuota_individual,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Gasto":
        return cls(
            id_gasto=data["id"],
            concepto=data["concepto"],
            importe=data["importe"],
            fecha=data["fecha"],
            pagador=data["pagador"],
            divididos=data["divididos"],
        )


class Grupo:
    """Entidad principal que administra participantes, gastos y balances (RF1)."""

    def __init__(self, nombre: str = "Nuevo Grupo"):
        self.nombre = nombre.strip() if nombre else "Nuevo Grupo"
        self.participantes: List[str] = []
        self.gastos: List[Gasto] = []
        self._contador_gasto_id = 1

    # RF1: Crear / resetear grupo
    def reiniciar_grupo(self, nombre: str) -> None:
        """Reinicia el grupo con un nuevo nombre."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del grupo no puede estar vacío.")
        self.nombre = nombre.strip()
        self.participantes = []
        self.gastos = []
        self._contador_gasto_id = 1

    # RF2: Agregar, editar y eliminar participantes
    def agregar_participante(self, nombre: str) -> None:
        """Agrega un participante al grupo."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del participante no puede estar vacío.")
        nombre_limpio = nombre.strip()
        if nombre_limpio in self.participantes:
            raise ValueError(f"El participante '{nombre_limpio}' ya existe en el grupo.")
        self.participantes.append(nombre_limpio)

    def editar_participante(self, nombre_actual: str, nuevo_nombre: str) -> None:
        """Edita el nombre de un participante existente actualizando sus referencias."""
        nombre_actual = nombre_actual.strip()
        nuevo_nombre = nuevo_nombre.strip()
        if not nuevo_nombre:
            raise ValueError("El nuevo nombre no puede estar vacío.")
        if nombre_actual not in self.participantes:
            raise ValueError(f"El participante '{nombre_actual}' no existe.")
        if nuevo_nombre != nombre_actual and nuevo_nombre in self.participantes:
            raise ValueError(f"El nombre '{nuevo_nombre}' ya está en uso.")

        # Actualizar lista de participantes
        idx = self.participantes.index(nombre_actual)
        self.participantes[idx] = nuevo_nombre

        # Actualizar en los gastos existentes
        for gasto in self.gastos:
            if gasto.pagador == nombre_actual:
                gasto.pagador = nuevo_nombre
            if nombre_actual in gasto.divididos:
                gasto.divididos = [
                    nuevo_nombre if p == nombre_actual else p
                    for p in gasto.divididos
                ]

    def eliminar_participante(self, nombre: str) -> None:
        """Elimina un participante si no compromete gastos registrados."""
        nombre_limpio = nombre.strip()
        if nombre_limpio not in self.participantes:
            raise ValueError(f"El participante '{nombre_limpio}' no existe.")

        # Verificar si está asociado a gastos
        for gasto in self.gastos:
            if gasto.pagador == nombre_limpio:
                raise ValueError(
                    f"No se puede eliminar a '{nombre_limpio}' porque figura como pagador de gastos."
                )
            if nombre_limpio in gasto.divididos:
                raise ValueError(
                    f"No se puede eliminar a '{nombre_limpio}' porque participa en la división de gastos."
                )

        self.participantes.remove(nombre_limpio)

    # RF3, RF4, RF5, RF6: Registrar gastos y división equitativa
    def registrar_gasto(
        self,
        concepto: str,
        importe: float,
        fecha: str,
        pagador: str,
        divididos: List[str],
    ) -> Gasto:
        """Registra un nuevo gasto indicando concepto, importe, fecha, pagador y divididos."""
        pagador_limpio = pagador.strip()
        if pagador_limpio not in self.participantes:
            raise ValueError(f"El pagador '{pagador_limpio}' debe ser un participante del grupo.")

        divididos_limpios = [p.strip() for p in divididos]
        for p in divididos_limpios:
            if p not in self.participantes:
                raise ValueError(f"El participante '{p}' no pertenece al grupo.")

        nuevo_gasto = Gasto(
            id_gasto=self._contador_gasto_id,
            concepto=concepto,
            importe=importe,
            fecha=fecha,
            pagador=pagador_limpio,
            divididos=divididos_limpios,
        )
        self._contador_gasto_id += 1
        self.gastos.append(nuevo_gasto)
        return nuevo_gasto

    def eliminar_gasto(self, id_gasto: int) -> None:
        """Elimina un gasto por su identificador."""
        longitud_inicial = len(self.gastos)
        self.gastos = [g for g in self.gastos if g.id_gasto != id_gasto]
        if len(self.gastos) == longitud_inicial:
            raise ValueError(f"No se encontró el gasto con ID {id_gasto}.")

    # RF7: Mostrar cuánto pagó cada persona
    def calcular_totales_pagados(self) -> Dict[str, float]:
        """Calcula el total de dinero desembolsado por cada persona."""
        totales = {p: 0.0 for p in self.participantes}
        for gasto in self.gastos:
            if gasto.pagador in totales:
                totales[gasto.pagador] += gasto.importe
            else:
                totales[gasto.pagador] = gasto.importe
        return {p: round(monto, 2) for p, monto in totales.items()}

    # RF8: Calcular los saldos individuales
    def calcular_saldos_individuales(self) -> Dict[str, Dict[str, float]]:
        """
        Calcula el total pagado, la cuota consumida y el saldo neto de cada participante.
        Saldo neto = Total Pagado - Cuota Consumida
        Saldo > 0 : A favor (le deben dinero)
        Saldo < 0 : En contra (debe dinero)
        Saldo == 0: Al día
        """
        resultado = {
            p: {"pagado": 0.0, "consumido": 0.0, "saldo": 0.0}
            for p in self.participantes
        }

        # Acumular pagos
        for gasto in self.gastos:
            if gasto.pagador in resultado:
                resultado[gasto.pagador]["pagado"] += gasto.importe

            # Acumular consumo según cuota igualitaria entre divididos
            if gasto.divididos:
                cuota = gasto.importe / len(gasto.divididos)
                for part in gasto.divididos:
                    if part in resultado:
                        resultado[part]["consumido"] += cuota

        # Calcular saldo neto redondeado
        for p in self.participantes:
            pag = resultado[p]["pagado"]
            cons = resultado[p]["consumido"]
            resultado[p]["pagado"] = round(pag, 2)
            resultado[p]["consumido"] = round(cons, 2)
            resultado[p]["saldo"] = round(pag - cons, 2)

        return resultado

    # RF9: Proponer transferencias para cancelar deudas (Algoritmo Greedy mínimo)
    def calcular_transferencias(self) -> List[Dict[str, Any]]:
        """
        Calcula el conjunto óptimo y mínimo de transferencias para saldar todas las deudas.
        Retorna lista de diccionarios: [{"de": "Mateo", "a": "Carlos", "monto": 80.0}]
        """
        saldos_dict = self.calcular_saldos_individuales()

        # Separar en deudores (saldo < 0) y acreedores (saldo > 0)
        deudores = []  # [(nombre, monto_a_pagar)]
        acreedores = []  # [(nombre, monto_a_recibir)]

        for nombre, datos in saldos_dict.items():
            saldo = datos["saldo"]
            if saldo < -0.009:
                deudores.append([nombre, round(abs(saldo), 2)])
            elif saldo > 0.009:
                acreedores.append([nombre, round(saldo, 2)])

        transferencias = []

        i = 0
        j = 0
        while i < len(deudores) and j < len(acreedores):
            deudor_nombre, deuda = deudores[i]
            acreedor_nombre, credito = acreedores[j]

            monto = min(deuda, credito)
            monto = round(monto, 2)

            if monto > 0:
                transferencias.append({
                    "de": deudor_nombre,
                    "a": acreedor_nombre,
                    "monto": monto,
                })

            deudores[i][1] = round(deuda - monto, 2)
            acreedores[j][1] = round(credito - monto, 2)

            if deudores[i][1] < 0.01:
                i += 1
            if acreedores[j][1] < 0.01:
                j += 1

        return transferencias

    # RF10: Guardar y recuperar la información del grupo
    def a_dict(self) -> Dict[str, Any]:
        """Serializa la entidad completa a un diccionario JSON-compatible."""
        return {
            "nombre": self.nombre,
            "participantes": self.participantes,
            "gastos": [g.to_dict() for g in self.gastos],
            "contador_gasto_id": self._contador_gasto_id,
            "version": "1.0.0",
        }

    def desde_dict(self, data: Dict[str, Any]) -> None:
        """Restaura el estado completo del grupo desde un diccionario."""
        self.nombre = data.get("nombre", "Grupo Restaurado")
        self.participantes = list(data.get("participantes", []))
        self.gastos = [Gasto.from_dict(g) for g in data.get("gastos", [])]
        self._contador_gasto_id = data.get(
            "contador_gasto_id",
            max([g.id_gasto for g in self.gastos], default=0) + 1,
        )

    def guardar_en_archivo(self, ruta: str) -> None:
        """Guarda los datos en un archivo JSON local (RF10)."""
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.a_dict(), f, indent=2, ensure_ascii=False)

    def cargar_desde_archivo(self, ruta: str) -> None:
        """Carga y restablece los datos desde un archivo JSON local (RF10)."""
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.desde_dict(data)
