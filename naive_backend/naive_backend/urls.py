
from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from django.views.static import serve
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path("graphql", GraphQLView.as_view(graphiql=True)),
    path(r'^(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]
