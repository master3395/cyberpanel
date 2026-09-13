from django.urls import path
from . import views

urlpatterns = [
    # Bare /filemanager/ must resolve (was Django 404 / LiteSpeed Not Found)
    path('', views.FileManagerRoot, name='filemanagerIndex'),
    path('upload', views.upload, name='upload'),
    path('changePermissions', views.changePermissions, name='changePermissions'),
    path('controller', views.controller, name='controller'),
    path('downloadFile', views.downloadFile, name='downloadFile'),
    path('RootDownloadFile', views.RootDownloadFile, name='RootDownloadFile'),
    path('editFile', views.editFile, name='editFile'),
    path('Filemanager', views.FileManagerRoot, name='Filemanager'),
    path('<domain>', views.loadFileManagerHome, name='loadFileManagerHome'),
]
