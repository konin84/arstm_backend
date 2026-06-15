# apps/events/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Event, PromotionBanner, NewsPost

@register(Event)
class EventTranslationOptions(TranslationOptions):
    # Les champs qui auront automatiquement des versions _fr et _en générées en base de données
    fields = ('title', 'description')


@register(PromotionBanner)
class PromotionBannerTranslationOptions(TranslationOptions):
    fields = ('image',)


@register(NewsPost)
class NewsPostTranslationOptions(TranslationOptions):
    fields = ('title', 'content')