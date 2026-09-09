from django.shortcuts import render

nama = "Evan Andrian"

mhs1 = "Kak PeBePe"

def landing_page(request):

    return render(request, "index.html")