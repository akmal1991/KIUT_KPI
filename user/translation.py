from modeltranslation.translator import translator, TranslationOptions
from .models import Division, Teacher, TeacherLevel, AcademicLevel, Target


class DivisionTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Division, DivisionTranslationOptions)


# ///////////////////////////////////////

class TargetTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Target, TargetTranslationOptions)


# ///////////////////////////////////////

class TeacherTranslationOptions(TranslationOptions):
    fields = ('first_name', 'last_name', 'father_name', 'position')


translator.register(Teacher, TeacherTranslationOptions)


# ///////////////////////////////////////

class TeacherLevelTranslationOptions(TranslationOptions):
    fields = ('name',)


class AcademicLevelTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(TeacherLevel, TeacherLevelTranslationOptions)
translator.register(AcademicLevel, AcademicLevelTranslationOptions)
