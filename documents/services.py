from django.core.files.storage import default_storage
import logging
from .models import Document
from .utils import DocumentChunkingStatus
from extractous import Extractor
import re
from chonkie import SDPMChunker, SemanticChunk


logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing documents"""

    @staticmethod
    def extract_text(document: Document, file_path: str) -> (str, dict):
        """
        Extract text from a document based on its type

        Args:
            document: Document model instance
            file_path: Path to the file in storage

        Returns:
            Extracted text content
        """
        # instantiate extractor
        ex = Extractor()

        # get mime type
        # mime_type = document.metadata.get("mime_type")

        # prepare file buffer for extractor
        file_buffer = bytearray("", encoding="utf-8")
        result = ""

        # Read the file content
        with default_storage.open(file_path, "rb") as file:
            BUFFER_SIZE = file.size // 8
            while True:
                buff = file.read(BUFFER_SIZE)
                if not buff:
                    break
                file_buffer += bytearray(buff)

            # Extract text
            reader, metadata = ex.extract_bytes(file_buffer)
            buffer = reader.read(BUFFER_SIZE)
            while len(buffer) > 0:
                result += buffer.decode("utf-8", errors="replace")
                buffer = reader.read(BUFFER_SIZE)

        # Remove spaces around newlines
        result = re.sub(r"\s*\n\s*", "\n", result)
        # Normalize spaces and tabs
        result = re.sub(r"[ \t]+", " ", result)

        # Return the extracted text
        return result.strip(), metadata

    @staticmethod
    def chunk_text(
        text: str, chunk_size: int = 512, threshold: float = 0.6
    ) -> list[SemanticChunk]:
        """
        Split text into chunks

        Args:
            text: Text to split
            chunk_size: Maximum size of each chunk
            threshold: Similarity threshold for chunking

        Returns:
            List of text chunks
        """
        chunks: list[SemanticChunk] = []

        # instantiate chunker
        ch = SDPMChunker(
            embedding_model="minishlab/potion-base-32M",  # Default model
            threshold=threshold,  # Similarity threshold (0-1)
            chunk_size=chunk_size,  # Maximum tokens per chunk
            min_sentences=20,  # Initial sentences per chunk
            skip_window=1,  # Number of chunks to skip when looking for similarities
        )

        if len(text) <= chunk_size:
            chunks.append(text)
        else:
            chunks = ch.chunk(text)

        return chunks

    @staticmethod
    def update_document_chunking_status(
        document: Document, status: DocumentChunkingStatus, error=None
    ):
        """
        Update document processing status

        Args:
            document: Document model instance
            status: DocumentChunkingStatus enum
            error: Optional error message
        """

        document.chunking_status = status

        if error:
            document.metadata["chunking_error"] = str(error)
            document.save(update_fields=["chunking_status", "chunking_error"])
        else:
            document.save(update_fields=["chunking_status"])
