# İFİ Butik

İFİ Butik, modern web teknolojileri kullanılarak geliştirilmiş, mobil öncelikli (mobile-first) ve kampanya odaklı bir e-ticaret platformudur. Kullanıcı deneyimini en üst düzeye çıkarmak için modern tasarım prensipleri ve interaktif ön yüz teknolojileri ile donatılmıştır.

## 🚀 Özellikler

### Ön Yüz (Frontend)
- **Modern & Responsive Tasarım**: Tailwind CSS ile geliştirilmiş, her cihaza uyumlu arayüz.
- **İnteraktif Kullanıcı Deneyimi**: Alpine.js ve HTMX ile güçlendirilmiş dinamik etkileşimler.
- **Görsel Efektler**:
  - Glassmorphism (Buzlu cam) efektleri
  - Parallax bannerlar
  - 3D Tilt efektli ürün kartları
  - Kayan yazı şeritleri (Marquee)
  - Yumuşak geçişler ve animasyonlar
- **Alışveriş Deneyimi**:
  - Kampanya bazlı ürün listeleme
  - Dinamik sepet ve ürün seçimi
  - HTMX ile kademeli adres seçimi (İl -> İlçe -> Mahalle)
  - Stok takibi ve beden seçimi

### Arka Yüz (Backend)
- **Django Framework**: Güçlü ve güvenli altyapı.
- **Yönetim Paneli**:
  - Kampanya yönetimi
  - Ürün ve stok yönetimi
  - Sipariş takibi ve yönetimi
  - Raporlama ekranları
- **Veritabanı**: SQLite (Geliştirme ortamı için), PostgreSQL uyumlu yapı.

## 🛠 Teknoloji Yığını

**Backend:**
- Python
- Django

**Frontend:**
- HTML5 / CSS3
- Tailwind CSS (Utility-first CSS framework)
- Alpine.js (Lightweight reactive framework)
- HTMX (High power tools for HTML)

## ⚙️ Kurulum

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin:

1. **Projeyi Klonlayın**
   ```bash
   git clone https://github.com/ifisoftw/ifibutik.git
   cd ifibutik
   ```

2. **Sanal Ortam Oluşturun ve Aktifleştirin**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Mac/Linux için
   # .venv\Scripts\activate   # Windows için
   ```

3. **Gereksinimleri Yükleyin**
   ```bash
   pip install -r requirements.txt
   ```
   *(Not: Eğer `requirements.txt` henüz oluşturulmadıysa, Django ve diğer bağımlılıkların kurulu olduğundan emin olun.)*

4. **Veritabanı Migrasyonlarını Uygulayın**
   ```bash
   python manage.py migrate
   ```

5. **Süper Kullanıcı Oluşturun (Opsiyonel)**
   Admin paneline erişmek için:
   ```bash
   python manage.py createsuperuser
   ```

6. **Sunucuyu Başlatın**
   ```bash
   python manage.py runserver
   ```

Proje şu adreste çalışacaktır: `http://127.0.0.1:8000/`

## 📂 Proje Yapısı

- `admin_panel/`: Özel yönetim paneli görünümleri ve mantığı.
- `campaigns/`: Kampanya yönetimi ve listeleme işlemleri.
- `products/`: Ürün veritabanı modelleri ve işlemleri.
- `orders/`: Sipariş oluşturma, takip ve yönetim.
- `addresses/`: Adres yönetimi ve il/ilçe verileri.
- `gumbuz_shop/`: Ana proje ayarları ve konfigürasyonları.
- `templates/`: HTML şablon dosyaları.
- `staticfiles/`: CSS, JavaScript ve görsel dosyalar.

## 📝 Lisans

Bu proje özel bir yazılımdır. İzinsiz kopyalanması veya dağıtılması yasaktır.
