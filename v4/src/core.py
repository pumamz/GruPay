"""
Lógica del Dominio - GruPay V4 (Cumplimiento Estricto de los 5 RNF)
Versión 4 del Gestor de Gastos Compartidos.
Cumple con:
- RNF1: Formateo monetario estándar ($ X,XXX.XX) y auto-formato decimal (onBlur).
- RNF2: Validación y bloqueo de registros incompletos.
- RNF3: Optimización O(N) con lectura única en memoria hash y memoización de resultados.
- RNF4: Exportación automática e importación protegida con validación estricta de esquema.
- RNF5: Semántica visual de saldos (verde/rojo/gris con textos e iconos explícitos).
"""

from datetime import datetime
import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple


def formatear_moneda(monto: float, simbolo: str = "$") -> str:
    """
    RNF1: Formatea un valor monetario aplicando símbolo, separador de miles y 2 decimales.
    Ejemplo: 1250.5 -> '$ 1,250.50'
    """
    monto_redondeado = round(float(monto), 2)
    # Formato con coma de miles y punto decimal
    return f"{simbolo} {monto_redondeado:,.2f}"


def autoformatear_monto_texto(texto: str) -> str:
    """
    RNF1: Al perder foco (onBlur), toma el número ingresado y lo completa matemáticamente
    para que siempre muestre dos decimales.
    Ejemplos: '50' -> '50.00', '15' -> '15.00', '120.5' -> '120.50'.
    Lanza ValueError si el texto no es un número positivo válido.
    """
    if not texto:
        return ""
    limpio = texto.strip().replace("$", "").replace(",", "").strip()
    if not limpio:
        return ""

    # Verificar que solo contenga dígitos y como máximo un punto
    if not re.match(r"^\d+(\.\d+)?$", limpio):
        raise ValueError("El importe solo puede contener números y un punto decimal.")

    monto = float(limpio)
    if monto <= 0.0:
        raise ValueError("El importe debe ser mayor a 0.")

    return f"{monto:.2f}"


def es_caracter_monto_permitido(char_ingresado: str, texto_futuro: str) -> bool:
    """
    RNF1: Validador de teclado en tiempo real. Bloquea signos negativos, letras y caracteres no numéricos.
    Solo permite dígitos del 0 al 9 y un único punto decimal con máximo 2 decimales.
    """
    if not char_ingresado:
        return True

    # Bloquear signos negativos y cualquier carácter alfabético o especial
    if char_ingresado in "-+eE abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return False

    # El texto resultante solo puede tener dígitos y hasta un punto
    if not re.match(r"^\d*(\.\d{0,2})?$", texto_futuro):
        return False

    return True


def validar_fecha_estricta(fecha_str: str) -> str:
    """
    RNF2: Valida que la fecha tenga el formato DD/MM/AAAA y exista en el calendario.
    """
    if not fecha_str or not isinstance(fecha_str, str):
        raise ValueError("La fecha no puede estar vacía.")

    limpio = fecha_str.strip().replace("-", "/")
    partes = limpio.split("/")
    if len(partes) != 3 or len(partes[0]) != 2 or len(partes[1]) != 2 or len(partes[2]) != 4:
        raise ValueError("Formato de fecha inválido. Debe ser DD/MM/AAAA (ej. 06/10/2026).")

    try:
        dt = datetime.strptime(limpio, "%d/%m/%Y")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        raise ValueError(f"La fecha '{fecha_str}' no es una fecha válida en el calendario.")


def validar_esquema_archivo(data: Any) -> Tuple[bool, str]:
    """
    RNF4: Inspecciona exhaustivamente el contenido de un archivo JSON antes de cargarlo
    para verificar que no esté corrupto y cumpla con el esquema requerido.
    """
    if not isinstance(data, dict):
        return False, "El archivo debe contener un objeto JSON raíz válido."

    if "participantes" not in data or not isinstance(data["participantes"], list):
        return False, "El archivo carece de la lista requerida de 'participantes'."

    if "gastos" not in data or not isinstance(data["gastos"], list):
        return False, "El archivo carece de la lista requerida de 'gastos'."

    # Validar participantes
    nombres_vistos = set()
    for idx, p in enumerate(data["participantes"]):
        if isinstance(p, str):
            nom = p.strip()
        elif isinstance(p, dict) and "nombre" in p:
            nom = str(p["nombre"]).strip()
        else:
            return False, f"El participante en la posición {idx + 1} no tiene un formato válido."

        if not nom:
            return False, f"El participante en la posición {idx + 1} tiene un nombre vacío."
        nombres_vistos.add(nom)

    # Validar gastos (tickets)
    for idx, g in enumerate(data["gastos"]):
        if not isinstance(g, dict):
            return False, f"El gasto en la posición {idx + 1} no es un objeto válido."

        for campo in ["concepto", "importe", "pagador", "divididos"]:
            if campo not in g:
                return False, f"El gasto #{idx + 1} no contiene el campo obligatorio '{campo}'."

        try:
            monto = float(g["importe"])
            if monto <= 0:
                return False, f"El gasto #{idx + 1} tiene un importe menor o igual a cero."
        except (ValueError, TypeError):
            return False, f"El importe del gasto #{idx + 1} no es numérico."

        if not isinstance(g["divididos"], list) or len(g["divididos"]) == 0:
            return False, f"El gasto #{idx + 1} debe dividirse entre al menos una persona."

        pagador = str(g["pagador"]).strip()
        if pagador not in nombres_vistos:
            return False, f"El pagador '{pagador}' del gasto #{idx + 1} no figura en la lista de participantes."

        for part in g["divididos"]:
            if str(part).strip() not in nombres_vistos:
                return False, f"El participante '{part}' en la división del gasto #{idx + 1} no pertenece al grupo."

    return True, "Esquema verificado correctamente."


def sanitizar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        raise ValueError("El valor debe ser una cadena de texto.")
    limpio = re.sub(r"[<>{}\[\]\\]", "", texto).strip()
    limpio = re.sub(r"\s+", " ", limpio)
    if not limpio:
        raise ValueError("El campo de texto no puede estar vacío.")
    return limpio


class Gasto:
    """Entidad Gasto para V4."""

    def __init__(
        self,
        id_gasto: int,
        concepto: str,
        importe: float,
        fecha: str,
        pagador: str,
        divididos: List[str],
    ):
        self.id_gasto = id_gasto
        self.concepto = sanitizar_texto(concepto)
        self.importe = round(float(importe), 2)
        if self.importe <= 0:
            raise ValueError("El importe debe ser mayor a 0.")
        self.fecha = validar_fecha_estricta(fecha)
        self.pagador = sanitizar_texto(pagador)
        self.divididos = [sanitizar_texto(p) for p in divididos]
        if not self.divididos:
            raise ValueError("Debe existir al menos un beneficiario para dividir el gasto.")

    @property
    def cuota_individual(self) -> float:
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


class GrupoV4:
    """
    Grupo de gastos optimizado para RNF3 (O(N) single-pass con memoización)
    y RNF4 (protección ante corrupción de archivos).
    """

    def __init__(self, nombre: str = "Nuevo Grupo"):
        self._nombre = sanitizar_texto(nombre) if nombre else "Nuevo Grupo"
        self.participantes: List[Dict[str, str]] = []  # [{"nombre": str, "rol": str}]
        self.gastos: List[Gasto] = []
        self._contador_gasto_id = 1

        # RNF3: Memoria de resultados (Memoization) y flag de datos modificados
        self._datos_modificados: bool = True
        self._cache_saldos: Optional[Dict[str, Dict[str, Any]]] = None
        self._cache_transferencias: Optional[List[Dict[str, Any]]] = None

    @property
    def nombre(self) -> str:
        return self._nombre

    def cambiar_nombre(self, nuevo_nombre: str) -> None:
        self._nombre = sanitizar_texto(nuevo_nombre)
        self._datos_modificados = True

    @property
    def nombres_participantes(self) -> List[str]:
        return [p["nombre"] for p in self.participantes]

    def invalidar_cache(self) -> None:
        """Marca los datos como modificados para que el próximo cálculo actualice el caché."""
        self._datos_modificados = True
        self._cache_saldos = None
        self._cache_transferencias = None

    def agregar_participante(self, nombre: str, rol: str = "Miembro") -> None:
        nom = sanitizar_texto(nombre)
        rol_limpio = "Organizador" if rol in ["Organizador", "Admin/Organizador", "Admin"] else "Miembro"

        if nom in self.nombres_participantes:
            raise ValueError(f"Ya existe un participante llamado '{nom}'.")

        if rol_limpio == "Organizador":
            for p in self.participantes:
                if p["rol"] == "Organizador":
                    p["rol"] = "Miembro"

        self.participantes.append({"nombre": nom, "rol": rol_limpio})
        self.invalidar_cache()

    def editar_participante(self, nombre_actual: str, nuevo_nombre: str, nuevo_rol: Optional[str] = None) -> None:
        nom_act = sanitizar_texto(nombre_actual)
        nuevo_nom = sanitizar_texto(nuevo_nombre)

        if nom_act not in self.nombres_participantes:
            raise ValueError(f"El participante '{nom_act}' no existe.")

        if nuevo_nom != nom_act and nuevo_nom in self.nombres_participantes:
            raise ValueError(f"El nombre '{nuevo_nom}' ya está en uso.")

        rol_destino = None
        if nuevo_rol:
            rol_destino = "Organizador" if nuevo_rol in ["Organizador", "Admin/Organizador", "Admin"] else "Miembro"

        if rol_destino == "Organizador":
            for p in self.participantes:
                if p["nombre"] != nom_act and p["rol"] == "Organizador":
                    p["rol"] = "Miembro"

        for p in self.participantes:
            if p["nombre"] == nom_act:
                p["nombre"] = nuevo_nom
                if rol_destino:
                    p["rol"] = rol_destino
                break

        for gasto in self.gastos:
            if gasto.pagador == nom_act:
                gasto.pagador = nuevo_nom
            if nom_act in gasto.divididos:
                gasto.divididos = [nuevo_nom if part == nom_act else part for part in gasto.divididos]

        self.invalidar_cache()

    def eliminar_participante(self, nombre: str) -> None:
        nom = sanitizar_texto(nombre)
        if nom not in self.nombres_participantes:
            raise ValueError(f"El participante '{nom}' no existe.")

        for gasto in self.gastos:
            if gasto.pagador == nom:
                raise ValueError(f"Bloqueo: '{nom}' es pagador del gasto '{gasto.concepto}'.")
            if nom in gasto.divididos:
                raise ValueError(f"Bloqueo: '{nom}' participa en la división del gasto '{gasto.concepto}'.")

        self.participantes = [p for p in self.participantes if p["nombre"] != nom]
        self.invalidar_cache()

    def registrar_gasto(
        self,
        concepto: str,
        importe: float,
        fecha: str,
        pagador: str,
        divididos: List[str],
    ) -> Gasto:
        pag_limpio = sanitizar_texto(pagador)
        if pag_limpio not in self.nombres_participantes:
            raise ValueError(f"El pagador '{pag_limpio}' no pertenece al grupo.")

        div_limpios = [sanitizar_texto(p) for p in divididos]
        if not div_limpios:
            raise ValueError("Debe seleccionarse al menos un participante para dividir el gasto.")

        for p in div_limpios:
            if p not in self.nombres_participantes:
                raise ValueError(f"El participante '{p}' no pertenece al grupo.")

        gasto = Gasto(
            id_gasto=self._contador_gasto_id,
            concepto=concepto,
            importe=importe,
            fecha=fecha,
            pagador=pag_limpio,
            divididos=div_limpios,
        )
        self._contador_gasto_id += 1
        self.gastos.append(gasto)
        self.invalidar_cache()
        return gasto

    def eliminar_gasto(self, id_gasto: int) -> None:
        ini = len(self.gastos)
        self.gastos = [g for g in self.gastos if g.id_gasto != id_gasto]
        if len(self.gastos) == ini:
            raise ValueError(f"No se encontró el gasto con ID #{id_gasto}.")
        self.invalidar_cache()

    # --- RNF3: ESTRATEGIA DE CÁLCULO DIRECTO O(N) CON MEMORIA DE RESULTADOS ---
    def calcular_saldos_individuales(self) -> Dict[str, Dict[str, Any]]:
        """
        RNF3:
        1. Si no hay modificaciones de datos, devuelve el resultado memorizado (O(1)).
        2. Si hay cambios, crea un directorio hash interno con saldos en cero.
        3. Realiza un RECORRIDO ÚNICO de los gastos sumando al pagador y restando la cuota.
        """
        if not self._datos_modificados and self._cache_saldos is not None:
            return self._cache_saldos

        # Directorio temporal interno con todos los miembros en cero
        directorio_saldos: Dict[str, Dict[str, Any]] = {
            nom: {"pagado": 0.0, "consumido": 0.0, "saldo": 0.0}
            for nom in self.nombres_participantes
        }

        # RECORRIDO ÚNICO: Leer el historial completo de gastos una única vez
        for gasto in self.gastos:
            pagador = gasto.pagador
            monto = gasto.importe
            divs = gasto.divididos

            if pagador in directorio_saldos:
                directorio_saldos[pagador]["pagado"] += monto

            if divs:
                cuota = monto / len(divs)
                for part in divs:
                    if part in directorio_saldos:
                        directorio_saldos[part]["consumido"] += cuota

        # Consolidar saldos finales y enriquecer con semántica visual (RNF5)
        for nom in self.nombres_participantes:
            pag = round(directorio_saldos[nom]["pagado"], 2)
            cons = round(directorio_saldos[nom]["consumido"], 2)
            saldo = round(pag - cons, 2)

            estado_semantico = self.interpretar_estado_financiero(saldo)

            directorio_saldos[nom]["pagado"] = pag
            directorio_saldos[nom]["consumido"] = cons
            directorio_saldos[nom]["saldo"] = saldo
            directorio_saldos[nom]["semantica"] = estado_semantico

        self._cache_saldos = directorio_saldos
        self._datos_modificados = False
        return self._cache_saldos

    # --- RNF5: INTERPRETACIÓN VISUAL Y SEMÁNTICA FINANCIERA ---
    @staticmethod
    def interpretar_estado_financiero(saldo: float) -> Dict[str, Any]:
        """
        RNF5:
        - Saldo positivo: Color verde, texto 'Recibe dinero', ícono '+ / ▲', monto positivo.
        - Saldo negativo: Color rojo, texto 'Debe dinero', ícono '- / ▼', omitiendo signo menos.
        - Saldo cero: Tono gris/neutro, texto 'Cuentas saldadas', ícono '✓'.
        """
        if saldo > 0.009:
            return {
                "estado": "positivo",
                "color": "#059669",  # Verde esmeralda accesible
                "texto": "Recibe dinero",
                "icono": "▲ (+)",
                "monto_visual": formatear_moneda(saldo),
            }
        elif saldo < -0.009:
            return {
                "estado": "negativo",
                "color": "#dc2626",  # Rojo visible
                "texto": "Debe dinero",
                "icono": "▼ (-)",
                "monto_visual": formatear_moneda(abs(saldo)),  # Omitir el signo menos
            }
        else:
            return {
                "estado": "cero",
                "color": "#64748b",  # Gris neutro
                "texto": "Cuentas saldadas",
                "icono": "✓",
                "monto_visual": formatear_moneda(0.0),
            }

    def calcular_transferencias(self) -> List[Dict[str, Any]]:
        """Calcula las transferencias óptimas memorizando el resultado."""
        if not self._datos_modificados and self._cache_transferencias is not None:
            return self._cache_transferencias

        saldos = self.calcular_saldos_individuales()
        deudores: List[List[Any]] = []
        acreedores: List[List[Any]] = []

        for nom, d in saldos.items():
            s = d["saldo"]
            if s < -0.009:
                deudores.append([nom, round(abs(s), 2)])
            elif s > 0.009:
                acreedores.append([nom, round(s, 2)])

        transferencias = []
        i, j = 0, 0
        while i < len(deudores) and j < len(acreedores):
            deudor_nom, deuda = deudores[i]
            acreedor_nom, credito = acreedores[j]

            monto = round(min(deuda, credito), 2)
            if monto > 0:
                transferencias.append({
                    "de": deudor_nom,
                    "a": acreedor_nom,
                    "monto": monto,
                    "monto_formateado": formatear_moneda(monto),
                })

            deudores[i][1] = round(deuda - monto, 2)
            acreedores[j][1] = round(credito - monto, 2)

            if deudores[i][1] < 0.01:
                i += 1
            if acreedores[j][1] < 0.01:
                j += 1

        self._cache_transferencias = transferencias
        return self._cache_transferencias

    # --- RNF4: PERSISTENCIA Y PROTECCIÓN DE DATOS ANTE CORRUPCIÓN ---
    def a_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "participantes": self.participantes,
            "gastos": [g.to_dict() for g in self.gastos],
            "contador_gasto_id": self._contador_gasto_id,
            "version": "4.0.0",
        }

    def guardar_en_archivo(self, ruta: str) -> None:
        """RNF4: Exporta y empaqueta en JSON asegurando formato estándar."""
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.a_dict(), f, indent=2, ensure_ascii=False)

    def cargar_con_proteccion(self, ruta: str) -> None:
        """
        RNF4: Inspecciona el interior del archivo antes de cargar.
        Si no cumple con el esquema requerido o está corrupto, aborta inmediatamente
        y mantiene intactos los datos actuales sin modificar la instancia.
        """
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"El archivo '{ruta}' no existe.")

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Archivo corrupto o no es JSON válido: {str(e)}")

        es_valido, motivo = validar_esquema_archivo(data)
        if not es_valido:
            # Abortar inmediatamente manteniendo intacto el estado actual
            raise ValueError(f"Protección del Sistema activada: El archivo no cumple con el esquema requerido ({motivo}).")

        # Cargar de forma segura
        self._nombre = sanitizar_texto(data.get("nombre", "Grupo Restaurado"))
        self.participantes = []
        for p in data["participantes"]:
            if isinstance(p, str):
                self.participantes.append({"nombre": sanitizar_texto(p), "rol": "Miembro"})
            elif isinstance(p, dict):
                self.participantes.append({
                    "nombre": sanitizar_texto(p.get("nombre", "")),
                    "rol": sanitizar_texto(p.get("rol", "Miembro")),
                })

        self.gastos = [Gasto.from_dict(g) for g in data["gastos"]]
        self._contador_gasto_id = data.get(
            "contador_gasto_id",
            max([g.id_gasto for g in self.gastos], default=0) + 1,
        )
        self.invalidar_cache()
