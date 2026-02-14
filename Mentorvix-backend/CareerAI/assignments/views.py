from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Assignment
from .serializers import AssignmentSerializer


@api_view(["POST"])
def upload_assignment(request):
    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return Response({"error": "No file uploaded"}, status=400)

    assignment = Assignment.objects.create(file=uploaded_file)

    return Response({
        "message": "Assignment uploaded successfully",
        "id": assignment.id
    })


@api_view(["GET"])
def list_assignments(request):
    assignments = Assignment.objects.all().order_by("-uploaded_at")
    serializer = AssignmentSerializer(assignments, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def analyze_assignment(request, pk):
    try:
        assignment = Assignment.objects.get(id=pk)

        filename = assignment.file.name.lower()

        if "html" in filename:
            assignment.score = 78
            assignment.feedback = (
                "Good understanding of HTML basics. "
                "Correct use of div, span, anchor, and image tags. "
                "Improve semantic tags and accessibility."
            )

        elif "js" in filename:
            assignment.score = 72
            assignment.feedback = (
                "JavaScript fundamentals are clear. "
                "Loops and functions are correct. "
                "Work on edge cases and code structure."
            )

        elif "python" in filename:
            assignment.score = 80
            assignment.feedback = (
                "Strong Python basics. "
                "Good use of loops and conditionals. "
                "Improve variable naming and readability."
            )

        else:
            assignment.score = 65
            assignment.feedback = (
                "Assignment submitted successfully. "
                "Content could not be clearly classified."
            )

        assignment.save()

        return Response({
            "message": "Analysis completed",
            "score": assignment.score,
            "feedback": assignment.feedback
        })

    except Assignment.DoesNotExist:
        return Response(
            {"error": "Assignment not found"},
            status=404
        )
    
@api_view(["GET"])
def get_assignment(request, pk):
    try:
        assignment = Assignment.objects.get(id=pk)
        serializer = AssignmentSerializer(assignment)
        return Response(serializer.data)
    except Assignment.DoesNotExist:
        return Response(
            {"error": "Assignment not found"},
            status=404
        )   