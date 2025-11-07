from rest_framework import viewsets
from .models import Hello
from .serializers import HelloSerializer


class HelloViewSet(viewsets.ModelViewSet):
	"""A simple ViewSet for viewing and editing Hello messages."""
	queryset = Hello.objects.all()
	serializer_class = HelloSerializer
