from django.urls import path
from apps.areas.views import AreasView

urlpatterns = [
    path('areas/', AreasView.as_view()),
]