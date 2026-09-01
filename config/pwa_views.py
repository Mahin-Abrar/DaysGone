from pathlib import Path

from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@never_cache
@require_GET
def service_worker(request):
    sw_path = Path(settings.BASE_DIR) / "static" / "sw.js"
    response = FileResponse(sw_path.open("rb"), content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    return response


@require_GET
def install_guide(request):
    import socket
    hostname = socket.gethostname().lower().replace(" ", "-")
    return HttpResponse(
        _render_install_page(hostname),
        content_type="text/html",
    )


def _render_install_page(hostname):
  return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Install Life Tracker</title>
<link rel="stylesheet" href="/static/css/app.css">
<script src="https://cdn.tailwindcss.com"></script>
</head><body class="bg-gray-50 p-6 max-w-lg mx-auto">
<h1 class="text-2xl font-bold mb-2">📲 Install Life Tracker</h1>
<p class="text-gray-500 mb-6">Add to your home screen — no IP typing needed after setup!</p>
<div class="space-y-4">
<div class="card"><h2 class="font-bold mb-2">iPhone (Safari)</h2>
<ol class="text-sm space-y-1 text-gray-600 list-decimal list-inside">
<li>Open <strong>http://{hostname}.local:8000</strong> or your PC IP</li>
<li>Tap the <strong>Share</strong> button (box with arrow)</li>
<li>Tap <strong>Add to Home Screen</strong></li>
<li>Name it <strong>Life Tracker</strong> → Add</li>
</ol></div>
<div class="card"><h2 class="font-bold mb-2">Android (Chrome)</h2>
<ol class="text-sm space-y-1 text-gray-600 list-decimal list-inside">
<li>Open the site in Chrome</li>
<li>Tap <strong>⋮</strong> menu → <strong>Add to Home screen</strong></li>
<li>Or tap the install banner if shown</li>
</ol></div>
<div class="card"><h2 class="font-bold mb-2">Use a name instead of IP</h2>
<p class="text-sm text-gray-600">Rename your PC to <strong>lifetracker</strong> in Windows Settings → System → About, then try:</p>
<p class="mt-2 font-mono text-indigo-600 bg-indigo-50 p-2 rounded-lg text-sm">http://lifetracker.local:8000</p>
<p class="text-xs text-gray-400 mt-2">Works on many Android phones. iPhone may still need the IP once to bookmark.</p>
</div>
</div>
<a href="/" class="btn-primary block text-center mt-6">Back to app</a>
</body></html>"""
