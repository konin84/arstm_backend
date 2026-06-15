from modeltranslation.translator import register, TranslationOptions
from .models import School, Infrastructure


@register(School)
class SchoolTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Infrastructure)
class InfrastructureTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
