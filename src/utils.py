import os
from flask import send_file
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime

# Colores oficiales de la UTP
UTP_BLUE = colors.Color(0, 0.129, 0.278)
UTP_RED = colors.Color(0.682, 0.125, 0.204)

def get_logo_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'static', 'img', 'logo.png')

def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(UTP_BLUE)
    page_num = canvas.getPageNumber()
    text = "Página %s" % page_num
    canvas.drawRightString(7.5 * inch, 0.75 * inch, text)
    canvas.restoreState()

def header_footer(canvas, doc):
    canvas.saveState()
    # Header
    logo = get_logo_path()
    try:
        # Ajusta estas coordenadas para bajar la posición del logo
        canvas.drawImage(logo, inch, 9 * inch, width=1.2*inch, height=1.2*inch, mask='auto')
    except:
        print(f"No se pudo cargar el logo desde {logo}")
        # Dibuja un rectángulo como placeholder si la imagen no se puede cargar
        canvas.setStrokeColor(UTP_BLUE)
        canvas.setFillColor(UTP_BLUE)
        canvas.rect(inch, 9.8 * inch, 1.5*inch, 1.5*inch, fill=True)
    canvas.setFont('Helvetica-Bold', 16)
    canvas.setFillColor(UTP_BLUE)
    canvas.drawString(2.5*inch, 9.7 * inch, "Universidad Tecnológica del Perú")
    canvas.setFont('Helvetica-Bold', 14)
    canvas.drawString(2.5*inch, 9.4 * inch, "Reporte de Mantenimiento de Equipos")
    canvas.setFont('Helvetica', 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(2.5*inch, 9.1 * inch, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    # Footer
    canvas.setStrokeColor(UTP_RED)
    canvas.line(inch, inch, 7.5*inch, inch)
    add_page_number(canvas, doc)
    canvas.restoreState()

def generate_maintenance_report(programacion):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            rightMargin=inch, leftMargin=inch,
                            topMargin=2*inch, bottomMargin=inch)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))
    styles.add(ParagraphStyle(name='JustifyWithBorder', 
                              borderColor=UTP_BLUE, 
                              borderWidth=1, 
                              borderPadding=5, 
                              textColor=UTP_BLUE,
                              fontSize=10))
    
    elements = []

    # Información del reporte
    elements.append(Paragraph("Detalles del Mantenimiento", styles['Heading1']))
    elements.append(Spacer(1, 0.25*inch))

    info = f"""Este reporte detalla el mantenimiento programado para el equipo {programacion['equipo_nombre']} 
    ubicado en el laboratorio {programacion['laboratorio_nombre']} de la carrera de {programacion['carrera_nombre']}. 
    El mantenimiento está programado para el año {programacion['anio']}, mes {programacion['mes']}, 
    y su estado actual es {programacion['estado']}."""
    elements.append(Paragraph(info, styles['JustifyWithBorder']))
    elements.append(Spacer(1, 0.25*inch))

    data = [
        ['Equipo', programacion['equipo_nombre']],
        ['Código', programacion['equipo_codigo']],
        ['Marca', programacion['equipo_marca']],
        ['Serie', programacion['equipo_serie']],
        ['Modelo', programacion['equipo_modelo']],
        ['Laboratorio', programacion['laboratorio_nombre']],
        ['Carrera', programacion['carrera_nombre']],
        ['Tipo de Mantenimiento', programacion['tipo_mantenimiento']],
        ['Año', programacion['anio']],
        ['Mes', programacion['mes']],
        ['Estado', programacion['estado']],
        ['Fecha Realizado', programacion['fecha_realizado'] or 'N/A'],
        ['Realizado Por', programacion['realizado_por'] or 'N/A'],
        ['Observaciones', programacion['observaciones'] or 'N/A']

    ]

    table = Table(data, colWidths=[2.75*inch, 3.75*inch])
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (0,-1), UTP_BLUE),
        ('TEXTCOLOR', (0,0), (0,-1), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, UTP_BLUE),
        ('BOX', (0,0), (-1,-1), 1, UTP_BLUE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (1,0), (1,-1), colors.white),
        ('TEXTCOLOR', (1,0), (1,-1), colors.black),
    ])

    table.setStyle(table_style)
    elements.append(table)

    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Este es un documento oficial de la Universidad Tecnológica del Perú. "
                              "Para cualquier consulta, por favor contacte al Departamento de Mantenimiento.", 
                              styles['Italic']))

    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

    buffer.seek(0)
    return buffer