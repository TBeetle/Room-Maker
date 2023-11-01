from django.shortcuts import render

# Create your views here.

def ImportPage(request):
    return render(request, "import.html")

def RegisterPage(request):
    return render(request, 'register.html')

def LoginPage(request):
    return render(request, 'login.html')

def HomePage(request):
    return render(request, 'home.html')