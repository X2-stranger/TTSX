# Generated by Django 2.2.5 on 2019-10-08 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LoginUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=32)),
                ('username', models.CharField(blank=True, max_length=32, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=11, null=True)),
                ('photo', models.ImageField(default='images/default_photo.jpg', upload_to='images')),
                ('age', models.IntegerField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=32, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('user_type', models.IntegerField(default=0)),
            ],
        ),
    ]
