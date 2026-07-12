from rest_framework import serializers
import os
from .services.rag.loader import SUPPORTED_EXTENSIONS

class RAGUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            raise serializers.ValidationError(
                f"Unsupported file extension '{ext}'. Supported: {supported}"
            )
        return value


class DocumentInfoSerializer(serializers.Serializer):
    document_id = serializers.CharField()
    source = serializers.CharField()
    file_type = serializers.CharField()
    chunk_count = serializers.IntegerField()
    filename = serializers.CharField(required=False, default="")
    upload_time = serializers.CharField(required=False, default="")
    file_size = serializers.IntegerField(required=False, default=0)
    status = serializers.CharField(required=False, default="Indexed")



class IndexResultSerializer(serializers.Serializer):
    document_id = serializers.CharField()
    source = serializers.CharField()
    file_type = serializers.CharField()
    chunks_indexed = serializers.IntegerField()
