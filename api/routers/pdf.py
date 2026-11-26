import os
import tempfile
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

from api.deps import get_current_user
from ui.dialogs.pdf_generator import (
    generar_pdf_receta,
    generar_pdf_sesion,
    generar_pdf_cita_consulta,
    generar_pdf_expediente,
    generar_pdf_historia_clinica,
    generar_pdf_listado_pacientes,
    generar_pdf_listado_historias,
    generar_pdf_agenda_citas,
)

router = APIRouter(prefix="/api/pdf", tags=["PDF ReportLab"])


def _cleanup_file(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def _stream_pdf(fn, filename: str, background_tasks: BackgroundTasks, *args) -> FileResponse:
    fd, tmp_path = tempfile.mkstemp(suffix=".pdf", prefix="psique_")
    os.close(fd)
    try:
        fn(tmp_path, *args)
    except Exception as e:
        _cleanup_file(tmp_path)
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {e}")

    background_tasks.add_task(_cleanup_file, tmp_path)
    return FileResponse(
        path=tmp_path,
        media_type="application/pdf",
        filename=filename,
    )


@router.post("/receta")
def pdf_receta(
    payload: dict[str, Any],
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    nombre = str(payload.get("paciente_nombre", "Paciente")).replace(" ", "_")
    return _stream_pdf(generar_pdf_receta, f"Receta_{nombre}.pdf", background_tasks, payload)


@router.post("/sesion")
def pdf_sesion(
    payload: dict[str, Any],
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    nombre = str(payload.get("paciente_nombre", "Paciente")).replace(" ", "_")
    return _stream_pdf(generar_pdf_sesion, f"Sesion_{nombre}.pdf", background_tasks, payload)


@router.post("/cita")
def pdf_cita(
    payload: dict[str, Any],
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    nombre = str(payload.get("paciente_nombre", "Paciente")).replace(" ", "_")
    return _stream_pdf(generar_pdf_cita_consulta, f"Cita_{nombre}.pdf", background_tasks, payload)


@router.post("/expediente")
def pdf_expediente(
    payload: dict[str, Any],
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    paciente = payload.get("paciente", {})
    sesiones = payload.get("sesiones", [])
    recetas = payload.get("recetas", [])
    nombre = str(paciente.get("nombre", "Paciente")).replace(" ", "_")
    return _stream_pdf(
        generar_pdf_expediente,
        f"Expediente_{nombre}.pdf",
        background_tasks,
        paciente,
        sesiones,
        recetas,
    )


@router.post("/historia")
def pdf_historia(
    payload: dict[str, Any],
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    nombre = str(payload.get("nombre", "Paciente")).replace(" ", "_")
    return _stream_pdf(generar_pdf_historia_clinica, f"HistoriaClinica_{nombre}.pdf", background_tasks, payload)


@router.post("/listado-pacientes")
def pdf_listado_pacientes(
    payload: dict[str, Any],
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    pacientes = payload.get("pacientes", [])
    filtros = payload.get("filtros", {})
    return _stream_pdf(
        generar_pdf_listado_pacientes,
        "Listado_Pacientes_PSIQUE.pdf",
        background_tasks,
        pacientes,
        filtros,
    )


@router.post("/listado-historias")
def pdf_listado_historias(
    payload: dict[str, Any],
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    historias = payload.get("historias", [])
    filtros = payload.get("filtros", {})
    return _stream_pdf(
        generar_pdf_listado_historias,
        "Listado_Historias_PSIQUE.pdf",
        background_tasks,
        historias,
        filtros,
    )


@router.post("/agenda-citas")
def pdf_agenda_citas(
    payload: dict[str, Any],
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    citas = payload.get("citas", [])
    titulo = payload.get("titulo_filtro", "")
    return _stream_pdf(
        generar_pdf_agenda_citas,
        "Agenda_Citas_PSIQUE.pdf",
        background_tasks,
        citas,
        titulo,
    )
