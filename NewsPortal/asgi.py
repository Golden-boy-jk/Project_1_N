import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NewsPortal.settings")

# Если используешь только HTTP (без WebSockets) — этого достаточно:
application = get_asgi_application()

# ────────────────────────────────────────────────────────────────
# Если в будущем добавишь Django Channels:
#
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import news.routing   # например, news/routing.py с websocket_urlpatterns
#
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(news.routing.websocket_urlpatterns)
#     ),
# })
# ────────────────────────────────────────────────────────────────
