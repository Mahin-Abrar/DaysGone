import json

from django.conf import settings
from django.core.cache import cache


def draft_key(user_id, form_type, object_id="new"):
    return f"draft:{user_id}:{form_type}:{object_id}"


def save_draft(user_id, form_type, data, object_id="new"):
    key = draft_key(user_id, form_type, object_id)
    cache.set(key, json.dumps(data), settings.DRAFT_TTL)
    return key


def load_draft(user_id, form_type, object_id="new"):
    key = draft_key(user_id, form_type, object_id)
    raw = cache.get(key)
    if raw:
        return json.loads(raw)
    return None


def delete_draft(user_id, form_type, object_id="new"):
    cache.delete(draft_key(user_id, form_type, object_id))
