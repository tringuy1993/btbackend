from django.urls import path
# from .views import my_view, hello
from . import views
urlpatterns = [
    path('', views.hello.as_view(), name="my_view"),
    path('backtest_db/', views.my_view.as_view(), name="db"),
    path('0DTE/', views.zdte_dates.as_view(), name="zdtes"),
    path('partitionedTables/', views.get_table_partitions.as_view(), name="part_table"),
    path('option-chain/', views.option_chain.as_view(), name="option_chain")
]
