from celery import shared_task
from .models import Document, Chunk
from .services import DocumentProcessor
from .utils import DocumentChunkingStatus
from chonkie import SemanticChunk
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
    acks_late=True,
)
def extract_document(self, document_id: str, stored_path: str):
    """
    Process a document asynchronously

    Args:
        document_id: ID of the document to process
        stored_path: Path where the file is stored in S3/storage
    """
    try:
        # Get the document instance
        document = Document.objects.get(id=document_id)

        # Update status to processing
        DocumentProcessor.update_document_chunking_status(
            document, DocumentChunkingStatus.PROCESSING
        )

        # Extract text, metadata from document
        text, metadata = DocumentProcessor.extract_text(document, stored_path)

        # Split text into chunks
        chunks: list[SemanticChunk] = DocumentProcessor.chunk_text(text)

        # Update document with chunk count
        document.total_chunks = len(chunks)

        # Define the mapping from source metadata keys to document metadata keys
        metadata_mapping = {
            "X-TIKA:Parsed-By": "parsed_by",
            "dc:title": "title",
            "dc:creator": "author",
            "dc:description": "description",
            "dc:publisher": "publisher",
        }

        # Prepare metadata update using a dictionary comprehension
        doc_metadata_update = {
            "extraction": {
                target_key: metadata[source_key]
                for source_key, target_key in metadata_mapping.items()
                if source_key in metadata
            }
        }

        # Handle potential None value in metadata and preserve existing data
        existing_metadata = document.metadata or {}
        document.metadata = {**existing_metadata, **doc_metadata_update}
        document.save(update_fields=["total_chunks", "metadata"])

        # Store chunks in database, create chunk objs in bulk
        Chunk.objects.bulk_create(
            [
                Chunk(
                    tenant=document.tenant,
                    document=document,
                    kb=document.kb,
                    content=chunk.text,
                    chunk_number=i,
                    token_count=chunk.token_count,
                    character_count=len(chunk.text),
                    metadata={
                        "start_index": chunk.start_index,
                        "end_index": chunk.end_index,
                    },
                )
                for i, chunk in enumerate(chunks)
            ]
        )

        # Mark document processing as completed
        DocumentProcessor.update_document_chunking_status(
            document, DocumentChunkingStatus.COMPLETED
        )
        logger.info(f"Successfully processed document {document_id}")

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")

        # Update document with error status
        try:
            document = Document.objects.get(id=document_id)
            DocumentProcessor.update_document_chunking_status(
                document, DocumentChunkingStatus.FAILED, error=str(e)
            )

        except Exception as inner_e:
            logger.error(
                f"Error updating document {document_id} status: {str(inner_e)}"
            )

        # Re-raise the exception to trigger Celery retry
        raise


@shared_task(bind=True)
def create_embeddings(self, document_id: str):
    """
    Create embeddings for a chunks in a document

    Args:
        document_id: ID of the document
    """
    try:
        # Get the document
        document = Document.objects.get(id=document_id)

    except Exception as e:
        logger.error(f"Error creating embeddings for document {document_id}: {str(e)}")
        raise
