from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, CreateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .models import UserDashboard
from django.views import View
from tenants.models import Tenant
from knowledge_bases.models import KnowledgeBase
from django.http import HttpResponse
from documents.models import Document
from typing import BinaryIO
from magika import Magika
from documents.utils import DocumentChunkingStatus


class DashboardBaseView(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_dashboard"] = self.request.user.dashboard

        # Try to get the current tenant ID from session
        current_tenant_id = self.request.session.get("current_tenant_id")

        if current_tenant_id:
            # If session has a tenant ID, verify user still has access to it
            tenant = self.request.user.tenants.filter(id=current_tenant_id).first()
            # Use found tenant or fallback to default if tenant not found/accessible
            context["current_tenant"] = tenant or self.request.user.default_tenant
            # get tenant role
            context["current_tenant"].role = self.request.user.get_tenant_role(
                context["current_tenant"]
            )

            # Update session if we fell back to default tenant
            if not tenant:
                self.request.session["current_tenant_id"] = str(
                    context["current_tenant"].id
                )
        else:
            # No tenant in session, use default tenant and set in session
            context["current_tenant"] = self.request.user.default_tenant
            self.request.session["current_tenant_id"] = str(
                context["current_tenant"].id
            )

        return context


class HomeView(DashboardBaseView, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


### Knowledge bases ###
class KnowledgeBaseView(DashboardBaseView, TemplateView):
    template_name = "dashboard/kb/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Get the current tenant ID from session
            current_tenant_id = self.request.session.get("current_tenant_id")

            # If no tenant in session, use default tenant
            if not current_tenant_id:
                current_tenant_id = self.request.user.default_tenant.id

                # Store current tenant ID in session
                self.request.session["current_tenant_id"] = str(current_tenant_id)

            # check if user has acces to the current tenant
            if current_tenant_id not in [
                str(tenant.id) for tenant in self.request.user.tenants.all()
            ]:
                current_tenant_id = self.request.user.default_tenant.id

            # Get all knowledge bases for the current tenant
            context["knowledge_bases"] = KnowledgeBase.objects.filter(
                tenant_id=current_tenant_id
            ).order_by("-created_at")

        except Exception as e:
            print(f"Error in DashboardKnowledgeBaseView: {str(e)}")
            context["knowledge_bases"] = KnowledgeBase.objects.none()
            messages.error(self.request, "Unable to load knowledge bases")

        return context


class KnowledgeBaseCreateView(DashboardBaseView, CreateView):
    template_name = "dashboard/kb/create.html"
    model = KnowledgeBase
    fields = ["name", "description"]

    def form_valid(self, form):
        form.instance.tenant = self.request.user.default_tenant
        form.instance.metadata = {}  # Initialize an empty metadata
        response = super().form_valid(form)

        if self.request.headers.get("HX-Request"):
            messages.success(
                self.request,
                f"Knowledge base '{form.instance.name}' created successfully!",
            )
            return HttpResponse(
                status=204, headers={"HX-Redirect": self.get_success_url()}
            )

        return response

    def get_success_url(self):
        return reverse_lazy("dashboard:knowledge-bases")


class KnowledgeBaseDetailView(DashboardBaseView, TemplateView):
    template_name = "dashboard/kb/detail.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            kb = get_object_or_404(KnowledgeBase, id=kwargs["knowledge_base_id"])
            if kb.tenant.id not in [tenant.id for tenant in request.user.tenants.all()]:
                messages.error(request, "Access denied to this knowledge base")
                return redirect("dashboard:knowledge-bases")
            return super().dispatch(request, *args, **kwargs)
        except Exception:
            messages.error(request, "Unable to load knowledge base")
            return redirect("dashboard:knowledge-bases")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kb = get_object_or_404(KnowledgeBase, id=kwargs["knowledge_base_id"])
        context["knowledge_base"] = kb
        context["documents"] = Document.objects.filter(
            kb=kb, tenant=context["current_tenant"]
        ).order_by("-created_at")
        return context


### Documents ###
class DocumentCreateView(DashboardBaseView, TemplateView):
    # Standard file path template for document storage
    DOCUMENT_PATH_TEMPLATE = "documents/{tenant_id}/{kb_id}/{document_id}.{extension}"

    CHUNK_SIZE = 32768  # 32KB chunks for detection
    MAX_READ_SIZE = 262144  # 256KB max for type detection
    SUPPORTED_MIME_TYPES = [
        "text/plain",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/epub+zip",
    ]

    def detect_file_type(self, file: BinaryIO) -> dict:
        """
        Detect the file type using Magika.
        """

        # Initialize Magika once and reuse
        magika = getattr(self, "_magika", None)
        if not magika:
            magika = Magika()
            setattr(self, "_magika", magika)

        # Read larger portion for better detection
        content_sample = b""
        bytes_read = 0

        while bytes_read < self.MAX_READ_SIZE:
            chunk = file.read(self.CHUNK_SIZE)
            if not chunk:
                break
            content_sample += chunk
            bytes_read += len(chunk)

        file.seek(0)  # Reset file pointer

        result = magika.identify_bytes(content_sample)

        return {
            "mime_type": result.output.mime_type,
            "content_type": result.output.ct_label,
            "confidence": result.output.score,
            "group": result.output.group,
        }

    def save_document_file(self, document: Document, file):
        """
        Save a document file using the standard path template

        Args:
            document: Document model instance
            file: File object from request.FILES

        Returns:
            The path where the file was stored
        """
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        # Extract file extension
        file_extension = file.name.split(".")[-1] if "." in file.name else ""

        # Generate the file path using the template
        file_path = self.DOCUMENT_PATH_TEMPLATE.format(
            tenant_id=document.tenant.id,
            kb_id=document.kb.id,
            document_id=document.id,
            extension=file_extension,
        )

        # Save the file to storage
        return default_storage.save(file_path, ContentFile(file.read()))

    def process_document(self, document: Document, stored_path: str):
        """
        Process the document after it has been uploaded

        Args:
            document: Document model instance
            stored_path: Path where the file is stored in S3/storage
        """
        from documents.tasks import extract_document

        # Schedule document processing task using the document's ID
        extract_document.delay(document_id=document.id, stored_path=stored_path)

        # Update document with scheduled status
        document.chunking_status = DocumentChunkingStatus.SCHEDULED
        document.save(update_fields=["chunking_status"])

    def post(self, request, *args, **kwargs):
        kb = get_object_or_404(KnowledgeBase, id=kwargs["knowledge_base_id"])
        files = request.FILES.getlist("documents")

        for file in files:
            # Detect file type efficiently
            file_info = self.detect_file_type(file)

            # Check if file type is supported
            if file_info["group"] != "document":
                messages.error(request, f"Unsupported file type: {file_info['group']}")
                continue

            # Check if file type is supported for documents
            if file_info["mime_type"] not in self.SUPPORTED_MIME_TYPES:
                messages.error(
                    request, f"Unsupported document type: {file_info['mime_type']}"
                )
                continue

            # TODO: get file size and check if it is too large

            # Create document instance
            try:
                document = Document.objects.create(
                    tenant=self.request.user.default_tenant,
                    kb=kb,
                    name=file.name,
                    content_type=file_info["content_type"],
                    file_size=file.size,
                    metadata={
                        "mime_type": file_info["mime_type"],
                        "confidence": file_info["confidence"],
                        "s3": {},
                    },
                )

                # upload files to s3 (in memory to s3)
                stored_path = self.save_document_file(document, file)

                # Update the document with the file path
                document.metadata["s3"]["path"] = stored_path
                document.save(update_fields=["metadata"])

                # print(f"Document {document.id} saved to {stored_path}")

                # schedule document for processing
                self.process_document(document, stored_path)

            except Exception as e:
                messages.error(request, f"Error creating document: {str(e)}")
                # TODO: send error back to user with htmx
                continue

        if request.headers.get("HX-Request"):
            messages.success(request, f"{len(files)} documents uploaded successfully")
            return HttpResponse(
                status=204,
                headers={
                    "HX-Redirect": reverse_lazy(
                        "dashboard:knowledge-base-detail",
                        kwargs={"knowledge_base_id": kb.id},
                    )
                },
            )


class DashboardProfileView(DashboardBaseView, UpdateView):
    model = UserDashboard
    template_name = "dashboard/profile.html"
    fields = ["bio"]
    success_url = reverse_lazy("dashboard:profile")

    def get_object(self):
        return self.request.user.dashboard


class DashboardTenantsView(DashboardBaseView, TemplateView):
    template_name = "dashboard/tenants.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["administered_tenants"] = self.request.user.get_administered_tenants()
        context["all_tenants"] = self.request.user.get_accessible_tenants()
        return context


class SwitchTenantView(LoginRequiredMixin, View):
    def post(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, id=tenant_id)

        if tenant in request.user.tenants.all():
            # Store current tenant ID in session
            request.session["current_tenant_id"] = str(tenant.id)
            messages.success(request, f"Switched to {tenant.name}")
        else:
            messages.error(request, "Access denied to this tenant")

        return redirect(request.META.get("HTTP_REFERER", "dashboard:home"))
