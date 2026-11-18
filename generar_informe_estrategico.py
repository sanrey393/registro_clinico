# -*- coding: utf-8 -*-
"""
Script para generar el Informe de Análisis y Plan Estratégico de Mejoras
para el Sistema de Registro Clínico y Gestión Médica.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas para numeración de páginas tipo 'Página X de Y' y encabezado/pie institucional."""
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
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Encabezado (a partir de la página 2)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Sistema de Registro Clínico — Plan Estratégico & Hoja de Ruta 2027")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Pie de página (en todas las páginas)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)

        self.drawString(54, 32, "Confidencial — Uso Interno y Desarrollo Tecnológico")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Definición de paleta de colores profesional
    PRIMARY = colors.HexColor("#1a2744")   # Azul marino oscuro
    SECONDARY = colors.HexColor("#0284c7") # Azul celeste corporativo
    TEXT_DARK = colors.HexColor("#1e293b") # Carbón lectura
    TEXT_MUTED = colors.HexColor("#64748b")
    BG_LIGHT = colors.HexColor("#f8fafc")  # Fondo paneles suaves
    BORDER_CLR = colors.HexColor("#e2e8f0")
    ACCENT_GREEN = colors.HexColor("#059669")

    # Estilos tipográficos
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=PRIMARY,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=TEXT_DARK,
        leftIndent=14,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK
    )

    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=PRIMARY
    )

    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=TEXT_DARK
    )

    story = []

    # ─────────────────────────────────────────────────────────────
    # PORTADA / ENCABEZADO EJECUTIVO
    # ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(Paragraph("INFORME DE ANÁLISIS Y PLAN ESTRATÉGICO", title_style))
    story.append(Paragraph("Sistema de Registro Clínico, Gestión Médica y Salud Digital", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceAfter=14))

    # Ficha de metadatos en tabla estética
    meta_data = [
        [Paragraph("<b>Proyecto:</b>", meta_label), Paragraph("Sistema Clínico - Psicología & Medicina General", meta_val),
         Paragraph("<b>Fecha:</b>", meta_label), Paragraph("Noviembre 2026 / Plan de Evolución 2027", meta_val)],
        [Paragraph("<b>Tecnología:</b>", meta_label), Paragraph("Python 3.10+, PyQt6, Firebase, SQLite", meta_val),
         Paragraph("<b>Estado Actual:</b>", meta_label), Paragraph("Fase de Producción / Base Consolidada", meta_val)],
        [Paragraph("<b>Distribución:</b>", meta_label), Paragraph("PyInstaller (.exe) + Inno Setup (.iss)", meta_val),
         Paragraph("<b>Alcance Futuro:</b>", meta_label), Paragraph("HealthTech / Multi-Clínica / IA Asistencial", meta_val)]
    ]
    meta_table = Table(meta_data, colWidths=[70, 180, 80, 174])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # ─────────────────────────────────────────────────────────────
    # SECCIÓN 1: BALANCE GENERAL DEL SISTEMA ACTUAL
    # ─────────────────────────────────────────────────────────────
    story.append(Paragraph("1. Diagnóstico y Balance General del Sistema Desarrollado", h1_style))
    story.append(Paragraph(
        "El sistema ha alcanzado un <b>nivel de madurez, arquitectura y robustez notablemente alto</b>, "
        "superando con creces la etapa de prototipo experimental. Se encuentra estructurado como una solución "
        "de escritorio profesional y comercializable para consultorios médicos y psicológicos.",
        body_style
    ))

    # Tabla resumen de fortalezas actuales
    balance_data = [
        [Paragraph("<b>Dimensión</b>", meta_label), Paragraph("<b>Evaluación & Implementación Lograda</b>", meta_label)],
        [
            Paragraph("<b>Arquitectura & UI</b>", meta_label),
            Paragraph("Separación modular estricta (<code>core/</code>, <code>database/</code>, <code>ui/</code>, <code>data/</code>). Soporte para tema Claro y Oscuro (QSS), navegación fluida mediante Dashboard lateral y barra de menú con atajos de teclado nativos.", body_style)
        ],
        [
            Paragraph("<b>Persistencia Híbrida</b>", meta_label),
            Paragraph("Filosofía <i>Offline-First</i>: almacenamiento local en SQLite de alta velocidad con sincronización bidireccional en la nube mediante Firebase Firestore. Permite consulta ininterrumpida sin conexión.", body_style)
        ],
        [
            Paragraph("<b>Cobertura Clínica</b>", meta_label),
            Paragraph("Ficha de paciente, antecedentes patológicos, notas de evolución por sesión, catálogo oficial CIE-10, catálogo de fármacos, calculadora de IMC/edad/dosis y generación de recetas en PDF.", body_style)
        ],
        [
            Paragraph("<b>Seguridad & Privacidad</b>", meta_label),
            Paragraph("Cifrado AES-256 (Fernet) de registros sensibles, cierre de sesión por inactividad a los 15 minutos, protección contra ataques de fuerza bruta en login.", body_style)
        ],
        [
            Paragraph("<b>Licenciamiento & Distribución</b>", meta_label),
            Paragraph("Control de licencias por Hardware ID (MachineGuid + CPU), activación local y en la nube. Script de compilación desatendida a binario (PyInstaller) e instalador profesional con Inno Setup.", body_style)
        ]
    ]

    balance_table = Table(balance_data, colWidths=[130, 374])
    balance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(balance_table)
    story.append(Spacer(1, 14))

    # ─────────────────────────────────────────────────────────────
    # SECCIÓN 2: PILARES DE EXPANSIÓN Y MEJORAS DE GRAN ALCANCE
    # ─────────────────────────────────────────────────────────────
    story.append(Paragraph("2. Pilares de Expansión Estratégica para la Próxima Etapa", h1_style))
    story.append(Paragraph(
        "Para transformar el software en un ecosistema de salud digital líder (HealthTech) con capacidad "
        "de comercialización a escala (SaaS) y despliegue en policonsultorios y clínicas, se definen los siguientes 5 pilares:",
        body_style
    ))

    # Pilar 1
    story.append(Paragraph("Pilar I: Inteligencia Clínica e IA Asistencial", h2_style))
    story.append(Paragraph("<b>• Dictado por Voz y Redacción Automatizada de Notas:</b> Integración de modelos de procesamiento de lenguaje natural y transcripción (ej. OpenAI Whisper). El especialista dicta la consulta libremente y el sistema estructura automáticamente los campos: Motivo, Exploración, Diagnóstico presuntivo y Plan.", bullet_style))
    story.append(Paragraph("<b>• Motor de Alertas de Interacciones Farmacológicas:</b> Cruce automático en tiempo real entre la receta médica emitida, alergias reportadas y antecedentes de prescripciones del paciente para alertar contraindicaciones o toxicidades sinérgicas.", bullet_style))
    story.append(Paragraph("<b>• Escalas y Tests Psicométricos Digitalizados:</b> Formularios automáticos de evaluación psicológica (PHQ-9 para depresión, GAD-7 para ansiedad, Test de Beck) con cálculo instantáneo de percentiles y gráficas comparativas de evolución entre sesiones.", bullet_style))

    # Pilar 2
    story.append(Paragraph("Pilar II: Comunicación Omnicanal y Experiencia del Paciente", h2_style))
    story.append(Paragraph("<b>• Automatización de Recordatorios por WhatsApp & SMS:</b> Integración con APIs de mensajería para confirmación interactiva de turnos ('Confirmar', 'Reprogramar', 'Cancelar'), reduciendo el ausentismo clínico hasta en un 40%.", bullet_style))
    story.append(Paragraph("<b>• Despacho Automatizado de Recetas:</b> Envío automático del PDF de la receta, indicaciones terapéuticas y comprobantes de pago al correo o WhatsApp del paciente al finalizar la consulta.", bullet_style))
    story.append(Paragraph("<b>• Portal Web del Paciente (PWA):</b> Módulo web complementario ligero donde el paciente puede consultar su historial de citas, descargar recetas vigentes y consultar saldos.", bullet_style))

    # Pilar 3
    story.append(Paragraph("Pilar III: Arquitectura Multiusuario, Roles Granulares y Auditoría (Clínicas)", h2_style))
    story.append(Paragraph("<b>• Control de Acceso Basado en Roles (RBAC):</b>", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;– <i>Médico / Psicólogo:</i> Acceso exclusivo a expedientes asignados e historias confidenciales.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;– <i>Recepción / Secretaria:</i> Acceso a agenda de turnos, cobranzas y datos demográficos; bloqueo estricto de notas clínicas confidenciales.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;– <i>Administrador:</i> Gestión global de usuarios, tarifas, finanzas y reportes.", bullet_style))
    story.append(Paragraph("<b>• Registro Inmutable de Auditoría (Audit Trail / Cumplimiento HIPAA):</b> Registro histórico protegido que almacena: fecha, hora, usuario, IP y tipo de operación (lectura, edición, eliminación) sobre cada ficha médica.", bullet_style))

    # Pilar 4
    story.append(Paragraph("Pilar IV: Interoperabilidad Médica y Firma Digital", h2_style))
    story.append(Paragraph("<b>• Receta Electrónica Verificable con QR:</b> Generación de código QR único por prescripción. Al escanearlo, las farmacias o pacientes pueden verificar la autenticidad e integridad del documento en un portal web seguro.", bullet_style))
    story.append(Paragraph("<b>• Firma Digital Criptográfica (X.509):</b> Integración de certificados digitales oficiales de colegios médicos para firma electrónica avanzada de informes periciales, certificados médicos y recetas.", bullet_style))
    story.append(Paragraph("<b>• Estándar HL7 / FHIR:</b> Capacidad de exportación e interoperabilidad para compartir expedientes con sistemas hospitalarios o aseguradoras de salud.", bullet_style))

    # Pilar 5
    story.append(Paragraph("Pilar V: Infraestructura, DevOps y Modelo Comercial (SaaS)", h2_style))
    story.append(Paragraph("<b>• Sistema de Actualizaciones Desatendidas (Auto-Updater):</b> Mecanismo en segundo plano para notificar y aplicar parches y mejoras desde servidores en la nube sin necesidad de reinstalación manual.", bullet_style))
    story.append(Paragraph("<b>• Soporte Backend Dual (Nube / Servidor Local):</b> Adaptador de datos que permita usar Firebase (nube) o un servidor local PostgreSQL contenerizado con Docker para clínicas con requisitos legales de datos en sitio (On-Premise).", bullet_style))
    story.append(Paragraph("<b>• Pasarelas de Pago Integradas:</b> Cobros con tarjeta y links de pago para telemedicina y consultas presenciales (Stripe, Mercado Pago o transferencias verificadas).", bullet_style))

    story.append(Spacer(1, 10))

    # ─────────────────────────────────────────────────────────────
    # SECCIÓN 3: HOJA DE RUTA Y CRONOGRAMA POR FASES
    # ─────────────────────────────────────────────────────────────
    story.append(Paragraph("3. Hoja de Ruta de Implementación (Roadmap)", h1_style))
    story.append(Paragraph("Plan de desarrollo estructurado en 3 fases secuenciales para garantizar avances estables y de alto impacto:", body_style))

    roadmap_data = [
        [Paragraph("<b>Fase</b>", meta_label), Paragraph("<b>Objetivos Principales</b>", meta_label), Paragraph("<b>Entregables Clave</b>", meta_label)],
        [
            Paragraph("<b>Fase 1<br/>Base Operativa & Roles</b>", meta_label),
            Paragraph("Adaptación multi-usuario y canales de notificación externa.", body_style),
            Paragraph("• Sistema RBAC (Médico/Secretaria/Admin)<br/>• Notificaciones y recordatorios por WhatsApp/Email<br/>• Receta electrónica con código QR verificable", bullet_style)
        ],
        [
            Paragraph("<b>Fase 2<br/>Expansión Clínica & Portal</b>", meta_label),
            Paragraph("Herramientas especializadas para psicología/medicina y conexión con el paciente.", body_style),
            Paragraph("• Módulo de tests y escalas psicométricas (PHQ-9, GAD-7)<br/>• Motor de alertas de interacción de fármacos<br/>• Portal Web del Paciente para recetas y citas", bullet_style)
        ],
        [
            Paragraph("<b>Fase 3<br/>IA & Escalamiento SaaS</b>", meta_label),
            Paragraph("Vanguardia tecnológica, modelo comercial y distribución corporativa.", body_style),
            Paragraph("• Transcripción y dictado médico por voz con IA<br/>• Sistema de Auto-Updater transparente en segundo plano<br/>• Soporte para servidor local PostgreSQL (On-Premise)", bullet_style)
        ]
    ]

    roadmap_table = Table(roadmap_data, colWidths=[95, 175, 234])
    roadmap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(roadmap_table)
    story.append(Spacer(1, 14))

    # ─────────────────────────────────────────────────────────────
    # SECCIÓN 4: CONCLUSIÓN Y RECOMENDACIONES TÉCNICAS
    # ─────────────────────────────────────────────────────────────
    story.append(Paragraph("4. Conclusión y Recomendaciones de Ingeniería", h1_style))
    story.append(Paragraph(
        "El proyecto posee cimientos arquitectónicos sumamente sólidos. Las decisiones tomadas en el diseño inicial "
        "(separación estricta de capas, SQLite local desacoplado de Firebase, encriptación AES-256 e instalador formal) "
        "facilitan enormemente la incorporación progresiva de estas nuevas capacidades sin necesidad de reescribir el sistema. "
        "Con la ejecución de esta hoja de ruta, la aplicación se posicionará como una plataforma de referencia "
        "en el sector de la salud digital.",
        body_style
    ))

    # Caja de resumen
    summary_data = [[
        Paragraph(
            "<b>Recomendación Inmediata:</b> Comenzar por la <b>Fase 1 (Roles y Notificaciones WhatsApp)</b>, "
            "ya que es la que produce el mayor impacto inmediato percibido por consultorios y profesionales médicos en su operación diaria.",
            callout_style
        )
    ]]
    summary_box = Table(summary_data, colWidths=[504])
    summary_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93c5fd")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(summary_box)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Documento PDF generado exitosamente: {filename}")

if __name__ == "__main__":
    output_pdf = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Plan_Estrategico_Y_Mejoras_Sistema_Clinico.pdf"
    )
    build_pdf(output_pdf)
