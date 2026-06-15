from modeltranslation.translator import register, TranslationOptions
from .models import Domain, Program


@register(Domain)
class DomainTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Program)
class ProgramTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'career_opportunities')
