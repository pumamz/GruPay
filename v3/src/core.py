"""
Lógica del Dominio - GruPay V3 (Arquitectura Refactorizada y Robustez de Negocio)
Versión 3 del Gestor de Gastos Compartidos.
Cumple con todas las especificaciones de las Fases 1 a 5:
- Inicia 100% en blanco (sin datos mock).
- Rol de Administrador/Organizador Único garantizado.
- Validación estricta de formato de fecha (DD/MM/AAAA).
- Formateador y validador numérico estricto de importes (positivos, máx 2 decimales).
- Saneamiento de texto con Regex.
- Regla de integridad referencial para participantes (bloqueo si tiene gastos).
- Desglose equitativo específico por gasto para máxima transparencia.
"""

from datetime import datetime
import json
import os
import re
from typing import Any, Dict, List, Optional


def sanitizar_texto(texto: str) -> str:
    """
    Sanea texto eliminando caracteres conflictivos (< > { } [ ] \\).
    Lanza ValueError si el texto está vacío o solo contiene espacios.
    """
    if not isinstance(texto, str):
        raise ValueError("El valor ingresado debe ser texto.")

    limpio = re.sub(r"[<>{}\[\]\\]", "", texto).strip()
    limpio = re.sub(r"\s+", " ", limpio)

    if not limpio:
        raise ValueError("El campo no puede estar vacío ni contener solo espacios o caracteres inválidos.")
    return limpio


def sanitizar_nombre_archivo(nombre_grupo: str) -> str:
    """
    Sanea el nombre del grupo para crear un nombre de archivo seguro en cualquier SO.
    """
    nombre_limpio = sanitizar_texto(nombre_grupo)
    seguro = re.sub(r'[\\/:*?"<>|¿?¡!]', "", nombre_limpio)
    seguro = re.sub(r"\s+", "_", seguro)
    seguro = re.sub(r"_+", "_", seguro).strip("._ ")
    if not seguro:
        seguro = "grupo"
    return f"{seguro}.json"


def validar_importe(importe_str: Any) -> float:
    """
    Valida y formatea un importe monetario:
    - Debe ser numérico positivo mayor a 0.
    - Máximo dos decimales.
    - Bloquea signos negativos, letras y ceros.
    """
    if isinstance(importe_str, (int, float)):
        importe_str = f"{importe_str:.2f}"
    elif not isinstance(importe_str, str):
        raise ValueError("El importe debe ser una cadena o número.")

    limpio = importe_str.strip().replace("$", "").strip()

    # Regex estricto: solo dígitos positivos, con parte decimal opcional de 1 o 2 dígitos
    patron = r"^\d+(\.\d{1,2})?$"
    if not re.match(patron, limpio):
        raise ValueError("El importe debe ser un número positivo válido con máximo dos decimales (ej. 120 o 120.50).")

    monto = round(float(limpio), 2)
    if monto <= 0.0:
        raise ValueError("El importe debe ser estrictamente mayor a $0.00.")

    return monto


def validar_fecha(fecha_str: str) -> str:
    """
    Valida que la fecha tenga el formato estricto DD/MM/AAAA y corresponda a una fecha real.
    """
    if not fecha_str or not isinstance(fecha_str, str):
        raise ValueError("La fecha no puede ser nula ni vacía.")

    limpio = fecha_str.strip()
    # Permitir tanto DD/MM/AAAA como DD-MM-AAAA
    limpio = limpio.replace("-", "/")

    partes = limpio.split("/")
    if len(partes) != 3 or len(partes[0]) != 2 or len(partes[1]) != 2 or len(partes[2]) != 4:
        raise ValueError("La fecha debe tener el formato estricto DD/MM/AAAA (ej. 06/10/2026).")

    try:
        dt = datetime.strptime(limpio, "%d/%m/%Y")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        raise ValueError(f"La fecha '{fecha_str}' no es una fecha válida en el calendario.")


class Gasto:
    """Representa un gasto verificado en el grupo."""

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
        self.importe = validar_importe(importe)
        self.fecha = validar_fecha(fecha)
        self.pagador = sanitizar_texto(pagador)

        div_limpios = [sanitizar_texto(p) for p in divididos]
        if not div_limpios:
            raise ValueError("Debe seleccionarse al menos un participante para dividir el gasto.")
        self.divididos = div_limpios

    @property
    def cuota_individual(self) -> float:
        """Cuota exacta por persona en partes iguales."""
        if not self.divididos:
            return 0.0
        return round(self.importe / len(self.divididos), 2)

    def obtener_texto_desglose(self) -> str:
        """
        Retorna la explicación transparente de la división (Fase 5):
        Ej: 'Cena: $120.00. Pagó Carlos. Dividido entre Carlos, Sofía y Mateo a $40.00 c/u.'
        """
        personas_str = ", ".join(self.divididos)
        return (
            f"{self.concepto}: ${self.importe:.2f}. "
            f"Pagó {self.pagador}. "
            f"Dividido entre {len(self.divididos)} personas ({personas_str}) a ${self.cuota_individual:.2f} c/u."
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id_gasto,
            "concepto": self.concepto,
            "importe": self.importe,
            "fecha": self.fecha,
            "pagador": self.pagador,
            "divididos": self.divididos,
            "cuota_individual": self.cuota_individual,
            "texto_desglose": self.obtener_texto_desglose(),
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
    """Entidad principal del grupo en GruPay V3."""

    def __init__(self, nombre: str = "Nuevo Grupo"):
        self._nombre = "Nuevo Grupo"
        self.cambiar_nombre(nombre)
        # Inicialización ESTRICTAMENTE VACÍA (Fase 1: sin datos mock)
        self.participantes: List[Dict[str, str]] = []  # [{"nombre": str, "rol": "Organizador" | "Miembro"}]
        self.gastos: List[Gasto] = []
        self._contador_gasto_id = 1

    @property
    def nombre(self) -> str:
        return self._nombre

    def cambiar_nombre(self, nuevo_nombre: str) -> None:
        self._nombre = sanitizar_texto(nuevo_nombre)

    @property
    def nombres_participantes(self) -> List[str]:
        return [p["nombre"] for p in self.participantes]

    # --- FASE 2: GESTIÓN DE PARTICIPANTES Y REGLA DE ADMINISTRADOR ÚNICO ---
    def agregar_participante(self, nombre: str, rol: str = "Miembro") -> None:
        """
        Agrega un participante validando duplicidad y regla de Administrador Único.
        """
        nom_limpio = sanitizar_texto(nombre)
        rol_limpio = "Organizador" if rol in ["Organizador", "Admin/Organizador", "Admin"] else "Miembro"

        if nom_limpio in self.nombres_participantes:
            raise ValueError(f"Ya existe un participante registrado con el nombre '{nom_limpio}'.")

        # Regla de Administrador Único: Si este usuario es Organizador, remover el rol del previo
        if rol_limpio == "Organizador":
            for p in self.participantes:
                if p["rol"] == "Organizador":
                    p["rol"] = "Miembro"

        self.participantes.append({"nombre": nom_limpio, "rol": rol_limpio})

    def editar_participante(
        self,
        nombre_actual: str,
        nuevo_nombre: str,
        nuevo_rol: Optional[str] = None,
    ) -> None:
        """
        Edita un participante con regla de Administrador Único y actualización en cascada.
        """
        nom_act = sanitizar_texto(nombre_actual)
        nuevo_nom = sanitizar_texto(nuevo_nombre)

        if nom_act not in self.nombres_participantes:
            raise ValueError(f"El participante '{nom_act}' no existe en el grupo.")

        if nuevo_nom != nom_act and nuevo_nom in self.nombres_participantes:
            raise ValueError(f"El nombre '{nuevo_nom}' ya está en uso por otro participante.")

        rol_destino = None
        if nuevo_rol:
            rol_destino = "Organizador" if nuevo_rol in ["Organizador", "Admin/Organizador", "Admin"] else "Miembro"

        # Si se le asigna rol Organizador, removerlo de los demás
        if rol_destino == "Organizador":
            for p in self.participantes:
                if p["nombre"] != nom_act and p["rol"] == "Organizador":
                    p["rol"] = "Miembro"

        # Actualizar en la lista de participantes
        for p in self.participantes:
            if p["nombre"] == nom_act:
                p["nombre"] = nuevo_nom
                if rol_destino:
                    p["rol"] = rol_destino
                break

        # Actualización en cascada en los gastos
        for gasto in self.gastos:
            if gasto.pagador == nom_act:
                gasto.pagador = nuevo_nom
            if nom_act in gasto.divididos:
                gasto.divididos = [nuevo_nom if part == nom_act else part for part in gasto.divididos]

    def eliminar_participante(self, nombre: str) -> None:
        """
        Regla de Integridad Estricta:
        Solo se podrá eliminar un participante si NO tiene gastos asociados.
        """
        nom_limpio = sanitizar_texto(nombre)
        if nom_limpio not in self.nombres_participantes:
            raise ValueError(f"El participante '{nom_limpio}' no existe.")

        # Verificar si figura como pagador
        for gasto in self.gastos:
            if gasto.pagador == nom_limpio:
                raise ValueError(
                    f"Integridad Bloqueada: No se puede eliminar a '{nom_limpio}' porque es el pagador del gasto '{gasto.concepto}'."
                )
            if nom_limpio in gasto.divididos:
                raise ValueError(
                    f"Integridad Bloqueada: No se puede eliminar a '{nom_limpio}' porque participa en la división del gasto '{gasto.concepto}'."
                )

        self.participantes = [p for p in self.participantes if p["nombre"] != nom_limpio]

    # --- FASE 4: REGISTRO DE GASTOS ---
    def registrar_gasto(
        self,
        concepto: str,
        importe: Any,
        fecha: str,
        pagador: str,
        divididos: List[str],
    ) -> Gasto:
        """Registra un nuevo gasto con validaciones estrictas."""
        pagador_limpio = sanitizar_texto(pagador)
        if pagador_limpio not in self.nombres_participantes:
            raise ValueError(f"El pagador '{pagador_limpio}' debe ser un participante registrado.")

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
            pagador=pagador_limpio,
            divididos=div_limpios,
        )
        self._contador_gasto_id += 1
        self.gastos.append(gasto)
        return gasto

    def eliminar_gasto(self, id_gasto: int) -> None:
        inicial = len(self.gastos)
        self.gastos = [g for g in self.gastos if g.id_gasto != id_gasto]
        if len(self.gastos) == inicial:
            raise ValueError(f"No se encontró el gasto con ID #{id_gasto}.")

    # --- FASE 5: TABLA DE DIVISIÓN ESPECÍFICA Y AUDITORÍA ---
    def obtener_desglose_division_especifica(self) -> List[Dict[str, Any]]:
        """
        Retorna la lista de gastos con su desglose equitativo explícito para la tabla de detalle.
        """
        desglose = []
        for g in self.gastos:
            desglose.append({
                "id": g.id_gasto,
                "fecha": g.fecha,
                "concepto": g.concepto,
                "importe": g.importe,
                "pagador": g.pagador,
                "participantes": ", ".join(g.divididos),
                "cant_participantes": len(g.divididos),
                "cuota_individual": g.cuota_individual,
                "texto_desglose": g.obtener_texto_desglose(),
            })
        return desglose

    def calcular_saldos_individuales(self) -> Dict[str, Dict[str, float]]:
        """
        Cálculo riguroso de balances netos:
        Saldo = Pagado - Consumido
        """
        balances = {
            nom: {"pagado": 0.0, "consumido": 0.0, "saldo": 0.0}
            for nom in self.nombres_participantes
        }

        for gasto in self.gastos:
            if gasto.pagador in balances:
                balances[gasto.pagador]["pagado"] += gasto.importe

            if gasto.divididos:
                cuota = gasto.importe / len(gasto.divididos)
                for part in gasto.divididos:
                    if part in balances:
                        balances[part]["consumido"] += cuota

        for nom in self.nombres_participantes:
            pag = round(balances[nom]["pagado"], 2)
            cons = round(balances[nom]["consumido"], 2)
            balances[nom]["pagado"] = pag
            balances[nom]["consumido"] = cons
            balances[nom]["saldo"] = round(pag - cons, 2)

        return balances

    def calcular_transferencias(self) -> List[Dict[str, Any]]:
        """
        Calcula las transferencias óptimas para liquidar todas las deudas.
        """
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
                })

            deudores[i][1] = round(deuda - monto, 2)
            acreedores[j][1] = round(credito - monto, 2)

            if deudores[i][1] < 0.01:
                i += 1
            if acreedores[j][1] < 0.01:
                j += 1

        return transferencias

    # --- FASE 1: PERSISTENCIA Y CARGA LIMPIA ---
    def reiniciar_en_blanco(self, nuevo_nombre: str = "Nuevo Grupo") -> None:
        """Limpia por completo el estado global inicializándolo en blanco."""
        self.cambiar_nombre(nuevo_nombre)
        self.participantes = []
        self.gastos = []
        self._contador_gasto_id = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "participantes": self.participantes,
            "gastos": [g.to_dict() for g in self.gastos],
            "contador_gasto_id": self._contador_gasto_id,
            "version": "3.0.0",
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        self.reiniciar_en_blanco(data.get("nombre", "Grupo Restaurado"))
        raw_parts = data.get("participantes", [])
        for p in raw_parts:
            if isinstance(p, str):
                self.agregar_participante(p, "Miembro")
            elif isinstance(p, dict):
                self.agregar_participante(p.get("nombre", ""), p.get("rol", "Miembro"))

        self.gastos = [Gasto.from_dict(g) for g in data.get("gastos", [])]
        self._contador_gasto_id = data.get(
            "contador_gasto_id",
            max([g.id_gasto for g in self.gastos], default=0) + 1,
        )

    def guardar_en_archivo(self, ruta: str) -> None:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def cargar_desde_archivo(self, ruta: str) -> None:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.from_dict(data)


class GestorMultiGruposV3:
    """Gestiona el listado y cambio de contexto limpio entre múltiples archivos .json."""

    def __init__(self, directorio_datos: str):
        self.directorio_datos = directorio_datos
        os.makedirs(self.directorio_datos, exist_ok=True)

    def listar_grupos(self) -> List[Dict[str, Any]]:
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
