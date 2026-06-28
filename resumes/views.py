from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Resume
from .serializers import ResumeSerializer
from .utils import extract_text_from_pdf, extract_skills, calculate_match_score
from django.shortcuts import render

class ResumeUploadView(APIView):

    def post(self, request):
        print('POST RECEIVED')
        serializer = ResumeSerializer(data=request.data)

        if serializer.is_valid():

            resume = serializer.save()

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

def upload_page(request):
    print("REQUEST METHOD:", request.method)

    if request.method == "POST":

        print("FORM SUBMITTED")
    return render(request, "upload.html")


