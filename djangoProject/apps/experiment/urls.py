from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'Category', CategoryView, 'Category')
router.register(r'BasicIngredientBase', BasicIngredientBaseView, 'BasicIngredientBase')
router.register(r'BasicIngredient', BasicIngredientView, 'BasicIngredient')
router.register(r'Recipe', RecipeView, 'Recipe')
router.register(r'Product', ProductView, 'Product')
router.register(r'SupplementBase', SupplementBaseView, 'SupplementBase')
router.register(r'Supplement', SupplementView, 'Supplement')
router.register(r'ExternalFactor', ExternalFactorView, 'ExternalFactor')
router.register(r'Sample', SampleView, 'Sample')
router.register(r'DetailedMetrics', DetailedMetricsView, 'DetailedMetrics')
router.register(r'Metrics', MetricsView, 'Metrics')
router.register(r'Experiment', ExperimentView, 'Experiment')
router.register(r'Result', ResultView, 'Result')

urlpatterns = [
    path('experiment/', include(router.urls)),
    path('experiment/geneerateXlsx/', generate_experiment_excel, name='generate_experiment_excel'),
    path('experiment/readXlsx/', read_experiment_data_from_xlsx, name='read_experiment_data_from_xlsx'),
    path('experiment/generatePDF/', generatePDF, name='generatePDF'),
    path('experiment/generatePlots/', generatePlots, name='generatePlots')
]