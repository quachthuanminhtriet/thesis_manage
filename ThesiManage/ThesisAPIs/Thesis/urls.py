from django.shortcuts import redirect
from django.urls import path, include
from rest_framework import routers
from . import views, admin

r = routers.DefaultRouter()
r.register('users', views.UserViewSet, 'users')
r.register('departments', views.DepartmentViewSet, 'departments')
r.register('majors', views.MajorViewSet, 'majors')
r.register('ministries', views.MinistryViewSet, 'ministries')
r.register('students', views.StudentViewSet, 'students')
r.register('thesis', views.ThesisViewSet, 'thesis')
r.register('lecturer', views.LecturerViewSet, 'lecturer')
r.register('council', views.CouncilViewSet, 'council')
r.register('criteria', views.CriteriaViewSet, 'criteria')
r.register('score', views.ScoreViewSet, 'score')
r.register('councildetail', views.CouncilDetailViewSet, 'councildetail')


urlpatterns = [
    path('', include(r.urls))
]