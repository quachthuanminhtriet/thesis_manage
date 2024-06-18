from ckeditor import configs
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage, send_mail
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from . import serializers, paginators, perms
from .export_pdf import export_pdf
from .models import User, Department, Major, Ministry, Student, Lecturer, Thesis, Council, Criteria, Score, \
    CouncilDetail
from .configs import MAX_LECTURER
from django.conf import settings

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, ]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            user_id = self.request.query_params.get('user_id')
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        return queryset

    def get_permissions(self):
        if self.action in ['get_current_user', 'change_pass']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        user = request.user

        if request.method.__eq__("patch"):
            for k, v in request.data.items():
                setattr(user, k, v)
                user.save()

        return Response(serializers.UserSerializer(user).data)

    @action(methods=['get', 'put'], url_path='change-pass', detail=False)
    def change_pass(self, request, *args, **kwargs):
        user = request.user
        serializer = serializers.ChangePasswordSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            if user.check_password(serializer.validated_data['current_password']):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({'message': 'Mật khẩu đã được thay đổi thành công.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Mật khẩu hiện tại không đúng.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepartmentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Department.objects.filter(active=True)
    serializer_class = serializers.DepartmentSerializer
    parser_classes = [parsers.MultiPartParser, ]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            depart_code = self.request.query_params.get('department_code')
            if depart_code:
                queryset = queryset.filter(department_code=depart_code)

        return queryset


class MajorViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Major.objects.filter(active=True)
    serializer_class = serializers.MajorSerializer
    parser_classes = [parsers.MultiPartParser, ]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            depart_code = self.request.query_params.get('department_code')
            if depart_code:
                queryset = queryset.filter(department_code=depart_code)

        return queryset


class MinistryViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Ministry.objects.filter(active=True)
    serializer_class = serializers.MinistrySerializer
    parser_classes = [parsers.MultiPartParser, ]
    # permission_classes = [perms.IsMinistryAuthenticated, perms.IsAdmin]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            ministry_code = self.request.query_params.get('ministry_code')
            if ministry_code:
                queryset = queryset.filter(ministry_code=ministry_code)

        return queryset


class StudentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Student.objects.filter(active=True)
    serializer_class = serializers.StudentSerializer
    parser_classes = [parsers.MultiPartParser, ]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            student_code = self.request.query_params.get('student_code')
            if student_code:
                queryset = queryset.filter(student_code=student_code)

        return queryset


class LecturerViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Lecturer.objects.filter(active=True)
    serializer_class = serializers.LecturerSerializer
    parser_classes = [parsers.MultiPartParser, ]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            lecturer_code = self.request.query_params.get('lecturer_code')
            if lecturer_code:
                queryset = queryset.filter(lecturer_code=lecturer_code)

        return queryset


class ThesisViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Thesis.objects.filter(active=True)
    serializer_class = serializers.ThesisSerializer
    parser_classes = [parsers.MultiPartParser, ]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        lecturer_code = self.request.query_params.get('lecturer_code')
        if lecturer_code:
            queryset = queryset.filter(lecturer_code=lecturer_code)

        return queryset

    @action(methods=["get"], url_path="total_score", detail=False)
    def get_total_score(self, request):
        year = request.GET.get('year', None)
        years = Thesis.objects.values_list("create_date__year", flat=True).distinct()

        average_scores = (Thesis.objects
                          .filter(total_score__isnull=False)
                          .values("id", "title", "total_score", "create_date"))

        if year:
            average_scores = average_scores.filter(create_date__year=year)
            context = {
                "average_scores": average_scores,
                "years": years,
                "request_year": int(year),
            }
        else:
            context = {
                "average_scores": average_scores,
                "years": years,
                "request_year": None,
            }

            return Response(context)


class CouncilViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Council.objects.filter(active=True)
    serializer_class = serializers.CouncilSerializer
    parser_classes = [parsers.MultiPartParser, ]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            council_code = self.request.query_params.get('council_code')
            if council_code:
                queryset = queryset.filter(council_code=council_code)

        return queryset

    # cập nhật trạng thái đóng mở của hội đồng
    @action(methods=['put'], url_path='update_blocked', detail=True)
    def update_blocked(self, request, pk=None):
        council = self.get_object()

        if council.is_blocked:
            council.is_blocked = False
        else:
            council.is_blocked = True

        council.save()

        if not all(thesis.total_score > 0 for thesis in council.thesis_set.all()):
            return Response({"detail": "Không thể cập nhật is_blocked khi có khóa luận chưa được cập nhật."},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'is_blocked': council.is_blocked}, status=status.HTTP_200_OK)


class CouncilDetailViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = CouncilDetail.objects.filter(active=True)
    serializer_class = serializers.CouncilDetailSerializer
    parser_classes = [parsers.MultiPartParser, ]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            council_code = self.request.query_params.get('council_code')
            if council_code:
                queryset = queryset.filter(council_code=council_code)

        return queryset


class CriteriaViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Criteria.objects.filter(active=True)
    serializer_class = serializers.CriteriaSerializer
    parser_classes = [parsers.MultiPartParser, ]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            criteria_id = self.request.query_params.get('criteria_id')
            if criteria_id:
                queryset = queryset.filter(criteria_id=criteria_id)

        return queryset


class ScoreViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Score.objects.filter(active=True)
    serializer_class = serializers.ScoreSerializer
    parser_classes = [parsers.MultiPartParser, ]
    pagination_class = paginators.ThesisPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            criteria_id = self.request.query_params.get('criteria_id')
            if criteria_id:
                queryset = queryset.filter(criteria_id=criteria_id)

        return queryset

    @action(methods=['put'], url_path='update_score', detail=True)
    def update_score(self, request, *args, **kwargs):
        instance = self.get_object()
        council_detail = instance.council_detail

        # Lấy dữ liệu từ request
        thesis = request.data.get('thesis')
        criteria = request.data.get('criteria')

        # Kiểm tra xem instance đã tồn tại chưa
        existing_instance = Score.objects.filter(thesis=thesis, criteria=criteria,
                                                 council_detail=council_detail).first()
        if existing_instance and existing_instance.pk != instance.pk:
            raise ValidationError(
                {"non_field_errors": ["Các trường thesis, criteria và council detail đều phải là duy nhất."]})

        if council_detail.council.is_blocked:
            raise ValidationError({"is_blocked": "Hội đồng đã bị khóa lại không được phép chỉnh sửa điểm."})
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=["get"], detail=True, url_path="export_pdf")
    def export_pdf(self, request, **kwargs):
        queryset = Score.objects.filter(thesis=kwargs.get("pk"))
        thesis_name = Thesis.objects.filter(id=kwargs.get("pk")).first().title

        data = self.get_serializer(queryset, many=True).data
        export_pdf(data, thesis_name, "triet123az@gmail.com")

        return Response(
            f"Export successfully to {request.user.email if request.user.is_authenticated else request.user}!",
            status.HTTP_200_OK)
