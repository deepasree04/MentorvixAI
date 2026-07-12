import os
from pathlib import Path
from django.core.management.base import BaseCommand
from mentor_api.services.rag import index_documents
from mentor_api.services.rag.utils import SUPPORTED_EXTENSIONS, RAGError

class Command(BaseCommand):
    help = "Bulk index documents (PDF, DOCX, TXT, MD) into ChromaDB for RAG"

    def add_arguments(self, parser):
        parser.add_argument(
            "paths",
            nargs="+",
            type=str,
            help="One or more file or directory paths to index.",
        )
        parser.add_argument(
            "--no-replace",
            action="store_true",
            help="Skip deleting existing chunks before re-indexing.",
        )

    def handle(self, *args, **options):
        replace_existing = not options["no_replace"]
        input_paths = options["paths"]
        
        files_to_index = []
        for path_str in input_paths:
            path = Path(path_str).resolve()
            if path.is_file():
                ext = path.suffix.lower()
                if ext == ".markdown":
                    ext = ".md"
                if ext in SUPPORTED_EXTENSIONS:
                    files_to_index.append(path)
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping file '{path}' (unsupported extension)."
                        )
                    )
            elif path.is_dir():
                self.stdout.write(f"Scanning directory '{path}'...")
                for root, _, files in os.walk(path):
                    for file in files:
                        file_path = Path(root) / file
                        ext = file_path.suffix.lower()
                        if ext == ".markdown":
                            ext = ".md"
                        if ext in SUPPORTED_EXTENSIONS:
                            files_to_index.append(file_path)
            else:
                self.stdout.write(
                    self.style.ERROR(f"Path does not exist: '{path_str}'")
                )

        if not files_to_index:
            self.stdout.write(self.style.WARNING("No supported files found to index."))
            return

        self.stdout.write(
            f"Found {len(files_to_index)} file(s) to process. Starting indexing..."
        )

        success_count = 0
        for file_path in files_to_index:
            self.stdout.write(f"Indexing '{file_path.name}'...")
            try:
                results = index_documents(
                    file_path,
                    replace_existing=replace_existing,
                )
                for res in results:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Successfully indexed '{res.source}' -> "
                            f"document_id: {res.document_id} ({res.chunks_indexed} chunks)"
                        )
                    )
                success_count += 1
            except RAGError as e:
                self.stdout.write(
                    self.style.ERROR(f"  Failed to index '{file_path.name}': {e}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  Unexpected error indexing '{file_path.name}': {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nIndexing finished. Successfully indexed {success_count}/{len(files_to_index)} files."
            )
        )
