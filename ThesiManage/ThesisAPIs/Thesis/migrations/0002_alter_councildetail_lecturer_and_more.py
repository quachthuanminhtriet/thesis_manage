# Generated by Django 5.0.4 on 2024-06-17 19:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Thesis', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='councildetail',
            name='lecturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Thesis.lecturer'),
        ),
        migrations.AlterField(
            model_name='councildetail',
            name='role',
            field=models.CharField(choices=[('secretary', 'Thư Ký'), ('debater ', 'Giáo Viên Phản Biện'), ('members', 'Thành Viên Hội Đồng'), ('chairman', 'Chủ Tịch Hội Đồng')], max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('lecturer', 'Giảng Viên'), ('admin', 'Quản Trị Viên'), ('ministry', 'Giáo Vụ'), ('student', 'Sinh Viên')], default='admin', max_length=10),
        ),
    ]
