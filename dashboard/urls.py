from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Dashboard home
    path("", views.HomeView.as_view(), name="home"),
    # Knowledge bases
    path(
        "knowledge-bases",
        views.KnowledgeBaseView.as_view(),
        name="knowledge-bases",
    ),
    path(
        "knowledge-bases/create",
        views.KnowledgeBaseCreateView.as_view(),
        name="knowledge-base-create",
    ),
    path(
        "knowledge-bases/<uuid:knowledge_base_id>",
        views.KnowledgeBaseDetailView.as_view(),
        name="knowledge-base-detail",
    ),
    # Documents
    path(
        "knowledge-bases/<uuid:knowledge_base_id>/documents/create",
        views.DocumentCreateView.as_view(),
        name="document-create",
    ),
]
