from django.http import HttpResponse
from rest_framework.decorators import api_view


@api_view(['GET'])
def ping(request):
    return HttpResponse("pong")