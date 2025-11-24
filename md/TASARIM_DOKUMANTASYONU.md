# İFİ Butik - Tasarım Dokümantasyonu

## Genel Bakış

İFİ Butik, modern e-ticaret deneyimi sunan, mobil-öncelikli bir kampanya bazlı satış platformudur. Tasarım, Alpine.js, HTMX ve Tailwind CSS teknolojileri kullanılarak geliştirilmiştir.

---

## Teknoloji Stack

### Frontend Framework'leri
- **Tailwind CSS**: Utility-first CSS framework
- **Alpine.js**: Lightweight reactive JavaScript framework
- **HTMX**: AJAX, CSS Transitions, WebSockets için minimal framework

### Font
- **Google Fonts - Inter**: Modern, okunabilir sans-serif font

### Renk Paleti
```css
brand-pink: #E91E63
brand-purple: #9C27B0
brand-coral: #FF6B6B
```

---

## Sayfa Yapısı

### 1. Header (Sabit Üst Bar)
**Dosya:** `templates/base.html` ve `templates/campaigns/detail.html`

**Özellikler:**
- Glassmorphism efekti ile yarı saydam arka plan
- Sticky positioning (top: 0, z-index: 50)
- Gradient text efekti ile marka adı
- Backdrop blur efekti

**Kod Örneği:**
```html
<div class="py-4 text-center border-b border-white/20 sticky top-0 z-50 glass-white shadow-lg">
    <h1 class="text-2xl font-black tracking-wider uppercase gradient-text animate-fade-in">
        İFİ BUTİK
    </h1>
</div>
```

---

### 2. Banner Bölümü

**Özellikler:**
- Minimum yükseklik: 25rem (400px)
- Parallax efekt (hover'da scale-105)
- Gradient overlay (bottom-to-top)
- Floating badge (sağ üst köşe)

**Banner Image:**
- Object-fit: cover
- Transform: transition-transform duration-700
- Group hover efekti

**Floating Badge:**
- Gradient background (red-500 to brand-pink)
- Glassmorphism (backdrop-blur + bg-white/10)
- Float animation
- İçerik: Kargo bedava + ürün sayısı

---

### 3. Kayan Yazı Şeridi (Marquee)

**Teknoloji:** Alpine.js ile requestAnimationFrame

**Animasyon Özellikleri:**
```javascript
position: 0          // Başlangıç pozisyonu
speed: 0.5          // Kayma hızı (pixel/frame)
isPaused: false     // Hover durumu
```

**Çalışma Prensibi:**
1. Her frame'de position değeri azaltılır
2. İlk setin genişliği hesaplanır
3. Bu genişliğe ulaşınca position sıfırlanır
4. Seamless loop oluşur

**Gradient Background:**
```css
bg-gradient-to-r from-brand-pink via-brand-purple to-brand-pink
```

**İçerik Öğeleri:**
- Kampanya başlığı (onay ikonu)
- Ürün sayısı (sepet ikonu)
- Ücretsiz kargo (kamyon ikonu)
- Fiyat bilgisi (artı ikonu)
- İade garantisi (kalp ikonu)

**Hover Davranışı:**
- Mouse enter: Animasyon durur
- Mouse leave: Animasyon devam eder

---

### 4. Kampanya Seçenekleri Section

**Layout:**
- Gradient background (gray-50 to white)
- Horizontal scroll (overflow-x-auto)
- No scrollbar style

**Başlık Bölümü:**
- Gradient ikon container (8x8, rounded-lg)
- Font-black başlık
- Kampanya sayısı badge'i

**Kampanya Kartları:**
- Genişlik: 170px
- Background: white
- Border: 2px (aktif: brand-pink, diğer: gray-200)
- Border-radius: 2xl (16px)
- Shadow: Aktif kartta pink-100 shadow

**Aktif Kampanya Badge:**
- Position: absolute top-0 right-0
- Gradient background
- Rounded-bl-xl rounded-tr-xl
- Text: "Seçili"

**Hover Efekti:**
- Border color change
- Gradient glow overlay
- Smooth transitions

---

### 5. Ürün Listesi

**Grid Layout:**
```css
grid-cols-2
gap-x-4  /* Yatay boşluk: 16px */
gap-y-7  /* Dikey boşluk: 28px */
```

**Ürün Kartı Özellikleri:**
- Background: white
- Border-radius: 2xl
- Shadow-lg
- Transform: hover scale-105
- Transition duration: 300ms

**3D Tilt Efekti (Alpine.js):**
```javascript
x-data="{ tilt: { x: 0, y: 0 } }"
@mousemove="// Mouse pozisyonuna göre hesaplama"
@mouseleave="tilt = { x: 0, y: 0 }"
:style="transform: perspective(1000px) rotateY(${tilt.x}deg) rotateX(${tilt.y}deg) scale(1.05)"
```

**İndirim Rozeti:**
- Position: absolute top-2 left-2
- Gradient: brand-pink to brand-purple
- Animate-pulse
- Text: "%30 İndirim"

**Ürün Görseli:**
- Aspect ratio: 3/4
- Object-fit: cover
- Group hover: scale-110
- Hover overlay: gradient bottom-to-top

**Güvenli Alışveriş Badge (Alpine.js Animasyonlu):**
```javascript
badges: ['Güvenli Alışveriş', 'Ücretsiz Kargo', 'Hızlı Teslimat']
currentBadge: 0
setInterval(() => { currentBadge = (currentBadge + 1) % badges.length }, 2500)
```
- Dikey kayma animasyonu
- translate-y ile geçişler
- 2.5 saniyede bir değişim

**Sosyal Kanıt Animasyonu:**
```javascript
texts: [
    'X kişinin sepetinde, kaçırma!',
    '24 saatte X kişi inceledi!',
    'Son 1 saatte X adet satıldı!'
]
```
- Yukarı kayma animasyonu
- 3 saniyede bir değişim
- Farklı renkler (orange, green, red)

**Ürün Özellikleri:**
- Font-size: 9px
- Text-gray-400
- Border-top ile ayrım
- Space-y-0.5

**Sepete Ekle Butonu:**
- Gradient background (brand-pink to brand-purple)
- Ripple effect (Alpine.js directive: x-ripple)
- Active scale: 95%
- Disabled state: gray-100 background

---

### 6. Seçili Ürünler Bölümü

**Başlık:**
- Gradient ikon container (10x10, rounded-full)
- Font-black başlık

**Ürün Kutuları:**
- Glassmorphism (glass-white)
- Rounded-2xl
- Padding: 3
- Space-y: 3
- Animate-slide-up
- Animation-delay: i * 0.1s (sıralı animasyon)

**Boş Slot:**
- Gradient background (gray-100 to gray-200)
- Pulse-glow animasyonu
- Gradient text numara

**Dolu Slot:**
- Border: 2px brand-pink
- Shadow-lg
- Scale: 1.02
- Ürün görseli rounded-xl

**Kaldır Butonu:**
- Hover: text-red-500
- Transition-colors
- Çöp kutusu ikonu

---

### 7. Beden Seçimi

**Görünürlük:**
```javascript
x-show="totalSelected >= minQty"
x-cloak
x-transition
```

**Grid Layout:**
```css
grid-cols-2
gap-3
```

**Beden Butonları:**
- Border: 2px
- Rounded-xl
- Padding: py-3.5 px-2
- Ripple effect (x-ripple)
- Active scale: 95%

**Seçili State:**
- Background: gradient (brand-pink to brand-purple)
- Text: white
- Shadow-lg
- Transform: scale-105

**Seçili Değil State:**
- Border: gray-200
- Text: gray-600
- Background: white
- Hover: border-gray-300

**Onay İkonu:**
- X-transition ile giriş animasyonu
- Scale: 0 to 100
- Duration: 300ms
- Ease-out

---

### 8. Teslimat Bilgileri Formu

**Container:**
- Glassmorphism (glass-white)
- Rounded-2xl
- Shadow-lg
- Padding: 6

**Başlık:**
- Gradient ikon container (10x10)
- Font-black

**Form Input'ları:**
- Rounded-xl
- Border: gray-200
- Focus: border-brand-pink + ring-2 ring-pink-200
- Padding: py-3.5 px-4
- Font-size: sm
- Transition-all
- Hover: border-gray-300

**HTMX Cascading Selects:**
```html
<select name="city" 
    hx-get="/get-districts/" 
    hx-target="#district-select">

<select name="district" 
    hx-get="/get-neighborhoods/" 
    hx-include="[name='city']" 
    hx-target="#neighborhood-select">
```

**Sipariş Özeti:**
- Background: gradient (brand-pink/10 to brand-purple/10)
- Border: brand-pink/20
- Rounded-2xl
- Padding: 5

**Fiyat Gösterimi:**
- Font-size: 2xl
- Font-weight: black
- Gradient-text

**Siparişi Tamamla Butonu:**
- Gradient background (brand-pink to brand-purple)
- Rounded-2xl
- Shadow-2xl
- Hover: scale-102
- Active: scale-98
- Animated gradient overlay
- Loading spinner (x-show="submitting")

---

### 9. SSS Bölümü

**Başlık:**
- Gradient ikon container (10x10)
- Font-black

**Accordion Kartları:**
- Glassmorphism (glass-white)
- Rounded-2xl
- Border: white/20
- Hover: shadow-lg

**Buton:**
- Padding: 4
- Group hover: text-brand-pink
- Arrow icon rotate animasyonu

**İçerik:**
- X-collapse directive
- Border-top
- Smooth açılma/kapanma

---

### 10. Footer

**Background:**
- Gradient: gray-50 via white to brand-pink/5
- Padding: py-12

**Özellik Kartları:**
- Grid: 2 cols (mobile), 4 cols (desktop)
- Gap: 8

**İkon Container:**
- Gradient background (her biri farklı renk)
- Boyut: 16x16
- Rounded-2xl
- Shadow-lg
- Group hover: scale-110

**Marka Bölümü:**
- Border-top
- Gradient-text başlık
- Font-size: 2xl
- Font-weight: black

---

## Animasyonlar ve Efektler

### CSS Keyframe Animasyonları

**Gradient:**
```css
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
```

**Float:**
```css
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
```

**Slide Up:**
```css
@keyframes slideUp {
    0% { transform: translateY(20px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
}
```

**Fade In:**
```css
@keyframes fadeIn {
    0% { opacity: 0; }
    100% { opacity: 1; }
}
```

**Pulse Glow:**
```css
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(233, 30, 99, 0.4); }
    50% { box-shadow: 0 0 0 10px rgba(233, 30, 99, 0); }
}
```

**Shimmer:**
```css
@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}
```

**Ripple:**
```css
@keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
}
```

### Alpine.js Directives

**x-ripple:**
Butonlara tıklandığında ripple efekti ekler. requestAnimationFrame kullanarak smooth animasyon sağlar.

**x-cloak:**
Alpine.js yüklenene kadar elementi gizler.

**x-transition:**
Elemanların girişi/çıkışı için smooth geçişler.

**x-collapse:**
Accordion benzeri açılma/kapanma efekti.

---

## Glassmorphism Efektleri

### Glass (Yarı Saydam)
```css
.glass {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}
```

### Glass-White (Daha Opak)
```css
.glass-white {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
}
```

---

## Gradient Kullanımları

### Text Gradient
```css
.gradient-text {
    background: linear-gradient(135deg, #E91E63 0%, #9C27B0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
```

### Background Gradients
- `from-brand-pink to-brand-purple`
- `from-red-500 to-brand-pink`
- `from-brand-pink via-brand-purple to-brand-pink`
- `from-gray-50 via-white to-brand-pink/5`

---

## Responsive Tasarım

### Breakpoints
Tailwind CSS default breakpoints:
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px
- 2xl: 1536px

### Mobile-First Approach
Tüm tasarım mobile-first prensibiyle yapılmıştır. Önce mobil için optimize edilmiş, sonra büyük ekranlar için genişletilmiştir.

### Container Max Width
```css
container max-w-md mx-auto
```
Maksimum genişlik: 448px (md breakpoint)

---

## Performance Optimizasyonları

### GPU Acceleration
```css
will-change: transform;
transform: translateZ(0);
-webkit-transform: translateZ(0);
backface-visibility: hidden;
```

### requestAnimationFrame
JavaScript animasyonları için native browser timing kullanılır. 60 FPS smooth animasyon garantisi.

### Lazy Loading
Görseller için lazy loading attribute kullanılabilir:
```html
<img loading="lazy" src="...">
```

---

## Accessibility (Erişilebilirlik)

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

### Semantic HTML
- Proper heading hierarchy (h1, h2, h3)
- Alt text for images
- ARIA labels where necessary

### Keyboard Navigation
Tüm interaktif elementler klavye ile erişilebilir.

---

## Kod Organizasyonu

### Dosya Yapısı
```
templates/
├── base.html              # Ana şablon, CSS ve JS imports
├── campaigns/
│   ├── detail.html        # Kampanya detay sayfası
│   └── no_campaign.html   # Kampanya yok sayfası
└── orders/
    └── success.html       # Sipariş başarı sayfası
```

### CSS Organizasyonu
- Global styles: `base.html` içinde
- Component-specific: Inline Tailwind classes
- Custom animations: `<style>` tag içinde keyframes

### JavaScript Organizasyonu
- Alpine.js components: x-data ile inline
- Global utilities: `<script>` tag içinde
- Directives: Alpine.js directive sistemi

---

## Best Practices Kullanımı

### 1. Transform Kullanımı
`left` ve `top` yerine `transform` kullanımı:
```css
/* Kötü */
left: 100px;

/* İyi */
transform: translateX(100px);
```

### 2. translate3d Kullanımı
2D yerine 3D transforms GPU acceleration için:
```css
transform: translate3d(50px, 0, 0);
```

### 3. will-change
Animasyonlu elementlerde:
```css
will-change: transform;
```

### 4. Semantic Class Names
Tailwind utility-first ama mantıklı component isimleri:
- `glass-white`
- `gradient-text`
- `animate-marquee`

### 5. Alpine.js Best Practices
- x-data için mantıklı state isimleri
- requestAnimationFrame kullanımı
- Cleanup işlemleri

---

## Renk Şeması Detayları

### Primary Colors
```
Brand Pink:   #E91E63 (RGB: 233, 30, 99)
Brand Purple: #9C27B0 (RGB: 156, 39, 176)
Brand Coral:  #FF6B6B (RGB: 255, 107, 107)
```

### Neutral Colors
```
Gray-50:  #F9FAFB
Gray-100: #F3F4F6
Gray-200: #E5E7EB
Gray-400: #9CA3AF
Gray-600: #4B5563
Gray-800: #1F2937
```

### Semantic Colors
```
Green (Success): #4CAF50
Red (Error):     #EF4444
Orange (Warning): #F59E0B
Blue (Info):     #3B82F6
```

---

## Tipografi Detayları

### Font Weights
```
font-normal:     400
font-medium:     500
font-semibold:   600
font-bold:       700
font-black:      900
```

### Font Sizes (Özel)
```
text-[9px]:  9px   (Ürün detayları)
text-[10px]: 10px  (Badge'ler)
text-[11px]: 11px  (Buton metinleri)
```

### Line Heights
```
leading-tight:  1.25
leading-normal: 1.5
leading-relaxed: 1.75
```

---

## Shadow Sistemi

### Standard Shadows
```
shadow-sm:  0 1px 2px rgba(0,0,0,0.05)
shadow:     0 1px 3px rgba(0,0,0,0.1)
shadow-md:  0 4px 6px rgba(0,0,0,0.1)
shadow-lg:  0 10px 15px rgba(0,0,0,0.1)
shadow-xl:  0 20px 25px rgba(0,0,0,0.1)
shadow-2xl: 0 25px 50px rgba(0,0,0,0.25)
```

### Colored Shadows
```
shadow-pink-100:  Pink tinted shadow
shadow-pink-200:  Stronger pink shadow
```

---

## Border Radius Sistemi

```
rounded-lg:   8px   (Standard)
rounded-xl:   12px  (Medium)
rounded-2xl:  16px  (Large)
rounded-3xl:  24px  (Extra large)
rounded-full: 9999px (Circle)
```

---

## Spacing Sistemi

### Padding/Margin Scale
```
1:  4px
2:  8px
3:  12px
4:  16px
5:  20px
6:  24px
8:  32px
```

### Gap Scale (Grid/Flex)
```
gap-2:  8px
gap-3:  12px
gap-4:  16px
gap-5:  20px
```

---

## Z-Index Layering

```
z-0:   0   (Default)
z-10:  10  (Dropdown overlays)
z-20:  20  (Modal backdrops)
z-30:  30  (Modal content)
z-40:  40  (Tooltips)
z-50:  50  (Header/Navigation)
```

---

## Form Styling

### Input States
```css
/* Default */
border-gray-200

/* Focus */
focus:border-brand-pink 
focus:ring-2 
focus:ring-pink-200

/* Hover */
hover:border-gray-300

/* Disabled */
disabled:bg-gray-100
disabled:cursor-not-allowed
```

### Select Styling
```css
rounded-xl
py-3.5 px-4
text-sm
bg-white
transition-all
```

---

## Button Styling Variants

### Primary Button
```html
<button class="
    bg-gradient-to-r 
    from-brand-pink 
    to-brand-purple 
    text-white 
    rounded-2xl 
    px-10 py-4 
    font-bold 
    shadow-lg 
    hover:shadow-2xl 
    transform 
    hover:scale-105 
    active:scale-95 
    transition-all
">
```

### Secondary Button
```html
<button class="
    bg-white 
    text-brand-pink 
    border-2 
    border-brand-pink 
    rounded-xl 
    px-6 py-3 
    font-bold 
    hover:bg-brand-pink 
    hover:text-white 
    transition-all
">
```

### Disabled Button
```html
<button class="
    bg-gray-100 
    text-gray-400 
    cursor-not-allowed 
    rounded-xl 
    px-6 py-3
" disabled>
```

---

## Icon System

### Icon Sizes
```
w-3 h-3:  12px (Çok küçük)
w-4 h-4:  16px (Küçük)
w-5 h-5:  20px (Normal)
w-6 h-6:  24px (Orta)
w-8 h-8:  32px (Büyük)
```

### Icon Colors
- `text-brand-pink`: Primary actions
- `text-green-500`: Success states
- `text-red-500`: Danger/Delete
- `text-gray-400`: Inactive states
- `text-white`: On colored backgrounds

---

## Loading States

### Spinner Animation
```html
<svg class="animate-spin h-5 w-5" ...>
    <circle class="opacity-25" ...></circle>
    <path class="opacity-75" ...></path>
</svg>
```

### Skeleton Loader
```css
.shimmer {
    background: linear-gradient(
        90deg, 
        #f0f0f0 25%, 
        #e0e0e0 50%, 
        #f0f0f0 75%
    );
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}
```

---

## Toast/Notification Pattern

### Success Toast
```html
<div class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4">
    <div class="flex">
        <svg class="w-6 h-6">...</svg>
        <p>İşlem başarılı!</p>
    </div>
</div>
```

### Error Toast
```html
<div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4">
    <div class="flex">
        <svg class="w-6 h-6">...</svg>
        <p>Bir hata oluştu!</p>
    </div>
</div>
```

---

## Image Optimization

### Aspect Ratios
```
aspect-[3/4]:  Ürün görselleri
aspect-square: Avatar/profile images
aspect-video:  Banner images
```

### Object Fit
```
object-cover:    Crop ve fill
object-contain:  Fit inside
```

---

## Scroll Behaviors

### No Scrollbar
```css
.no-scrollbar::-webkit-scrollbar {
    display: none;
}
.no-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
}
```

### Smooth Scroll
```css
.scroll-smooth {
    scroll-behavior: smooth;
}
```

---

## Utility Classes

### Custom Utilities
```css
.text-shadow: text-shadow: 0 2px 4px rgba(0,0,0,0.1)
.text-shadow-lg: text-shadow: 0 4px 6px rgba(0,0,0,0.3)
.glow-pink: text-shadow: 0 0 20px rgba(233, 30, 99, 0.5)
```

---

## Component Composition Examples

### Card Component
```
- Glass background
- Rounded corners (2xl)
- Shadow (lg)
- Padding (4-6)
- Hover effects
- Transition (all)
```

### Badge Component
```
- Small size
- Rounded-full
- Gradient background
- Font-bold
- Uppercase
- Tracking-wide
```

### Icon Button
```
- Circular (rounded-full)
- Size: w-10 h-10
- Center alignment (flex items-center justify-center)
- Gradient background
- Hover scale
```

---

## Browser Support

### Minimum Requirements
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Fallbacks
- CSS Grid: Flexbox fallback
- Backdrop-filter: Solid background fallback
- Custom properties: Static values fallback

---

## Deployment Considerations

### Production Build
1. Tailwind CSS purge kullan
2. Minify CSS/JS
3. Compress images (WebP)
4. Enable Gzip/Brotli
5. CDN kullan (fonts, libraries)

### Performance Checklist
- [ ] Image optimization
- [ ] Lazy loading
- [ ] Code splitting
- [ ] Minification
- [ ] Caching headers
- [ ] CDN setup

---

## Maintenance Guide

### Renk Değiştirme
`templates/base.html` içinde tailwind.config kısmını düzenle.

### Animasyon Hızı Değiştirme
Keyframe animation sürelerini ve Alpine.js timing değerlerini ayarla.

### Font Değiştirme
Google Fonts import linkini değiştir ve font-family'yi güncelle.

### Spacing Ayarları
Tailwind'in default spacing scale'ini kullan, gerekirse custom değerler ekle.

---

## Versiyon Bilgisi

**Tailwind CSS:** 3.x (CDN)
**Alpine.js:** 3.13.3
**HTMX:** 1.9.10
**Font:** Inter (Google Fonts)

---

## Katkıda Bulunanlar İçin Notlar

### CSS Yazım Kuralları
1. Tailwind utility classes kullan
2. Custom CSS minimum tut
3. Inline styles kaçın
4. Component bazlı düşün

### JavaScript Yazım Kuralları
1. Alpine.js directive'leri kullan
2. Vanilla JS minimum tut
3. requestAnimationFrame kullan
4. Event delegation kullan

### Naming Conventions
1. Semantic class names
2. BEM notation avoid
3. Descriptive Alpine.js data properties
4. Clear function names

---

Bu dokümantasyon, İFİ Butik projesinin tüm tasarım detaylarını içermektedir. Güncellemeler için bu dosyayı referans alın.

