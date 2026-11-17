# data/farmacos_catalogo.py
# Catálogo completo de fármacos con información clínica, posología e interacciones.
import os
import json

FARMACOS_PREDETERMINADOS = [
    {
        "id": "farm_01",
        "nombre_comercial": "Tylenol / Tempra",
        "nombre_generico": "Paracetamol (Acetaminofén)",
        "laboratorio": "Sanofi / Johnson & Johnson",
        "descripcion_indicaciones": "Analgésico y antipirético eficaz de primera línea. Indicado para el tratamiento sintomático del dolor de intensidad leve a moderada (cefaleas, odontalgias, mialgias) y reducción de la fiebre.",
        "contraindicaciones": "Hipersensibilidad al paracetamol o excipientes. Insuficiencia hepatocelular grave o hepatitis vírica activa. Precaución en alcoholismo crónico y desnutrición.",
        "efectos_secundarios": "Raros a dosis terapéuticas: erupciones cutáneas, náuseas, elevación transitoria de transaminasas. En sobredosis: necrosis hepática potencialmente fatal.",
        "interacciones": "El consumo concomitante de alcohol potencia el riesgo de daño hepático. Puede aumentar el efecto de anticoagulantes (Warfarina) con uso diario prolongado.",
        "recetacion_dosis": "Adultos: 500 mg a 1000 mg por vía oral cada 6 u 8 horas (dosis máxima 4000 mg/día). Niños: 10-15 mg/kg cada 6 horas. Administrar con abundante agua."
    },
    {
        "id": "farm_02",
        "nombre_comercial": "Advil / Motrin / Actron",
        "nombre_generico": "Ibuprofeno",
        "laboratorio": "Pfizer / Bayer",
        "descripcion_indicaciones": "Antiinflamatorio no esteroideo (AINE) con potente acción analgésica y antipirética. Indicado en artritis, dolores musculares, dismenorrea, cefalea y cuadros febriles.",
        "contraindicaciones": "Úlcera péptica activa o hemorragia digestiva previa. Insuficiencia renal o cardíaca severa. Tercer trimestre de embarazo. Asma inducida por AINEs.",
        "efectos_secundarios": "Dispepsia, ardor epigástrico, náuseas, pirosis, mareo, retención de líquidos. Mayor riesgo cardiovascular con dosis elevadas continuadas.",
        "interacciones": "Reduce la eficacia de antihipertensivos (IECA, ARA-II, betabloqueantes). Aumenta riesgo hemorrágico con aspirina, anticoagulantes y corticoides.",
        "recetacion_dosis": "Adultos: 400 mg a 600 mg cada 6 u 8 horas con las comidas (máximo 2400 mg/día). Procesos leves: 200 mg a 400 mg cada 6 a 8 horas."
    },
    {
        "id": "farm_03",
        "nombre_comercial": "Amoxil / Clavulin",
        "nombre_generico": "Amoxicilina",
        "laboratorio": "GSK (GlaxoSmithKline)",
        "descripcion_indicaciones": "Antibiótico betalactámico bactericida de amplio espectro. Indicado en infecciones del tracto respiratorio superior/inferior, otitis media, faringoamigdalitis, sinusitis e infecciones odontológicas.",
        "contraindicaciones": "Alergia conocida a penicilinas o betalactámicos. Mononucleosis infecciosa (riesgo muy alto de exantema eritematoso).",
        "efectos_secundarios": "Diarrea, náuseas, vómitos, candidiasis mucocutánea, erupción cutánea alérgica, prurito.",
        "interacciones": "Puede reducir la eficacia de anticonceptivos orales. El alopurinol eleva el riesgo de exantema cutáneo. El probenecid prolonga sus niveles plasmáticos.",
        "recetacion_dosis": "Adultos: 500 mg cada 8 horas u 875 mg cada 12 horas por 7 a 10 días según criterio médico. Completar el ciclo indicado con o sin alimentos."
    },
    {
        "id": "farm_04",
        "nombre_comercial": "Zoloft / Altruline",
        "nombre_generico": "Sertralina Clorhidrato",
        "laboratorio": "Pfizer",
        "descripcion_indicaciones": "Antidepresivo inhibidor selectivo de la recaptación de serotonina (ISRS). Indicado en trastorno depresivo mayor, trastorno de pánico, trastorno obsesivo-compulsivo (TOC), fobia social y TEPT.",
        "contraindicaciones": "Hipersensibilidad a sertralina. Uso concomitante con inhibidores de la MAO (IMAO) o pimozida. No indicado en menores sin control psiquiátrico.",
        "efectos_secundarios": "Náuseas, insomnio o somnolencia diurna, temblor, mareos, diarrea, sequedad bucal, disfunción sexual (retardo eyaculatorio, anorgasmia).",
        "interacciones": "Riesgo de síndrome serotoninérgico severo al combinarse con tramadol, triptanos, hierba de San Juan u otros antidepresivos. Eleva riesgo de sangrado con AINEs.",
        "recetacion_dosis": "Dosis inicial: 50 mg una vez al día (preferentemente por la mañana con el desayuno). Puede titularse en incrementos de 50 mg hasta un máximo de 200 mg/día."
    },
    {
        "id": "farm_05",
        "nombre_comercial": "Rivotril / Klonopin / Neuryl",
        "nombre_generico": "Clonazepam",
        "laboratorio": "Roche",
        "descripcion_indicaciones": "Benzodiacepina de acción intermedia y prolongada con marcadas propiedades ansiolíticas, sedantes, miorrelajantes y anticonvulsivantes. Indicado en crisis de angustia, ansiedad severa y epilepsia.",
        "contraindicaciones": "Miastenia gravis, insuficiencia respiratoria severa, apnea del sueño, glaucoma de ángulo estrecho, intoxicación alcohólica aguda, embarazo.",
        "efectos_secundarios": "Sedación, fatiga, somnolencia, ataxia, dificultades de concentración, enlentecimiento psicomotor. Riesgo de tolerancia y dependencia.",
        "interacciones": "Depresión respiratoria grave y coma al combinarse con alcohol, opioides u otros depresores centrales del SNC.",
        "recetacion_dosis": "Ansiedad y crisis: 0.25 mg a 0.5 mg cada 12 horas, ajustando gradualmente hasta 1 mg a 2 mg diarios. Venta y dispensación bajo receta médica archivada."
    },
    {
        "id": "farm_06",
        "nombre_comercial": "Losec / Genoprazol / Pepticum",
        "nombre_generico": "Omeprazol",
        "laboratorio": "AstraZeneca",
        "descripcion_indicaciones": "Inhibidor de la bomba de protones (IBP) gástrica. Indicado en reflujo gastroesofágico (ERGE), esofagitis erosiva, úlcera péptica gástrica y duodenal, y como gastroprotector en polifarmacia.",
        "contraindicaciones": "Hipersensibilidad a benzimidazoles. Coadministración con medicamentos antirretrovirales como nelfinavir o rilpivirina.",
        "efectos_secundarios": "Cefalea, dolor abdominal, diarrea o estreñimiento, flatulencias. Con uso prolongado: hipomagnesemia y posible déficit de absorción de vitamina B12.",
        "interacciones": "Reduce la absorción gástrica de antifúngicos azólicos (ketoconazol, itraconazol) y hierro. Puede aumentar niveles de fenitoína y diazepam.",
        "recetacion_dosis": "20 mg a 40 mg una vez al día por la mañana en ayunas (30 a 45 minutos antes del desayuno) durante 4 a 8 semanas según severidad."
    },
    {
        "id": "farm_07",
        "nombre_comercial": "Cozaar / Presartan / Angiotrofin",
        "nombre_generico": "Losartán Potásico",
        "laboratorio": "Merck Sharp & Dohme (MSD)",
        "descripcion_indicaciones": "Antagonista selectivo de los receptores de angiotensina II (ARA-II). Indicado en hipertensión arterial esencial, nefropatía en pacientes con diabetes tipo 2 y prevención de eventos cerebrovasculares.",
        "contraindicaciones": "Hipersensibilidad al losartán. Segundo y tercer trimestre de embarazo (riesgo teratogénico y daño fetal). Insuficiencia hepática grave.",
        "efectos_secundarios": "Mareos ortostáticos, hipotensión, fatiga, hiperpotasemia. Incidencia de tos seca notablemente menor que con los inhibidores ECA.",
        "interacciones": "Riesgo de hiperpotasemia al asociar con diuréticos ahorradores de potasio o suplementos de K+. Los AINEs disminuyen su respuesta antihipertensiva.",
        "recetacion_dosis": "Dosis inicial usual: 50 mg una vez al día. Puede ajustarse a 100 mg una vez al día según control tensional y evolución clínica del paciente."
    },
    {
        "id": "farm_08",
        "nombre_comercial": "Ventolin / Aerolin",
        "nombre_generico": "Salbutamol (Albuterol)",
        "laboratorio": "GSK (GlaxoSmithKline)",
        "descripcion_indicaciones": "Broncodilatador agonista adrenérgico beta-2 de acción rápida. Tratamiento y prevención del broncoespasmo agudo en crisis asmáticas, asma inducida por ejercicio y EPOC.",
        "contraindicaciones": "Hipersensibilidad demostrada al principio activo. Manejo de amenaza de aborto o parto prematuro no institucional.",
        "efectos_secundarios": "Temblor fino de extremidades, taquicardia sinusal, palpitaciones, cefalea, sensación de nerviosismo e hipopotasemia transitoria.",
        "interacciones": "Los betabloqueantes no selectivos (propranolol) bloquean completamente el efecto broncodilatador y pueden desencadenar broncoespasmo severo.",
        "recetacion_dosis": "Inhalador presurizado (100 mcg/puff): 1 a 2 inhalaciones de rescate ante inicio de síntomas (hasta 4 veces al día según indicación). Agitar bien antes de usar."
    },
    {
        "id": "farm_09",
        "nombre_comercial": "Glucophage / Glafornil",
        "nombre_generico": "Metformina Clorhidrato",
        "laboratorio": "Merck Serono",
        "descripcion_indicaciones": "Antihiperglicemiante oral del grupo de las biguanidas. Tratamiento de primera línea de diabetes mellitus tipo 2, prediabetes y síndrome de ovario poliquístico.",
        "contraindicaciones": "Insuficiencia renal moderada a severa (TFG < 30 mL/min). Acidosis metabólica aguda, cetoacidosis diabética, insuficiencia cardíaca o respiratoria descompensada.",
        "efectos_secundarios": "Síntomas digestivos al inicio: náuseas, diarrea acuosa, distensión abdominal, sabor metálico. Muy rara pero grave: acidosis láctica.",
        "interacciones": "Suspender temporalmente 48 horas previas a estudios con medios de contraste yodados. Los corticoides sistémicos contrarrestan su efecto hipoglucemiante.",
        "recetacion_dosis": "Iniciar con 500 mg u 850 mg con la comida principal para mitigar molestias digestivas. Ajustar semanalmente hasta 1500-2000 mg/día repartidos en 2 o 3 tomas."
    },
    {
        "id": "farm_10",
        "nombre_comercial": "Prozac / Daforin",
        "nombre_generico": "Fluoxetina Clorhidrato",
        "laboratorio": "Eli Lilly",
        "descripcion_indicaciones": "Antidepresivo ISRS con acción energizante y antidepresiva. Indicado en depresión mayor, trastorno obsesivo-compulsivo (TOC), bulimia nerviosa y trastorno de pánico.",
        "contraindicaciones": "Hipersensibilidad al fármaco. Asociación con IMAO (esperar al menos 5 semanas entre la interrupción de fluoxetina y el inicio de un IMAO).",
        "efectos_secundarios": "Insomnio, anorexia, pérdida leve de peso, nerviosismo, cefaleas, náuseas, temblores, disminución del deseo sexual.",
        "interacciones": "Inhibidor potente del CYP2D6: eleva niveles de antidepresivos tricíclicos, flecainida y carvedilol. Evitar consumo simultáneo con hipérico.",
        "recetacion_dosis": "20 mg al día por la mañana con el desayuno. En bulimia nerviosa o TOC resistente puede incrementarse de forma gradual hasta 60 mg/día."
    },
    {
        "id": "farm_11",
        "nombre_comercial": "Aspirina / Cardioaspirina",
        "nombre_generico": "Ácido Acetilsalicílico",
        "laboratorio": "Bayer",
        "descripcion_indicaciones": "Antiagregante plaquetario y analgésico antipirético. Indicado en prevención secundaria de infarto agudo de miocardio, accidente isquémico transitorio y angina inestable.",
        "contraindicaciones": "Úlcera gastroduodenal activa, diátesis hemorrágica, hemofilia, asma por salicilatos, niños y adolescentes con varicela o gripe (Síndrome de Reye).",
        "efectos_secundarios": "Riesgo de sangrado digestivo, epigastralgia, tinnitus a dosis altas, prolongación del tiempo de sangría, reacciones alérgicas.",
        "interacciones": "Suma de riesgo hemorrágico con anticoagulantes (Warfarina, heparina, DOACs) y otros AINEs. Disminuye la acción uricosúrica del probenecid.",
        "recetacion_dosis": "Antiagregante plaquetario: 81 mg a 100 mg al día por vía oral en dosis única diaria tras una comida. Analgésico/antipirético: 500 mg cada 6h."
    },
    {
        "id": "farm_12",
        "nombre_comercial": "Claritin / Civeran",
        "nombre_generico": "Loratadina",
        "laboratorio": "Bayer / Schering-Plough",
        "descripcion_indicaciones": "Antihistamínico H1 de segunda generación no sedante. Indicado para el alivio sintomático de rinitis alérgica estacional y perenne, conjuntivitis alérgica y urticaria idiopática crónica.",
        "contraindicaciones": "Hipersensibilidad a la loratadina o a sus componentes. Precaución en insuficiencia hepática severa.",
        "efectos_secundarios": "Poco frecuentes: somnolencia leve en pacientes susceptibles, cefalea, aumento de apetito, sequedad de boca, fatiga.",
        "interacciones": "Inhibidores del CYP3A4 o CYP2D6 (como eritromicina, ketoconazol, cimetidina) pueden aumentar concentraciones plasmáticas de loratadina sin toxicidad clínicamente relevante.",
        "recetacion_dosis": "Adultos y niños mayores de 12 años: 10 mg una vez al día por vía oral (con o sin alimentos). Niños de 2 a 12 años (>30kg): 10 mg/día; (<30kg): 5 mg/día en jarabe."
    }
]

# Catálogo simple original mantenido para compatibilidad con recetas existentes
FARMACOS = [
    {"nombre": f["nombre_generico"].split()[0], "principio": f["nombre_generico"], "presentacion": "Comprimidos", "dosis": f["recetacion_dosis"].split(":")[0], "frecuencia": "según prescripción"}
    for f in FARMACOS_PREDETERMINADOS
]

_DB_PATH = os.path.join(os.path.dirname(__file__), "farmacos_registrados.json")


def _cargar_datos_locales() -> list:
    """Carga los fármacos guardados localmente o inicializa con los predeterminados."""
    if os.path.exists(_DB_PATH):
        try:
            with open(_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception as e:
            print(f"[WARN] Error al leer {_DB_PATH}: {e}")
    
    # Si no existe archivo local, guardar la lista inicial predeterminada
    _guardar_datos_locales(FARMACOS_PREDETERMINADOS)
    return list(FARMACOS_PREDETERMINADOS)


def _guardar_datos_locales(lista_farmacos: list) -> bool:
    """Guarda la lista de fármacos en archivo JSON local."""
    try:
        with open(_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(lista_farmacos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] Error al guardar en {_DB_PATH}: {e}")
        return False


def obtener_catalogo_completo() -> list:
    """Retorna todos los fármacos registrados."""
    return _cargar_datos_locales()


def guardar_o_actualizar_farmaco(farmaco: dict) -> dict:
    """Guarda un nuevo fármaco o actualiza uno existente por id."""
    catalogo = _cargar_datos_locales()
    
    farmaco_id = farmaco.get("id")
    if not farmaco_id:
        import time
        farmaco_id = f"farm_{int(time.time() * 1000)}"
        farmaco["id"] = farmaco_id
        catalogo.insert(0, farmaco)
    else:
        actualizado = False
        for idx, item in enumerate(catalogo):
            if item.get("id") == farmaco_id:
                catalogo[idx] = farmaco
                actualizado = True
                break
        if not actualizado:
            catalogo.insert(0, farmaco)
            
    _guardar_datos_locales(catalogo)
    return farmaco


def eliminar_farmaco(farmaco_id: str) -> bool:
    """Elimina un fármaco del catálogo por su ID."""
    catalogo = _cargar_datos_locales()
    inicial = len(catalogo)
    catalogo = [f for f in catalogo if f.get("id") != farmaco_id]
    if len(catalogo) < inicial:
        return _guardar_datos_locales(catalogo)
    return False


def buscar_farmacos(termino: str = "", laboratorio: str = "") -> list:
    """Filtra fármacos por término (nombre comercial, genérico, indicación) y/o laboratorio."""
    catalogo = _cargar_datos_locales()
    t = termino.strip().lower()
    lab = laboratorio.strip().lower()
    
    resultados = []
    for f in catalogo:
        # Filtro de laboratorio
        if lab and lab != "todos" and lab not in f.get("laboratorio", "").lower():
            continue
            
        # Filtro de término
        if not t:
            resultados.append(f)
            continue
            
        candidatos = [
            f.get("nombre_comercial", ""),
            f.get("nombre_generico", ""),
            f.get("laboratorio", ""),
            f.get("descripcion_indicaciones", ""),
            f.get("contraindicaciones", ""),
            f.get("efectos_secundarios", ""),
            f.get("interacciones", ""),
            f.get("recetacion_dosis", ""),
        ]
        if any(t in c.lower() for c in candidatos):
            resultados.append(f)
            
    return resultados


def obtener_laboratorios() -> list:
    """Devuelve la lista única ordenada de laboratorios presentes en el catálogo."""
    catalogo = _cargar_datos_locales()
    labs = set()
    for f in catalogo:
        lab_str = f.get("laboratorio", "").strip()
        if lab_str:
            # Si hay múltiples separados por slash o coma, separarlos
            for parte in lab_str.replace("/", ",").split(","):
                p = parte.strip()
                if p:
                    labs.add(p)
    return sorted(list(labs))
