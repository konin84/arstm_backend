# apps/forum/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Category

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    # Permet de traduire les espaces officiels (ex: "Job Offers" / "Offres d'emploi")
    fields = ('name', 'description')