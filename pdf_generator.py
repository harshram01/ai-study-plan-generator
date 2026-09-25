import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def create_study_plan_pdf(profile, plan) -> io.BytesIO:
    """
    Generates a structured multi-section PDF containing:
    - Header & Student Metadata
    - Diagnostic Summary
    - Subject Score Gap Analysis Table
    - Weekly Timetable Schedule Table
    - Actionable Study Tips & Guidance
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=6
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )

    elements = []

    # --- Title & Metadata ---
    elements.append(Paragraph("Student Performance & Study Plan Report", title_style))
    student_id = getattr(profile, "student_id", "N/A")
    avail_hours = getattr(profile, "available_hours_per_week", "N/A")
    meta_text = f"<b>Student ID:</b> {student_id} &nbsp;|&nbsp; <b>Weekly Study Allocation:</b> {avail_hours} Hours"
    elements.append(Paragraph(meta_text, body_style))
    elements.append(Spacer(1, 10))

    # --- 1. Diagnostic Summary ---
    elements.append(Paragraph("1. Diagnostic Summary", section_style))
    diagnostic_text = getattr(plan, "diagnostic_summary", "No diagnostic summary available.")
    elements.append(Paragraph(diagnostic_text, body_style))
    elements.append(Spacer(1, 10))

    # --- 2. Subject Gap Analysis Table ---
    if hasattr(profile, "subjects") and profile.subjects:
        elements.append(Paragraph("2. Subject Gap Analysis", section_style))
        perf_data = [[
            Paragraph("Subject", table_header_style),
            Paragraph("Current", table_header_style),
            Paragraph("Target", table_header_style),
            Paragraph("Identified Weak Areas", table_header_style)
        ]]

        for sub_name, score_obj in profile.subjects.items():
            current = f"{getattr(score_obj, 'current_score', 'N/A')}%"
            target = f"{getattr(score_obj, 'target_score', 'N/A')}%"
            weak_topics = getattr(score_obj, 'weak_areas', [])
            weak_str = ", ".join(weak_topics) if weak_topics else "None specified"

            perf_data.append([
                Paragraph(str(sub_name), table_cell_style),
                Paragraph(current, table_cell_style),
                Paragraph(target, table_cell_style),
                Paragraph(weak_str, table_cell_style)
            ])

        t_perf = Table(perf_data, colWidths=[120, 60, 60, 300])
        t_perf.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        elements.append(t_perf)
        elements.append(Spacer(1, 10))

    # --- 3. Weekly Timetable Schedule ---
    weekly_schedule = getattr(plan, "weekly_schedule", [])
    if weekly_schedule:
        elements.append(Paragraph("3. Weekly Study Timetable", section_style))
        schedule_data = [[
            Paragraph("Day", table_header_style),
            Paragraph("Subject", table_header_style),
            Paragraph("Topic", table_header_style),
            Paragraph("Hours", table_header_style),
            Paragraph("Recommended Action", table_header_style)
        ]]

        for item in weekly_schedule:
            schedule_data.append([
                Paragraph(str(getattr(item, "day", "")), table_cell_style),
                Paragraph(str(getattr(item, "subject", "")), table_cell_style),
                Paragraph(str(getattr(item, "topic", "")), table_cell_style),
                Paragraph(f"{getattr(item, 'duration_hours', '')}h", table_cell_style),
                Paragraph(str(getattr(item, "recommended_action", "")), table_cell_style)
            ])

        t_sched = Table(schedule_data, colWidths=[65, 110, 110, 45, 210])
        t_sched.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        elements.append(t_sched)
        elements.append(Spacer(1, 10))

    # --- 4. Priority Remediation Topics ---
    priority_topics = getattr(plan, "priority_topics", [])
    if priority_topics:
        elements.append(Paragraph("4. High-Priority Remediation Topics", section_style))
        for topic in priority_topics:
            elements.append(Paragraph(f"• {topic}", body_style))
        elements.append(Spacer(1, 8))

    # --- 5. Study Tips & Strategies ---
    study_tips = getattr(plan, "study_tips", [])
    if study_tips:
        elements.append(Paragraph("5. Recommended Study Strategies", section_style))
        for tip in study_tips:
            elements.append(Paragraph(f"• {tip}", body_style))

    # Build the document into the memory buffer
    doc.build(elements)
    buffer.seek(0)
    return buffer