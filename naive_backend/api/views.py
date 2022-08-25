from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@ensure_csrf_cookie
def csrf_token(request):
    return Response({'token': 'token is set in cookies'},
                    status=status.HTTP_200_OK)
# Create your views here.

