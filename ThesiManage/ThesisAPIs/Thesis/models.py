from enum import Enum

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class BaseModel(models.Model):
    create_date = models.DateField(auto_now_add=True, null=True)
    update_date = models.DateField(auto_now=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


# user model
class User(AbstractUser):
    avatar = CloudinaryField(null=False)

    ROLE_CHOICES = {
        ('admin', 'Quản Trị Viên'),
        ('ministry', 'Giáo Vụ'),
        ('lecturer', 'Giảng Viên'),
        ('student', 'Sinh Viên'),
    }

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')

    class Meta:
        verbose_name_plural = 'Tài Khoản Người Dùng'

    def __str__(self):
        return self.username


# Khoa
class Department(BaseModel):
    code = models.CharField(max_length=10, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)

    class Meta:
        verbose_name_plural = 'Khoa'

    def __str__(self):
        return self.name


# Chuyên Ngành
class Major(BaseModel):
    code = models.CharField(max_length=10, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    department = models.ForeignKey(Department, on_delete=models.RESTRICT, null=True)

    class Meta:
        verbose_name_plural = 'Chuyên Ngành'

    def __str__(self):
        return self.name


# Giáo Vụ
class Ministry(BaseModel):
    code = models.CharField(max_length=10, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    user = models.OneToOneField(User, on_delete=models.RESTRICT, null=False, limit_choices_to={'role': 'ministry'})

    class Meta:
        verbose_name_plural = 'Giáo Vụ'

    def __str__(self):
        return self.name


# Sinh Viên
class Student(BaseModel):
    code = models.CharField(max_length=10, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    major = models.ForeignKey(Major, on_delete=models.RESTRICT, null=False)
    user = models.OneToOneField(User, on_delete=models.RESTRICT, null=False, limit_choices_to={'role': 'student'})
    start_study = models.DateField(null=False)
    end_study = models.DateField(null=False)

    class Meta:
        verbose_name_plural = 'Sinh Viên'

    def __str__(self):
        return self.name


class Lecturer(BaseModel):
    code = models.CharField(max_length=10, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    user = models.OneToOneField(User, on_delete=models.RESTRICT, null=False, limit_choices_to={'role': 'lecturer'})
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name_plural = 'Giảng viên'

    def __str__(self):
        return self.name


class Council(BaseModel):
    code = models.CharField(max_length=10, null=False, unique=True)
    name = models.CharField(max_length=255, null=False)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Hội Đồng'

    def __str__(self):
        return self.code

    def all_theses_scored(self):
        return all(thesis.total_score > 0 for thesis in self.thesis_set.all())


class Thesis(BaseModel):
    title = models.CharField(max_length=255, null=False)
    report_file = RichTextField(null=False, blank=True)
    total_score = models.FloatField(default=0.0, validators=[MaxValueValidator(limit_value=10.0),
                                                             MinValueValidator(limit_value=0.0)])
    council = models.ForeignKey(Council, on_delete=models.PROTECT, null=False, blank=True)
    advisors = models.ManyToManyField(Lecturer)
    students = models.ManyToManyField(Student)

    class Meta:
        verbose_name_plural = 'Khóa Luận'

    def __str__(self):
        return self.title


class CouncilDetail(BaseModel):
    ROLE_CHOICES = {
        ('chairman', 'Chủ Tịch Hội Đồng'),
        ('secretary', 'Thư Ký'),
        ('debater ', 'Giáo Viên Phản Biện'),
        ('members', 'Thành Viên Hội Đồng'),
    }

    role = models.CharField(max_length=255, choices=ROLE_CHOICES)

    lecturer = models.ForeignKey(Lecturer, on_delete=models.RESTRICT)
    council = models.ForeignKey(Council, on_delete=models.RESTRICT)

    class Meta:
        verbose_name_plural = 'Mô tả hội đồng'

    def __str__(self):
        return  f"{self.council.name} - {self.get_role_display()}"


class Criteria(BaseModel):
    title = models.CharField(max_length=255, unique=True, null=False)
    description = RichTextField(null=False)

    class Meta:
        verbose_name_plural = 'Tiêu chí đánh giá'

    def __str__(self):
        return f"{self.title}"


class Score(BaseModel):
    score = models.FloatField(default=0.0, validators=[MaxValueValidator(limit_value=2.0),
                                                       MinValueValidator(limit_value=0.0)])
    thesis = models.ForeignKey(Thesis, on_delete=models.RESTRICT)
    criteria = models.ForeignKey(Criteria, on_delete=models.RESTRICT)
    council_detail = models.ForeignKey(CouncilDetail, on_delete=models.RESTRICT)

    class Meta:
        unique_together = ('thesis', 'criteria', 'council_detail')
        verbose_name_plural = 'Điểm số'

    def __str__(self):
        return f"{self.thesis.title} - {self.criteria.title} - {self.council_detail.get_role_display()}"
