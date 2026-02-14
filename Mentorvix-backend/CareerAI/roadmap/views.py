from django.shortcuts import render
from django.http import JsonResponse
import json
def roadmap_api(request):
    career = request.GET.get("career")

    roadmaps = {
        "fullstack": {
            "title": "Full Stack Developer Roadmap",
            "sections": {
                "Frontend (HTML, CSS, JS)": {
                    "youtube": [
                        "https://www.youtube.com/@TraversyMedia",
                        "https://www.youtube.com/@freecodecamp"
                    ],
                    "websites": [
                        "https://developer.mozilla.org",
                        "https://www.w3schools.com"
                    ],
                    "github_projects": [
                        "https://github.com/bradtraversy/vanillawebprojects"
                    ]
                },
                "Frontend Frameworks": {
                    "youtube": ["https://www.youtube.com/@NetNinja"],
                    "websites": ["https://react.dev"],
                    "github_projects": ["https://github.com/facebook/react"]
                },
                "Backend (Django / APIs)": {
                    "youtube": ["https://www.youtube.com/@DennisIvy"],
                    "websites": ["https://docs.djangoproject.com"],
                    "github_projects": ["https://github.com/django/django"]
                }
            }
        },

        "data": {
            "title": "Data Analyst Roadmap",
            "sections": {
                "Python & Statistics": {
                    "youtube": ["https://www.youtube.com/@KrishNaik"],
                    "websites": ["https://www.kaggle.com/learn"],
                    "github_projects": ["https://github.com/data-analysis-projects"]
                },
                "SQL & BI Tools": {
                    "youtube": ["https://www.youtube.com/@AlexTheAnalyst"],
                    "websites": ["https://mode.com/sql-tutorial"],
                    "github_projects": []
                }
            }
        },

        "cloud": {
            "title": "Cloud Engineer Roadmap",
            "sections": {
                "Cloud Basics": {
                    "youtube": ["https://www.youtube.com/@TechWorldwithNana"],
                    "websites": ["https://aws.amazon.com/training"],
                    "github_projects": []
                },
                "DevOps": {
                    "youtube": ["https://www.youtube.com/@kodekloud"],
                    "websites": ["https://kubernetes.io"],
                    "github_projects": []
                }
            }
        }
    }

    if career not in roadmaps:
        return JsonResponse(
            {"error": "Invalid career path"},
            status=400
        )

    return JsonResponse(roadmaps[career], safe=False)
# Create your views here.
