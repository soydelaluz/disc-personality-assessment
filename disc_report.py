from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_pdf_report(normalized_score, relative_percentages, fig, style_info):
    """
    normalized_score: dict
    relative_percentages: dict
    fig: matplotlib figure object
    style_info: dict with title, description, strengths, challenges
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='Justify', alignment=4, leading=12))

    story = []

    story.append(Paragraph("Reporte de Evaluación de Personalidad DISC", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Gracias por completar la Evaluación de Personalidad DISC. Este reporte proporciona información sobre tu estilo de personalidad basada en tus respuestas.", styles['Justify']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Tu desglose de estilo DISC (Puntuaciones absolutas):", styles["Heading2"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Las siguientes puntuaciones representan tu nivel absoluto en cada estilo DISC en una escala del 0% al 100%. Un porcentaje más alto indica una tendencia más fuerte hacia ese estilo.", styles['Justify']))
    story.append(Spacer(1, 10))

    data = [['Estilo', 'Puntuación (0-100%)']]
    for style, score in normalized_score.items():
        data.append([style, f"{score:.2f}%"])

    table = Table(data, hAlign='LEFT', colWidths=[100, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Tu desglose de estilo DISC (Porcentajes relativos):", styles["Heading2"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Estos porcentajes representan la proporción de cada estilo DISC en relación con tu perfil de personalidad general. El total suma el 100%.", styles['Justify']))
    story.append(Spacer(1, 10))

    data = [['Estilo', 'Porcentaje relativo']]
    for style, score in relative_percentages.items():
        data.append([style, f"{score:.2f}%"])

    table = Table(data, hAlign='LEFT', colWidths=[100, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Cómo entender tus puntuaciones:", styles["Heading2"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Las puntuaciones absolutas indican la fuerza con la que manifiestas cada estilo DISC por sí solo, sin compararlo con otros estilos. Una puntuación más alta significa que tiendes a mostrar más comportamientos asociados a ese estilo.\n\n"
        "Los porcentajes relativos muestran cómo contribuye cada estilo a tu perfil de personalidad general en comparación con los demás estilos. Estos porcentajes suman el 100% y te ayudan a comprender qué estilos son más dominantes en tu personalidad.",
        styles['Justify']
    ))
    story.append(Spacer(1, 100))

    img_buffer = BytesIO()
    fig.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
    img_buffer.seek(0)
    img = Image(img_buffer, width=400, height=400)
    story.append(Spacer(1, 10))
    story.append(img)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Tu descripción personalizada del estilo DISC:", styles["Heading2"]))
    story.append(Spacer(1, 10))

    desc_text = f"<b>{style_info['title']}</b><br/><br/>{style_info['description']}<br/><br/><b>Fortalezas:</b> {style_info['strengths']}<br/><br/><b>Desafíos:</b> {style_info['challenges']}"
    story.append(Paragraph(desc_text, styles['Justify']))
    story.append(Spacer(1, 50))

    story.append(PageBreak())
    story.append(Paragraph("Cómo entender todos los estilos DISC:", styles["Heading2"]))
    story.append(Spacer(1, 10))
    styles_list = [
        ('Dominancia (D):', 'Tiendes a ser directo, orientado a los resultados y asertivo. Te motivan los retos y la consecución de resultados tangibles.'),
        ('Influencia (I):', 'Sueles ser extrovertido, entusiasta y optimista. Disfrutas de las interacciones sociales y de persuadir a los demás.'),
        ('Estabilidad (S):', 'Sueles ser paciente, solidario y estar orientado al equipo. Valoras la cooperación y la armonía en las relaciones.'),
        ('Cumplimiento (C):', 'Tiendes a ser analítico, preciso y detallista. Te centras en la exactitud, la calidad y la experiencia.')
    ]
    for title, description in styles_list:
        story.append(Paragraph(f"<b>{title}</b> {description}", styles['Justify']))
        story.append(Spacer(1, 5))
    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "Recuerda que todo el mundo tiene aspectos de los cuatro estilos, pero la mayoría de la gente tiende a gravitar hacia uno o dos estilos principales. "
            "Tu combinación única de estilos influye en tu forma de comunicarte, tomar decisiones e interactuar con los demás.",
            styles['Justify']
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "Utiliza esta información para mejorar tus relaciones personales y profesionales reconociendo y apreciando los diferentes estilos en ti mismo y en los demás.",
            styles['Justify']
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer
