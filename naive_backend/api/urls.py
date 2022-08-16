
from django.urls import path
from graphene_django.views import GraphQLView
from .views import csrf_token

urlpatterns = [
    path('graphql/', GraphQLView.as_view(graphiql=True)),
    path('csrf/', csrf_token)
]