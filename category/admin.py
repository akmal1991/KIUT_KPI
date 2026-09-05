from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Category, StatisticsScientific, CategoryType, AcademicBall, CoefficientCategoryByYear

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple


class CategoryTypeAdminForm(forms.ModelForm):
    class Meta:
        model = CategoryType
        fields = '__all__'
        widgets = {
            'categories': FilteredSelectMultiple('Categories', False),
        }


class TranslatableCategoryTypeAdmin(TranslationAdmin):
    form = CategoryTypeAdminForm


@admin.register(CategoryType)
class CategoryTypeAdmin(TranslatableCategoryTypeAdmin):
    pass


class StatisticsScientificAdminForm(forms.ModelForm):
    class Meta:
        model = CategoryType
        fields = '__all__'
        widgets = {
            'category_types': FilteredSelectMultiple('CategoryType', False),
        }


class TranslatableStatisticsScientificAdmin(TranslationAdmin):
    form = StatisticsScientificAdminForm


@admin.register(StatisticsScientific)
class StatisticsScientificAdmin(TranslatableStatisticsScientificAdmin):
    pass


# admin.site.register(StatisticsScientific, TranslationAdmin)
admin.site.register(AcademicBall)
admin.site.register(CoefficientCategoryByYear)


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('id', 'name', 'coef', 'group')
    list_filter = ('group', 'is_delete')
