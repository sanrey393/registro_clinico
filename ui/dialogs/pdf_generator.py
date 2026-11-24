# ui/dialogs/pdf_generator.py
# Generador de documentos PDF clínicos usando ReportLab

import os
import html
import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, Image
)
from reportlab.pdfgen import canvas
from core.app_paths import resource_path


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
        page_w = self._pagesize[0]
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        texto = f"Página {self._pageNumber} de {page_count}  •  PSIQUE"
        self.drawRightString(page_w - 36, 24, texto)
        self.drawString(36, 24, "PSIQUE — Documento Clínico Confidencial • Uso Profesional Exclusivo")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(36, 35, page_w - 36, 35)
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
    Genera un PDF con formato editorial clínico PSIQUE de Receta Médica / Fármacos.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=46,
        title=f"Receta Médica - {datos.get('paciente_nombre', 'Paciente')}",
        author="PSIQUE - Sistema de Gestión Clínico Psicológica",
    )

    story = []

    # ── Paleta Clínica PSIQUE ──
    C_PETROL = colors.HexColor("#0B2B2E")
    C_TEAL = colors.HexColor("#0F766E")
    C_TEAL_LIGHT = colors.HexColor("#F0FDFA")
    C_MINT_BORDER = colors.HexColor("#99F6E4")
    C_SLATE_DARK = colors.HexColor("#0F172A")
    C_SLATE = colors.HexColor("#334155")
    C_MUTED = colors.HexColor("#64748B")
    C_SURFACE = colors.HexColor("#F8FAFC")
    C_BORDER = colors.HexColor("#CBD5E1")
    C_GRID = colors.HexColor("#E2E8F0")
    C_WARN_BG = colors.HexColor("#FFFBEB")
    C_WARN_BORDER = colors.HexColor("#FCD34D")
    C_WARN_ACCENT = colors.HexColor("#D97706")

    st_brand = ParagraphStyle(
        'RecBrand', fontName='Helvetica-Bold', fontSize=18, leading=20, textColor=C_PETROL
    )
    st_brand_sub = ParagraphStyle(
        'RecBrandSub', fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=C_MUTED
    )
    st_pill_hdr = ParagraphStyle(
        'RecPillHdr', fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.white, alignment=1
    )
    st_pill_meta = ParagraphStyle(
        'RecPillMeta', fontName='Helvetica', fontSize=8.2, leading=11.5,
        textColor=C_SLATE_DARK, alignment=1
    )
    st_lbl_micro = ParagraphStyle(
        'RecLblMicro', fontName='Helvetica-Bold', fontSize=7.2, leading=9.5, textColor=C_MUTED
    )
    st_val_hero = ParagraphStyle(
        'RecValHero', fontName='Helvetica-Bold', fontSize=12, leading=14.5, textColor=C_PETROL
    )
    st_val = ParagraphStyle(
        'RecVal', fontName='Helvetica', fontSize=8.8, leading=12.5, textColor=C_SLATE_DARK
    )
    st_val_bold = ParagraphStyle(
        'RecValBold', fontName='Helvetica-Bold', fontSize=8.8, leading=12.5, textColor=C_SLATE_DARK
    )
    st_sec_num = ParagraphStyle(
        'RecSecNum', fontName='Helvetica-Bold', fontSize=9, leading=11,
        textColor=colors.white, alignment=1
    )
    st_sec_title = ParagraphStyle(
        'RecSecTitle', fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=C_PETROL
    )
    st_th = ParagraphStyle(
        'RecTh', fontName='Helvetica-Bold', fontSize=8.6, leading=11, textColor=colors.white
    )
    st_body = ParagraphStyle(
        'RecBody', fontName='Helvetica', fontSize=8.8, leading=13, textColor=C_SLATE
    )
    st_firma = ParagraphStyle(
        'RecFirma', fontName='Helvetica', fontSize=8.5, leading=13, textColor=C_SLATE, alignment=1
    )

    def _esc(val, default="—"):
        if val is None:
            return default
        s = str(val).strip()
        if not s:
            return default
        return html.escape(s).replace("\n", "<br/>")

    def _field_cell(label: str, value: str, bold_val: bool = False):
        return [
            Paragraph(html.escape(label.upper()), st_lbl_micro),
            Paragraph(value, st_val_bold if bold_val else st_val),
        ]

    def _section_banner(num: str, title: str):
        t_sec = Table(
            [[Paragraph(num, st_sec_num), Paragraph(html.escape(title.upper()), st_sec_title)]],
            colWidths=[24, 516],
        )
        t_sec.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), C_TEAL),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('LEFTPADDING', (1, 0), (1, 0), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 1.0, C_BORDER),
        ]))
        return t_sec

    # ── Encabezado Institucional PSIQUE ──
    logo_path = resource_path(os.path.join("data", "app_icon.png"))
    logo_cell = Image(logo_path, width=40, height=40) if os.path.exists(logo_path) else Paragraph("<b>Ψ</b>", st_brand)

    brand_block = Table(
        [[
            logo_cell,
            [
                Paragraph("PSIQUE", st_brand),
                Paragraph("Sistema de Gestión Clínico Psicológica", st_brand_sub),
                Paragraph("Prescripción Farmacológica y Seguimiento Terapéutico", st_brand_sub),
            ],
        ]],
        colWidths=[48, 292],
    )
    brand_block.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    fecha_rec = _esc(datos.get('fecha', datetime.date.today().strftime('%d/%m/%Y')))
    medico = datos.get('medico', 'Médico Tratante') or 'Médico Tratante'
    esp = datos.get('especialidad', 'Psiquiatría') or 'Psiquiatría'
    paciente = datos.get('paciente_nombre', 'Paciente') or 'Paciente'

    meta_card = Table(
        [
            [Paragraph("RECETA MÉDICA / FÁRMACOS", st_pill_hdr)],
            [Paragraph(f"<b>Fecha:</b> {fecha_rec}", st_pill_meta)],
            [Paragraph("<b>Régimen:</b> Ambulatorio", st_pill_meta)],
            [Paragraph(f"<font color='{C_TEAL.hexval()}'><b>● {_esc(esp)}</b></font>", st_pill_meta)],
        ],
        colWidths=[192],
    )
    meta_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), C_PETROL),
        ('BACKGROUND', (0, 1), (0, -1), C_TEAL_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.8, C_TEAL),
        ('LINEBELOW', (0, 1), (0, 2), 0.4, C_MINT_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    t_header = Table([[brand_block, meta_card]], colWidths=[344, 196])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_TEAL, spaceBefore=8, spaceAfter=10))

    # ── Tarjeta Resumen Paciente y Especialista ──
    t_info = Table(
        [[
            [
                Paragraph("PACIENTE", st_lbl_micro),
                Paragraph(_esc(paciente), st_val_hero),
            ],
            _field_cell("Especialista Tratante", _esc(medico), bold_val=True),
            _field_cell("Especialidad", _esc(esp)),
        ]],
        colWidths=[240, 175, 125],
    )
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_TEAL_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.6, C_MINT_BORDER),
        ('LINEBEFORE', (0, 0), (0, -1), 3.0, C_TEAL),
        ('LINEAFTER', (0, 0), (1, -1), 0.4, C_MINT_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 14))

    # ── 01. Prescripción Farmacológica (Rp/) ──
    story.append(_section_banner("01", "Rp / Prescripción Farmacológica"))
    story.append(Spacer(1, 6))

    meds = datos.get('medicamentos', [])
    meds_data = [[
        Paragraph("Medicamento / Principio", st_th),
        Paragraph("Presentación / Lab.", st_th),
        Paragraph("Dosis", st_th),
        Paragraph("Frecuencia / Pauta", st_th),
        Paragraph("Duración", st_th),
    ]]

    for m in meds:
        farmaco = _esc(m.get('farmaco') or m.get('nombre'))
        pres = _esc(m.get('presentacion'))
        dosis = _esc(m.get('dosis'))
        frec = _esc(m.get('frecuencia'))
        dur = _esc(m.get('duracion'))
        meds_data.append([
            Paragraph(f"<b>{farmaco}</b>", st_val_bold),
            Paragraph(pres, st_body),
            Paragraph(dosis, st_body),
            Paragraph(frec, st_body),
            Paragraph(dur, st_body),
        ])

    if len(meds_data) == 1:
        meds_data.append([
            Paragraph("Sin medicamentos prescritos", st_body),
            Paragraph("—", st_body),
            Paragraph("—", st_body),
            Paragraph("—", st_body),
            Paragraph("—", st_body),
        ])

    t_meds = Table(meds_data, colWidths=[150, 100, 95, 115, 80])
    t_meds.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PETROL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_SURFACE]),
        ('BOX', (0, 0), (-1, -1), 0.7, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, C_GRID),
    ]))
    story.append(t_meds)
    story.append(Spacer(1, 14))

    # ── 02. Indicaciones y Advertencias al Paciente ──
    instrucciones = (datos.get('instrucciones') or '').strip()
    if instrucciones:
        inst_table = Table(
            [[
                [
                    Paragraph("INDICACIONES CLÍNICAS, CONTRAINDICACIONES Y ADVERTENCIAS", st_lbl_micro),
                    Spacer(1, 3),
                    Paragraph(_esc(instrucciones), st_body),
                ]
            ]],
            colWidths=[540],
        )
        inst_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), C_WARN_BG),
            ('BOX', (0, 0), (-1, -1), 0.6, C_WARN_BORDER),
            ('LINEBEFORE', (0, 0), (0, -1), 3.0, C_WARN_ACCENT),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(KeepTogether([
            _section_banner("02", "Indicaciones y Advertencias al Paciente"),
            Spacer(1, 6),
            inst_table,
        ]))
        story.append(Spacer(1, 18))

    # ── Firma y Sello ──
    story.append(Spacer(1, 28))
    t_firma = Table(
        [[
            Paragraph(
                "______________________________________________<br/>"
                f"<b>{_esc(medico)}</b><br/>"
                f"{_esc(esp)} • Firma y Sello Profesional",
                st_firma,
            ),
            Paragraph(
                "______________________________________________<br/>"
                "<b>Fecha de Emisión</b><br/>"
                f"{fecha_rec} • PSIQUE",
                st_firma,
            ),
        ]],
        colWidths=[270, 270],
    )
    t_firma.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
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
    Genera un informe completo del expediente del paciente en PDF
    con diseño editorial clínico PSIQUE.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=46,
        title=f"Expediente Clínico - {paciente.get('nombre', 'Paciente')}",
        author="PSIQUE - Sistema de Gestión Clínico Psicológica",
    )

    story = []
    sesiones = sesiones or []
    recetas = recetas or []

    # ── Paleta Clínica PSIQUE ──
    C_PETROL = colors.HexColor("#0B2B2E")
    C_TEAL = colors.HexColor("#0F766E")
    C_TEAL_LIGHT = colors.HexColor("#F0FDFA")
    C_MINT_BORDER = colors.HexColor("#99F6E4")
    C_SLATE_DARK = colors.HexColor("#0F172A")
    C_SLATE = colors.HexColor("#334155")
    C_MUTED = colors.HexColor("#64748B")
    C_SURFACE = colors.HexColor("#F8FAFC")
    C_BORDER = colors.HexColor("#CBD5E1")
    C_GRID = colors.HexColor("#E2E8F0")

    st_brand = ParagraphStyle(
        'ExpBrand', fontName='Helvetica-Bold', fontSize=18, leading=20, textColor=C_PETROL
    )
    st_brand_sub = ParagraphStyle(
        'ExpBrandSub', fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=C_MUTED
    )
    st_pill_hdr = ParagraphStyle(
        'ExpPillHdr', fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.white, alignment=1
    )
    st_pill_meta = ParagraphStyle(
        'ExpPillMeta', fontName='Helvetica', fontSize=8.2, leading=11.5,
        textColor=C_SLATE_DARK, alignment=1
    )
    st_lbl_micro = ParagraphStyle(
        'ExpLblMicro', fontName='Helvetica-Bold', fontSize=7.2, leading=9.5, textColor=C_MUTED
    )
    st_val_hero = ParagraphStyle(
        'ExpValHero', fontName='Helvetica-Bold', fontSize=12.5, leading=15, textColor=C_PETROL
    )
    st_val = ParagraphStyle(
        'ExpVal', fontName='Helvetica', fontSize=8.8, leading=12.5, textColor=C_SLATE_DARK
    )
    st_val_bold = ParagraphStyle(
        'ExpValBold', fontName='Helvetica-Bold', fontSize=8.8, leading=12.5, textColor=C_SLATE_DARK
    )
    st_sec_num = ParagraphStyle(
        'ExpSecNum', fontName='Helvetica-Bold', fontSize=9, leading=11,
        textColor=colors.white, alignment=1
    )
    st_sec_title = ParagraphStyle(
        'ExpSecTitle', fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=C_PETROL
    )
    st_body = ParagraphStyle(
        'ExpBody', fontName='Helvetica', fontSize=8.8, leading=13, textColor=C_SLATE
    )
    st_card_hdr = ParagraphStyle(
        'ExpCardHdr', fontName='Helvetica-Bold', fontSize=8.8, leading=11.5, textColor=C_PETROL
    )
    st_firma = ParagraphStyle(
        'ExpFirma', fontName='Helvetica', fontSize=8.5, leading=13, textColor=C_SLATE, alignment=1
    )

    def _esc(val, default="—"):
        if val is None:
            return default
        s = str(val).strip()
        if not s:
            return default
        return html.escape(s).replace("\n", "<br/>")

    def _field_cell(label: str, value: str, bold_val: bool = False):
        return [
            Paragraph(html.escape(label.upper()), st_lbl_micro),
            Paragraph(value, st_val_bold if bold_val else st_val),
        ]

    def _section_banner(num: str, title: str):
        t_sec = Table(
            [[Paragraph(num, st_sec_num), Paragraph(html.escape(title.upper()), st_sec_title)]],
            colWidths=[24, 516],
        )
        t_sec.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), C_TEAL),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('LEFTPADDING', (1, 0), (1, 0), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 1.0, C_BORDER),
        ]))
        return t_sec

    # ── Encabezado Institucional PSIQUE ──
    logo_path = resource_path(os.path.join("data", "app_icon.png"))
    logo_cell = Image(logo_path, width=40, height=40) if os.path.exists(logo_path) else Paragraph("<b>Ψ</b>", st_brand)

    brand_block = Table(
        [[
            logo_cell,
            [
                Paragraph("PSIQUE", st_brand),
                Paragraph("Sistema de Gestión Clínico Psicológica", st_brand_sub),
                Paragraph("Expediente Integral de Identificación y Seguimiento", st_brand_sub),
            ],
        ]],
        colWidths=[48, 292],
    )
    brand_block.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    fecha_hoy = datetime.date.today().strftime('%d/%m/%Y')
    meta_card = Table(
        [
            [Paragraph("EXPEDIENTE DEL PACIENTE", st_pill_hdr)],
            [Paragraph(f"<b>Emisión:</b> {fecha_hoy}", st_pill_meta)],
            [Paragraph(f"<b>Sesiones:</b> {len(sesiones)}  •  <b>Recetas:</b> {len(recetas)}", st_pill_meta)],
            [Paragraph(f"<font color='{C_TEAL.hexval()}'><b>● REGISTRO ACTIVO</b></font>", st_pill_meta)],
        ],
        colWidths=[192],
    )
    meta_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), C_PETROL),
        ('BACKGROUND', (0, 1), (0, -1), C_TEAL_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.8, C_TEAL),
        ('LINEBELOW', (0, 1), (0, 2), 0.4, C_MINT_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    t_header = Table([[brand_block, meta_card]], colWidths=[344, 196])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_TEAL, spaceBefore=8, spaceAfter=10))

    # ── 01. Ficha de Identificación ──
    cedula = _esc(paciente.get('cedula'))
    nombre = _esc(paciente.get('nombre'))
    sexo = _esc(paciente.get('sexo'))
    fnac = _esc(paciente.get('fecha_nacimiento'))
    edad = _esc(paciente.get('edad'))
    civil = _esc(paciente.get('estado_civil'))
    aseg = _esc(paciente.get('aseguradora'))
    tel = _esc(paciente.get('telefono'))
    email = _esc(paciente.get('email'))
    dom = _esc(paciente.get('domicilio'))
    otros = _esc(paciente.get('otros_datos'))

    hero_patient = Table(
        [[
            [
                Paragraph("PACIENTE TITULAR", st_lbl_micro),
                Paragraph(nombre, st_val_hero),
            ],
            _field_cell("Cédula / ID", cedula, bold_val=True),
            _field_cell("Edad", f"{edad} años" if edad != "—" else "—"),
            _field_cell("Sexo", sexo),
        ]],
        colWidths=[240, 120, 85, 95],
    )
    hero_patient.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_TEAL_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.6, C_MINT_BORDER),
        ('LINEBEFORE', (0, 0), (0, -1), 3.0, C_TEAL),
        ('LINEAFTER', (0, 0), (2, -1), 0.4, C_MINT_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    id_rows = [
        [
            _field_cell("Fecha de Nacimiento", fnac),
            _field_cell("Estado Civil", civil),
            _field_cell("Aseguradora", aseg),
            _field_cell("Teléfono", tel),
        ],
        [
            _field_cell("Correo Electrónico", email),
            _field_cell("Domicilio", dom),
            _field_cell("Otros Datos / Alergias", otros),
            _field_cell("ID Expediente", _esc(paciente.get('id'))),
        ],
    ]
    pnf = paciente.get('pnf', '')
    if pnf:
        id_rows.append([
            _field_cell("PNF (Programa)", _esc(pnf)),
            _field_cell("Trayecto", _esc(paciente.get('trayecto') or 'N/A')),
            _field_cell("Sección", _esc(paciente.get('seccion') or 'N/A')),
            _field_cell("Año Académico", _esc(paciente.get('anio_academico') or 'N/A')),
        ])

    t_id = Table(id_rows, colWidths=[145, 135, 135, 125])
    t_id.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.6, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, C_GRID),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(KeepTogether([
        _section_banner("01", "Datos de Identificación del Paciente"),
        Spacer(1, 6),
        hero_patient,
        Spacer(1, 6),
        t_id,
    ]))
    story.append(Spacer(1, 14))

    # ── 02. Historial de Sesiones Clínicas ──
    story.append(_section_banner("02", f"Sesiones Clínicas Registradas ({len(sesiones)})"))
    story.append(Spacer(1, 6))

    if not sesiones:
        story.append(Paragraph("<i>No hay sesiones clínicas registradas para este paciente.</i>", st_body))
    else:
        for i, s in enumerate(sesiones, start=1):
            s_fecha = _esc(s.get('fecha'))
            s_tipo = _esc(s.get('tipo', 'Consulta'))
            s_motivo = _esc(s.get('motivo'))
            s_diag = _esc(s.get('diagnostico'))
            s_plan = _esc(s.get('plan'))
            s_ta = _esc(s.get('ta'))
            s_fc = _esc(s.get('fc'))
            s_temp = _esc(s.get('temp'))
            s_peso = _esc(s.get('peso'))
            s_prox = _esc(s.get('proxima_cita'))

            s_box = [
                [
                    Paragraph(f"Sesión #{i} — {s_tipo} ({s_fecha})", st_card_hdr),
                    Paragraph(f"<b>Signos:</b> TA: {s_ta} | FC: {s_fc} | T: {s_temp}°C | Peso: {s_peso}kg", st_body),
                ],
                [
                    _field_cell("Motivo", s_motivo),
                    _field_cell("Diagnóstico", s_diag),
                ],
                [
                    _field_cell("Plan Terapéutico", s_plan),
                    _field_cell("Próxima Cita", s_prox),
                ],
            ]
            t_s = Table(s_box, colWidths=[270, 270])
            t_s.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), C_TEAL_LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.6, C_BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 0.4, C_GRID),
                ('LINEBEFORE', (0, 0), (0, -1), 2.5, C_TEAL),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(KeepTogether([t_s, Spacer(1, 6)]))

    story.append(Spacer(1, 10))

    # ── 03. Historial de Recetas Médicas ──
    story.append(_section_banner("03", f"Recetas Médicas Emitidas ({len(recetas)})"))
    story.append(Spacer(1, 6))

    if not recetas:
        story.append(Paragraph("<i>No hay recetas registradas para este paciente.</i>", st_body))
    else:
        for r in recetas:
            r_fecha = _esc(r.get('fecha') or r.get('fecha_receta'))
            r_med = _esc(r.get('medico'))
            meds_lista = r.get('medicamentos', [])
            if meds_lista:
                meds_txt = ", ".join(
                    f"{_esc(m.get('farmaco') or m.get('nombre'), '')} ({_esc(m.get('dosis'), '')})"
                    for m in meds_lista
                ).strip(", ") or "—"
            else:
                nom_c = (r.get('nombre_comercial') or '').strip()
                nom_g = (r.get('nombre_generico') or '').strip()
                dosis_r = (r.get('dosis') or '').strip()
                med_base = f"{nom_c} ({nom_g})" if nom_c and nom_g else (nom_c or nom_g)
                meds_txt = _esc(f"{med_base} — {dosis_r}".strip(" —")) if (med_base or dosis_r) else "—"

            r_inst = _esc(r.get('instrucciones') or r.get('indicaciones'))
            r_box = [
                [Paragraph(f"Fecha: {r_fecha}  •  Especialista: {r_med}", st_card_hdr)],
                [Paragraph(f"<b>Medicamentos:</b> {meds_txt}", st_body)],
                [Paragraph(f"<b>Indicaciones:</b> {r_inst}", st_body)],
            ]
            t_r = Table(r_box, colWidths=[540])
            t_r.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), C_SURFACE),
                ('BOX', (0, 0), (-1, -1), 0.6, C_BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 0.4, C_GRID),
                ('LINEBEFORE', (0, 0), (0, -1), 2.5, C_TEAL),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(KeepTogether([t_r, Spacer(1, 6)]))

    # ── Firma Profesional ──
    story.append(Spacer(1, 24))
    t_firma = Table(
        [[
            Paragraph(
                "______________________________________________<br/>"
                "<b>Especialista / Psicólogo(a) Tratante</b><br/>"
                "Firma y Sello Profesional",
                st_firma,
            ),
            Paragraph(
                "______________________________________________<br/>"
                "<b>Fecha de Emisión</b><br/>"
                f"{fecha_hoy} • PSIQUE",
                st_firma,
            ),
        ]],
        colWidths=[270, 270],
    )
    t_firma.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(KeepTogether([t_firma]))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

def generar_pdf_historia_clinica(filepath: str, datos: dict) -> str:
    """
    Genera un informe oficial de Historia Clínica Psicológica y Neurodesarrollo en PDF
    con diseño editorial clínico PSIQUE (tipografía limpia, jerarquía visual,
    tarjetas de metadatos, secciones numeradas y bloque IPX destacado).
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=46,
        title=f"Historia Clínica - {datos.get('nombre', 'Paciente')}",
        author="PSIQUE - Sistema de Gestión Clínico Psicológica",
    )

    story = []

    # ── Paleta Clínica PSIQUE ──
    C_PETROL = colors.HexColor("#0B2B2E")
    C_TEAL = colors.HexColor("#0F766E")
    C_TEAL_LIGHT = colors.HexColor("#F0FDFA")
    C_MINT_BORDER = colors.HexColor("#99F6E4")
    C_SLATE_DARK = colors.HexColor("#0F172A")
    C_SLATE = colors.HexColor("#334155")
    C_MUTED = colors.HexColor("#64748B")
    C_SURFACE = colors.HexColor("#F8FAFC")
    C_BORDER = colors.HexColor("#CBD5E1")
    C_GRID = colors.HexColor("#E2E8F0")
    C_BLUE_BADGE = colors.HexColor("#0369A1")

    # ── Tipografía Editorial ──
    st_brand = ParagraphStyle(
        'PsiqueBrand', fontName='Helvetica-Bold', fontSize=18, leading=20, textColor=C_PETROL
    )
    st_brand_sub = ParagraphStyle(
        'PsiqueBrandSub', fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=C_MUTED
    )
    st_doc_pill_hdr = ParagraphStyle(
        'PsiqueDocHdr', fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.white, alignment=1
    )
    st_doc_meta = ParagraphStyle(
        'PsiqueDocMeta', fontName='Helvetica', fontSize=8.2, leading=11.5,
        textColor=C_SLATE_DARK, alignment=1
    )
    st_lbl_micro = ParagraphStyle(
        'PsiqueLblMicro', fontName='Helvetica-Bold', fontSize=7.2, leading=9.5,
        textColor=C_MUTED
    )
    st_val_hero = ParagraphStyle(
        'PsiqueValHero', fontName='Helvetica-Bold', fontSize=12.5, leading=15,
        textColor=C_PETROL
    )
    st_val = ParagraphStyle(
        'PsiqueVal', fontName='Helvetica', fontSize=8.8, leading=12.5, textColor=C_SLATE_DARK
    )
    st_val_bold = ParagraphStyle(
        'PsiqueValBold', fontName='Helvetica-Bold', fontSize=8.8, leading=12.5, textColor=C_SLATE_DARK
    )
    st_sec_num = ParagraphStyle(
        'PsiqueSecNum', fontName='Helvetica-Bold', fontSize=9, leading=11,
        textColor=colors.white, alignment=1
    )
    st_sec_title = ParagraphStyle(
        'PsiqueSecTitle', fontName='Helvetica-Bold', fontSize=10.5, leading=13,
        textColor=C_PETROL
    )
    st_body = ParagraphStyle(
        'PsiqueBody', fontName='Helvetica', fontSize=9, leading=13.5, textColor=C_SLATE
    )
    st_ipx_hdr = ParagraphStyle(
        'PsiqueIpxHdr', fontName='Helvetica-Bold', fontSize=9.5, leading=12,
        textColor=colors.white
    )
    st_ipx_body = ParagraphStyle(
        'PsiqueIpxBody', fontName='Helvetica-Bold', fontSize=9.5, leading=14,
        textColor=C_PETROL
    )
    st_firma = ParagraphStyle(
        'PsiqueFirma', fontName='Helvetica', fontSize=8.5, leading=13,
        textColor=C_SLATE, alignment=1
    )

    def _esc(val, default="—"):
        if val is None:
            return default
        s = str(val).strip()
        if not s:
            return default
        return html.escape(s).replace("\n", "<br/>")

    def _field_cell(label: str, value: str, bold_val: bool = False):
        val_style = st_val_bold if bold_val else st_val
        return [
            Paragraph(html.escape(label.upper()), st_lbl_micro),
            Paragraph(value, val_style),
        ]

    def _section_banner(num: str, title: str):
        t_sec = Table(
            [[
                Paragraph(num, st_sec_num),
                Paragraph(html.escape(title.upper()), st_sec_title),
            ]],
            colWidths=[24, 516],
        )
        t_sec.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), C_TEAL),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('LEFTPADDING', (1, 0), (1, 0), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 1.0, C_BORDER),
        ]))
        return t_sec

    def _clean_kv_table(rows_kv, label_w=155):
        """Tabla clínica limpia de 2 columnas con filas alternadas sutiles."""
        data = [
            [Paragraph(f"<b>{html.escape(k)}</b>", st_val_bold), Paragraph(v, st_body)]
            for k, v in rows_kv
        ]
        t = Table(data, colWidths=[label_w, 540 - label_w])
        cmds = [
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 0.6, C_BORDER),
            ('LINEBELOW', (0, 0), (-1, -2), 0.4, C_GRID),
            ('LINEAFTER', (0, 0), (0, -1), 0.4, C_GRID),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), C_SURFACE),
        ]
        for idx in range(len(data)):
            bg_val = colors.white if idx % 2 == 0 else C_SURFACE
            cmds.append(('BACKGROUND', (1, idx), (1, idx), bg_val))
        t.setStyle(TableStyle(cmds))
        return t

    # ── Encabezado Institucional PSIQUE ──
    logo_path = resource_path(os.path.join("data", "app_icon.png"))
    if os.path.exists(logo_path):
        logo_cell = Image(logo_path, width=40, height=40)
    else:
        logo_cell = Paragraph("<b>Ψ</b>", st_brand)

    brand_block = Table(
        [[
            logo_cell,
            [
                Paragraph("PSIQUE", st_brand),
                Paragraph("Sistema de Gestión Clínico Psicológica", st_brand_sub),
                Paragraph("Evaluación Psicológica, Seguimiento y Neurodesarrollo", st_brand_sub),
            ],
        ]],
        colWidths=[48, 292],
    )
    brand_block.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    es_primera = bool(datos.get('primera_vez', True))
    condicion_str = "PRIMERA CONSULTA" if es_primera else "CONTROL / SUBSECUENTE"
    cond_color = C_TEAL if es_primera else C_BLUE_BADGE
    fecha_elab = _esc(datos.get('fecha_elaboracion', datetime.date.today().strftime('%d/%m/%Y')))
    hora_elab = _esc(datos.get('hora_elaboracion', ''), "")
    fecha_full = f"{fecha_elab} {hora_elab}".strip()

    meta_card = Table(
        [
            [Paragraph("HISTORIA CLÍNICA INTEGRAL", st_doc_pill_hdr)],
            [Paragraph(f"<b>N° Historia:</b> {_esc(datos.get('num_historia', 'HC-001'))}", st_doc_meta)],
            [Paragraph(f"<b>Fecha:</b> {fecha_full}", st_doc_meta)],
            [Paragraph(f"<font color='{cond_color.hexval()}'><b>● {condicion_str}</b></font>", st_doc_meta)],
        ],
        colWidths=[192],
    )
    meta_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), C_PETROL),
        ('BACKGROUND', (0, 1), (0, -1), C_TEAL_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.8, C_TEAL),
        ('LINEBELOW', (0, 1), (0, 2), 0.4, C_MINT_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    t_header = Table([[brand_block, meta_card]], colWidths=[344, 196])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_TEAL, spaceBefore=8, spaceAfter=10))

    # ── Tarjeta Resumen del Paciente + 01. Filiación ──
    pac_nombre = _esc(datos.get('nombre', '—'))
    pac_cedula = _esc(datos.get('cedula', '—'))
    pac_sexo = _esc(datos.get('sexo', '—'))
    pac_edad = _esc(datos.get('edad', '—'))
    pac_fnac = _esc(datos.get('fecha_nacimiento', '—'))
    pac_lnac = _esc(datos.get('lugar_nacimiento', '—'))
    pac_tel = _esc(datos.get('telefono', '—'))
    pac_dir = _esc(datos.get('direccion', '—'))
    pac_ins = _esc(datos.get('nivel_instruccion', '—'))
    pac_ocu = _esc(datos.get('ocupacion', '—'))
    pac_rel = _esc(datos.get('creencias_religiosas', '—'))
    f_ing = _esc(datos.get('fecha_ingreso', '—'))
    f_egr = _esc(datos.get('fecha_egreso', '—'))

    hero_patient = Table(
        [[
            [
                Paragraph("PACIENTE EVALUADO", st_lbl_micro),
                Paragraph(pac_nombre, st_val_hero),
            ],
            _field_cell("Cédula / ID", pac_cedula, bold_val=True),
            _field_cell("Edad", f"{pac_edad} años" if pac_edad != "—" else "—"),
            _field_cell("Sexo", pac_sexo),
        ]],
        colWidths=[240, 120, 85, 95],
    )
    hero_patient.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_TEAL_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.6, C_MINT_BORDER),
        ('LINEBEFORE', (0, 0), (0, -1), 3.0, C_TEAL),
        ('LINEAFTER', (0, 0), (2, -1), 0.4, C_MINT_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    fil_grid_rows = [
        [
            _field_cell("Fecha de Nacimiento", pac_fnac),
            _field_cell("Lugar de Nacimiento", pac_lnac),
            _field_cell("Fecha de Ingreso", f_ing),
            _field_cell("Fecha de Egreso", f_egr),
        ],
        [
            _field_cell("Teléfono", pac_tel),
            _field_cell("Nivel de Instrucción", pac_ins),
            _field_cell("Ocupación", pac_ocu),
            _field_cell("Creencias Religiosas", pac_rel),
        ],
        [
            _field_cell("Dirección / Domicilio", pac_dir),
            _field_cell("Solicitante / Referencia", _esc(datos.get('referencias', '—'))),
            _field_cell("Entorno Familiar", _esc(datos.get('entorno_familiar', '—'))),
            _field_cell("Estado del Expediente", condicion_str),
        ],
    ]
    if datos.get('pnf'):
        fil_grid_rows.append([
            _field_cell("PNF (Programa)", _esc(datos.get('pnf'))),
            _field_cell("Trayecto", _esc(datos.get('trayecto', 'N/A'))),
            _field_cell("Sección", _esc(datos.get('seccion', 'N/A'))),
            _field_cell("Año Académico", _esc(datos.get('anio_academico', 'N/A'))),
        ])

    t_fil = Table(fil_grid_rows, colWidths=[145, 135, 130, 130])
    t_fil.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.6, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, C_GRID),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(KeepTogether([
        _section_banner("01", "Identificación y Datos de Filiación"),
        Spacer(1, 6),
        hero_patient,
        Spacer(1, 6),
        t_fil,
    ]))
    story.append(Spacer(1, 12))

    # ── 02. Motivo de Consulta y Antecedentes ──
    motivo_box = Table(
        [[
            [
                Paragraph("MOTIVO DE CONSULTA PRINCIPAL", st_lbl_micro),
                Spacer(1, 2),
                Paragraph(_esc(datos.get('motivo_consulta', '—')), st_body),
            ]
        ]],
        colWidths=[540],
    )
    motivo_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_SURFACE),
        ('BOX', (0, 0), (-1, -1), 0.6, C_BORDER),
        ('LINEBEFORE', (0, 0), (0, -1), 3.0, C_TEAL),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))

    t_ant = _clean_kv_table([
        ("Ant. No Patológicos", _esc(datos.get('ant_no_patologicos'))),
        ("Ant. Patológicos", _esc(datos.get('ant_patologicos'))),
        ("Ant. Heredo-Familiares", _esc(datos.get('ant_heredo_mentales'))),
        ("Gestas / Pérdidas", _esc(datos.get('gestas_perdidas'))),
        ("Atención Psicológica Previa", _esc(datos.get('atencion_psicologica_previa'))),
        ("Evaluaciones Especialidad", _esc(datos.get('evaluaciones_especialidad'))),
    ])
    story.append(KeepTogether([
        _section_banner("02", "Motivo de Consulta y Antecedentes Clínicos"),
        Spacer(1, 6),
        motivo_box,
        Spacer(1, 6),
    ]))
    story.append(t_ant)
    story.append(Spacer(1, 12))

    # ── 03. Datos del Representante ──
    rep_nom = _esc(datos.get('rep_nombre', '—'))
    rep_ced = _esc(datos.get('rep_cedula', '—'))
    rep_edad = _esc(datos.get('rep_edad', '—'))
    rep_tel = _esc(datos.get('rep_telefono', datos.get('rep_edad_tel', '—')))
    rep_ins = _esc(datos.get('rep_instruccion', '—'))
    rep_ocu = _esc(datos.get('rep_ocupacion', '—'))

    t_rep_meta = Table(
        [
            [
                _field_cell("Nombre del Representante", rep_nom, bold_val=True),
                _field_cell("Cédula", rep_ced),
                _field_cell("Edad", f"{rep_edad} años" if rep_edad != "—" else "—"),
                _field_cell("Teléfono", rep_tel),
            ],
            [
                _field_cell("Instrucción Académica", rep_ins),
                _field_cell("Ocupación", rep_ocu),
                _field_cell("Etapa Amorosa", _esc(datos.get('rep_etapa_amorosa'))),
                _field_cell("Vínculo", "Padre / Madre / Representante"),
            ],
        ],
        colWidths=[165, 115, 130, 130],
    )
    t_rep_meta.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.6, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, C_GRID),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    t_rep_nar = _clean_kv_table([
        ("Antecedentes de Infancia", _esc(datos.get('rep_infancia'))),
        ("Antecedentes de Adultez", _esc(datos.get('rep_adultez'))),
    ])
    story.append(KeepTogether([
        _section_banner("03", "Datos del Padre, Madre o Representante"),
        Spacer(1, 6),
        t_rep_meta,
        Spacer(1, 5),
        t_rep_nar,
    ]))
    story.append(Spacer(1, 12))

    # ── 04. Preguntas de Autoexploración Emocional ──
    t_emoc = _clean_kv_table([
        ("1) ¿Eres feliz?", _esc(datos.get('pregunta_feliz'))),
        ("2) ¿Qué modificarías en tu vida?", _esc(datos.get('pregunta_modificar'))),
        ("3) ¿Cómo te proyectas en el futuro?", _esc(datos.get('pregunta_futuro'))),
    ], label_w=190)
    story.append(KeepTogether([
        _section_banner("04", "Autoexploración y Reflexión Emocional"),
        Spacer(1, 6),
        t_emoc,
    ]))
    story.append(Spacer(1, 12))

    # ── 05. Neurodesarrollo, Examen Clínico e IPX ──
    t_neuro = _clean_kv_table([
        ("Cuadro Clínico", _esc(datos.get('cuadro_clinico'))),
        ("Exploración Física", _esc(datos.get('exploracion_fisica'))),
        ("Hábitos Exterior", _esc(datos.get('habitos_exterior'))),
        ("Autonomía Motora", _esc(datos.get('autonomia_motora'))),
        ("Etapa Prenatal", _esc(datos.get('etapa_prenatal'))),
        ("Etapa Neonatal", _esc(datos.get('etapa_neonatal'))),
        ("Desarrollo Psicomotor", _esc(datos.get('desarrollo_psicomotor'))),
        ("Instrumentos de Evaluación", _esc(datos.get('instrumentos_evaluacion'))),
    ])
    story.append(KeepTogether([
        _section_banner("05", "Neurodesarrollo, Examen Clínico e Impresión Diagnóstica"),
        Spacer(1, 6),
    ]))
    story.append(t_neuro)
    story.append(Spacer(1, 10))

    # Bloque IPX destacado
    ipx_texto = _esc(datos.get('ipx'), 'Sin impresión diagnóstica registrada')
    t_ipx = Table(
        [
            [Paragraph("IMPRESIÓN DIAGNÓSTICA CLÍNICA (IPX)", st_ipx_hdr)],
            [Paragraph(ipx_texto, st_ipx_body)],
        ],
        colWidths=[540],
    )
    t_ipx.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), C_PETROL),
        ('BACKGROUND', (0, 1), (0, 1), C_TEAL_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1.2, C_TEAL),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(KeepTogether([t_ipx]))

    # ── Firma Profesional ──
    story.append(Spacer(1, 28))
    t_firma = Table(
        [[
            Paragraph(
                "______________________________________________<br/>"
                "<b>Especialista / Psicólogo(a) Evaluador(a)</b><br/>"
                "Firma, N° de Colegiado y Sello Profesional",
                st_firma,
            ),
            Paragraph(
                "______________________________________________<br/>"
                "<b>Fecha de Emisión y Conformidad</b><br/>"
                f"Generado el {fecha_elab} • PSIQUE",
                st_firma,
            ),
        ]],
        colWidths=[270, 270],
    )
    t_firma.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(KeepTogether([t_firma]))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath


def generar_pdf_listado_pacientes(filepath: str, pacientes: list, filtros: dict = None) -> str:
    """
    Genera un reporte PDF horizontal (apaisado) con el listado de pacientes
    filtrado, usando el diseño editorial clínico PSIQUE.
    """
    pacientes = pacientes or []
    filtros = filtros or {}

    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=30,
        bottomMargin=44,
        title="Listado de Pacientes - PSIQUE",
        author="PSIQUE - Sistema de Gestión Clínico Psicológica",
    )

    story = []

    # ── Paleta Clínica PSIQUE ──
    C_PETROL = colors.HexColor("#0B2B2E")
    C_TEAL = colors.HexColor("#0F766E")
    C_TEAL_LIGHT = colors.HexColor("#F0FDFA")
    C_MINT_BORDER = colors.HexColor("#99F6E4")
    C_SLATE_DARK = colors.HexColor("#0F172A")
    C_SLATE = colors.HexColor("#334155")
    C_MUTED = colors.HexColor("#64748B")
    C_SURFACE = colors.HexColor("#F8FAFC")
    C_BORDER = colors.HexColor("#CBD5E1")
    C_GRID = colors.HexColor("#E2E8F0")

    st_brand = ParagraphStyle(
        'LstBrand', fontName='Helvetica-Bold', fontSize=18, leading=20, textColor=C_PETROL
    )
    st_brand_sub = ParagraphStyle(
        'LstBrandSub', fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=C_MUTED
    )
    st_pill_hdr = ParagraphStyle(
        'LstPillHdr', fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.white, alignment=1
    )
    st_pill_meta = ParagraphStyle(
        'LstPillMeta', fontName='Helvetica', fontSize=8.2, leading=11.5,
        textColor=C_SLATE_DARK, alignment=1
    )
    st_lbl_micro = ParagraphStyle(
        'LstLblMicro', fontName='Helvetica-Bold', fontSize=7.2, leading=9.5, textColor=C_MUTED
    )
    st_th = ParagraphStyle(
        'LstTh', fontName='Helvetica-Bold', fontSize=8.3, leading=10.5, textColor=colors.white
    )
    st_td = ParagraphStyle(
        'LstTd', fontName='Helvetica', fontSize=8.2, leading=11, textColor=C_SLATE_DARK
    )
    st_td_bold = ParagraphStyle(
        'LstTdBold', fontName='Helvetica-Bold', fontSize=8.2, leading=11, textColor=C_PETROL
    )
    st_body = ParagraphStyle(
        'LstBody', fontName='Helvetica', fontSize=8.6, leading=12.5, textColor=C_SLATE
    )

    def _esc(val, default="—"):
        if val is None:
            return default
        s = str(val).strip()
        if not s:
            return default
        return html.escape(s).replace("\n", " ")

    # ── Encabezado Institucional PSIQUE (720pt ancho útil) ──
    logo_path = resource_path(os.path.join("data", "app_icon.png"))
    logo_cell = Image(logo_path, width=38, height=38) if os.path.exists(logo_path) else Paragraph("<b>Ψ</b>", st_brand)

    brand_block = Table(
        [[
            logo_cell,
            [
                Paragraph("PSIQUE", st_brand),
                Paragraph("Sistema de Gestión Clínico Psicológica", st_brand_sub),
                Paragraph("Reporte Filtrado de Pacientes Registrados", st_brand_sub),
            ],
        ]],
        colWidths=[46, 454],
    )
    brand_block.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    ahora_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    meta_card = Table(
        [
            [Paragraph("LISTADO DE PACIENTES", st_pill_hdr)],
            [Paragraph(f"<b>Emisión:</b> {ahora_str}", st_pill_meta)],
            [Paragraph(f"<b>Registros en reporte:</b> {len(pacientes)}", st_pill_meta)],
        ],
        colWidths=[216],
    )
    meta_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), C_PETROL),
        ('BACKGROUND', (0, 1), (0, -1), C_TEAL_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.8, C_TEAL),
        ('LINEBELOW', (0, 1), (0, 1), 0.4, C_MINT_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    t_header = Table([[brand_block, meta_card]], colWidths=[500, 220])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_TEAL, spaceBefore=7, spaceAfter=9))

    # ── Tarjeta de Criterios / Filtros Aplicados ──
    etiquetas_filtro = []
    for k, lbl in [
        ("busqueda", "Búsqueda"),
        ("tipo_cedula", "Tipo ID"),
        ("pnf", "PNF"),
        ("trayecto", "Trayecto"),
        ("seccion", "Sección"),
        ("anio", "Año"),
        ("sexo", "Sexo"),
    ]:
        val = (filtros.get(k) or "").strip()
        if val:
            etiquetas_filtro.append(f"<b>{html.escape(lbl)}:</b> {html.escape(val)}")

    resumen_filtros = "   •   ".join(etiquetas_filtro) if etiquetas_filtro else "Todos los pacientes registrados (sin filtros activos)"

    t_filtros = Table(
        [[[
            Paragraph("CRITERIOS DE FILTRADO APLICADOS", st_lbl_micro),
            Spacer(1, 2),
            Paragraph(resumen_filtros, st_body),
        ]]],
        colWidths=[720],
    )
    t_filtros.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_TEAL_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.6, C_MINT_BORDER),
        ('LINEBEFORE', (0, 0), (0, -1), 3.0, C_TEAL),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_filtros)
    story.append(Spacer(1, 10))

    # ── Tabla de Pacientes (720pt totales) ──
    rows = [[
        Paragraph("#", st_th),
        Paragraph("Cédula / ID", st_th),
        Paragraph("Nombres y Apellidos", st_th),
        Paragraph("Sexo", st_th),
        Paragraph("PNF / Programa", st_th),
        Paragraph("Trayecto", st_th),
        Paragraph("Secc.", st_th),
        Paragraph("Año", st_th),
        Paragraph("Teléfono", st_th),
        Paragraph("Edad", st_th),
    ]]

    for idx, p in enumerate(pacientes, start=1):
        ced = _esc(p.get("cedula") or p.get("id"))
        nom = _esc(p.get("nombre"))
        sexo = _esc(p.get("sexo"))
        pnf = _esc(p.get("pnf"), "Sin asignar")
        tray = _esc(p.get("trayecto"))
        sec = _esc(p.get("seccion"))
        anio = _esc(p.get("anio_academico"))
        tel = _esc(p.get("telefono"))
        edad = _esc(p.get("edad"))
        rows.append([
            Paragraph(str(idx), st_td),
            Paragraph(ced, st_td_bold),
            Paragraph(nom, st_td_bold),
            Paragraph(sexo, st_td),
            Paragraph(pnf, st_td),
            Paragraph(tray, st_td),
            Paragraph(sec, st_td),
            Paragraph(anio, st_td),
            Paragraph(tel, st_td),
            Paragraph(edad, st_td),
        ])

    if len(rows) == 1:
        rows.append([Paragraph("—", st_td)] * 10)

    col_w = [26, 78, 152, 56, 130, 68, 38, 38, 94, 40]  # suma = 720
    t_lista = Table(rows, colWidths=col_w, repeatRows=1)
    t_lista.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PETROL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (6, 0), (7, -1), 'CENTER'),
        ('ALIGN', (9, 0), (9, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_SURFACE]),
        ('BOX', (0, 0), (-1, -1), 0.7, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, C_GRID),
    ]))
    story.append(t_lista)

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath
