# apps/library/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import ResearchPaper, SectorWatch, Category

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    # Le nom de la catégorie aura automatiquement ses colonnes name_fr et name_en en base de données
    fields = ('name',)


@register(ResearchPaper)
class ResearchPaperTranslationOptions(TranslationOptions):
    fields = ('title', 'abstract')


@register(SectorWatch)
class SectorWatchTranslationOptions(TranslationOptions):
    # Plus besoin de traduire 'category' ici, car elle est gérée par son propre modèle ci-dessus
    fields = ('title', 'content')