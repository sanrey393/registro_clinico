from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.deps import get_current_user, get_db, serialize_firestore
from core.academic_catalog import (
    PNF_TRAYECTOS,
    PNF_OPTIONS,
    ALL_TRAYECTOS,
    DEFAULT_CONDICIONES_CLINICAS,
)
from data.cie10_catalogo import CIE10_CATALOGO
from data.farmacos_catalogo import FARMACOS_PREDETERMINADOS
from database.firebase_manager import FirebaseManager

router = APIRouter(prefix="/api", tags=["Clínica"])


def _verify_ownership(db: FirebaseManager, collection: str, doc_id: str, uid: str) -> dict:
    doc = db._db.collection(collection).document(doc_id).get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado.")
    data = doc.to_dict() or {}
    doc_uid = data.get("user_id")
    if doc_uid and doc_uid != uid and not data.get("is_global"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso sobre este registro.")
    return data | {"id": doc.id}


# ── Dashboard Summary ─────────────────────────────────────────
@router.get("/dashboard/summary")
def dashboard_summary(user: dict = Depends(get_current_user), db: FirebaseManager = Depends(get_db)):
    uid = user["uid"]
    pacientes = db.obtener_pacientes(solo_activos=True, user_id=uid)
    citas = db.obtener_citas(user_id=uid)
    sesiones = db.obtener_sesiones(user_id=uid)
    historias = db.obtener_historias_clinicas(user_id=uid)
    recetas = db.obtener_todas_recetas(user_id=uid)
    facturas = db.obtener_facturas(user_id=uid)

    hoy_iso = datetime.now().strftime("%Y-%m-%d")
    hoy_dmy = datetime.now().strftime("%d/%m/%Y")
    citas_hoy = [
        c for c in citas
        if str(c.get("fecha", "")).strip() in (hoy_iso, hoy_dmy)
    ]
    citas_programadas = [
        c for c in citas if str(c.get("estado", "")).lower() in ("programada", "confirmada", "pendiente")
    ]

    total_cobrado = sum(
        float(f.get("monto", 0) or 0)
        for f in facturas
        if str(f.get("estado", "")).lower() in ("pagada", "pagado", "completada")
    )
    total_pendiente = sum(
        float(f.get("monto", 0) or 0)
        for f in facturas
        if str(f.get("estado", "")).lower() in ("pendiente", "por cobrar")
    )

    return serialize_firestore({
        "counts": {
            "pacientes": len(pacientes),
            "citas": len(citas),
            "citas_hoy": len(citas_hoy),
            "citas_programadas": len(citas_programadas),
            "sesiones": len(sesiones),
            "historias": len(historias),
            "recetas": len(recetas),
            "facturas": len(facturas),
            "total_cobrado": round(total_cobrado, 2),
            "total_pendiente": round(total_pendiente, 2),
        },
        "citas_hoy": citas_hoy[:10],
        "ultimos_pacientes": pacientes[:6],
    })


# ── Pacientes ─────────────────────────────────────────────────
@router.get("/pacientes")
def list_pacientes(
    solo_activos: bool = Query(True),
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    items = db.obtener_pacientes(solo_activos=solo_activos, user_id=user["uid"])
    return serialize_firestore(items)


@router.post("/pacientes", status_code=status.HTTP_201_CREATED)
def create_paciente(
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    data = dict(payload)
    data["user_id"] = user["uid"]
    new_id = db.crear_paciente(data)
    if not new_id:
        raise HTTPException(status_code=500, detail="No se pudo crear el paciente.")
    return serialize_firestore(data | {"id": new_id})


@router.put("/pacientes/{paciente_id}")
def update_paciente(
    paciente_id: str,
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "pacientes", paciente_id, user["uid"])
    data = {k: v for k, v in payload.items() if k not in ("id", "user_id", "fecha_registro")}
    if not db.actualizar_paciente(paciente_id, data):
        raise HTTPException(status_code=500, detail="No se pudo actualizar el paciente.")
    return {"ok": True, "id": paciente_id}


@router.delete("/pacientes/{paciente_id}")
def delete_paciente(
    paciente_id: str,
    borrado_logico: bool = Query(True),
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "pacientes", paciente_id, user["uid"])
    if not db.eliminar_paciente(paciente_id, borrado_logico=borrado_logico):
        raise HTTPException(status_code=500, detail="No se pudo eliminar el paciente.")
    return {"ok": True}


# ── Citas ─────────────────────────────────────────────────────
@router.get("/citas")
def list_citas(user: dict = Depends(get_current_user), db: FirebaseManager = Depends(get_db)):
    return serialize_firestore(db.obtener_citas(user_id=user["uid"]))


@router.post("/citas", status_code=status.HTTP_201_CREATED)
def create_cita(
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    data = dict(payload)
    data["user_id"] = user["uid"]
    new_id = db.crear_cita(data)
    if not new_id:
        raise HTTPException(status_code=500, detail="No se pudo crear la cita.")
    return serialize_firestore(data | {"id": new_id})


@router.put("/citas/{cita_id}")
def update_cita(
    cita_id: str,
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "citas", cita_id, user["uid"])
    data = {k: v for k, v in payload.items() if k not in ("id", "user_id", "created_at")}
    if not db.actualizar_cita(cita_id, data):
        raise HTTPException(status_code=500, detail="No se pudo actualizar la cita.")
    return {"ok": True, "id": cita_id}


@router.delete("/citas/{cita_id}")
def delete_cita(
    cita_id: str,
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "citas", cita_id, user["uid"])
    if not db.eliminar_cita(cita_id):
        raise HTTPException(status_code=500, detail="No se pudo eliminar la cita.")
    return {"ok": True}


# ── Sesiones Clínicas ─────────────────────────────────────────
@router.get("/sesiones")
def list_sesiones(
    paciente_id: str | None = Query(None),
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    items = db.obtener_sesiones(user_id=user["uid"])
    if paciente_id:
        items = [s for s in items if s.get("paciente_id") == paciente_id]
    return serialize_firestore(items)


@router.post("/sesiones", status_code=status.HTTP_201_CREATED)
def create_sesion(
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    data = dict(payload)
    data["user_id"] = user["uid"]
    new_id = db.crear_sesion(data)
    if not new_id:
        raise HTTPException(status_code=500, detail="No se pudo crear la sesión.")
    return serialize_firestore(data | {"id": new_id})


@router.put("/sesiones/{sesion_id}")
def update_sesion(
    sesion_id: str,
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    try:
        _verify_ownership(db, "sesiones", sesion_id, user["uid"])
    except HTTPException as ex:
        if ex.status_code == 404:
            _verify_ownership(db, "sesiones_clinicas", sesion_id, user["uid"])
        else:
            raise
    data = {k: v for k, v in payload.items() if k not in ("id", "user_id", "fecha_registro")}
    if not db.actualizar_sesion(sesion_id, data):
        raise HTTPException(status_code=500, detail="No se pudo actualizar la sesión.")
    return {"ok": True, "id": sesion_id}


@router.delete("/sesiones/{sesion_id}")
def delete_sesion(
    sesion_id: str,
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    try:
        _verify_ownership(db, "sesiones", sesion_id, user["uid"])
    except HTTPException as ex:
        if ex.status_code == 404:
            _verify_ownership(db, "sesiones_clinicas", sesion_id, user["uid"])
        else:
            raise
    if not db.eliminar_sesion(sesion_id):
        raise HTTPException(status_code=500, detail="No se pudo eliminar la sesión.")
    return {"ok": True}


# ── Historias Clínicas ────────────────────────────────────────
@router.get("/historias")
def list_historias(user: dict = Depends(get_current_user), db: FirebaseManager = Depends(get_db)):
    return serialize_firestore(db.obtener_historias_clinicas(user_id=user["uid"]))


@router.post("/historias", status_code=status.HTTP_201_CREATED)
def create_historia(
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    data = dict(payload)
    data["user_id"] = user["uid"]
    new_id = db.crear_historia_clinica(data)
    if not new_id:
        raise HTTPException(status_code=500, detail="No se pudo crear la historia clínica.")
    return serialize_firestore(data | {"id": new_id})


@router.put("/historias/{historia_id}")
def update_historia(
    historia_id: str,
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "historias_clinicas", historia_id, user["uid"])
    data = {k: v for k, v in payload.items() if k not in ("id", "user_id", "created_at")}
    if not db.actualizar_historia_clinica(historia_id, data):
        raise HTTPException(status_code=500, detail="No se pudo actualizar la historia clínica.")
    return {"ok": True, "id": historia_id}


@router.delete("/historias/{historia_id}")
def delete_historia(
    historia_id: str,
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "historias_clinicas", historia_id, user["uid"])
    if not db.eliminar_historia_clinica(historia_id):
        raise HTTPException(status_code=500, detail="No se pudo eliminar la historia clínica.")
    return {"ok": True}


# ── Recetas ───────────────────────────────────────────────────
@router.get("/recetas")
def list_recetas(
    paciente_id: str | None = Query(None),
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    items = db.obtener_todas_recetas(user_id=user["uid"])
    if paciente_id:
        items = [r for r in items if r.get("paciente_id") == paciente_id]
    return serialize_firestore(items)


@router.post("/recetas", status_code=status.HTTP_201_CREATED)
def create_receta(
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    data = dict(payload)
    data["user_id"] = user["uid"]
    new_id = db.crear_receta(data)
    if not new_id:
        raise HTTPException(status_code=500, detail="No se pudo crear la receta.")
    return serialize_firestore(data | {"id": new_id})


@router.put("/recetas/{receta_id}")
def update_receta(
    receta_id: str,
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "recetas", receta_id, user["uid"])
    data = {k: v for k, v in payload.items() if k not in ("id", "user_id", "fecha_emision")}
    if not db.actualizar_receta(receta_id, data):
        raise HTTPException(status_code=500, detail="No se pudo actualizar la receta.")
    return {"ok": True, "id": receta_id}


@router.delete("/recetas/{receta_id}")
def delete_receta(
    receta_id: str,
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "recetas", receta_id, user["uid"])
    if not db.eliminar_receta(receta_id):
        raise HTTPException(status_code=500, detail="No se pudo eliminar la receta.")
    return {"ok": True}


# ── Fármacos ──────────────────────────────────────────────────
@router.get("/farmacos")
def list_farmacos(user: dict = Depends(get_current_user), db: FirebaseManager = Depends(get_db)):
    custom = db.obtener_farmacos(user_id=user["uid"])
    return serialize_firestore({"base": FARMACOS_PREDETERMINADOS, "custom": custom})


@router.post("/farmacos", status_code=status.HTTP_201_CREATED)
def create_farmaco(
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    data = dict(payload)
    data["user_id"] = user["uid"]
    new_id = db.crear_farmaco(data)
    if not new_id:
        raise HTTPException(status_code=500, detail="No se pudo registrar el fármaco.")
    return serialize_firestore(data | {"id": new_id})


@router.put("/farmacos/{farmaco_id}")
def update_farmaco(
    farmaco_id: str,
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "farmacos", farmaco_id, user["uid"])
    data = {k: v for k, v in payload.items() if k not in ("id", "user_id")}
    if not db.actualizar_farmaco(farmaco_id, data):
        raise HTTPException(status_code=500, detail="No se pudo actualizar el fármaco.")
    return {"ok": True, "id": farmaco_id}


@router.delete("/farmacos/{farmaco_id}")
def delete_farmaco(
    farmaco_id: str,
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "farmacos", farmaco_id, user["uid"])
    if not db.eliminar_farmaco(farmaco_id):
        raise HTTPException(status_code=500, detail="No se pudo eliminar el fármaco.")
    return {"ok": True}


# ── Facturación ───────────────────────────────────────────────
@router.get("/facturas")
def list_facturas(user: dict = Depends(get_current_user), db: FirebaseManager = Depends(get_db)):
    return serialize_firestore(db.obtener_facturas(user_id=user["uid"]))


@router.post("/facturas", status_code=status.HTTP_201_CREATED)
def create_factura(
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    data = dict(payload)
    data["user_id"] = user["uid"]
    new_id = db.crear_factura(data)
    if not new_id:
        raise HTTPException(status_code=500, detail="No se pudo crear la factura.")
    return serialize_firestore(data | {"id": new_id})


@router.put("/facturas/{factura_id}")
def update_factura(
    factura_id: str,
    payload: dict[str, Any],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    _verify_ownership(db, "facturas", factura_id, user["uid"])
    data = {k: v for k, v in payload.items() if k not in ("id", "user_id", "fecha_emision")}
    if not db.actualizar_factura(factura_id, data):
        raise HTTPException(status_code=500, detail="No se pudo actualizar la factura.")
    return {"ok": True, "id": factura_id}


# ── Catálogos (CIE-10, Académico, Condiciones) ────────────────
@router.get("/catalogs")
def get_catalogs(user: dict = Depends(get_current_user), db: FirebaseManager = Depends(get_db)):
    condiciones_custom = db.obtener_condiciones_clinicas(user_id=user["uid"])
    condiciones = sorted(set(DEFAULT_CONDICIONES_CLINICAS + condiciones_custom), key=str.lower)
    return {
        "cie10": CIE10_CATALOGO,
        "pnf_trayectos": PNF_TRAYECTOS,
        "pnf": PNF_OPTIONS,
        "trayectos": ALL_TRAYECTOS,
        "condiciones_clinicas": condiciones,
    }


@router.post("/catalogs/condiciones", status_code=status.HTTP_201_CREATED)
def add_condicion(
    payload: dict[str, str],
    user: dict = Depends(get_current_user),
    db: FirebaseManager = Depends(get_db),
):
    nombre = (payload.get("nombre") or "").strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio.")
    ref = db._db.collection("diagnosticos_catalogo").add({
        "nombre": nombre,
        "user_id": user["uid"],
    })
    return {"id": ref[1].id, "nombre": nombre}
