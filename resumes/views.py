from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Resume
from .serializers import ResumeSerializer
from .utils import extract_text_from_pdf, extract_skills, calculate_match_score

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

class ResumeUploadView(APIView):

    def post(self, request):
        print('POST RECEIVED')
        serializer = ResumeSerializer(data=request.data)

        if serializer.is_valid():

            resume = serializer.save(user=request.user)

            extracted_text = extract_text_from_pdf(
                resume.file.path
            )

            text = extracted_text.lower()

            sections = {
                "Education": any(word in text for word in [
                    "education", "bachelor", "b.tech", "btech",
                    "degree", "university", "college","be","bachelor of engineering","BE"
                ]),

                "Skills": any(word in text for word in [
                    "skills", "technical skills", "technologies",
                    "programming languages,html,css,javascript,github"
                ]),

                "Projects": any(word in text for word in [
                    "project", "projects"
                ]),

                "Experience": any(word in text for word in [
                    "experience", "internship", "work experience"
                ]),

                "Certifications": any(word in text for word in [
                    "certification", "certifications",
                    "certificate", "certificates"
                ]),
            }

            skills = extract_skills(extracted_text)
            print(extracted_text[:1000])
            
            jd_text = request.data.get("job_description", "")

            jd_skills = extract_skills(jd_text)

            matched_skills = []

            for skill in skills:
                if skill in jd_skills:
                    matched_skills.append(skill)

            missing_skills = []

            for skill in jd_skills:
                if skill not in skills:
                    missing_skills.append(skill)

            match_score = calculate_match_score(
                skills,
                jd_skills
            )
          
            ats_score = 0

            ats_score += min(len(skills) * 5, 40)

            if "bachelor" in extracted_text.lower():
                        ats_score += 15
                    
            if "project" in extracted_text.lower():
                        ats_score += 20
                    
            if "experience" in extracted_text.lower():
                    ats_score += 15

            if "certification" in extracted_text.lower():
                ats_score += 10

              # ATS Score Color
            if ats_score >= 80:
                ats_color = "success"
            elif ats_score >= 50:
                ats_color = "warning"
            else:
                ats_color = "danger"

            # Match Score Color
            if match_score >= 80:
                match_color = "success"
            elif match_score >= 50:
                match_color = "warning"
            else:
                match_color = "danger"

            resume.extracted_text = extracted_text
            resume.skills = ", ".join(skills)
            resume.ats_score = ats_score
            resume.job_description = jd_text
            resume.match_score = match_score

            resume.save()

            matched_skills = list(set(skills) & set(jd_skills))
            missing_skills = list(set(jd_skills) - set(skills))
            
            print(sections)
            
            return render(
                request,
                "results.html",
                {
                    "ats_score": ats_score,
                    "match_score": match_score,
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills,

                    "ats_color": ats_color,
                    "match_color": match_color,
                    

                    "education": sections["Education"],
                    "skills_section": sections["Skills"],
                    "projects": sections["Projects"],
                    "experience": sections["Experience"],
                    "certifications": sections["Certifications"],

                    "resume": resume,
                }
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
from django.shortcuts import render

@login_required
def upload_page(request):
    print("REQUEST METHOD:", request.method)

    if request.method == "POST":
        print("FORM SUBMITTED")

    return render(request, "upload.html")

@login_required
def my_resumes(request):

    resumes = Resume.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")

    return render(
        request,
        "my_resumes.html",
        {
            "resumes": resumes
        }
    )
@login_required
def resume_detail(request, pk):
    resume = get_object_or_404(
        Resume,
        pk=pk,
        user=request.user
    )

    return render(
        request,
        "resume_detail.html",
        {
            "resume": resume
        }
    )

@login_required
def delete_resume(request, resume_id):

    resume = get_object_or_404(
        Resume,
        id=resume_id,
        user=request.user
    )

    resume.file.delete()

    resume.delete()

    return redirect("my-resumes")


@login_required
def dashboard(request):

    resumes = Resume.objects.filter(user=request.user)

    total = resumes.count()

    if total:
        avg_ats = round(sum(r.ats_score for r in resumes) / total)
        highest = max(r.ats_score for r in resumes)
    else:
        avg_ats = 0
        highest = 0

    context = {
        "total_resumes": total,
        "average_ats": avg_ats,
        "highest_ats": highest,
        "resumes": resumes.order_by("-uploaded_at")[:5],
    }

    return render(request, "dashboard.html", context)

@login_required
def download_report(request, pk):

    resume = get_object_or_404(
        Resume,
        pk=pk,
        user=request.user
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Resume_Report.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>Resume Analyzer Report</b>", styles["Title"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(f"<b>Resume:</b> {resume.file.name}", styles["BodyText"]))
    story.append(Paragraph(f"<b>ATS Score:</b> {resume.ats_score}%", styles["BodyText"]))
    story.append(Paragraph(f"<b>Match Score:</b> {resume.match_score}%", styles["BodyText"]))
    story.append(Paragraph(f"<b>Skills:</b> {resume.skills}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Uploaded:</b> {resume.uploaded_at}", styles["BodyText"]))

    doc.build(story)

    return response