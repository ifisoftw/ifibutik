# 🎯 Kampanya Kartları Detaylı Analiz

**Dosya:** `/templates/campaigns/detail.html` (Satır 154-214)  
**Bileşen:** Kampanya Seçenekleri Kartları  
**Amaç:** Kullanıcının farklı kampanya paketleri arasından seçim yapabilmesi

---

## 📋 Genel Bakış

### Görünürlük Koşulu
```django
{% if all_campaigns.count > 1 %}
```
- Sadece **birden fazla kampanya** varsa gösterilir
- Tek kampanya varsa bu bölüm render edilmez

### Container Yapısı
```html
<div class="bg-gradient-to-r from-gray-50 to-white py-6 border-y border-gray-100">
    <div class="container max-w-md mx-auto px-4">
        <div class="overflow-x-auto no-scrollbar -mx-4 px-4">
            <div class="flex gap-3 pb-2">
                <!-- Kampanya kartları buraya -->
            </div>
        </div>
    </div>
</div>
```

**Özellikler:**
- **Arka plan:** Gradient (gri-beyaz geçişli)
- **Max genişlik:** `max-w-md` (448px)
- **Yatay scroll:** Mobilde kaydırılabilir (`overflow-x-auto`)
- **Scrollbar gizli:** `.no-scrollbar` sınıfı

---

## 🎴 Kart Yapısı Detayları

### 1. 📐 Boyutlar ve Layout

```html
<a href="{% url 'campaign_detail' c.slug %}" 
   class="flex-none w-[170px] relative group">
```

| Özellik | Değer | Açıklama |
|---------|-------|----------|
| **Genişlik** | `w-[170px]` | Sabit genişlik |
| **Flex** | `flex-none` | Küçülmez/büyümez |
| **Pozisyon** | `relative` | Absolute child'lar için |
| **Grup** | `group` | Hover efektleri için |

### 2. 🎨 Kart Container

```html
<div class="bg-white rounded-2xl p-4 border-2 transition-all relative overflow-hidden
            {% if c.id == campaign.id %}
            border-brand-pink shadow-lg shadow-pink-100
            {% else %}
            border-gray-200 hover:border-brand-pink hover:shadow-md
            {% endif %}">
```

#### Aktif (Seçili) Kampanya:
```css
border-brand-pink        /* Pembe border */
shadow-lg               /* Büyük gölge */
shadow-pink-100         /* Pembe tonlu gölge */
```

#### Pasif (Seçili Değil) Kampanya:
```css
border-gray-200         /* Gri border */
hover:border-brand-pink /* Hover'da pembe */
hover:shadow-md         /* Hover'da orta gölge */
```

**Sabit Özellikler:**
- `bg-white` - Beyaz arka plan
- `rounded-2xl` - Çok yuvarlatılmış köşeler
- `p-4` - 16px padding (her yönden)
- `border-2` - 2px kalın border
- `transition-all` - Tüm özelliklerde animasyon
- `relative` - Badge için
- `overflow-hidden` - Taşan içeriği gizle

---

## 🏷️ Badge Sistemi

### Aktif Kampanya Badge'i

```html
{% if c.id == campaign.id %}
<div class="absolute top-0 right-0 
            bg-gradient-to-br from-brand-pink to-brand-purple 
            text-white text-[9px] font-bold 
            px-3 py-1 
            rounded-bl-xl rounded-tr-xl">
    Seçili
</div>
{% endif %}
```

**Özellikler:**
- **Pozisyon:** Sağ üst köşe (`top-0 right-0`)
- **Arka plan:** Pembe-mor gradient
- **Font:** 9px, bold, beyaz
- **Padding:** 12px yatay, 4px dikey
- **Border radius:** Sol alt ve sağ üst yuvarlatılmış
- **Metin:** "Seçili"

**Görsel Etki:** Üçgen şeklinde köşe rozeti 🏷️

---

## 📝 İçerik Yapısı

### 1. Başlık

```html
<h3 class="font-bold text-gray-800 text-xs mb-3 line-clamp-2 h-8 leading-tight">
    {{ c.title }}
</h3>
```

| Özellik | Değer | Açıklama |
|---------|-------|----------|
| **Font boyutu** | `text-xs` (12px) | Küçük başlık |
| **Font ağırlığı** | `font-bold` | Kalın |
| **Renk** | `text-gray-800` | Koyu gri |
| **Margin** | `mb-3` | Alt boşluk 12px |
| **Satır sınırı** | `line-clamp-2` | Max 2 satır |
| **Yükseklik** | `h-8` | Sabit 32px |
| **Line height** | `leading-tight` | Sıkı satır aralığı |

**Not:** Sabit yükseklik sayesinde tüm kartlar aynı hizada kalır ✅

### 2. Ürün Sayısı

```html
<div class="flex items-center gap-1.5 mb-2 text-[10px] text-gray-500">
    <svg class="w-3.5 h-3.5 text-brand-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
    </svg>
    <span>{{ c.min_quantity }} Ürün Paketi</span>
</div>
```

**Bileşenler:**
- 📦 **Icon:** 14x14px alışveriş çantası (pembe)
- 📝 **Metin:** "3 Ürün Paketi" formatında
- **Font:** 10px, gri

**Gap:** 6px icon ile metin arası

### 3. Fiyat Bölümü

```html
<div class="flex items-baseline justify-between mt-3 pt-3 border-t border-gray-100">
    <span class="text-[10px] text-gray-400 font-medium">Toplam</span>
    <div class="flex flex-col items-end">
        <span class="text-xl font-black 
                     {% if c.id == campaign.id %}text-brand-pink
                     {% else %}text-gray-800{% endif %}">
            {{ c.price|floatformat:0 }}₺
        </span>
        {% if c.id != campaign.id %}
        <span class="text-[9px] text-gray-400">Ücretsiz Kargo</span>
        {% endif %}
    </div>
</div>
```

**Layout:**
```
┌────────────────────────┐
│ Toplam        1899₺    │
│               ↑        │
│            Ücretsiz    │
│              Kargo     │
└────────────────────────┘
```

**Fiyat Renk Mantığı:**
- **Aktif kampanya:** `text-brand-pink` (pembe - vurgulu)
- **Pasif kampanya:** `text-gray-800` (gri - normal)

**"Toplam" Label:**
- Font: 10px, orta kalınlık
- Renk: Açık gri (`text-gray-400`)

**Fiyat:**
- Font: 20px (`text-xl`), ekstra kalın (`font-black`)
- Format: Ondalıksız (örn: 1899₺)

**"Ücretsiz Kargo":**
- Sadece **pasif** kampanyalarda gösterilir
- Font: 9px, açık gri
- Fiyatın altında sağ hizada

**Üst border:**
- `border-t border-gray-100` - İnce gri çizgi
- `mt-3 pt-3` - Hem margin hem padding (toplamda 24px boşluk)

---

## ✨ Hover Efektleri

### Pasif Kampanyalar için Glow Efekti

```html
{% if c.id != campaign.id %}
<div class="absolute inset-0 
            bg-gradient-to-br from-brand-pink/5 to-brand-purple/5 
            rounded-2xl 
            opacity-0 group-hover:opacity-100 
            transition-opacity 
            pointer-events-none">
</div>
{% endif %}
```

**Özellikler:**
- **Pozisyon:** Tüm kartı kaplar (`inset-0`)
- **Arka plan:** Çok hafif pembe-mor gradient (5% opacity)
- **Başlangıç:** Görünmez (`opacity-0`)
- **Hover:** Görünür (`group-hover:opacity-100`)
- **Animasyon:** Opacity geçişi
- **Etkileşim:** Tıklamayı engellmez (`pointer-events-none`)

**Sadece aktif olmayan kampanyalarda gösterilir** ✅

---

## 🎯 Responsive Davranış

### Mobil (< 448px)
```html
<div class="overflow-x-auto no-scrollbar -mx-4 px-4">
    <div class="flex gap-3 pb-2">
```

- **Yatay scroll:** Kartlar yatay sıralanır
- **Scrollbar gizli:** Temiz görünüm
- **Negative margin:** `-mx-4` ile kenar boşluğu kaldırılır
- **Padding:** `px-4` ile tekrar eklenir (scroll için alan)
- **Gap:** 12px kartlar arası

**Kart genişliği:** 170px sabit

### Masaüstü
- Container max genişlik: 448px
- Kartlar hala yatay sıralanır
- Scroll aktif (çok kampanya varsa)

---

## 📊 Kart Durumları Karşılaştırması

### Aktif (Seçili) Kampanya
```
┌────────────────────────┐
│         (Seçili) 🏷️    │
│                        │
│  3 Adet Tesettür       │
│  Alt-Üst Takım         │
│                        │
│  📦 3 Ürün Paketi      │
│                        │
│  ─────────────────     │
│  Toplam      1899₺     │
│              (pembe)   │
└────────────────────────┘

Border: Pembe, 2px
Shadow: Büyük, pembe tonlu
Glow: YOK
```

### Pasif Kampanya (Normal)
```
┌────────────────────────┐
│                        │
│  5 Adet Tesettür       │
│  Alt-Üst Takım         │
│                        │
│  📦 5 Ürün Paketi      │
│                        │
│  ─────────────────     │
│  Toplam      2999₺     │
│              (gri)     │
│         Ücretsiz Kargo │
└────────────────────────┘

Border: Gri, 2px
Shadow: YOK
Glow: YOK
```

### Pasif Kampanya (Hover)
```
┌────────────────────────┐
│    ✨ (hafif glow) ✨   │
│  5 Adet Tesettür       │
│  Alt-Üst Takım         │
│                        │
│  📦 5 Ürün Paketi      │
│                        │
│  ─────────────────     │
│  Toplam      2999₺     │
│              (gri)     │
│         Ücretsiz Kargo │
└────────────────────────┘

Border: Pembe, 2px (transition)
Shadow: Orta (transition)
Glow: Görünür (transition)
```

---

## 🎨 Renk Paleti

| Element | Aktif | Pasif | Hover |
|---------|-------|-------|-------|
| **Border** | `brand-pink` | `gray-200` | `brand-pink` |
| **Shadow** | `shadow-lg shadow-pink-100` | - | `shadow-md` |
| **Badge BG** | Gradient (pembe-mor) | - | - |
| **Başlık** | `gray-800` | `gray-800` | `gray-800` |
| **Ürün Sayısı** | `gray-500` | `gray-500` | `gray-500` |
| **Icon** | `brand-pink` | `brand-pink` | `brand-pink` |
| **Fiyat** | `brand-pink` | `gray-800` | `gray-800` |
| **"Toplam"** | `gray-400` | `gray-400` | `gray-400` |
| **"Ücretsiz Kargo"** | - | `gray-400` | `gray-400` |
| **Glow** | - | - | `pink/purple 5%` |

---

## 📏 Spacing Sistemi

```
Card Container:
  - Padding: p-4 (16px tüm yönler)
  - Border: 2px

Badge (Aktif):
  - Padding: px-3 py-1 (12px-4px)

Başlık:
  - Margin bottom: mb-3 (12px)
  - Height: h-8 (32px)

Ürün Sayısı:
  - Margin bottom: mb-2 (8px)
  - Gap: gap-1.5 (6px)

Fiyat Bölümü:
  - Margin top: mt-3 (12px)
  - Padding top: pt-3 (12px)
  - Total space: 24px

Kartlar Arası:
  - Gap: gap-3 (12px)
```

---

## 🔧 Teknik Detaylar

### Django Template Logic

```django
{% for c in all_campaigns %}
    <!-- Her kampanya için döngü -->
    
    {% if c.id == campaign.id %}
        <!-- Aktif kampanya durumu -->
    {% else %}
        <!-- Pasif kampanya durumu -->
    {% endif %}
{% endfor %}
```

**Değişkenler:**
- `all_campaigns` - Tüm kampanyalar listesi
- `campaign` - Şu anki aktif kampanya
- `c` - Loop içindeki kampanya

### Link Yapısı
```html
<a href="{% url 'campaign_detail' c.slug %}">
```
- Kampanyaya tıklandığında ilgili kampanya detay sayfasına gider
- URL: `/campaigns/{slug}/`

---

## ⚡ Performans Özellikleri

### Animasyonlar
```css
transition-all          /* Tüm CSS özellikleri animasyonlu */
transition-opacity      /* Sadece opacity (glow için) */
```

**GPU Accelerated:** Border ve shadow değişimleri modern tarayıcılarda hızlıdır.

### Scroll Performans
```css
overflow-x-auto        /* Native scroll */
-webkit-overflow-scrolling: touch  /* Smooth scroll iOS'ta */
```

---

## 🐛 Potansiyel Sorunlar

### 1. Scrollbar Gizleme
`.no-scrollbar` sınıfı CSS'te tanımlı olmalı:
```css
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
```

### 2. Sabit Genişlik
- `w-[170px]` çok küçük ekranlarda sorun olabilir
- Min width kontrolü yapılabilir

### 3. Line Clamp Support
```css
line-clamp-2
```
- Eski tarayıcılarda çalışmayabilir
- Fallback gerekebilir

---

## 💡 İyileştirme Önerileri

### 1. Responsive Width
```html
<!-- Önerilen -->
<a class="flex-none w-[170px] sm:w-[200px] md:w-[220px]">
```

### 2. Keyboard Navigation
```html
<!-- Erişilebilirlik -->
<a tabindex="0" 
   aria-label="3 ürün paketi kampanya, 1899 TL"
   role="button">
```

### 3. Touch Feedback
```html
<!-- Mobil için -->
<a class="active:scale-95 transition-transform">
```

### 4. Loading State
```html
<!-- Skeleton loading -->
<div class="animate-pulse bg-gray-200 rounded-2xl h-48"></div>
```

### 5. Badge Animasyonu
```html
<!-- Badge için -->
<div class="animate-bounce">Seçili</div>
```

### 6. Kompakt Mod
Ekrandan daha az yer kaplaması için:
```diff
- <div class="bg-white rounded-2xl p-4">
+ <div class="bg-white rounded-xl p-3">

- <h3 class="text-xs">
+ <h3 class="text-[11px]">

- <span class="text-xl">
+ <span class="text-lg">
```

---

## 🎯 Kullanım Senaryoları

### Senaryo 1: Tek Kampanya
```django
{% if all_campaigns.count > 1 %}
```
❌ Bölüm render edilmez  
✅ Kullanıcı direkt ürün seçimine geçer

### Senaryo 2: 2-3 Kampanya
✅ Kartlar yan yana görünür  
✅ Scroll gerekmez  
✅ Optimal deneyim

### Senaryo 3: 4+ Kampanya
✅ Yatay scroll aktif  
⚠️ Kullanıcı kaydırmalı  
💡 Scroll indicator eklenebilir

---

## 📊 Özet Tablo

| Özellik | Değer | Not |
|---------|-------|-----|
| **Kart Genişliği** | 170px | Sabit |
| **Kart Padding** | 16px | Tüm yönler |
| **Border** | 2px | Aktif: pembe, Pasif: gri |
| **Border Radius** | rounded-2xl | Çok yuvarlatılmış |
| **Başlık Font** | 12px | Bold, 2 satır max |
| **Fiyat Font** | 20px | Extra bold |
| **Kartlar Arası** | 12px | Gap |
| **Hover Efekt** | Glow + Border | Sadece pasif |

---

**Genel Değerlendirme:** ⭐⭐⭐⭐ (4/5)

### ✅ Güçlü Yönler:
- Clean ve modern tasarım
- Görsel hiyerarşi net
- Aktif/pasif durum farkı belirgin
- Responsive (yatay scroll)
- Smooth animasyonlar

### ⚠️ İyileştirilebilir:
- Mobilde daha kompakt olabilir
- Erişilebilirlik iyileştirmesi
- Touch feedback yoktur
- Scroll indicator eksik
