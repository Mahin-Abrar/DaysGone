import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .utils import delete_draft, load_draft, save_draft


@login_required
@require_POST
def save_draft_view(request):
    form_type = request.POST.get("form_type", "")
    object_id = request.POST.get("object_id", "new")
    data = {k: v for k, v in request.POST.items() if k not in ("csrfmiddlewaretoken", "form_type", "object_id")}
    save_draft(request.user.id, form_type, data, object_id)
    return JsonResponse({"status": "saved"})


@login_required
def load_draft_view(request):
    form_type = request.GET.get("form_type", "")
    object_id = request.GET.get("object_id", "new")
    data = load_draft(request.user.id, form_type, object_id)
    return JsonResponse({"draft": data})


@login_required
@require_POST
def delete_draft_view(request):
    form_type = request.POST.get("form_type", "")
    object_id = request.POST.get("object_id", "new")
    delete_draft(request.user.id, form_type, object_id)
    return JsonResponse({"status": "deleted"})
