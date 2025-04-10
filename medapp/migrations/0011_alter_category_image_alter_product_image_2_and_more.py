# Generated by Django 5.2 on 2025-04-08 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medapp', '0010_product_delete_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='navbar_categories/categories/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_2',
            field=models.ImageField(blank=True, null=True, upload_to='navbar_categories/categories/subcategories/prdoucts/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_3',
            field=models.ImageField(blank=True, null=True, upload_to='navbar_categories/categories/subcategories/prdoucts/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_4',
            field=models.ImageField(blank=True, null=True, upload_to='navbar_categories/categories/subcategories/prdoucts/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_5',
            field=models.ImageField(blank=True, null=True, upload_to='navbar_categories/categories/subcategories/prdoucts/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='main_image',
            field=models.ImageField(blank=True, null=True, upload_to='navbar_categories/categories/subcategories/prdoucts/'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='navbar_categories/categories/subcategories/'),
        ),
    ]
