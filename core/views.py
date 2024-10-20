
from django.shortcuts import render

def home_view(request):
    return render(request, 'core/index.html')

def cv_view(request):
    return render(request, 'core/cv.html')
