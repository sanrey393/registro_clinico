# ui/dialogs/pdf_generator.py
# Generador de documentos PDF clínicos usando ReportLab

import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para numerar páginas dinámicamente."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        texto = f"Página {self._pageNumber} de {page_count} — Sistema de Registro Clínico"
        self.drawRightString(letter[0] - 36, 25, texto)
        self.drawString(36, 25, "Documento Médico Confidencial — Válido bajo normativa vigente")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 35, letter[0] - 36, 35)
        self.restoreState()


def _get_base_styles():
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        'ClinicaTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        'ClinicaSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        'DocSectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1e40af"),
        spaceBefore=8,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b")
    ))
    styles.add(ParagraphStyle(
        'CellTextBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0f172a")
    ))
    styles.add(ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    ))
    styles.add(ParagraphStyle(
        'IndicacionesText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    ))
    return styles


def generar_pdf_receta(filepath: str, datos: dict) -> str:
    """
    Genera un PDF con formato de Receta Médica.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )

    styles = _get_base_styles()
    story = []

    # ── Encabezado Institucional ──
    header_data = [
        [
            Paragraph("<b>CENTRO MÉDICO & REGISTRO CLÍNICO</b>", styles['ClinicaTitle']),
            Paragraph(f"<b>FECHA:</b> {datos.get('fecha', datetime.date.today().strftime('%d/%m/%Y'))}", styles['CellTextBold'])
        ],
        [
            Paragraph("Atención Primaria y Especializada • Consulta y Tratamiento", styles['ClinicaSubtitle']),
            Paragraph("<b>RECETA MÉDICA</b>", ParagraphStyle('RMBold', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#2563eb"), alignment=2))
        ]
    ]
    t_header = Table(header_data, colWidths=[380, 160])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)

    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb"), spaceBefore=6, spaceAfter=10))

    # ── Datos Médico y Paciente ──
    medico = datos.get('medico', 'Médico Tratante') or 'Médico Tratante'
    esp = datos.get('especialidad', 'Medicina General') or 'Medicina General'
    paciente = datos.get('paciente_nombre', 'Paciente') or 'Paciente'

    info_box_data = [
        [
            Paragraph(f"<b>PACIENTE:</b> {paciente}", styles['CellText']),
            Paragraph(f"<b>DR(A):</b> {medico}", styles['CellText']),
        ],
        [
            Paragraph(f"<b>RÉGIMEN:</b> Ambulatorio", styles['CellText']),
            Paragraph(f"<b>ESPECIALIDAD:</b> {esp}", styles['CellText']),
        ]
    ]
    t_info = Table(info_box_data, colWidths=[270, 270])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))

    # ── Título Rp/ ──
    story.append(Paragraph("<b>Rp / Prescripción Farmacológica:</b>", styles['DocSectionTitle']))

    # ── Tabla de Medicamentos ──
    meds = datos.get('medicamentos', [])
    meds_data = [
        [
            Paragraph("<b>Medicamento / Fármaco</b>", styles['HeaderCell']),
            Paragraph("<b>Presentación</b>", styles['HeaderCell']),
            Paragraph("<b>Dosis</b>", styles['HeaderCell']),
            Paragraph("<b>Frecuencia</b>", styles['HeaderCell']),
            Paragraph("<b>Duración</b>", styles['HeaderCell'])
        ]
    ]

    for m in meds:
        farmaco = m.get('farmaco', '') or '—'
        pres = m.get('presentacion', '') or '—'
        dosis = m.get('dosis', '') or '—'
        frec = m.get('frecuencia', '') or '—'
        dur = m.get('duracion', '') or '—'
        meds_data.append([
            Paragraph(f"<b>{farmaco}</b>", styles['CellTextBold']),
            Paragraph(pres, styles['CellText']),
            Paragraph(dosis, styles['CellText']),
            Paragraph(frec, styles['CellText']),
            Paragraph(dur, styles['CellText']),
        ])

    if len(meds_data) == 1:
        meds_data.append([
            Paragraph("Sin medicamentos prescritos", styles['CellText']),
            Paragraph("—", styles['CellText']),
            Paragraph("—", styles['CellText']),
            Paragraph("—", styles['CellText']),
            Paragraph("—", styles['CellText'])
        ])

    t_meds = Table(meds_data, colWidths=[150, 100, 95, 115, 80])
    t_meds.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t_meds)
    story.append(Spacer(1, 15))

    # ── Instrucciones especiales / Advertencias ──
    instrucciones = datos.get('instrucciones', '').strip()
    if instrucciones:
        story.append(Paragraph("<b>Indicaciones y Advertencias al Paciente:</b>", styles['DocSectionTitle']))
        inst_table = Table([[Paragraph(instrucciones.replace('\n', '<br/>'), styles['IndicacionesText'])]], colWidths=[540])
        inst_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef9c3")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#fde047")),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(inst_table)
        story.append(Spacer(1, 20))

    # ── Firma y Sello ──
    story.append(Spacer(1, 35))
    firma_data = [
        [
            Paragraph("", styles['CellText']),
            Paragraph(f"____________________________________________<br/><b>Dr(a). {medico}</b><br/>{esp}<br/>Firma y Sello Médico", ParagraphStyle('Firma', fontName='Helvetica', fontSize=9, alignment=1, leading=13))
        ]
    ]
    t_firma = Table(firma_data, colWidths=[240, 300])
    t_firma.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ]))
    story.append(KeepTogether([t_firma]))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath


def generar_pdf_sesion(filepath: str, datos: dict) -> str:
    """
    Genera un PDF con el resumen de una Sesión Clínica individual.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )

    styles = _get_base_styles()
    story = []

    # Encabezado
    story.append(Paragraph("<b>CENTRO MÉDICO & REGISTRO CLÍNICO</b>", styles['ClinicaTitle']))
    story.append(Paragraph(f"INFORME DE CONSULTA MÉDICA — {datos.get('tipo', 'Consulta General')}", styles['ClinicaSubtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284c7"), spaceBefore=4, spaceAfter=10))

    # Datos Generales
    paciente_str = datos.get('paciente_nombre', 'Paciente')
    fecha_str = datos.get('fecha', datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
    tipo_str = datos.get('tipo', 'Control')

    box_general = [
        [
            Paragraph(f"<b>Paciente:</b> {paciente_str}", styles['CellText']),
            Paragraph(f"<b>Fecha / Hora:</b> {fecha_str}", styles['CellText']),
            Paragraph(f"<b>Tipo:</b> {tipo_str}", styles['CellText'])
        ]
    ]
    t_gen = Table(box_general, colWidths=[240, 160, 140])
    t_gen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#bbf7d0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#bbf7d0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_gen)
    story.append(Spacer(1, 10))

    # Motivo y Anamnesis
    story.append(Paragraph("<b>1. Motivo de Consulta y Enfermedad Actual</b>", styles['DocSectionTitle']))
    motivo = datos.get('motivo', 'No especificado').strip() or 'No especificado'
    anamnesis = datos.get('anamnesis', 'Sin datos adicionales').strip() or 'Sin datos adicionales'

    ma_data = [
        [Paragraph("<b>Motivo:</b>", styles['CellTextBold']), Paragraph(motivo.replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Enfermedad actual:</b>", styles['CellTextBold']), Paragraph(anamnesis.replace('\n', '<br/>'), styles['CellText'])]
    ]
    t_ma = Table(ma_data, colWidths=[120, 420])
    t_ma.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_ma)
    story.append(Spacer(1, 10))

    # Signos Vitales
    story.append(Paragraph("<b>2. Signos Vitales y Examen Físico</b>", styles['DocSectionTitle']))
    vitals_data = [
        [
            Paragraph("<b>TA:</b> " + (datos.get('ta', '—') or '—') + " mmHg", styles['CellText']),
            Paragraph("<b>FC:</b> " + (datos.get('fc', '—') or '—') + " lpm", styles['CellText']),
            Paragraph("<b>FR:</b> " + (datos.get('fr', '—') or '—') + " rpm", styles['CellText']),
            Paragraph("<b>Temp:</b> " + (datos.get('temp', '—') or '—') + " °C", styles['CellText']),
            Paragraph("<b>Peso:</b> " + (datos.get('peso', '—') or '—') + " kg", styles['CellText']),
            Paragraph("<b>Talla:</b> " + (datos.get('talla', '—') or '—') + " m", styles['CellText']),
        ]
    ]
    t_vit = Table(vitals_data, colWidths=[90, 90, 90, 90, 90, 90])
    t_vit.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_vit)
    story.append(Spacer(1, 6))

    examen = datos.get('examen_fisico', '').strip()
    if examen:
        t_ex = Table([[Paragraph(f"<b>Hallazgos:</b> {examen.replace(chr(10), '<br/>')}", styles['CellText'])]], colWidths=[540])
        t_ex.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_ex)
    story.append(Spacer(1, 10))

    # Diagnóstico y Plan
    story.append(Paragraph("<b>3. Diagnóstico e Impresión Clínica</b>", styles['DocSectionTitle']))
    diag = datos.get('diagnostico', 'Sin diagnóstico registrado').strip() or 'Sin diagnóstico registrado'
    t_diag = Table([[Paragraph(diag.replace('\n', '<br/>'), styles['CellTextBold'])]], colWidths=[540])
    t_diag.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93c5fd")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_diag)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>4. Plan Terapéutico y Próxima Cita</b>", styles['DocSectionTitle']))
    plan = datos.get('plan', 'Continuar seguimiento habitual').strip() or 'Continuar seguimiento habitual'
    prox = datos.get('proxima_cita', 'Según evolución').strip() or 'Según evolución'

    plan_data = [
        [Paragraph("<b>Plan / Indicaciones:</b>", styles['CellTextBold']), Paragraph(plan.replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Próximo control:</b>", styles['CellTextBold']), Paragraph(prox, styles['CellText'])]
    ]
    t_plan = Table(plan_data, colWidths=[130, 410])
    t_plan.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_plan)

    # Firma
    story.append(Spacer(1, 40))
    t_firma = Table([[Paragraph("____________________________________________<br/>Firma y Sello del Médico Tratante", ParagraphStyle('Firma2', fontName='Helvetica', fontSize=9, alignment=1, leading=13))]], colWidths=[540])
    t_firma.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    story.append(KeepTogether([t_firma]))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath


def generar_pdf_cita_consulta(filepath: str, datos: dict) -> str:
    """
    Genera un comprobante oficial de Cita y Consulta Médica con Diagnóstico CIE-10, Tratamiento y Receta en PDF.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )

    styles = _get_base_styles()
    story = []

    # Encabezado
    medico = datos.get('personal_medico', 'Personal Médico').strip() or 'Personal Médico'
    header_data = [
        [
            Paragraph("<b>CENTRO MÉDICO & REGISTRO CLÍNICO</b>", styles['ClinicaTitle']),
            Paragraph(f"<b>ANOTACIÓN N°:</b> {datos.get('numero_anotacion', '#1')}", styles['CellTextBold'])
        ],
        [
            Paragraph(f"Atención y Consulta Médica • Dr(a). {medico}", styles['ClinicaSubtitle']),
            Paragraph(f"<b>FECHA:</b> {datos.get('fecha_consulta', datetime.date.today().strftime('%d/%m/%Y'))} {datos.get('hora_consulta', '')}", styles['CellText'])
        ]
    ]
    t_header = Table(header_data, colWidths=[380, 160])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)

    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb"), spaceBefore=4, spaceAfter=8))
    story.append(Paragraph(f"<b>HOJA DE CONSULTA, DIAGNÓSTICO Y TRATAMIENTO</b> — ESTADO: <b>{datos.get('estado', 'Programada').upper()}</b>", ParagraphStyle('SubSubCita', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#1d4ed8"), spaceAfter=10)))

    def _make_table_box(rows, widths):
        t = Table(rows, colWidths=widths)
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return t

    # 1. Datos Generales de la Consulta
    story.append(Paragraph("<b>1. DATOS DE LA CONSULTA Y PACIENTE</b>", styles['DocSectionTitle']))
    rows_info = [
        [
            Paragraph(f"<b>Paciente:</b> {datos.get('paciente_nombre', '—')}", styles['CellTextBold']),
            Paragraph(f"<b>Cédula:</b> {datos.get('paciente_cedula', '—')}", styles['CellText']),
            Paragraph(f"<b>Tipo Cita:</b> {datos.get('tipo', 'Consulta general')}", styles['CellText']),
        ],
        [
            Paragraph(f"<b>Personal Médico:</b> {medico}", styles['CellText']),
            Paragraph(f"<b>Fecha Consulta:</b> {datos.get('fecha_consulta', '—')} {datos.get('hora_consulta', '')}", styles['CellText']),
            Paragraph(f"<b>N° Anotación:</b> {datos.get('numero_anotacion', '#1')}", styles['CellText']),
        ]
    ]
    story.append(_make_table_box(rows_info, [220, 160, 160]))
    story.append(Spacer(1, 10))

    # 2. Diagnóstico CIE-10
    story.append(Paragraph("<b>2. DIAGNÓSTICO (CIE-10)</b>", styles['DocSectionTitle']))
    cie10 = datos.get('diagnostico_cie10', 'Sin diagnóstico registrado').strip() or 'Sin diagnóstico registrado'
    t_cie = Table([[Paragraph(f"<b>Diagnóstico / CIE-10:</b> {cie10}", styles['CellTextBold'])]], colWidths=[540])
    t_cie.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93c5fd")),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_cie)
    story.append(Spacer(1, 10))

    # 3. Tratamiento e Indicaciones
    story.append(Paragraph("<b>3. TRATAMIENTO E INDICACIONES MÉDICAS</b>", styles['DocSectionTitle']))
    tratamiento = datos.get('tratamiento', 'Continuar seguimiento y pautas previas.').strip() or 'Continuar seguimiento y pautas previas.'
    t_trat = Table([[Paragraph(tratamiento.replace('\n', '<br/>'), styles['CellText'])]], colWidths=[540])
    t_trat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_trat)
    story.append(Spacer(1, 10))

    # 4. Receta Médica / Prescripción
    receta = datos.get('receta', '').strip()
    if receta:
        story.append(Paragraph("<b>4. PRESCRIPCIÓN FARMACOLÓGICA / RECETA MÉDICA</b>", styles['DocSectionTitle']))
        t_rec = Table([[Paragraph(receta.replace('\n', '<br/>'), styles['IndicacionesText'])]], colWidths=[540])
        t_rec.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef9c3")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#fde047")),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(t_rec)
        story.append(Spacer(1, 10))

    # 5. Próxima Cita de Control
    story.append(Paragraph("<b>5. PRÓXIMA CITA / CONTROL PROGRAMADO</b>", styles['DocSectionTitle']))
    prox = datos.get('proxima_cita', 'Según evolución clínica o llamado del paciente').strip() or 'Según evolución clínica'
    t_prox = Table([[Paragraph(f"<b>Próxima Cita Sugerida:</b> {prox}", styles['CellTextBold'])]], colWidths=[540])
    t_prox.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#86efac")),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_prox)

    # Firma del personal médico
    story.append(Spacer(1, 35))
    t_firma_med = Table([[
        Paragraph(
            "_____________________________________________________<br/>"
            f"<b>Dr(a). {medico}</b><br/>"
            "Firma y Sello del Personal Médico",
            ParagraphStyle('FirmaMedCita', fontName='Helvetica', fontSize=9, alignment=1, leading=14)
        )
    ]], colWidths=[540])
    t_firma_med.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    story.append(KeepTogether([t_firma_med]))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath


def generar_pdf_expediente(filepath: str, paciente: dict, sesiones: list = None, recetas: list = None) -> str:
    """
    Genera un informe completo del expediente del paciente en PDF.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )

    styles = _get_base_styles()
    story = []

    # Encabezado
    story.append(Paragraph("<b>HISTORIA CLÍNICA & EXPEDIENTE MÉDICO</b>", styles['ClinicaTitle']))
    story.append(Paragraph("Documento de Registro Clínico Integral", styles['ClinicaSubtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1e3a8a"), spaceBefore=4, spaceAfter=12))

    # Ficha de Identificación
    story.append(Paragraph("<b>1. DATOS DE IDENTIFICACIÓN</b>", styles['DocSectionTitle']))
    cedula = paciente.get('cedula', '—')
    nombre = paciente.get('nombre', '—')
    sexo = paciente.get('sexo', '—')
    fnac = paciente.get('fecha_nacimiento', '—')
    edad = str(paciente.get('edad', '—'))
    civil = paciente.get('estado_civil', '—')
    aseg = paciente.get('aseguradora', '—')
    tel = paciente.get('telefono', '—')
    email = paciente.get('email', '—')
    dom = paciente.get('domicilio', '—')

    id_data = [
        [
            Paragraph(f"<b>Cédula / ID:</b> {cedula}", styles['CellText']),
            Paragraph(f"<b>Nombre Completo:</b> {nombre}", styles['CellTextBold'])
        ],
        [
            Paragraph(f"<b>Sexo:</b> {sexo}", styles['CellText']),
            Paragraph(f"<b>F. Nacimiento:</b> {fnac} (Edad: {edad} años)", styles['CellText'])
        ],
        [
            Paragraph(f"<b>Estado Civil:</b> {civil}", styles['CellText']),
            Paragraph(f"<b>Aseguradora:</b> {aseg}", styles['CellText'])
        ],
        [
            Paragraph(f"<b>Teléfono:</b> {tel}", styles['CellText']),
            Paragraph(f"<b>Correo Electrónico:</b> {email}", styles['CellText'])
        ],
        [
            Paragraph(f"<b>Domicilio:</b> {dom}", styles['CellText']),
            Paragraph(f"<b>Otros datos:</b> {paciente.get('otros_datos', '—')}", styles['CellText'])
        ]
    ]
    t_id = Table(id_data, colWidths=[220, 320])
    t_id.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_id)
    story.append(Spacer(1, 14))

    # Historial de Sesiones Clínicas
    sesiones = sesiones or []
    story.append(Paragraph(f"<b>2. SESIONES CLÍNICAS REGISTRADAS ({len(sesiones)})</b>", styles['DocSectionTitle']))

    if not sesiones:
        story.append(Paragraph("<i>No hay sesiones clínicas registradas para este paciente.</i>", styles['IndicacionesText']))
    else:
        for i, s in enumerate(sesiones, start=1):
            s_fecha = s.get('fecha', '—')
            s_tipo = s.get('tipo', 'Consulta')
            s_motivo = s.get('motivo', '—')
            s_diag = s.get('diagnostico', '—')
            s_plan = s.get('plan', '—')
            s_ta = s.get('ta', '—')
            s_fc = s.get('fc', '—')
            s_temp = s.get('temp', '—')
            s_peso = s.get('peso', '—')

            s_box = [
                [
                    Paragraph(f"<b>Sesión #{i}: {s_tipo}</b> ({s_fecha})", styles['CellTextBold']),
                    Paragraph(f"<b>Signos:</b> TA:{s_ta} | FC:{s_fc} | T:{s_temp}°C | P:{s_peso}kg", styles['CellText'])
                ],
                [
                    Paragraph(f"<b>Motivo:</b> {s_motivo}", styles['CellText']),
                    Paragraph(f"<b>Diagnóstico:</b> {s_diag}", styles['CellText'])
                ],
                [
                    Paragraph(f"<b>Plan Terapéutico:</b> {s_plan}", styles['CellText']),
                    Paragraph(f"<b>Próxima cita:</b> {s.get('proxima_cita', '—')}", styles['CellText'])
                ]
            ]
            t_s = Table(s_box, colWidths=[270, 270])
            t_s.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t_s)
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 14))

    # Historial de Recetas
    recetas = recetas or []
    story.append(Paragraph(f"<b>3. RECETAS MÉDICAS EMITIDAS ({len(recetas)})</b>", styles['DocSectionTitle']))
    if not recetas:
        story.append(Paragraph("<i>No hay recetas registradas para este paciente.</i>", styles['IndicacionesText']))
    else:
        for r in recetas:
            r_fecha = r.get('fecha', '—')
            r_med = r.get('medico', '—')
            meds_lista = r.get('medicamentos', [])
            meds_txt = ", ".join([f"{m.get('farmaco', '')} ({m.get('dosis', '')})" for m in meds_lista]) or "—"
            r_box = [
                [Paragraph(f"<b>Fecha:</b> {r_fecha}  |  <b>Médico:</b> {r_med}", styles['CellTextBold'])],
                [Paragraph(f"<b>Medicamentos:</b> {meds_txt}", styles['CellText'])],
                [Paragraph(f"<b>Instrucciones:</b> {r.get('instrucciones', '—')}", styles['CellText'])],
            ]
            t_r = Table(r_box, colWidths=[540])
            t_r.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t_r)
            story.append(Spacer(1, 6))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath


def generar_pdf_historia_clinica(filepath: str, datos: dict) -> str:
    """
    Genera un informe oficial de Historia Clínica Psicológica y Neurodesarrollo en PDF.
    Contiene todas las secciones clínicas solicitadas con formato profesional.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )

    styles = _get_base_styles()
    story = []

    # ── Encabezado Institucional ──
    header_data = [
        [
            Paragraph("<b>CENTRO DE ATENCIÓN INTEGRAL & SALUD MENTAL</b>", styles['ClinicaTitle']),
            Paragraph(f"<b>N° HISTORIA:</b> {datos.get('num_historia', 'HC-001')}", styles['CellTextBold'])
        ],
        [
            Paragraph("Servicio de Psicología Clínica, Evaluación y Neurodesarrollo", styles['ClinicaSubtitle']),
            Paragraph(f"<b>FECHA:</b> {datos.get('fecha_elaboracion', datetime.date.today().strftime('%d/%m/%Y'))} {datos.get('hora_elaboracion', '')}", styles['CellText'])
        ]
    ]
    t_header = Table(header_data, colWidths=[380, 160])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)

    condicion_str = "PRIMERA VEZ" if datos.get('primera_vez', True) else "CONTROL / SUBSECUENTE"
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1e3a8a"), spaceBefore=4, spaceAfter=6))
    story.append(Paragraph(f"<b>HISTORIA CLÍNICA INTEGRAL</b> — CONDICIÓN: <b>{condicion_str}</b>", ParagraphStyle('SubSub', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#1d4ed8"), spaceAfter=10)))

    def _make_table_box(rows, widths):
        t = Table(rows, colWidths=widths)
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        return t

    # ── 1. Filiación y Datos de Ingreso ──
    story.append(Paragraph("<b>1. DATOS DE IDENTIFICACIÓN Y FILIACIÓN</b>", styles['DocSectionTitle']))

    pac_nombre = datos.get('nombre', '—')
    pac_cedula = datos.get('cedula', '—')
    pac_sexo = datos.get('sexo', '—')
    pac_edad = str(datos.get('edad', '—'))
    pac_fnac = datos.get('fecha_nacimiento', '—')
    pac_lnac = datos.get('lugar_nacimiento', '—')
    pac_tel = datos.get('telefono', '—')
    pac_dir = datos.get('direccion', '—')
    pac_ins = datos.get('nivel_instruccion', '—')
    pac_ocu = datos.get('ocupacion', '—')
    pac_rel = datos.get('creencias_religiosas', '—')
    f_ing = datos.get('fecha_ingreso', '—')
    f_egr = datos.get('fecha_egreso', '—')

    rows_fil = [
        [
            Paragraph(f"<b>Paciente:</b> {pac_nombre}", styles['CellTextBold']),
            Paragraph(f"<b>Cédula / ID:</b> {pac_cedula}", styles['CellText']),
            Paragraph(f"<b>Sexo:</b> {pac_sexo}", styles['CellText']),
            Paragraph(f"<b>Edad:</b> {pac_edad} años", styles['CellText']),
        ],
        [
            Paragraph(f"<b>F. Nacimiento:</b> {pac_fnac}", styles['CellText']),
            Paragraph(f"<b>Lugar Nac.:</b> {pac_lnac}", styles['CellText']),
            Paragraph(f"<b>F. Ingreso:</b> {f_ing}", styles['CellText']),
            Paragraph(f"<b>F. Egreso:</b> {f_egr}", styles['CellText']),
        ],
        [
            Paragraph(f"<b>Teléfono:</b> {pac_tel}", styles['CellText']),
            Paragraph(f"<b>Dirección:</b> {pac_dir}", styles['CellText']),
            Paragraph(f"<b>Instrucción:</b> {pac_ins}", styles['CellText']),
            Paragraph(f"<b>Ocupación:</b> {pac_ocu}", styles['CellText']),
        ],
        [
            Paragraph(f"<b>Religión:</b> {pac_rel}", styles['CellText']),
            Paragraph(f"<b>Solicitante / Ref.:</b> {datos.get('referencias', '—')}", styles['CellText']),
            Paragraph(f"<b>Entorno Familiar:</b> {datos.get('entorno_familiar', '—')}", styles['CellText']),
            Paragraph("", styles['CellText']),
        ]
    ]
    story.append(_make_table_box(rows_fil, [140, 140, 130, 130]))
    story.append(Spacer(1, 10))

    # ── 2. Motivo de Consulta y Antecedentes ──
    story.append(Paragraph("<b>2. MOTIVO DE CONSULTA Y ANTECEDENTES CLÍNICOS</b>", styles['DocSectionTitle']))

    rows_ant = [
        [Paragraph("<b>Motivo de Consulta:</b>", styles['CellTextBold']), Paragraph(datos.get('motivo_consulta', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Ant. No Patológicos:</b>", styles['CellTextBold']), Paragraph(datos.get('ant_no_patologicos', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Ant. Patológicos:</b>", styles['CellTextBold']), Paragraph(datos.get('ant_patologicos', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Ant. Heredo-Familiares:</b>", styles['CellTextBold']), Paragraph(datos.get('ant_heredo_mentales', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Gestas / Pérdidas:</b>", styles['CellTextBold']), Paragraph(datos.get('gestas_perdidas', '—'), styles['CellText'])],
        [Paragraph("<b>Atención Psicológica Previa:</b>", styles['CellTextBold']), Paragraph(datos.get('atencion_psicologica_previa', '—'), styles['CellText'])],
        [Paragraph("<b>Evaluaciones Especialidad:</b>", styles['CellTextBold']), Paragraph(datos.get('evaluaciones_especialidad', '—').replace('\n', '<br/>'), styles['CellText'])],
    ]
    story.append(_make_table_box(rows_ant, [160, 380]))
    story.append(Spacer(1, 10))

    # ── 3. Datos del Representante ──
    story.append(Paragraph("<b>3. DATOS DEL PADRE, MADRE O REPRESENTANTE</b>", styles['DocSectionTitle']))
    rep_nom = datos.get('rep_nombre', '—')
    rep_ced = datos.get('rep_cedula', '—')
    rep_edad = str(datos.get('rep_edad', '—'))
    rep_tel = datos.get('rep_telefono', datos.get('rep_edad_tel', '—'))
    rep_ins = datos.get('rep_instruccion', '—')
    rep_ocu = datos.get('rep_ocupacion', '—')

    rows_rep = [
        [
            Paragraph(f"<b>Representante:</b> {rep_nom}", styles['CellTextBold']),
            Paragraph(f"<b>Cédula:</b> {rep_ced}", styles['CellText']),
            Paragraph(f"<b>Edad:</b> {rep_edad} años", styles['CellText']),
            Paragraph(f"<b>Teléfono:</b> {rep_tel}", styles['CellText']),
        ],
        [
            Paragraph(f"<b>Instrucción Académica:</b> {rep_ins}", styles['CellText']),
            Paragraph(f"<b>Ocupación:</b> {rep_ocu}", styles['CellText']),
            Paragraph("", styles['CellText']),
            Paragraph("", styles['CellText']),
        ],
        [
            Paragraph("<b>Infancia:</b>", styles['CellTextBold']),
            Paragraph(datos.get('rep_infancia', '—').replace('\n', '<br/>'), styles['CellText']),
            Paragraph("<b>Adultez:</b>", styles['CellTextBold']),
            Paragraph(datos.get('rep_adultez', '—').replace('\n', '<br/>'), styles['CellText']),
        ],
        [
            Paragraph("<b>Etapa Amorosa:</b>", styles['CellTextBold']),
            Paragraph(datos.get('rep_etapa_amorosa', '—').replace('\n', '<br/>'), styles['CellText']),
            Paragraph("", styles['CellText']),
            Paragraph("", styles['CellText']),
        ]
    ]
    story.append(_make_table_box(rows_rep, [135, 135, 135, 135]))
    story.append(Spacer(1, 10))

    # ── 4. Preguntas de Autoexploración Emocional ──
    story.append(Paragraph("<b>4. PREGUNTAS DE AUTOEXPLORACIÓN Y REFLEXIÓN EMOCIONAL</b>", styles['DocSectionTitle']))
    rows_emoc = [
        [Paragraph("<b>1) ¿Eres feliz?</b>", styles['CellTextBold']), Paragraph(datos.get('pregunta_feliz', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>2) ¿Qué modificarías en tu vida?</b>", styles['CellTextBold']), Paragraph(datos.get('pregunta_modificar', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>3) ¿Cómo te proyectas en el futuro?</b>", styles['CellTextBold']), Paragraph(datos.get('pregunta_futuro', '—').replace('\n', '<br/>'), styles['CellText'])],
    ]
    story.append(_make_table_box(rows_emoc, [180, 360]))
    story.append(Spacer(1, 10))

    # ── 5. Examen Clínico, Neurodesarrollo e IPX ──
    story.append(Paragraph("<b>5. NEURODESARROLLO, EXAMEN CLÍNICO E IMPRESIÓN DIAGNÓSTICA (IPX)</b>", styles['DocSectionTitle']))
    rows_neuro = [
        [Paragraph("<b>Cuadro Clínico:</b>", styles['CellTextBold']), Paragraph(datos.get('cuadro_clinico', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Exploración Física:</b>", styles['CellTextBold']), Paragraph(datos.get('exploracion_fisica', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Hábitos Exterior:</b>", styles['CellTextBold']), Paragraph(datos.get('habitos_exterior', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Autonomía Motora:</b>", styles['CellTextBold']), Paragraph(datos.get('autonomia_motora', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Etapa Prenatal:</b>", styles['CellTextBold']), Paragraph(datos.get('etapa_prenatal', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Etapa Neonatal:</b>", styles['CellTextBold']), Paragraph(datos.get('etapa_neonatal', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Desarrollo Psicomotor:</b>", styles['CellTextBold']), Paragraph(datos.get('desarrollo_psicomotor', '—').replace('\n', '<br/>'), styles['CellText'])],
        [Paragraph("<b>Instrumentos de Evaluación:</b>", styles['CellTextBold']), Paragraph(datos.get('instrumentos_evaluacion', '—').replace('\n', '<br/>'), styles['CellText'])],
    ]
    story.append(_make_table_box(rows_neuro, [160, 380]))
    story.append(Spacer(1, 8))

    # IPX resaltado
    ipx_texto = datos.get('ipx', 'Sin impresión diagnóstica registrada').strip() or 'Sin impresión diagnóstica registrada'
    t_ipx = Table([[
        Paragraph(f"<b>IPX (IMPRESIÓN DIAGNÓSTICA):</b><br/>{ipx_texto.replace(chr(10), '<br/>')}", styles['CellTextBold'])
    ]], colWidths=[540])
    t_ipx.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#22c55e")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_ipx)

    # ── Firma Profesional ──
    story.append(Spacer(1, 35))
    t_firma = Table([[
        Paragraph(
            "_____________________________________________________<br/>"
            "<b>Especialista / Psicólogo(a) Evaluador(a)</b><br/>"
            "Firma, Número de Colegiado y Sello Profesional",
            ParagraphStyle('FirmaHist', fontName='Helvetica', fontSize=9, alignment=1, leading=14)
        )
    ]], colWidths=[540])
    t_firma.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    story.append(KeepTogether([t_firma]))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath
