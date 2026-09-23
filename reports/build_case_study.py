"""Build the recruiter-facing survey tabulation case study PDF.

Run from the repository root with Python 3.11:
    py -3.11 reports/build_case_study.py

The report uses only validated values and documentation already persisted in
this repository. It does not read or modify raw survey data or the Excel file.
"""

import csv
from io import BytesIO
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "reports" / "Social_Media_Survey_Tabulation_Case_Study.pdf"
PREVIEW = ROOT / "assets" / "tab-book-preview.png"

PAGE_W, PAGE_H = landscape(letter)
PORTRAIT_W, PORTRAIT_H = letter

NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2E6F95")
TEAL = colors.HexColor("#3E7C83")
CORAL = colors.HexColor("#D86C4A")
INK = colors.HexColor("#24313A")
MID = colors.HexColor("#5D6A72")
LIGHT = colors.HexColor("#E7EEF2")
PALE = colors.HexColor("#F4F7F8")
WHITE = colors.white

BODY = ParagraphStyle(
    "body", fontName="Helvetica", fontSize=9.2, leading=12.2,
    textColor=INK, spaceAfter=0,
)
SMALL = ParagraphStyle(
    "small", fontName="Helvetica", fontSize=7.2, leading=9.3,
    textColor=MID,
)
CAPTION = ParagraphStyle(
    "caption", fontName="Helvetica-Oblique", fontSize=6.7, leading=8.2,
    textColor=MID,
)


def paragraph(canvas, text, x, y_top, width, height, style=BODY):
    item = Paragraph(text, style)
    _, h = item.wrap(width, height)
    item.drawOn(canvas, x, y_top - h)
    return h


def header(canvas, page_no, title, subtitle=None):
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 70, PAGE_W, 70, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 21)
    canvas.drawString(38, PAGE_H - 38, title)
    if subtitle:
        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor(colors.HexColor("#D6E3EA"))
        canvas.drawRightString(PAGE_W - 38, PAGE_H - 37, subtitle)
    canvas.setStrokeColor(LIGHT)
    canvas.line(38, 26, PAGE_W - 38, 26)
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 6.8)
    canvas.drawString(38, 14, "Carlos Henrique Nakagomi | Independent survey tabulation portfolio project")
    canvas.drawRightString(PAGE_W - 38, 14, str(page_no))


def stat(canvas, x, y, value, label, color=BLUE, width=120):
    canvas.setFillColor(color)
    canvas.setFont("Helvetica-Bold", 20)
    canvas.drawString(x, y, value)
    canvas.setFillColor(MID)
    paragraph(canvas, label, x, y - 6, width, 30, SMALL)


def bar(canvas, x, y, width, value, label, color, max_value=100, suffix="%"):
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(INK)
    canvas.drawString(x, y + 5, label)
    track_x = x + 112
    track_w = width - 155
    canvas.setFillColor(LIGHT)
    canvas.roundRect(track_x, y, track_w, 10, 5, fill=1, stroke=0)
    canvas.setFillColor(color)
    canvas.roundRect(track_x, y, track_w * value / max_value, 10, 5, fill=1, stroke=0)
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawRightString(x + width, y + 2.5, f"{value:.1f}{suffix}")


def rule_title(canvas, text, x, y, width):
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(x, y, text)
    text_w = stringWidth(text, "Helvetica-Bold", 11)
    canvas.setStrokeColor(LIGHT)
    canvas.setLineWidth(1)
    canvas.line(x + text_w + 10, y + 3, x + width, y + 3)


def page_one(canvas):
    header(canvas, 1, "Social Media Platform Usage & User Motivations", "PROJECT OVERVIEW")

    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 23)
    canvas.drawString(38, 500, "Cross-platform survey tabulation study")
    paragraph(
        canvas,
        "A reproducible portfolio analysis that converts routed survey microdata into "
        "weighted cross-tabulations, demographic comparisons, significance markers, "
        "independent QA, and a formatted Excel tab book.",
        38, 474, 430, 58,
        ParagraphStyle("lead", parent=BODY, fontSize=12, leading=16, textColor=INK),
    )

    canvas.setFillColor(PALE)
    canvas.roundRect(38, 332, 430, 82, 7, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(52, 392, "RESEARCH QUESTION")
    paragraph(
        canvas,
        "How do social media usage patterns and motivations differ across Facebook, "
        "Instagram, X, and TikTok, and across demographic groups?",
        52, 380, 400, 48,
        ParagraphStyle("question", parent=BODY, fontSize=12, leading=15, textColor=NAVY),
    )

    stat(canvas, 505, 485, "10,454", "analytic-file records", BLUE)
    stat(canvas, 635, 485, "10,287", "survey respondents", TEAL)
    stat(canvas, 505, 420, "195", "source variables", CORAL)
    stat(canvas, 635, 420, "28", "motivation outcomes", BLUE)
    stat(canvas, 505, 355, "4", "social platforms", TEAL)
    stat(canvas, 635, 355, "5", "demographic banners", CORAL)
    stat(canvas, 505, 290, "28", "final cross-tabulations", NAVY, 250)

    rule_title(canvas, "Methodology at a glance", 38, 250, 430)
    steps = [
        "Questionnaire", "Initial screening", "Routing & universe validation",
        "Variable selection", "Weighted cross-tabs", "Effective bases",
        "Significance testing", "Independent QA", "Excel tab book",
    ]
    x = 38
    y = 215
    row_width = 716
    gap = 8
    widths = [74, 82, 130, 82, 92, 74, 96, 76, 78]
    for index, (step, width) in enumerate(zip(steps, widths)):
        if x + width > 38 + row_width:
            x = 38
            y -= 36
        canvas.setFillColor(PALE if index % 2 == 0 else colors.HexColor("#EAF2F4"))
        canvas.roundRect(x, y, width, 24, 4, fill=1, stroke=0)
        canvas.setFillColor(NAVY)
        canvas.setFont("Helvetica-Bold", 6.8)
        canvas.drawCentredString(x + width / 2, y + 9, step)
        x += width + gap

    canvas.setFillColor(PALE)
    canvas.roundRect(38, 80, 716, 84, 7, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 9.5)
    canvas.drawString(52, 142, "Dataset")
    paragraph(
        canvas,
        "Pew Research Center American Trends Panel Wave 144, fielded March 18-24, 2024. "
        "The analytic file includes 10,287 survey respondents plus 167 demographic/profile "
        "records for active panel members who did not use the internet.",
        52, 132, 420, 50, SMALL,
    )
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 9.5)
    canvas.drawString(500, 142, "Independent analysis")
    paragraph(
        canvas,
        "This case study uses Pew Research Center public-use data. It is an independent "
        "portfolio analysis and not an official Pew Research Center product.",
        500, 132, 235, 50, SMALL,
    )
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 6.4)
    canvas.drawString(38, 37, "Source: https://www.pewresearch.org/dataset/american-trends-panel-wave-144/")


def page_two(canvas):
    header(canvas, 2, "Validated findings", "WEIGHTED MAJOR-REASON PERCENTAGES")

    canvas.setFillColor(MID)
    paragraph(
        canvas,
        "Platform percentages describe different platform-specific or routed universes. "
        "Cross-platform comparisons are descriptive and were not significance-tested.",
        38, 516, 716, 30,
        ParagraphStyle("note", parent=BODY, fontSize=8.5, leading=11, textColor=MID),
    )

    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(38, 472, "Platform profiles")
    bar(canvas, 38, 440, 342, 74.8, "Facebook: friends & family", BLUE)
    bar(canvas, 38, 410, 342, 81.4, "TikTok: entertainment", TEAL)
    bar(canvas, 38, 380, 342, 44.8, "X: entertainment", CORAL)

    canvas.setFillColor(PALE)
    canvas.roundRect(414, 365, 340, 107, 7, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(430, 451, "X: descriptive middle cluster")
    paragraph(
        canvas,
        "Shared interests, sports/pop culture, news, and politics range from "
        "<b>24.3% to 28.3%</b>. Entertainment leads at <b>44.8%</b>.",
        430, 435, 304, 46, BODY,
    )
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 6.8)
    canvas.drawString(430, 379, "Descriptive comparison across motivation items within the X user universe.")

    rule_title(canvas, "Within-platform demographic differences", 38, 330, 716)

    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(38, 294, "Instagram entertainment")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MID)
    canvas.drawString(38, 280, "Major reason by age")
    bar(canvas, 38, 245, 330, 65.3, "Ages 18-29", BLUE)
    bar(canvas, 38, 215, 330, 32.8, "Ages 65+", colors.HexColor("#AABCC6"))
    canvas.setFillColor(TEAL)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(150, 188, "Statistically significant within-platform difference")

    canvas.setStrokeColor(LIGHT)
    canvas.line(396, 184, 396, 305)

    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(424, 294, "Facebook friends & family")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MID)
    canvas.drawString(424, 280, "Major reason by gender")
    bar(canvas, 424, 245, 330, 80.2, "Women", CORAL)
    bar(canvas, 424, 215, 330, 67.6, "Men", colors.HexColor("#AABCC6"))
    canvas.setFillColor(TEAL)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(536, 188, "Statistically significant within-platform difference")

    canvas.setFillColor(PALE)
    canvas.roundRect(38, 69, 716, 82, 7, fill=1, stroke=0)
    paragraph(
        canvas,
        "<b>Interpretation.</b> Weighted percentages reflect each platform's analytical universe and survey weight. "
        "The Instagram and Facebook demographic contrasts above are supported by the persisted significance "
        "results. The platform profile percentages and X motivation cluster remain descriptive.",
        52, 134, 688, 44, ParagraphStyle("interpret", parent=BODY, fontSize=8.6, leading=11.2),
    )
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 6.3)
    canvas.drawString(52, 80, "Sources: final tables T05, T11, T15-T18, T20, T25; qa/significance_test_results.csv.")


def page_three(canvas):
    header(canvas, 3, "Survey tabulation, testing & QA", "METHOD AND VALIDATION")

    preview = ImageReader(str(PREVIEW))
    canvas.drawImage(preview, 38, 449, width=716, height=53, preserveAspectRatio=True, mask="auto")
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica-Oblique", 6.5)
    canvas.drawString(38, 438, "Representative output: T11 - Instagram entertainment, from the final Excel tab book.")

    rule_title(canvas, "Platform universes and weights", 38, 412, 350)
    rows = [
        ("Facebook", "DOV_ASKFB_W144 == 1", "WEIGHT_W144_FB"),
        ("Instagram", "DOV_ASKIG_W144 == 1", "WEIGHT_W144_IG"),
        ("X", "SMUSE_c_W144 == 1", "WEIGHT_W144_XT"),
        ("TikTok", "SMUSE_i_W144 == 1", "WEIGHT_W144_TT"),
    ]
    x0, y0 = 38, 384
    col_x = [x0, x0 + 72, x0 + 222]
    canvas.setFillColor(NAVY)
    canvas.rect(x0, y0, 350, 20, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 7.2)
    for x, label in zip(col_x, ["Platform", "Analytical universe", "Survey weight"]):
        canvas.drawString(x + 5, y0 + 7, label)
    for index, row in enumerate(rows):
        y = y0 - 22 * (index + 1)
        canvas.setFillColor(PALE if index % 2 == 0 else WHITE)
        canvas.rect(x0, y, 350, 22, fill=1, stroke=0)
        canvas.setFillColor(INK)
        canvas.setFont("Helvetica", 7.3)
        for x, value in zip(col_x, row):
            canvas.drawString(x + 5, y + 7.5, value)

    paragraph(
        canvas,
        "Facebook and Instagram use routed module universes. The pipeline reconstructs "
        "module eligibility and validates routing before tabulation. X and TikTok use "
        "their respective platform-user universes.",
        38, 282, 350, 45, SMALL,
    )

    rule_title(canvas, "Estimation and testing", 420, 412, 334)
    methods = [
        "Five banners: Age, Gender, Education, Census Region, Income",
        "Weighted column percentages with unweighted bases",
        "Kish-adjusted effective sample sizes",
        "Approximate two-sided weighted proportion comparisons",
        "Minimum unweighted N = 100 for significance testing",
        "Small base: N = 30-99; very small base: N < 30",
    ]
    y = 382
    for item in methods:
        canvas.setFillColor(TEAL)
        canvas.circle(425, y + 2, 2.2, fill=1, stroke=0)
        paragraph(canvas, item, 435, y + 9, 310, 22, ParagraphStyle("method", parent=BODY, fontSize=7.8, leading=9.5))
        y -= 23
    paragraph(
        canvas,
        "No multiplicity correction is applied. Tests are exploratory and do not replicate "
        "Pew Research Center's complete complex-survey variance methodology.",
        420, 244, 334, 38,
        ParagraphStyle("limitation", parent=SMALL, fontSize=7.1, leading=9.2, textColor=MID),
    )

    rule_title(canvas, "Independent QA", 38, 218, 716)
    qa = [
        ("504 / 504", "percentage-sum validations"),
        ("1,512 / 1,512", "persisted weighted percentages reconciled"),
        ("504", "effective-base cells validated"),
        ("1,596", "pairwise significance tests"),
        ("495", "significant comparisons"),
        ("342", "unique significance-marker cells"),
    ]
    qx = [38, 157, 300, 420, 536, 640]
    widths = [106, 132, 108, 104, 94, 114]
    for (value, label), x, width in zip(qa, qx, widths):
        canvas.setFillColor(NAVY)
        canvas.setFont("Helvetica-Bold", 12.5)
        canvas.drawString(x, 185, value)
        paragraph(canvas, label, x, 174, width, 30, ParagraphStyle("qa", parent=SMALL, fontSize=6.5, leading=8))

    canvas.setFillColor(PALE)
    canvas.roundRect(38, 75, 716, 62, 6, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(52, 119, "Base-size review")
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(TEAL)
    canvas.drawString(52, 94, "476 reviewed")
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(163, 96, "448 OK")
    canvas.drawString(231, 96, "21 small")
    canvas.drawString(298, 96, "7 very small")
    canvas.setFillColor(CORAL)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(414, 96, "0 cells with N < 100 entered significance testing")
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 6.2)
    canvas.drawString(38, 52, "Technical deliverable: output/tab_books/Reach3_Social_Media_TabBook.xlsx")
    canvas.drawRightString(PAGE_W - 38, 52, "Sources: documentation/methodology.md; tabulation/tabulation_plan.csv; qa/* outputs")


RBODY = ParagraphStyle(
    "redesign-body", fontName="Helvetica", fontSize=9.2, leading=11.2,
    textColor=INK,
)
RTABLE = ParagraphStyle(
    "redesign-table", fontName="Helvetica", fontSize=8.0, leading=8.8,
    textColor=INK,
)
RFOOT = ParagraphStyle(
    "redesign-foot", fontName="Helvetica", fontSize=7.2, leading=8.4,
    textColor=MID,
)


def redesign_section_title(canvas, text, x, y, width=None):
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 13.2)
    canvas.drawString(x, y, text)
    if width:
        canvas.setStrokeColor(colors.HexColor("#BDCDD4"))
        canvas.setLineWidth(0.6)
        canvas.line(x, y - 4, x + width, y - 4)


def redesign_footer(canvas, page_no):
    canvas.setStrokeColor(colors.HexColor("#BDCDD4"))
    canvas.setLineWidth(0.6)
    canvas.line(28, 25, PORTRAIT_W - 28, 25)
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 7.2)
    canvas.drawString(28, 13, "Carlos Henrique Nakagomi | Social Media Survey Tabulation Case Study")
    canvas.drawRightString(PORTRAIT_W - 28, 13, f"Page {page_no}")


def redesign_kpi(canvas, x, y, width, value, label):
    canvas.setFillColor(PALE)
    canvas.setStrokeColor(colors.HexColor("#BDCDD4"))
    canvas.setLineWidth(0.7)
    canvas.rect(x, y, width, 53, fill=1, stroke=1)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawCentredString(x + width / 2, y + 29, value)
    paragraph(
        canvas, label, x + 5, y + 20, width - 10, 18,
        ParagraphStyle(
            f"kpi-{label}", parent=RTABLE, fontSize=8.1, leading=8.8,
            alignment=TA_CENTER, textColor=MID,
        ),
    )


def redesign_finding(canvas, x, y, width, platform, value, motivation, accent):
    canvas.setFillColor(PALE)
    canvas.setStrokeColor(colors.HexColor("#BDCDD4"))
    canvas.setLineWidth(0.6)
    canvas.roundRect(x, y, width, 68, 4, fill=1, stroke=1)
    canvas.setFillColor(accent)
    canvas.rect(x, y, 5, 68, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 9.5)
    canvas.drawString(x + 12, y + 49, platform)
    canvas.setFillColor(accent)
    canvas.setFont("Helvetica-Bold", 19)
    canvas.drawString(x + 12, y + 24, value)
    canvas.setFillColor(INK)
    paragraph(
        canvas, motivation, x + 12, y + 16, width - 20, 14,
        ParagraphStyle(f"finding-{platform}", parent=RTABLE, fontName="Helvetica-Bold", fontSize=8.0, leading=8.6),
    )


def redesign_comparison(canvas, x, y, width, title, subtitle, rows, accent):
    canvas.setFillColor(WHITE)
    canvas.setStrokeColor(colors.HexColor("#BDCDD4"))
    canvas.setLineWidth(0.7)
    canvas.rect(x, y, width, 116, fill=1, stroke=1)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 10.5)
    canvas.drawString(x + 12, y + 94, title)
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 8.4)
    canvas.drawString(x + 12, y + 79, subtitle)
    for index, (label, value) in enumerate(rows):
        row_y = y + 54 - index * 25
        canvas.setFillColor(INK)
        canvas.setFont("Helvetica", 8.5)
        canvas.drawString(x + 12, row_y + 2, label)
        bar_x, bar_w = x + 83, width - 128
        canvas.setFillColor(colors.HexColor("#E2EAEE"))
        canvas.roundRect(bar_x, row_y, bar_w, 11, 5.5, fill=1, stroke=0)
        canvas.setFillColor(accent if index == 0 else colors.HexColor("#A9BBC4"))
        canvas.roundRect(bar_x, row_y, bar_w * value / 100, 11, 5.5, fill=1, stroke=0)
        canvas.setFillColor(INK)
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.drawRightString(x + width - 10, row_y + 2, f"{value:.1f}%")
    canvas.setFillColor(TEAL)
    canvas.setFont("Helvetica-Bold", 8.2)
    canvas.drawString(x + 12, y + 10, "Statistically significant within platform")


def redesign_table(canvas, x, y_top, widths, rows, row_height=21, font_size=8.0):
    total_width = sum(widths)
    for row_index, row in enumerate(rows):
        y = y_top - row_height * (row_index + 1)
        is_header = row_index == 0
        canvas.setFillColor(NAVY if is_header else (PALE if row_index % 2 else WHITE))
        canvas.setStrokeColor(colors.HexColor("#BDCDD4"))
        canvas.setLineWidth(0.55)
        canvas.rect(x, y, total_width, row_height, fill=1, stroke=1)
        cell_x = x
        for col_index, (cell, width) in enumerate(zip(row, widths)):
            if col_index:
                canvas.line(cell_x, y, cell_x, y + row_height)
            style = ParagraphStyle(
                f"redesign-table-{row_index}-{col_index}", parent=RTABLE,
                fontName="Helvetica-Bold" if is_header else "Helvetica",
                fontSize=font_size, leading=font_size + 0.8,
                textColor=WHITE if is_header else INK,
            )
            paragraph(canvas, cell, cell_x + 5, y + row_height - 5, width - 10, row_height - 4, style)
            cell_x += width
    return y_top - row_height * len(rows)


def redesigned_page_one(canvas):
    canvas.setFillColor(WHITE)
    canvas.rect(0, 0, PORTRAIT_W, PORTRAIT_H, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 22)
    canvas.drawString(28, 755, "Social Media Platform Usage & User Motivations")
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 9.5)
    canvas.drawString(28, 738, "Survey Tabulation & Data Analytics Portfolio Case Study | Carlos Henrique Nakagomi")

    canvas.setFillColor(NAVY)
    canvas.rect(28, 705, 556, 23, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8.2)
    canvas.drawString(35, 713, "Independent portfolio analysis using Pew Research Center public-use data - not affiliated with or commissioned by Pew Research Center.")

    redesign_section_title(canvas, "Research Objective", 28, 685)
    paragraph(
        canvas,
        "<b>How do social media usage patterns and motivations differ across Facebook, Instagram, X, and TikTok, and across demographic groups?</b>",
        28, 670, 556, 34,
        ParagraphStyle("redesign-question", parent=RBODY, fontSize=10.8, leading=13, textColor=NAVY),
    )
    paragraph(
        canvas,
        "Routed survey microdata became weighted cross-tabs, demographic comparisons, significance tests, QA, and an Excel tab book.",
        28, 637, 556, 27, RBODY,
    )

    gap = 8
    card_width = (556 - gap * 4) / 5
    for index, (value, label) in enumerate((
        ("10,287", "Survey Respondents"), ("4", "Social Platforms"),
        ("28", "Motivation Outcomes"), ("5", "Demographic Banners"),
        ("28", "Final Cross-Tabs"),
    )):
        redesign_kpi(canvas, 28 + index * (card_width + gap), 565, card_width, value, label)

    redesign_section_title(canvas, "Key Findings", 28, 546, 556)
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 8.2)
    canvas.drawRightString(584, 546, "Weighted percentage identifying the motivation as a Major reason")

    finding_gap = 8
    finding_width = (556 - finding_gap * 3) / 4
    for index, finding in enumerate((
        ("Facebook", "74.8%", "Friends & Family", BLUE),
        ("Instagram", "55.9%", "Entertainment", TEAL),
        ("X", "44.8%", "Entertainment", CORAL),
        ("TikTok", "81.4%", "Entertainment", NAVY),
    )):
        redesign_finding(canvas, 28 + index * (finding_width + finding_gap), 464, finding_width, *finding)

    redesign_comparison(
        canvas, 28, 326, 270, "Instagram - Entertainment", "Major reason by age",
        (("Ages 18-29", 65.3), ("Ages 65+", 32.8)), BLUE,
    )
    redesign_comparison(
        canvas, 314, 326, 270, "Facebook - Friends & Family", "Major reason by gender",
        (("Women", 80.2), ("Men", 67.6)), CORAL,
    )

    canvas.setFillColor(PALE)
    canvas.setStrokeColor(colors.HexColor("#BDCDD4"))
    canvas.roundRect(28, 251, 556, 56, 4, fill=1, stroke=1)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(40, 288, "X descriptive motivation cluster")
    paragraph(
        canvas,
        "Shared interests, sports/pop culture, news, and politics range from <b>24.3% to 28.3%</b> among X users. Entertainment leads at <b>44.8%</b>.",
        40, 278, 526, 28, RBODY,
    )

    canvas.setFillColor(colors.HexColor("#E7F0F3"))
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(1)
    canvas.rect(28, 174, 556, 58, fill=1, stroke=1)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 9.5)
    canvas.drawString(40, 214, "Interpretation guardrail")
    paragraph(
        canvas,
        "Platform percentages use different platform-specific or routed analytical universes. <b>Cross-platform comparisons are descriptive; significance testing is conducted within platform.</b>",
        40, 203, 530, 36,
        ParagraphStyle("redesign-guardrail", parent=RBODY, fontSize=9, leading=11),
    )

    paragraph(
        canvas,
        "Dataset: Pew Research Center American Trends Panel Wave 144, fielded March 18-24, 2024. Analytic file: 10,454 records, including 10,287 survey respondents.",
        28, 151, 556, 24, RFOOT,
    )
    paragraph(
        canvas,
        "Sources: final tables T05, T11, T15-T18, T20, T25; qa/significance_test_results.csv; https://www.pewresearch.org/dataset/american-trends-panel-wave-144/",
        28, 123, 556, 24, RFOOT,
    )
    redesign_footer(canvas, 1)


def redesign_workflow(canvas, y):
    redesign_section_title(canvas, "Survey Tabulation Workflow", 28, y)
    stages = (
        "Questionnaire", "Routing & Universe<br/>Validation", "Variable<br/>Selection",
        "Weighting", "Cross-Tabs", "Effective<br/>Bases", "Significance<br/>Testing", "QA", "Excel Tab Book",
    )
    gap = 5
    box_widths = (70, 78, 55, 50, 55, 55, 70, 35, 48)
    x = 28
    for index, (stage, box_width) in enumerate(zip(stages, box_widths)):
        canvas.setFillColor(NAVY if index in (0, 8) else PALE)
        canvas.setStrokeColor(colors.HexColor("#BDCDD4"))
        canvas.roundRect(x, y - 52, box_width, 39, 3, fill=1, stroke=1)
        paragraph(
            canvas, stage, x + 3, y - 25, box_width - 6, 26,
            ParagraphStyle(
                f"workflow-{index}", parent=RTABLE, fontName="Helvetica-Bold",
                fontSize=7.8, leading=8.2, alignment=TA_CENTER,
                textColor=WHITE if index in (0, 8) else NAVY,
            ),
        )
        x += box_width + gap


def redesigned_preview_crop():
    with Image.open(PREVIEW) as source:
        cropped = source.crop((0, 0, int(source.width * 0.43), source.height))
        stream = BytesIO()
        cropped.save(stream, format="PNG")
        stream.seek(0)
        return ImageReader(stream), cropped.width / cropped.height


def redesigned_page_two(canvas):
    canvas.setFillColor(WHITE)
    canvas.rect(0, 0, PORTRAIT_W, PORTRAIT_H, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 22)
    canvas.drawString(28, 755, "Survey Tabulation, QA & Technical Delivery")
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 9.5)
    canvas.drawString(28, 738, "Documented universes, weighted estimation, statistical testing, and independent output validation")
    redesign_workflow(canvas, 714)

    redesign_section_title(canvas, "Platform Universes & Weights", 28, 645)
    universe_rows = [
        ["Platform", "Analytical Universe", "Survey Weight"],
        ["Facebook", "DOV_ASKFB_W144 == 1", "WEIGHT_W144_FB"],
        ["Instagram", "DOV_ASKIG_W144 == 1", "WEIGHT_W144_IG"],
        ["X", "SMUSE_c_W144 == 1", "WEIGHT_W144_XT"],
        ["TikTok", "SMUSE_i_W144 == 1", "WEIGHT_W144_TT"],
    ]
    universe_bottom = redesign_table(canvas, 28, 632, [59, 126, 85], universe_rows, 21, 7.8)
    paragraph(
        canvas,
        "Facebook and Instagram use routed module universes. X and TikTok use their respective platform-user universes.",
        28, universe_bottom - 8, 270, 31, RTABLE,
    )

    redesign_section_title(canvas, "Statistical Testing", 314, 645)
    testing_rows = [
        ["Measure", "Project procedure"],
        ["Banner design", "Age, Gender, Education, Census Region, Income"],
        ["Estimates", "Weighted column percentages; unweighted bases"],
        ["Variance input", "Kish-adjusted effective sample sizes"],
        ["Comparisons", "Approx. two-sided weighted proportions"],
        ["Testing floor", "Minimum unweighted N = 100"],
        ["Base flags", "Small: N = 30-99; Very small: N < 30"],
    ]
    testing_bottom = redesign_table(canvas, 314, 632, [76, 194], testing_rows, 21, 7.8)
    paragraph(
        canvas,
        "<b>Guardrail:</b> No multiplicity correction is applied. Tests are exploratory and do not replicate Pew Research Center's complete complex-survey variance methodology.",
        314, testing_bottom - 8, 270, 38, RTABLE,
    )

    redesign_section_title(canvas, "Quality Assurance", 28, 438, 556)
    metrics = (
        ("504 / 504", "Percentage-sum validations"),
        ("1,512 / 1,512", "Persisted weighted percentages reconciled"),
        ("504", "Effective-base cells validated"),
        ("1,596", "Pairwise significance tests"),
        ("495", "Significant comparisons"),
        ("342", "Unique significance-marker cells"),
    )
    metric_gap = 7
    metric_width = (556 - metric_gap * 5) / 6
    for index, (value, label) in enumerate(metrics):
        x = 28 + index * (metric_width + metric_gap)
        canvas.setFillColor(PALE)
        canvas.setStrokeColor(colors.HexColor("#BDCDD4"))
        canvas.rect(x, 365, metric_width, 60, fill=1, stroke=1)
        canvas.setFillColor(NAVY)
        canvas.setFont("Helvetica-Bold", 12.5)
        canvas.drawCentredString(x + metric_width / 2, 404, value)
        paragraph(
            canvas, label, x + 4, 393, metric_width - 8, 29,
            ParagraphStyle(
                f"qa-{index}", parent=RTABLE, fontSize=7.8, leading=8.5,
                alignment=TA_CENTER, textColor=MID,
            ),
        )

    canvas.setFillColor(colors.HexColor("#E7F0F3"))
    canvas.setStrokeColor(colors.HexColor("#BDCDD4"))
    canvas.rect(28, 328, 556, 29, fill=1, stroke=1)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(38, 339, "Base-size review")
    canvas.setFont("Helvetica", 8.2)
    canvas.drawString(132, 339, "476 reviewed")
    canvas.drawString(209, 339, "448 OK")
    canvas.drawString(265, 339, "21 small")
    canvas.drawString(325, 339, "7 very small")
    canvas.setFillColor(CORAL)
    canvas.setFont("Helvetica-Bold", 8.2)
    canvas.drawString(400, 339, "0 with N < 100 tested")

    redesign_section_title(canvas, "Final Tab Book", 28, 315)
    image, aspect = redesigned_preview_crop()
    preview_width = 556
    preview_height = preview_width / aspect
    canvas.drawImage(image, 28, 201, width=preview_width, height=preview_height, preserveAspectRatio=True, mask="auto")
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica-Oblique", 7.5)
    canvas.drawString(28, 190, "Representative enlarged crop of T11 - Instagram entertainment, showing Total, Age, and Gender banners.")

    redesign_section_title(canvas, "Technical Delivery & Reproducibility", 28, 168)
    delivery_rows = [
        ["Technology", "Role in the project"],
        ["Python / pandas / NumPy", "Validation, tabulation, weighting, significance testing, and QA"],
        ["openpyxl / Excel", "Automated final tab book and workbook round-trip validation"],
        ["Git / GitHub", "Version control and reproducible project delivery"],
        ["Source-controlled evidence", "Methodology, tabulation plan, QA outputs, and report builder"],
    ]
    redesign_table(canvas, 28, 155, [142, 414], delivery_rows, 18, 8.0)

    canvas.setFillColor(colors.HexColor("#E7F0F3"))
    canvas.setStrokeColor(BLUE)
    canvas.rect(28, 30, 556, 29, fill=1, stroke=1)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 8.2)
    canvas.drawString(36, 47, "Final technical deliverable:")
    canvas.setFont("Helvetica", 8.2)
    canvas.drawString(154, 47, "output/tab_books/Reach3_Social_Media_TabBook.xlsx")
    canvas.setFillColor(BLUE)
    canvas.setFont("Helvetica-Bold", 7.8)
    canvas.drawString(36, 35, "Full project repository: https://github.com/CarlosNakagomi/Social-Media-Survey-Tabulation")
    redesign_footer(canvas, 2)


def table_value(table_id, row_label, column):
    path = ROOT / "output" / "tables" / f"{table_id}.csv"
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        row_key = reader.fieldnames[0]
        for row in reader:
            if row[row_key] == row_label:
                return float(row[column])
    raise KeyError(f"{row_label} / {column} not found in {table_id}")


def validate_sources():
    expected = [
        ("T05", "Major reason", "Total", 74.8),
        ("T05", "Major reason", "Gender | A man", 67.6),
        ("T05", "Major reason", "Gender | A woman", 80.2),
        ("T11", "Major reason", "Total", 55.9),
        ("T11", "Major reason", "Age | 18-29", 65.3),
        ("T11", "Major reason", "Age | 65+", 32.8),
        ("T15", "Major reason", "Total", 25.1),
        ("T16", "Major reason", "Total", 24.3),
        ("T17", "Major reason", "Total", 26.8),
        ("T18", "Major reason", "Total", 44.8),
        ("T20", "Major reason", "Total", 28.3),
        ("T25", "Major reason", "Total", 81.4),
    ]
    for table_id, row, column, displayed in expected:
        actual = round(table_value(table_id, row, column), 1)
        if actual != displayed:
            raise ValueError(f"Source mismatch: {table_id} {row} {column}: {actual} != {displayed}")

    with (ROOT / "qa" / "significance_test_results.csv").open(
        newline="", encoding="utf-8-sig"
    ) as stream:
        records = list(csv.DictReader(stream))
    required_tests = [
        ("T05", "Gender", "Major reason", "A man", "A woman"),
        ("T11", "Age", "Major reason", "18-29", "65+"),
    ]
    for table_id, banner, response, category_1, category_2 in required_tests:
        match = next(
            (
                row for row in records
                if row["table_id"] == table_id
                and row["banner"] == banner
                and row["response"] == response
                and row["category_1"] == category_1
                and row["category_2"] == category_2
            ),
            None,
        )
        if match is None or match["significant_95"] != "True":
            raise ValueError(f"Persisted significance result missing or false for {table_id}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    methodology = (ROOT / "documentation" / "methodology.md").read_text(encoding="utf-8")
    for token in ("10,454", "10,287", "195", "28", "1,512", "1,596", "495", "342"):
        if token not in readme:
            raise ValueError(f"README validation token missing: {token}")
    for token in (
        "504 / 504", "1,512 / 1,512", "504 / 504 effective-base",
        "1,596 significance tests", "495 significant comparisons",
        "342 unique", "476 / 476", "448 adequate-base", "21 small-base",
        "7 very-small-base",
    ):
        if token not in methodology:
            raise ValueError(f"Methodology validation token missing: {token}")


def build():
    required = [
        ROOT / "README.md",
        ROOT / "documentation" / "methodology.md",
        ROOT / "tabulation" / "tabulation_plan.csv",
        ROOT / "qa" / "qa_summary.csv",
        ROOT / "qa" / "effective_bases.csv",
        ROOT / "qa" / "significance_test_results.csv",
        ROOT / "qa" / "small_base_qa.csv",
        ROOT / "output" / "tables" / "T05.csv",
        ROOT / "output" / "tables" / "T11.csv",
        ROOT / "output" / "tables" / "T15.csv",
        ROOT / "output" / "tables" / "T16.csv",
        ROOT / "output" / "tables" / "T17.csv",
        ROOT / "output" / "tables" / "T18.csv",
        ROOT / "output" / "tables" / "T20.csv",
        ROOT / "output" / "tables" / "T25.csv",
        PREVIEW,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing report source files: {missing}")

    validate_sources()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(OUTPUT), pagesize=letter, pageCompression=1)
    canvas.setTitle("Social Media Survey Tabulation Case Study")
    canvas.setAuthor("Carlos Henrique Nakagomi")
    canvas.setSubject("Cross-platform survey tabulation portfolio case study")

    for page in (redesigned_page_one, redesigned_page_two):
        page(canvas)
        canvas.showPage()
    canvas.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
