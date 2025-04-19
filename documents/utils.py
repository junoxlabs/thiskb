from enum import StrEnum


class DocumentChunkingStatus(StrEnum):
    """
    Enum representing the possible states of a document during the chunking process.

    These statuses track a document's progress through the text extraction and
    chunking pipeline, from initial upload to final processing.
    """

    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

    @property
    def is_terminal(self):
        """Return True if this status represents a terminal state."""
        return self in (self.COMPLETED, self.FAILED)

    @property
    def is_active(self):
        """Return True if document is actively being processed."""
        return self in (self.PENDING, self.SCHEDULED, self.PROCESSING)

    @classmethod
    def choices(cls):
        """
        Return a list of tuples for use in Django model field choices.

        Returns:
            List of (db_value, human_readable_name) tuples
        """
        return [(status.value, status.value.title()) for status in cls]
