from django.urls import path
from .router import router


urlpatterns = [
    path("", router.urls),
]
