from collections import defaultdict
import datetime

from _cffi_backend import buffer
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework import viewsets
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
import io

from . import utils
from .models import Criteria, CouncilDetail, Thesis, Council


def export_pdf(data, thesis_name, email="", table_data=None):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    filename = f"Báo cáo khóa luận {thesis_name}.pdf"

    # Đăng Ký Font Ký Tự
    pdfmetrics.registerFont(TTFont('Baloo-Regular', 'thesis/static/fonts/Baloo-Regular.ttf'))

    # Sắp xếp dữ liệu theo tiêu chí và giảng viên
    data_by_criteria = defaultdict(list)

    # Tính điểm
    total_score = 0.0
    lecturer_count = 0

    for record in data:
        criteria_id = record['criteria']
        criteria_data = Criteria.objects.get(id=criteria_id)
        key = criteria_data.title
        council_detail_id = record['council_detail']
        council_detail_data = CouncilDetail.objects.get(id=council_detail_id)
        lecturer = council_detail_data.lecturer.name

        score = record['score']

        if lecturer:
            lecturer_count += 1

        total_score += score

        data_by_criteria[key].append((score, lecturer))

    total_score /= lecturer_count

    # Chuẩn bị dữ liệu cho bảng
    table_data = []
    header = ['Tiêu Chí', 'Điểm', 'Giảng Viên']
    table_data.append(header)

    for criterion, values in data_by_criteria.items():
        if len(values) > 1:
            for i, (score, lecturer) in enumerate(values):
                if i == 0:
                    table_data.append([criterion, score, lecturer])
                else:
                    table_data.append(['', score, lecturer])
        else:
            score, lecturer = values[0]
            table_data.append([criterion, score, lecturer])
    table_data.append(["Điểm trung bình", round(total_score, 2), ""])

    # tạo pdf
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72,
                            bottomMargin=18)
    styles = getSampleStyleSheet()
    elements = []

    #Chỉnh Font
    title_style = styles['Title'].clone('CustomTitle')
    title_style.fontName = 'Baloo-Regular'
    title_style.fontSize = 18
    title_style.leading = 22
    title_style.alignment = TA_CENTER

    heading2_style = styles['Heading2'].clone('CustomHeading2')
    heading2_style.fontName = 'Baloo-Regular'
    heading2_style.fontSize = 14
    heading2_style.leading = 18
    heading2_style.alignment = TA_CENTER


    # Tiêu đề trang
    title = Paragraph("Báo cáo khóa luận tốt nghiệp", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    table_title = Paragraph("Bảng Điểm Trung Bình", heading2_style)
    elements.append(table_title)
    elements.append(Spacer(1, 12))

    # Chỉnh Font và Kiểu Của Bảng
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Baloo-Regular'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 2, colors.black),
    ])

    tbl = Table(table_data, colWidths=[200, 50, 200])
    tbl.setStyle(style)
    elements.append(tbl)

    # Chữ Ký Lãnh Đạo
    elements.append(Spacer(1, 48))
    signatures = Paragraph("Chữ Ký Lãnh Đạo", heading2_style)
    elements.append(signatures)
    elements.append(Spacer(1, 24))
    current_date = datetime.datetime.now().strftime("%d/%m/%Y")
    elements.append(Paragraph(f"Date: {current_date}", heading2_style))

    # Build the document
    doc.build(elements)

    with open(f'Thesis/static/pdf/{filename}', 'wb') as f:
        f.write(buffer.getvalue())