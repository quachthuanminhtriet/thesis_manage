from django.db.models import Count, Avg, ExpressionWrapper, F, fields, Sum
from datetime import datetime

# Lấy năm hiện tại
from .models import *

# Tính điểm tông theo năm

def get_score_by_year(year):
    query = Thesis.objects.values('id', 'title', 'total_score')

    if year:
        query = Thesis.objects.values('id', 'title', 'total_score').filter(create_date__year=year)

    return query


def get_thesis_counts_by_major(year):
    query = Thesis.objects.prefetch_related('students__major') \
        .values('students__major__name', 'students__major__code')\
        .annotate(count=Count('id')) \
        .annotate(total_count=Count('id', distinct=True)) \
        .values('students__major__name', 'count', 'total_count', 'students__major__code')

    data = list(query)
    total_theses = sum(item['count'] for item in data)

    for item in data:
        item['percentage'] = round((item['count'] / total_theses) * 100, 2)

    return data

