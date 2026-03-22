from django.urls import path
from . import views

urlpatterns = [
    path('math/factorial/', views.factorial),
    path('math/combination/', views.combination),
    path('math/permutations/', views.permutations),
    path('math/combination-product/', views.combination_product),
    path('backtest/run/', views.run_backtest),
]
