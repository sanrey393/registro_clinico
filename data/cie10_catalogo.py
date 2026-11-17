# data/cie10_catalogo.py
# Catálogo referencial CIE-10 para autocompletado en consultas y citas clínicas

CIE10_CATALOGO = [
    # ── Salud Mental y Psicología (Capítulo V - Trastornos Mentales y del Comportamiento) ──
    {"codigo": "F32.0", "descripcion": "Episodio depresivo leve"},
    {"codigo": "F32.1", "descripcion": "Episodio depresivo moderado"},
    {"codigo": "F32.2", "descripcion": "Episodio depresivo grave sin síntomas psicóticos"},
    {"codigo": "F33.1", "descripcion": "Trastorno depresivo recurrente, episodio actual moderado"},
    {"codigo": "F34.1", "descripcion": "Distimia (Trastorno depresivo persistente)"},
    {"codigo": "F40.0", "descripcion": "Agorafobia"},
    {"codigo": "F40.1", "descripcion": "Fobia social"},
    {"codigo": "F41.0", "descripcion": "Trastorno de pánico (ansiedad episódica paroxística)"},
    {"codigo": "F41.1", "descripcion": "Trastorno de ansiedad generalizada (TAG)"},
    {"codigo": "F41.2", "descripcion": "Trastorno mixto ansioso-depresivo"},
    {"codigo": "F42",   "descripcion": "Trastorno obsesivo-compulsivo (TOC)"},
    {"codigo": "F43.0", "descripcion": "Reacción al estrés agudo"},
    {"codigo": "F43.1", "descripcion": "Trastorno de estrés postraumático (TEPT)"},
    {"codigo": "F43.2", "descripcion": "Trastornos de adaptación"},
    {"codigo": "F45.0", "descripcion": "Trastorno de somatización"},
    {"codigo": "F50.0", "descripcion": "Anorexia nerviosa"},
    {"codigo": "F50.2", "descripcion": "Bulimia nerviosa"},
    {"codigo": "F51.0", "descripcion": "Insomnio no orgánico"},
    {"codigo": "F80.0", "descripcion": "Trastorno específico de la pronunciación (Dislalia)"},
    {"codigo": "F80.1", "descripcion": "Trastorno del lenguaje expresivo"},
    {"codigo": "F81.0", "descripcion": "Trastorno específico de la lectura (Dislexia)"},
    {"codigo": "F81.2", "descripcion": "Trastorno específico de las habilidades aritméticas (Discalculia)"},
    {"codigo": "F84.0", "descripcion": "Autismo en la niñez (Trastorno del Espectro Autista)"},
    {"codigo": "F84.5", "descripcion": "Síndrome de Asperger"},
    {"codigo": "F90.0", "descripcion": "Trastorno por déficit de atención con hiperactividad (TDAH)"},
    {"codigo": "F91.0", "descripcion": "Trastorno de la conducta limitado al ámbito familiar"},
    {"codigo": "F91.3", "descripcion": "Trastorno de oposición desafiante (TOD)"},
    {"codigo": "F98.0", "descripcion": "Enuresis no orgánica"},
    {"codigo": "F98.5", "descripcion": "Tartamudez (Espasmofemia)"},

    # ── Neurología y Síntomas Generales ──
    {"codigo": "G40.9", "descripcion": "Epilepsia, tipo no especificado"},
    {"codigo": "G43.9", "descripcion": "Migraña, no especificada"},
    {"codigo": "G44.2", "descripcion": "Cefalea tensional"},
    {"codigo": "R51",   "descripcion": "Cefalea (dolor de cabeza)"},
    {"codigo": "R53",   "descripcion": "Malestar y fatiga / Astenia"},

    # ── Medicina General y Enfermedades Crónicas ──
    {"codigo": "I10",   "descripcion": "Hipertensión arterial esencial (primaria)"},
    {"codigo": "E11.9", "descripcion": "Diabetes mellitus tipo 2 sin complicaciones"},
    {"codigo": "E66.9", "descripcion": "Obesidad, no especificada"},
    {"codigo": "E03.9", "descripcion": "Hipotiroidismo, no especificado"},
    {"codigo": "J00",   "descripcion": "Rinofaringitis aguda (Resfriado común)"},
    {"codigo": "J02.9", "descripcion": "Faringitis aguda, no especificada"},
    {"codigo": "J20.9", "descripcion": "Bronquitis aguda, no especificada"},
    {"codigo": "J45.9", "descripcion": "Asma, no especificada"},
    {"codigo": "K29.7", "descripcion": "Gastritis, no especificada"},
    {"codigo": "K21.9", "descripcion": "Enfermedad por reflujo gastroesofágico sin esofagitis"},
    {"codigo": "M54.5", "descripcion": "Lumbago no especificado"},
    {"codigo": "Z00.0", "descripcion": "Examen médico general / Chequeo de rutina"},
    {"codigo": "Z73.0", "descripcion": "Estado de agotamiento vital (Síndrome de Burnout)"},
]

def get_cie10_display_list() -> list[str]:
    """Retorna la lista de diagnósticos en formato '[CÓDIGO] Descripción'."""
    return [f"[{item['codigo']}] {item['descripcion']}" for item in CIE10_CATALOGO]

def buscar_cie10(query: str) -> list[dict]:
    """Busca diagnósticos por código o palabra clave."""
    q = query.lower().strip()
    if not q:
        return []
    return [
        item for item in CIE10_CATALOGO
        if q in item['codigo'].lower() or q in item['descripcion'].lower()
    ]
