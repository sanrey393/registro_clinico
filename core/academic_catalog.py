# core/academic_catalog.py
# Catálogo compartido de PNF, Trayectos, Secciones y Año Académico

PNF_TRAYECTOS = {
    "No aplica / Externo": [],
    "Informática": ["Trayecto I", "Trayecto II", "Trayecto III", "Trayecto IV"],
    "Agroalimentación": ["Trayecto I", "Trayecto II", "Trayecto III", "Trayecto IV"],
    "Administración de Empresas": ["Trayecto I", "Trayecto II", "Trayecto III", "Trayecto IV"],
    "Veterinaria": ["Trayecto I", "Trayecto II", "Trayecto III", "Trayecto IV", "Trayecto V"],
}

PNF_OPTIONS = list(PNF_TRAYECTOS.keys())
ALL_TRAYECTOS = ["Trayecto I", "Trayecto II", "Trayecto III", "Trayecto IV", "Trayecto V"]


def is_external_pnf(pnf: str) -> bool:
    """Devuelve True si el PNF corresponde a paciente externo o sin PNF."""
    return not pnf or pnf == "No aplica / Externo"


def get_trayectos_for_pnf(pnf: str) -> list[str]:
    """Retorna la lista de trayectos válidos para el PNF indicado."""
    return list(PNF_TRAYECTOS.get(pnf, []))


def normalize_seccion(raw: str) -> str:
    """Normaliza la sección a formato de 2 dígitos ('1' -> '01', '02' -> '02')."""
    val = (raw or "").strip()
    if not val:
        return ""
    if val.isdigit():
        num = int(val)
        if 1 <= num <= 99:
            return f"{num:02d}"
    return val


import re

EMAIL_DOMAINS = [
    "gmail.com",
    "hotmail.com",
    "outlook.com",
    "outlook.es",
    "yahoo.com",
    "yahoo.es",
    "icloud.com",
    "live.com",
    "proton.me",
]


PNF_CODES = {
    "Informática": "INF",
    "Agroalimentación": "AGR",
    "Administración de Empresas": "ADM",
    "Veterinaria": "VET",
    "No aplica / Externo": "EXT",
}

DEFAULT_CONDICIONES_CLINICAS = [
    "Sin especificar",
    "TEA (Trastorno del Espectro Autista)",
    "TDA (Trastorno por Déficit de Atención)",
    "TDAH (Déficit de Atención e Hiperactividad)",
    "Dislexia / Dificultad de Aprendizaje",
    "Trastorno del Lenguaje",
    "Discapacidad Intelectual",
    "Trastorno de Ansiedad",
    "Episodio Depresivo",
    "Estrés Postraumático",
    "Trastorno de Conducta",
]


def generar_codigo_historia(
    pnf: str = "", cedula: str = "", anio: str = "", correlativo: int = 1
) -> str:
    """Genera un código único estándar para la historia clínica: HC-<PNF>-[AÑO]-<CÉDULA>."""
    code = PNF_CODES.get(pnf, "GEN")
    digits = re.sub(r"\D", "", cedula or "")
    anio_clean = re.sub(r"\D", "", str(anio or ""))[:4]
    if digits:
        if anio_clean and not is_external_pnf(pnf):
            return f"HC-{code}-{anio_clean}-{digits}"
        return f"HC-{code}-{digits}"
    return f"HC-{code}-{correlativo:03d}"


def validate_num_historia(raw: str) -> tuple[bool, str]:
    """Valida el formato del número de historia clínica (alfanumérico y guiones, 3-28 chars)."""
    val = (raw or "").strip().upper()
    if len(val) < 3 or len(val) > 28:
        return False, "El N° de Historia debe tener entre 3 y 28 caracteres."
    if not re.fullmatch(r"[A-Z0-9\-]+", val):
        return False, "El N° de Historia solo permite letras, números y guiones (ej: HC-INF-2026-12345678)."
    if re.search(r"(.)\1{4,}", val.replace("-", "")):
        return False, "El N° de Historia contiene caracteres repetidos inválidos."
    return True, ""


def validate_cedula_num(raw: str) -> tuple[bool, str]:
    """Valida que el número de cédula contenga entre 6 y 9 dígitos."""
    val = (raw or "").strip()
    if not val.isdigit() or not (6 <= len(val) <= 9):
        return False, "La cédula debe contener entre 6 y 9 dígitos numéricos."
    if len(set(val)) == 1:
        return False, "La cédula ingresada no es válida (dígitos repetidos)."
    return True, ""


def validate_telefono_num(raw: str) -> tuple[bool, str]:
    """Valida que el teléfono (sin prefijo) tenga exactamente 7 dígitos si se ingresa."""
    val = (raw or "").strip()
    if not val:
        return True, ""
    if not val.isdigit() or len(val) != 7:
        return False, "El teléfono debe tener exactamente 7 dígitos después del prefijo (ej: 1234567)."
    return True, ""


def validate_person_name(raw_name: str) -> tuple[bool, str]:
    """Valida nombre y apellido evitando spam, símbolos o palabras absurdamente largas."""
    name = " ".join((raw_name or "").strip().split())
    if len(name) < 3:
        return False, "El nombre y apellido debe tener al menos 3 caracteres."
    if len(name) > 80:
        return False, "El nombre y apellido no puede superar los 80 caracteres."
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü'\-\s]+", name):
        return False, "El nombre solo puede contener letras y espacios (sin números ni símbolos)."
    if re.search(r"(.)\1{3,}", name.replace(" ", "").lower()):
        return False, "El nombre contiene caracteres repetidos inválidos."
    words = name.split()
    if len(words) < 2:
        return False, "Ingresa al menos un nombre y un apellido."
    if any(len(w) > 25 for w in words):
        return False, "Alguna palabra del nombre es demasiado larga; verifica que sea un nombre real."
    return True, ""


def is_valid_seccion(raw: str) -> bool:
    """Valida que la sección sea un número entre 01 y 99."""
    val = (raw or "").strip()
    if not val or not val.isdigit():
        return False
    num = int(val)
    return 1 <= num <= 99
