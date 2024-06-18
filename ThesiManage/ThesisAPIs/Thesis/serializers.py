from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from rest_framework import serializers

from . import models
from .models import User, Department, Major, Ministry, Student, Lecturer, Thesis, Council, Criteria, Score, \
    CouncilDetail
from django.conf import settings


# user
class UserSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['avatar'] = instance.avatar.url
        # rep['username'] = instance.user.username

        return rep

    def create(self, validated_data):
        data = validated_data.copy()

        user = User(**data)
        user.set_password(data["password"])
        user.save()
        return user

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar', 'role']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context['user']
        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError({'current_password': 'Mật khẩu hiện tại không đúng.'})
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['code', 'name']


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ['code', 'name']


class MinistrySerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        data = validated_data.copy()
        minis = Ministry(**data)
        minis.save()
        return minis

    class Meta:
        model = Ministry
        fields = ['code', 'name', 'user']


class StudentSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['major'] = instance.major.name if instance.major else None
        return rep

    def create(self, validated_data):
        data = validated_data.copy()

        stud = Student(**data)
        if stud.end_study.year - stud.start_study.year < 4:
            raise serializers.ValidationError({"minimum_4_year": "Tối thiểu 4 năm đại học."})

        stud.save()
        return stud

    class Meta:
        model = Student
        fields = '__all__'


class LecturerSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['department'] = instance.department.name if instance.department else None
        return rep

    def create(self, validated_data):
        data = validated_data.copy()

        lect = Lecturer(**data)
        lect.save()
        return lect

    class Meta:
        model = Lecturer
        fields = ['id', 'code', 'name', 'department', 'user']


class ThesisSerializer(serializers.ModelSerializer):
    def validate_council(self, council):
        thesis_count = Thesis.objects.filter(council=council).count()
        if thesis_count >= 5:
            raise serializers.ValidationError({"max_council": "Mỗi hội đồng không được chứa quá 5 khóa luận."})
        return council

    def create(self, validated_data):
        data = validated_data.copy()

        advisors = data.pop('advisors', [])
        students = data.pop('students', [])

        if len(advisors) > 2:
            raise serializers.ValidationError({"max_adviors": "Tối đa 2 giảng viên."})
        if len(students) > 2:
            raise serializers.ValidationError({"max_students": "Tối đa 2 sinh viên."})

        thesis = Thesis.objects.create(**data)

        # Không chỉ lấy id mà còn lấy code, name
        for advisor in advisors:
            thesis.advisors.add(advisor)
        for student in students:
            thesis.students.add(student)

        return thesis

    class Meta:
        model = Thesis
        fields = "__all__"


class CouncilSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        data = validated_data.copy()

        cuon = Council(**data)
        cuon.save()
        return cuon

    class Meta:
        model = Council
        fields = "__all__"


class CriteriaSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        data = validated_data.copy()
        crit = Criteria.objects.create(**data)
        return crit

    class Meta:
        model = Criteria
        fields = "__all__"


class CouncilDetailSerializer(serializers.ModelSerializer):
    def validate(self, data):
        role = data['role']
        council = data['council']

        # Kiểm tra tổng số giảng viên trong hội đồng
        total_lecturers = CouncilDetail.objects.filter(council=council).count()
        if total_lecturers >= 5:
            raise serializers.ValidationError("Một hội đồng chỉ được phép có tối đa 5 giảng viên.")

        if role == 'members':
            members_count = CouncilDetail.objects.filter(council=council, role='members').count()
            if members_count >= 2:
                raise serializers.ValidationError(f"Không thể chọn vai trò {role} quá 2 lần cho cùng một hội đồng.")
        else:
            if CouncilDetail.objects.filter(council=council, role=role).exists():
                raise serializers.ValidationError(f"Vai trò '{role}' đã được chọn cho hội đồng này.")

        return data

    def create(self, validated_data):
        data = validated_data.copy()

        council_detail = CouncilDetail.objects.create(**data)

        self.send_mail(council_detail)

        return council_detail

    def send_mail(self, council_detail):
        subject = 'Thông báo về việc bổ nhiệm mới vào Hội đồng'
        message = f"""Bạn đã được bổ nhiệm vào vị trí "{council_detail.get_role_display()}" kể từ ngày "{council_detail.create_date}"
            
            Trân Trọng,
        """

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [council_detail.lecturer.user.email],
            fail_silently=False,
        )

    class Meta:
        model = CouncilDetail
        fields = "__all__"


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = "__all__"

    def create(self, validated_data):
        data = validated_data.copy()

        thesis = data.get('thesis')
        council_detail = data.get('council_detail')

        if thesis and council_detail:
            existing_scores = Score.objects.filter(thesis=thesis).exclude(council_detail=council_detail)
            if existing_scores.exists():
                raise serializers.ValidationError("Khóa luận này đã được chấm bởi hội đồng khác")

        score = Score.objects.create(**validated_data)
        return score