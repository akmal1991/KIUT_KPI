from modeltranslation.translator import translator, TranslationOptions
from .models import Category, StatisticsScientific, CategoryType


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', )

class StatisticsScientificTranslationOptions(TranslationOptions):
    fields = ('name', )


translator.register(Category, CategoryTranslationOptions)
translator.register(StatisticsScientific, StatisticsScientificTranslationOptions)
translator.register(CategoryType, StatisticsScientificTranslationOptions)
