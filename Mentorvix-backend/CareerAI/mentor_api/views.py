from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
@api_view(['GET'])
def home(request):
    return Response({"status":"MentorVix API working"})

@api_view(["POST"])
def ai_chat(request):
    text = request.data.get("interest", "").lower()
    if "data" in text:
        return Response({
            "career": "Data Scientist",
            "roadmap": [
                "Python",
                "Statistics & Probability",
                "Data Analysis (Pandas, NumPy)",
                "Machine Learning",
                "Projects & Kaggle"
            ],
            "resources": {
                "youtube": [
                    "https://www.youtube.com/@KrishNaik",
                    "https://www.youtube.com/@codebasics"
                ],
                "pdf": [
                    "https://github.com/ossu/data-science"
                ]
            }
        })

    elif "ai" in text:
        return Response({
            "career": "AI Engineer",
            "roadmap": [
                "Python",
                "Linear Algebra",
                "Machine Learning",
                "Deep Learning",
                "AI Projects"
            ],
            "resources": {
                "youtube": [
                    "https://www.youtube.com/@sentdex",
                    "https://www.youtube.com/@AndrewNg"
                ],
                "pdf": [
                    "https://github.com/karpathy/nn-zero-to-hero"
                ]
            }
        })

    elif "cloud" in text:
        return Response({
            "career": "Cloud Engineer",
            "roadmap": [
                "Networking Basics",
                "Linux",
                "AWS / Azure / GCP",
                "Docker & Kubernetes",
                "Cloud Security Basics"
            ],
            "resources": {
                "youtube": [
                    "https://www.youtube.com/@freecodecamp",
                    "https://www.youtube.com/@TechWorldwithNana"
                ],
                "pdf": [
                    "https://roadmap.sh/cloud"
                ]
            }
        })

    elif "web" in text or "full stack" in text:
        return Response({
            "career": "Full Stack Developer",
            "roadmap": [
                "HTML, CSS, JavaScript",
                "React",
                "Backend (Django / Node)",
                "Databases",
                "Projects"
            ],
            "resources": {
                "youtube": [
                    "https://www.youtube.com/@TraversyMedia",
                    "https://www.youtube.com/@freecodecamp"
                ],
                "pdf": [
                    "https://roadmap.sh/full-stack"
                ]
            }
        })

    return Response({
        "message": "Please ask about Data Science, AI, Cloud, or Full Stack"
    })