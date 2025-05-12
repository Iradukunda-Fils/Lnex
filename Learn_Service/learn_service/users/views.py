from django.shortcuts import render
from django.views.generic import ListView

# Create your views here.

def landing_view(request):
    return render(request, 'landing.html')