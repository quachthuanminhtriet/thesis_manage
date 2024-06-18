from datetime import datetime
from datetime import timedelta

from cloudinary.templatetags import cloudinary
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from rest_framework.response import Response

from . import utils
from .models import User, Department, Major, Ministry, Student, Lecturer, Thesis, Council, Criteria, Score, \
    CouncilDetail


class ThesisAdminSite(admin.AdminSite):
    site_header = 'Hệ thống quản lý khóa luận tốt nghiệp'

    def get_urls(self):
        return [
            path('thesis-stats/', self.stats_view_year),
            path('thesis-stats-major/', self.stats_view_year_major)
        ] + super().get_urls()

    # lấy điêm theo năm
    def stats_view_year(self, request):
        year = request.GET.get('year')
        if year:
            year = int(year)
        else:
            year = datetime.now().year
        return TemplateResponse(request, ('admin/stats.html'), {
            "stats": utils.get_score_by_year(year=year),
        })

    def stats_view_year_major(self, request):
        year = request.GET.get('year')
        if year:
            year = int(year)
        else:
            year = datetime.now().year
        return TemplateResponse(request, ('admin/stats_major.html'), {
            "stats_major": utils.get_thesis_counts_by_major(year=year)
        })


admin_site = ThesisAdminSite(name='MyThesisAdmin')

admin_site.register(User)
admin_site.register(Department)
admin_site.register(Major)
admin_site.register(Ministry)
admin_site.register(Student)
admin_site.register(Lecturer)
admin_site.register(Thesis)
admin_site.register(Council)
admin_site.register(Criteria)
admin_site.register(CouncilDetail)
admin_site.register(Score)
