"""
Lógica del Dominio - GruPay V2 (Estabilización, Corrección de Errores y Validaciones Estrictas)
Versión 2 del Gestor de Gastos Compartidos.
Incorpora:
- Corrección de vinculación del nombre del grupo.
- Saneamiento de entradas con Regex (anti-inyección de caracteres conflictivos).
- Generación y saneamiento de nombres de archivo seguros para el SO.
- Edición de participantes con actualización en cascada.
- Cálculo riguroso de división equitativa y saldos individuales.
- Soporte para administración de múltiples grupos locales.
"""

from datetime import datetime
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple


def sanitizar_texto(texto: str) -> str:
    """
    Sanea texto eliminando caracteres que puedan romper estructuras o serialización (< > { } [ ]).
    Lanza ValueError si el texto resulta vacío tras el saneamiento.
    """
    if not isinstance(texto, str):
        raise ValueError("El valor debe ser una cadena de texto.")

    # Remover caracteres conflictivos: < > { } [ ] \
    limpio = re.sub(r"[<>{}\[\]\\]", "", texto).strip()
    # Reducir espacios múltiples
    limpio = re.sub(r"\s+", " ", limpio)

    if not limpio:
        raise ValueError("El texto contiene caracteres no válidos o está vacío.")
    return limpio


def sanitizar_nombre_archivo(nombre_grupo: str) -> str:
    """
    Convierte el nombre del grupo en un nombre de archivo seguro y válido en cualquier SO.
    Ejemplo: 'Viaje a la playa / 2026??' -> 'Viaje_a_la_playa_2026.json'
    """
    nombre_limpio = sanitizar_texto(nombre_grupo)
    # Reemplazar caracteres no permitidos en sistemas de archivos: \ / : * ? " < > |
    seguro = re.sub(r'[\\/:*?"<>|¿?¡!]', "", nombre_limpio)
    # Reemplazar espacios y guiones repetidos por guión bajo
    seguro = re.sub(r"\s+", "_", seguro)
    seguro = re.sub(r"_+", "_", seguro).strip("._ ")

    if not seguro:
        seguro = "grupo"

    return f"{seguro}.json"


class Gasto:
    """Representa un gasto en el grupo con cálculo dinámico y validaciones estrictas."""

    def __init__(
        self,
        id_gasto: int,
        concepto: str,
        importe: float,
        fecha: str,
        pagador: str,
        divididos: List[str],
    ):
        concepto_limpio = sanitizar_texto(concepto)
        pagador_limpio = sanitizar_texto(pagador)

        try:
            importe_num = round(float(importe), 2)
        except (ValueError, TypeError):
            raise ValueError("El importe debe ser un número válido.")

        if importe_num <= 0:
            raise ValueError("El importe debe ser estrictamente mayor a $0.00.")

        divididos_limpios = [sanitizar_texto(p) for p in divididos]
        if not divididos_limpios:
            raise ValueError("Debe seleccionarse al menos un beneficiario para dividir el gasto.")

        self.id_gasto = id_gasto
        self.concepto = concepto_limpio
        self.importe = importe_num
        self.fecha = fecha.strip() if fecha else datetime.today().strftime("%Y-%m-%d")
        self.pagador = pagador_limpio
        self.divididos = divididos_limpios

    @property
    def cuota_individual(self) -> float:
        """Cálculo dinámico y exacto de la cuota equitativa: Importe / Cantidad de participantes."""
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
            fecha=data.get("fecha", ""),
            pagador=data["pagador"],
            divididos=data["divididos"],
        )


class Grupo:
    """Administra participantes, gastos, saldos y persistencia para un grupo."""

    def __init__(self, nombre: str = "Nuevo Grupo"):
        self._nombre = "Nuevo Grupo"
        self.cambiar_nombre(nombre)
        self.participantes: List[Dict[str, str]] = []  # [{"nombre": str, "rol": str}]
        self.gastos: List[Gasto] = []
        self._contador_gasto_id = 1

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        self.cambiar_nombre(valor)

    def cambiar_nombre(self, nuevo_nombre: str) -> None:
        """Actualiza el nombre del grupo saneando la entrada."""
        self._nombre = sanitizar_texto(nuevo_nombre)

    @property
    def nombres_participantes(self) -> List[str]:
        return [p["nombre"] for p in self.participantes]

    # --- FASE 1 & 2: GESTIÓN DE PARTICIPANTES ---
    def agregar_participante(self, nombre: str, rol: str = "Miembro") -> None:
        """Agrega un participante con validación de no duplicidad y saneamiento."""
        nom_limpio = sanitizar_texto(nombre)
        rol_limpio = sanitizar_texto(rol) if rol else "Miembro"

        if nom_limpio in self.nombres_participantes:
            raise ValueError(f"Ya existe un participante registrado con el nombre '{nom_limpio}'.")

        self.participantes.append({"nombre": nom_limpio, "rol": rol_limpio})

    def editar_participante(self, nombre_actual: str, nuevo_nombre: str, nuevo_rol: Optional[str] = None) -> None:
        """
        Edita un participante y propaga en CASCADA el cambio de nombre
        a todos los gastos donde sea pagador o beneficiario sin perder historial.
        """
        nom_act = sanitizar_texto(nombre_actual)
        nuevo_nom = sanitizar_texto(nuevo_nombre)

        if nom_act not in self.nombres_participantes:
            raise ValueError(f"El participante '{nom_act}' no existe en el grupo.")

        if nuevo_nom != nom_act and nuevo_nom in self.nombres_participantes:
            raise ValueError(f"El nombre '{nuevo_nom}' ya está asignado a otro participante.")

        # Actualizar lista de participantes
        for p in self.participantes:
            if p["nombre"] == nom_act:
                p["nombre"] = nuevo_nom
                if nuevo_rol:
                    p["rol"] = sanitizar_texto(nuevo_rol)
                break

        # Actualización en CASCADA en los gastos
        for gasto in self.gastos:
            if gasto.pagador == nom_act:
                gasto.pagador = nuevo_nom
            if nom_act in gasto.divididos:
                gasto.divididos = [nuevo_nom if part == nom_act else part for part in gasto.divididos]

    def eliminar_participante(self, nombre: str) -> None:
        """Elimina un participante solo si no tiene deudas ni gastos asociados."""
        nom_limpio = sanitizar_texto(nombre)
        if nom_limpio not in self.nombres_participantes:
            raise ValueError(f"El participante '{nom_limpio}' no existe.")

        for gasto in self.gastos:
            if gasto.pagador == nom_limpio:
                raise ValueError(
                    f"No se puede eliminar a '{nom_limpio}' porque figura como pagador en el gasto '{gasto.concepto}'."
                )
            if nom_limpio in gasto.divididos:
                raise ValueError(
                    f"No se puede eliminar a '{nom_limpio}' porque participa en la división del gasto '{gasto.concepto}'."
                )

        self.participantes = [p for p in self.participantes if p["nombre"] != nom_limpio]

    # --- FASE 1: REGISTRO Y CÁLCULO DE GASTOS ---
    def registrar_gasto(
        self,
        concepto: str,
        importe: float,
        fecha: str,
        pagador: str,
        divididos: List[str],
    ) -> Gasto:
        """Registra un nuevo gasto con validación estricta de beneficiarios y pagador."""
        pagador_limpio = sanitizar_texto(pagador)
        if pagador_limpio not in self.nombres_participantes:
            raise ValueError(f"El pagador '{pagador_limpio}' no es un participante registrado en el grupo.")

        divididos_limpios = [sanitizar_texto(p) for p in divididos]
        if not divididos_limpios:
            raise ValueError("Debe seleccionarse al menos un participante para dividir el gasto.")

        for p in divididos_limpios:
            if p not in self.nombres_participantes:
                raise ValueError(f"El participante '{p}' no pertenece al grupo.")

        gasto = Gasto(
            id_gasto=self._contador_gasto_id,
            concepto=concepto,
            importe=importe,
            fecha=fecha,
            pagador=pagador_limpio,
            divididos=divididos_limpios,
        )
        self._contador_gasto_id += 1
        self.gastos.append(gasto)
        return gasto

    def eliminar_gasto(self, id_gasto: int) -> None:
        """Elimina un gasto existente por su identificador."""
        inicial = len(self.gastos)
        self.gastos = [g for g in self.gastos if g.id_gasto != id_gasto]
        if len(self.gastos) == inicial:
            raise ValueError(f"No se encontró el gasto con ID #{id_gasto}.")

    # --- FASE 1 & 2: CÁLCULOS EXACTOS Y AUDITORÍA DE PAGOS ---
    def obtener_auditoria_pagos(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna el desglose de aportes reales de cada miembro:
        - total_pagado: monto total desembolsado por la persona.
        - cantidad_gastos_pagados: cuántas veces pagó.
        - detalle_gastos: lista de conceptos pagados.
        """
        auditoria = {
            nom: {"total_pagado": 0.0, "cantidad_gastos_pagados": 0, "detalle": []}
            for nom in self.nombres_participantes
        }

        for gasto in self.gastos:
            if gasto.pagador in auditoria:
                auditoria[gasto.pagador]["total_pagado"] += gasto.importe
                auditoria[gasto.pagador]["cantidad_gastos_pagados"] += 1
                auditoria[gasto.pagador]["detalle"].append({
                    "id": gasto.id_gasto,
                    "concepto": gasto.concepto,
                    "importe": gasto.importe,
                    "fecha": gasto.fecha,
                })

        for nom in auditoria:
            auditoria[nom]["total_pagado"] = round(auditoria[nom]["total_pagado"], 2)

        return auditoria

    def calcular_saldos_individuales(self) -> Dict[str, Dict[str, float]]:
        """
        Cálculo riguroso de balances:
        Saldo Neto = (Total Pagado por el usuario) - (Cuota Consumida por el usuario)
        Positivo: A favor (recibe dinero)
        Negativo: En contra (debe dinero)
        """
        balances = {
            nom: {"pagado": 0.0, "consumido": 0.0, "saldo": 0.0}
            for nom in self.nombres_participantes
        }

        # 1. Total pagado por cada uno
        for gasto in self.gastos:
            if gasto.pagador in balances:
                balances[gasto.pagador]["pagado"] += gasto.importe

            # 2. Cuota consumida por cada participante incluido en la división
            if gasto.divididos:
                cuota_exacta = gasto.importe / len(gasto.divididos)
                for part in gasto.divididos:
                    if part in balances:
                        balances[part]["consumido"] += cuota_exacta

        # 3. Saldo neto exacto
        for nom in self.nombres_participantes:
            pag = round(balances[nom]["pagado"], 2)
            cons = round(balances[nom]["consumido"], 2)
            balances[nom]["pagado"] = pag
            balances[nom]["consumido"] = cons
            balances[nom]["saldo"] = round(pag - cons, 2)

        return balances

    def calcular_transferencias(self) -> List[Dict[str, Any]]:
        """
        Algoritmo para proponer las transferencias mínimas y liquidar todas las deudas.
        """
        saldos = self.calcular_saldos_individuales()

        deudores: List[List[Any]] = []
        acreedores: List[List[Any]] = []

        for nom, datos in saldos.items():
            s = datos["saldo"]
            if s < -0.009:
                deudores.append([nom, round(abs(s), 2)])
            elif s > 0.009:
                acreedores.append([nom, round(s, 2)])

        transferencias = []
        i = 0
        j = 0
        while i < len(deudores) and j < len(acreedores):
            deudor_nom, deuda = deudores[i]
            acreedor_nom, credito = acreedores[j]

            monto = round(min(deuda, credito), 2)
            if monto > 0:
                transferencias.append({
                    "de": deudor_nom,
                    "a": acreedor_nom,
                    "monto": monto,
                })

            deudores[i][1] = round(deuda - monto, 2)
            acreedores[j][1] = round(credito - monto, 2)

            if deudores[i][1] < 0.01:
                i += 1
            if acreedores[j][1] < 0.01:
                j += 1

        return transferencias

    # --- SERIALIZACIÓN Y PERSISTENCIA SEGURA ---
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "participantes": self.participantes,
            "gastos": [g.to_dict() for g in self.gastos],
            "contador_gasto_id": self._contador_gasto_id,
            "version": "2.0.0",
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        self.cambiar_nombre(data.get("nombre", "Grupo Restaurado"))
        raw_parts = data.get("participantes", [])
        self.participantes = []
        for p in raw_parts:
            if isinstance(p, str):
                self.participantes.append({"nombre": sanitizar_texto(p), "rol": "Miembro"})
            elif isinstance(p, dict):
                self.participantes.append({
                    "nombre": sanitizar_texto(p.get("nombre", "")),
                    "rol": sanitizar_texto(p.get("rol", "Miembro")),
                })

        self.gastos = [Gasto.from_dict(g) for g in data.get("gastos", [])]
        self._contador_gasto_id = data.get(
            "contador_gasto_id",
            max([g.id_gasto for g in self.gastos], default=0) + 1,
        )

    def guardar_en_directorio(self, directorio: str) -> str:
        """
        Guarda el grupo en un archivo saneando automáticamente el nombre.
        Retorna la ruta completa del archivo guardado.
        """
        os.makedirs(directorio, exist_ok=True)
        nombre_arch = sanitizar_nombre_archivo(self.nombre)
        ruta = os.path.join(directorio, nombre_arch)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        return ruta

    def cargar_desde_archivo(self, ruta: str) -> None:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.from_dict(data)


class GestorMultiGrupos:
    """Gestiona múltiples grupos almacenados en un directorio (Fase 2)."""

    def __init__(self, directorio_datos: str):
        self.directorio_datos = directorio_datos
        os.makedirs(self.directorio_datos, exist_ok=True)

    def listar_grupos(self) -> List[Dict[str, Any]]:
        """Escanea el directorio y devuelve la lista de grupos disponibles con metadatos."""
        grupos = []
        if not os.path.exists(self.directorio_datos):
            return grupos

        for archivo in sorted(os.listdir(self.directorio_datos)):
            if archivo.endswith(".json"):
                ruta = os.path.join(self.directorio_datos, archivo)
                try:
                    with open(ruta, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        grupos.append({
                            "archivo": archivo,
                            "ruta": ruta,
                            "nombre": data.get("nombre", archivo[:-5]),
                            "cant_participantes": len(data.get("participantes", [])),
                            "cant_gastos": len(data.get("gastos", [])),
                        })
                except Exception:
                    continue
        return grupos
