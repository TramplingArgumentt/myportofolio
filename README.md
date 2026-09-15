Nama : Evan Andrian

NPM : 2506539082

Kelas : PBP B

# Website Portofolio Pribadi

## Deskripsi
Website ini merupakan proyek portofolio pribadi yang dibuat untuk menampilkan informasi mengenai profil, pengalaman, pendidikan, proyek, dan keterampilan yang saya miliki. Proyek ini dikembangkan secara bertahap mengikuti instruksi yang diberikan pada setiap penugasan.

Pada implementasi awal, website dibuat menggunakan HTML dan CSS untuk membuat struktur dan tampilan halaman. Website dirancang untuk dapat menyesuaikan tampilan pada mode desktop maupun mobile. 

## Fitur
- Profile
- Experience
- Projects
- Education
- Skills

## Language
- HTML
- CSS

## Setup
### Week 1 - 7 September 2026 (Tugas 1)
- Menambahkan tampilan website mengikuti instruksi Tutorial 1
- Menambahkan section Experience, Project, Education, dan Skill

### Week 2 - 14 September 2026 (Tugas 2)
- Memindahkan section Experience, Project, Education, dan Skill ke template yang berbeda
- Menerapkan MVT untuk data yang ditampilkan pada website

### Tugas 1

1. Ya, saya menggunakan elemen <section> dan <article>. Penggunaan section saya gunakan untuk membagi halaman berdasarkan topik seperti Skill, Project, Experience, dan Education, sementara article digunakan untuk konten yang lebih spesifik di dalam satu section agar lebih rapi, contohnya pada konten Project. Tag <aside> tidak saya gunakan karena kompleksitas website yang masih tergolong sederhana sehingga tidak memerlukan fitur yang disediakan dari tag <aside>.

2. Tantangan yang saya temukan adalah reference link pada site-header yang menghasilkan interaksi yang aneh ketika section hero dibuat position: sticky. Perpindahan section melalui navigation link yang terjadi tidak sesuai dengan yang saya harapkan, sehingga saya memutuskan untuk mengubah pendekatan karena tidak dapat menemukan solusi bahkan ketika sudah menggunakan Gen AI.

Karena keterbatasan ruang pada tampilan mobile, kebanyakan konten yang semula disusun secara horizontal pada tampilan desktop disusun ulang secara vertikal agar muat ditampilkan. Kebanyakan padding juga dibuat lebih kecil menyesuaikan skala tampilan layar yang lebih kecil.

3. Batasan yang saya rasakan adalah pada pembuatan header versi mobile. Pada static web murni, hamburger menu belum dapat diimplementasi, sehingga header pada versi mobile terasa sesak karena banyaknya menu yang ada. Pada iterasi proyek selanjutnya, saya ingin menambahkan hamburger menu pada versi mobile.

### Tugas 2
1. Ketika pengguna membuka halaman portofolio, browser mengirimkan HTTP Request ke Django. Request kemudian diterima oleh `urls.py proyek`, dan kemudian diteruskan ke `urls.py aplikasi` dengan include(). `urls.py proyek` berfungsi sebagai pengatur URL utama dan menentukan aplikasi mana yang bertanggung jawab menangani request tersebut. Setelah diteruskan, Django akan mencocokkan URL dengan pola URL yang ada lalu memanggil fungsi atau class view yang sesuai. View berperan sebagai penghubung request pengguna, data dari model, dan template yang akan dikirim kembali. Jika halaman membutuhkan data portofolio, view akan mengambilnya melalui model. Model adalah struktur data yang tersimpan pada database. Setelah mendapatkan data, view akan meneruskannya ke template. Template bertanggung jawab untuk menentukan bagaimana data ditampilkan dalam HTML. Django kemudian akan melakukan rendering template menjadi HTML dan dikirim sebagai HTTP Response, dan browser akan menampilkan HTML tersebut sebagai halaman portofolio.

2. Karena model dan template memiliki tugas yang berbeda. Model bertanggung jawab terhadap data, sedangkan template bertanggung jawab terhadap bagaimana data ditampilkan. Jika data ditulis langsung pada template, setiap perubahan data mengharuskan developer mengubah kode HTML/template. Hal ini menjadi kurang efisien ketika jumlah data semakin banyak.

Dengan menyimpan data pada model, template dapat menggunakan data secara dinamis. Misal untuk beberapa data, template dapat menggunakan Django Template Language untuk melakukan perulangan untuk menampilkan seluruh data. Ketika ada data baru, developer cukup menambahkan data tanpa mengubah struktur HTML secara manual.

Perubahan pada database dapat dilakukan tanpa mengubah desain template, dan perubahan pada template dapat dilakukan tanpa mengubah data di database. Data yang tersimpan di model juga dapat digunakan pada fitur lain di masa depan.

3. `makemigrations` digunakan untuk membuat file migration berdasarkan perubahan pada model di Django. File migration berisi instruksi perubahan struktur database yang perlu dilakukan.

Sedangkan `migrate` digunakan untuk menerapkan instruksi pada file migration ke database sehingga struktur database sesuai dengan model terbaru.

Contohnya, awalnya terdapat model Item

```
class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
```

Tetapi kemudian saya menyadari bahwa ada class Tag yang berfungsi mirip dengan Item, sehingga saya memutuskan untuk menghapus class Item. Setelah menghapus class Item pada file `models.py`, saya menjalankan `python manage.py makemigrations main`. Pada file migration, tercatat 

```
migrations.DeleteModel(
    name='Item',
),
```

Kemudian saya menjalankan `python manage.py migrate`, perintah tersebut diterapkan pada database, sehingga Item pada database akan terhapus.

## AI Disclosure: 
### Tools
ChatGPT, Claude

### Penggunaan AI
AI saya gunakan terutama sebagai coding assistant untuk membantu menerjemahkan rancangan dan ide layout yang saya jelaskan menjadi implementasi HTML/CSS. Saya tetap menentukan struktur website, section yang dibuat, desain yang diinginkan, serta melakukan pengujian terhadap hasil implementasi. Kode yang diberikan AI tidak langsung saya gunakan tanpa pemeriksaan karena beberapa solusi yang diberikan tidak sesuai dengan struktur proyek atau menghasilkan perilaku yang tidak diinginkan.

### Strategi Prompting
Strategi prompting yang digunakan adalah dengan menyalin dan menempel kode yang saya miliki kepada AI ditambah dengan penjelasan penambahan atau perubahan yang saya inginkan. Meski demikian, AI tersebut tetap melakukan beberapa kesalahan (terutama ChatGPT).

### Keterbatasan AI
Ketika AI melakukan kesalahan, saya akan melakukan follow-up prompt untuk memperbaiki kesalahan spesifik yang dilakukan. Kelemahannya adalah ketika terlalu banyak chat digunakan, AI tersebut akan mulai melupakan beberapa prompt sebelumnya, sehingga percakapan hanya setengah nyambung. Hal tersebut menyebabkan saya harus kembali memasukkan kode yang ada kepada AI-nya. 

### Perbaikan Manual
Perbaikan manual yang saya lakukan juga dibantu dengan AI. Hanya saja, saya akan memasukkan ulang permasalahan yang ingin diperbaiki dengan skala yang lebih kecil. Hanya dengan beberapa baris kode dan pertanyaan simpel dapat menjawab permasalahannya.

### AI Chat Logs
https://chatgpt.com/share/6a9eb251-1074-83ec-9fe9-9349647738de
https://claude.ai/share/172e5d3d-730e-4ec4-99bb-5151be60a5ca