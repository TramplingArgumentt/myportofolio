from django.shortcuts import render

nama = "Evan Andrian"

def landing_page(request):

    return render(request, "index.html")