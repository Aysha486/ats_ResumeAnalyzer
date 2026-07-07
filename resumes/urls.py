from django.urls import path
from .views import (
    ResumeUploadView,
    upload_page,
    my_resumes,
    resume_detail,
    delete_resume,
    dashboard,
    download_report,
    
)
urlpatterns = [
    # path('', upload_page, name='upload_page'),

    path(
        'upload/',
        ResumeUploadView.as_view(),
        name='resume-upload'
    ),
    path(
    "my-resumes/",
    my_resumes,
    name="my-resumes"
    ),
    path(
        "resume/<int:pk>/",
        resume_detail,
        name="resume-detail"
    ),
    path(
        "delete/<int:resume_id>/",
        delete_resume,
        name="delete-resume",
    ),
    path(
    "dashboard/",
    dashboard,
    name="dashboard",
    ),
    path(
    "download/<int:pk>/",
    download_report,
    name="download-report",
    ),
]
