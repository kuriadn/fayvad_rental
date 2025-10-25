"""
Document management views
File upload, storage, and document tracking
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import HttpResponse, Http404
from .models import Document, DocumentType, DocumentStatus
from .forms import DocumentForm, DocumentUpdateForm, DocumentUploadForm, DocumentFilterForm

@login_required
def document_list(request):
    """List all documents"""
    documents = Document.objects.select_related('tenant', 'rental_agreement', 'room', 'uploaded_by').all()

    # Filters
    document_type_filter = request.GET.get('document_type', '')
    status_filter = request.GET.get('status', '')
    tenant_filter = request.GET.get('tenant', '')
    room_filter = request.GET.get('room', '')
    is_required_filter = request.GET.get('is_required', '')

    if document_type_filter:
        documents = documents.filter(document_type=document_type_filter)
    if status_filter:
        documents = documents.filter(status=status_filter)
    if tenant_filter:
        documents = documents.filter(tenant_id=tenant_filter)
    if room_filter:
        documents = documents.filter(room_id=room_filter)
    if is_required_filter:
        documents = documents.filter(is_required=is_required_filter == 'True')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(filename__icontains=search_query) |
            Q(tenant__name__icontains=search_query) |
            Q(room__room_number__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(documents, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_documents = documents.count()
    active_documents = documents.filter(status='active').count()
    draft_documents = documents.filter(status='draft').count()
    archived_documents = documents.filter(status='archived').count()

    # Filter form
    filter_form = DocumentFilterForm(request.GET)

    context = {
        'page_title': 'Documents',
        'page_obj': page_obj,
        'filter_form': filter_form,
        'search_query': search_query,
        'total_documents': total_documents,
        'active_documents': active_documents,
        'draft_documents': draft_documents,
        'archived_documents': archived_documents,
    }
    return render(request, 'documents/document_list.html', context)

@login_required
def document_detail(request, pk):
    """View document details"""
    document = get_object_or_404(
        Document.objects.select_related('tenant', 'rental_agreement', 'room', 'uploaded_by'),
        pk=pk
    )

    context = {
        'page_title': f'Document: {document.title}',
        'document': document,
    }
    return render(request, 'documents/document_detail.html', context)

@login_required
def document_create(request):
    """Create new document"""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            messages.success(request, f'Document "{document.title}" created successfully.')
            return redirect('documents:document_detail', pk=document.pk)
    else:
        form = DocumentForm()

    context = {
        'page_title': 'Create Document',
        'form': form,
    }
    return render(request, 'documents/document_form.html', context)

@login_required
def document_update(request, pk):
    """Update existing document"""
    document = get_object_or_404(Document, pk=pk)

    if request.method == 'POST':
        form = DocumentUpdateForm(request.POST, instance=document)
        if form.is_valid():
            document = form.save()
            messages.success(request, f'Document "{document.title}" updated successfully.')
            return redirect('documents:document_detail', pk=document.pk)
    else:
        form = DocumentUpdateForm(instance=document)

    context = {
        'page_title': f'Edit Document: {document.title}',
        'form': form,
        'document': document,
    }
    return render(request, 'documents/document_form.html', context)

@login_required
def document_delete(request, pk):
    """Delete document"""
    document = get_object_or_404(Document, pk=pk)

    if request.method == 'POST':
        title = document.title
        # Delete the file if it exists
        if document.file:
            document.file.delete(save=False)
        document.delete()
        messages.success(request, f'Document "{title}" deleted successfully.')
        return redirect('documents:document_list')

    context = {
        'page_title': f'Delete Document: {document.title}',
        'object': document,
        'object_name': 'document',
        'cancel_url': reverse('documents:document_detail', kwargs={'pk': pk}),
    }
    return render(request, 'documents/document_confirm_delete.html', context)

@login_required
def document_upload(request):
    """Upload new document"""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            document = form.save()
            messages.success(request, f'Document "{document.title}" uploaded successfully.')
            return redirect('documents:document_detail', pk=document.pk)
    else:
        form = DocumentUploadForm(user=request.user)

    context = {
        'page_title': 'Upload Document',
        'form': form,
    }
    return render(request, 'documents/document_upload.html', context)

@login_required
def document_download(request, pk):
    """Download document file"""
    document = get_object_or_404(Document, pk=pk)

    if not document.file:
        raise Http404("Document file not found")

    # Check permissions (simplified - in production, add proper permission checks)
    if not document.is_public and document.uploaded_by != request.user:
        # Add additional permission checks here
        pass

    try:
        response = HttpResponse(document.file.read(), content_type=document.mime_type)
        response['Content-Disposition'] = f'attachment; filename="{document.filename}"'
        return response
    except FileNotFoundError:
        raise Http404("File not found")

@login_required
def document_activate(request, pk):
    """Activate a document"""
    document = get_object_or_404(Document, pk=pk)

    if document.status != DocumentStatus.DRAFT:
        messages.error(request, f'Document {document.title} is not in draft status.')
        return redirect('documents:document_detail', pk=pk)

    if request.method == 'POST':
        document.activate_document()
        messages.success(request, f'Document "{document.title}" activated successfully.')
        return redirect('documents:document_detail', pk=pk)

    context = {
        'page_title': f'Activate Document: {document.title}',
        'document': document,
        'action': 'activate',
    }
    return render(request, 'documents/document_action.html', context)

@login_required
def document_archive(request, pk):
    """Archive a document"""
    document = get_object_or_404(Document, pk=pk)

    if document.status == DocumentStatus.ARCHIVED:
        messages.error(request, f'Document {document.title} is already archived.')
        return redirect('documents:document_detail', pk=pk)

    if request.method == 'POST':
        document.archive_document()
        messages.success(request, f'Document "{document.title}" archived successfully.')
        return redirect('documents:document_detail', pk=pk)

    context = {
        'page_title': f'Archive Document: {document.title}',
        'document': document,
        'action': 'archive',
    }
    return render(request, 'documents/document_action.html', context)

@login_required
def tenant_documents(request, tenant_pk):
    """View documents for a specific tenant"""
    from tenants.models import Tenant
    tenant = get_object_or_404(Tenant, pk=tenant_pk)

    documents = Document.objects.filter(
        tenant=tenant
    ).select_related('rental_agreement', 'room', 'uploaded_by').order_by('-created_at')

    context = {
        'page_title': f'Documents - {tenant.name}',
        'tenant': tenant,
        'documents': documents,
        'total_documents': documents.count(),
        'active_documents': documents.filter(status='active').count(),
        'required_documents': documents.filter(is_required=True).count(),
    }
    return render(request, 'documents/tenant_documents.html', context)
