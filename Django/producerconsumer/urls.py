from django.urls import path
from .import views

# KM - Added urlpatterns
urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.startSimulation, name='startSimulation'),
    path('adjust_sleep/', views.adjustSleepTime, name='adjustSleepTime'),
    path('terminate/', views.terminateSimulation, name='terminateSimulation'),
    path('status/', views.getBufferStatus, name='getBufferStatus'),
    path('getTaskOutput/', views.getTaskOutput, name='getTaskOutput'),
    path('adjustBufferSize/', views.adjustBufferSize, name='adjustBufferSize')
]