
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def generate_report(data, output_path):

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#1d4ed8"),
        fontSize=20,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1d4ed8"),
        spaceBefore=15,
        spaceAfter=8
    )

    story = []

    story.append(Paragraph(
        "AI Resume Analyzer Report",
        title_style
    ))

    story.append(Paragraph(
        f"Overall Resume Match: {data['match_score']}%",
        styles["Heading2"]
    ))

    story.append(Spacer(1, 15))

    story.append(Paragraph(
        "Score Breakdown",
        heading_style
    ))

    score_data = [
        ["Category", "Score"],
        ["Skill Matching", f"{data['skill_score']}%"],
        ["Semantic Similarity", f"{data['semantic_score']}%"],
        ["Education Matching", f"{data['education_score']}%"],
        ["Project Relevance", f"{data['project_score']}%"],
        ["Experience Matching", f"{data['experience_score']}%"]
    ]

    table = Table(score_data, colWidths=[3 * inch, 2 * inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(table)


    # ATS Compatibility Analysis

    story.append(Paragraph(
        "ATS Compatibility Analysis",
        heading_style
    ))

    story.append(Paragraph(
        f"<b>ATS Compatibility Score: {data['ats_score']}%</b>",
        styles["Heading2"]
    ))

    ats_data = [
        ["ATS Screening Check", "Result"]
    ]

    for check, passed in data["ats_checks"].items():
        status = "Passed" if passed else "Needs Improvement"
        ats_data.append([check, status])

    ats_table = Table(
        ats_data,
        colWidths=[3 * inch, 2 * inch]
    )

    ats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(ats_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "ATS Improvement Recommendations",
        heading_style
    ))

    for recommendation in data["ats_recommendations"]:
        story.append(Paragraph(
            f"- {recommendation}",
            styles["BodyText"]
        ))
        story.append(Spacer(1, 5))

    # Job Description Keyword Match

    story.append(Paragraph(
        "Job Description Keyword Match",
        heading_style
    ))

    story.append(Paragraph(
        f"Keyword Match Percentage: "
        f"{data['keyword_match_percentage']}%",
        styles["BodyText"]
    ))

    story.append(Spacer(1, 10))


    story.append(Paragraph("Skills Analysis", heading_style))

   
    # Skills Analysis

    story.append(Paragraph(
        "Skills Analysis",
        heading_style
    ))

    story.append(Paragraph(
        "Matched Skills: " + ", ".join(data["matched_skills"]),
        styles["BodyText"]
    ))

    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Missing Skills: " + ", ".join(data["missing_skills"]),
        styles["BodyText"]
    ))

    story.append(Paragraph(
        "Skill Recommendations",
        heading_style
    ))

    for item in data["skill_gap_recommendations"]:
        story.append(Paragraph(
            f"<b>{item['skill']}</b> - "
            f"Priority: {item['priority']}<br/>"
            f"{item['recommendation']}",
            styles["BodyText"]
        ))
        story.append(Spacer(1, 5))

    # Certification Analysis

    story.append(Paragraph(
        "Certification Analysis",
        heading_style
    ))

    story.append(Paragraph(
        "Certifications Found: " +
        (", ".join(data["resume_certifications"]) or "None"),
        styles["BodyText"]
    ))

    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "Certifications in Job Description: " +
        (", ".join(data["jd_certifications"]) or "None"),
        styles["BodyText"]
    ))

    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "Matching Certifications: " +
        (", ".join(data["matched_certifications"]) or "None"),
        styles["BodyText"]
    ))

    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "Missing or Recommended Certifications: " +
        (", ".join(data["missing_certifications"]) or "None"),
        styles["BodyText"]
    ))

    story.append(Spacer(1, 10))

    # Resume Section Completeness

    # Resume Section Completeness

    story.append(Paragraph(
        "Resume Section Completeness",
        heading_style
    ))

    story.append(Paragraph(
        f"Completeness Score: {data['section_completeness']}%",
        styles["Heading2"]
    ))

    section_data = [
        ["Resume Section", "Status"]
    ]

    for section, completed in data["resume_sections"].items():
        status = "Detected" if completed else "Missing"
        section_data.append([section, status])

    section_table = Table(
        section_data,
        colWidths=[3 * inch, 2 * inch]
    )

    section_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(section_table)
    story.append(Spacer(1, 12))


    # Resume Improvement Scorecard

    scorecard = data["resume_scorecard"]

    story.append(Paragraph(
        "Resume Improvement Scorecard",
        heading_style
    ))

    story.append(Paragraph(
        f"<b>Overall Improvement Score: {scorecard['total']}/100</b>",
        styles["Heading2"]
    ))

    scorecard_data = [
        ["Category", "Score"],
        ["Resume Sections", f"{scorecard['sections']}/40"],
        ["Measurable Achievements", f"{scorecard['achievements']}/20"],
        ["Action Verbs", f"{scorecard['action_verbs']}/15"],
        ["Project Descriptions", f"{scorecard['projects']}/15"],
        ["Resume Length", f"{scorecard['length']}/10"]
    ]

    scorecard_table = Table(
        scorecard_data,
        colWidths=[3 * inch, 2 * inch]
    )

    scorecard_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(scorecard_table)
    story.append(Spacer(1, 12))


    for section, completed in data["resume_sections"].items():
        status = "Detected" if completed else "Missing"

        story.append(Paragraph(
            f"{section}: {status}",
            styles["BodyText"]
        ))

    story.append(Paragraph(
        "Project Analysis",
        heading_style
    ))

    for project in data["project_analysis"]:

        story.append(Paragraph(
            f"<b>{project['project_name']}</b>",
            styles["Heading3"]
        ))

        story.append(Paragraph(
            f"Project Relevance: {project['relevance_score']}%",
            styles["BodyText"]
        ))

        story.append(Paragraph(
            f"Technologies: {', '.join(project['all_technologies'])}",
            styles["BodyText"]
        ))

        story.append(Spacer(1, 10))

    story.append(Paragraph(
        "Resume Improvement Suggestions",
        heading_style
    ))

    for suggestion in data["suggestions"]:
        story.append(Paragraph(
            f"- {suggestion}",
            styles["BodyText"]
        ))
        story.append(Spacer(1, 5))

    doc.build(story)
