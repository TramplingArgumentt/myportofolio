from django.shortcuts import render
from portofolio.models import Mahasiswa

nama = "Evan Andrian"

mhs1 = "Kak PeBePe"

def landing_page(request):
    ma = Mahasiswa.objects.all()

    response = {"name": nama, "mahasiswa": ma}
    return render(request, "index.html", response)