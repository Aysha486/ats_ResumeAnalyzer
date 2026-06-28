from django.db import models

class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    ats_score = models.IntegerField(default=0)

    job_description = models.TextField(blank=True, null=True)
    match_score = models.IntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name