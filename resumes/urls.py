from django.urls import path
from .views import ResumeUploadView, upload_page

urlpatterns = [
    # path('', upload_page, name='upload_page'),

    path(
        'upload/',
        ResumeUploadView.as_view(),
        name='resume-upload'
    ),
]

