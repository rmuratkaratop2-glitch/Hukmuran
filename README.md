# HÜKMÜMRAN — Python Sürümü (pygame)

Victoria 3 esinli, ülke yönetimi odaklı büyük strateji oyunu. Orijinal tarayıcı
sürümünden (HTML/JS) Python/pygame'e taşınmıştır ve **yeni bir yetenek (güç)
sistemi** eklenmiştir. Dönem: 1836–1936. Arayüz tamamen Türkçedir.

## Çalıştırma

1. Python 3.10+ kurulu olmalı.
2. pygame kurun: `python -m pip install pygame`
3. Oyunu başlatın: `python main.py`

> Tüm dosyalar (data.py, engine.py, ui.py, main.py) aynı klasörde kalmalı.

## Oynanış

- **Amaç:** 1936'da en yüksek skor. Skor = GSYH + refah + düşük radikalizm +
  eyalet sayısı + hukuk ilerlemesi + teknoloji + prestij.
- **Ekonomi:** Eyaletler mal üretir → ulusal pazarda fiyat oluşur → binalar işçi
  alır → refah ve tabaka dengesi değişir → vergi/harcama bütçeyi belirler.
- **Siyaset:** 7 çıkar grubu (Aşiret, Ordu, Aydın, Sermaye, Sendika, Ruhani,
  Memur) hukuk reformlarını destekler ya da engeller (7 kategori, kademeli).
- **Teknoloji:** 24 teknoloji, 3 kol (sanayi/toplum/ordu); aynı anda 1 araştırma.
- **Dış politika:** İlişki, ittifak, hudut talebi, savaş ilanı; savaşta strateji
  seçimi (Yıldırma / Kuşatma / İnkitab) ve beyaz barış.
- **Olaylar:** 26 dönem olayı + 3 yetenek-sinerjili yeni olay.
- **Harita:** 9 ülke, 39 eyalet stilize haritada; eyalete tıklayınca inşaat paneli.

## YENİ: Yetenek Sistemi (Devlet Başkanı Güçleri)

Oyunun orijinalinde bulunmayan, bu sürüme eklenen aktif güç sistemi:

- **10 yetenek**, 4 kategori: Askeri (3), Ekonomi (3), Toplum (2), Diplomasi (2).
- Kaynak: **altın + bekleme süresi** (puan havuzu yok); **ayda en fazla 1 yetenek**.
- Kilit koşulları (ör. prestij eşiği) sağlanmazsa buton pasiftir ve **sebebi
  yazar** ("Prestij 0.45 gerekli — şu an 0.41").
- Savaş gerektiren yetenekler (Yıldırım Taarruzu, Tahkimat Hattı) ancak savaş
  sırasında kullanılabilir; hedef isteyenler (Elçi Heyeti, Güvenlik Paktı) ülke
  seçim moduna girer.
- Denge önlemleri: aynı savaşta yetenek kaynaklı ilerleme +16 tavanı; Elçi
  Heyeti'nde azalan getiri; İç Borçlanma'da taksit sürerken ikinci borçlanma
  kilidi; Pakt bozmanın prestij cezası; Zorluk seviyesi yetenek maliyetlerini
  de etkiler (kolay ×0.8 / zor ×1.25).

| Yetenek | Kategori | Maliyet | Bekleme | Etki |
|---|---|---|---|---|
| Genel Seferberlik | Askeri | 100 | 36 ay | 12 ay askeri güç ×1.20 |
| Yıldırım Taarruzu | Askeri | 90 | 30 ay | anlık savaş ilerlemesi +8; radikalizm +0.02 |
| Tahkimat Hattı | Askeri | 70 | 30 ay | 12 ay düşman ilerlemesi ×0.6 |
| İç Borçlanma | Ekonomi | 0 | 48 ay | +150 altın anında; +150 borç ve 24 ay −8/ay taksit |
| Ticaret Anlaşmaları | Ekonomi | 120 | 36 ay | 24 ay +7⟡/ay gelir |
| Altyapı Seferberliği | Ekonomi | 100 | 36 ay | 24 ay inşaatlar %25 hızlı |
| Aydınlanma Hamlesi | Toplum | 90 | 36 ay | 24 ay araştırma +0.5/ay |
| Ulusal Bayram | Toplum | 60 | 24 ay | radikalizm kademeli düşer; refah +0.03; prestij +0.01 |
| Elçi Heyeti | Diplomasi | 50 | 18 ay | seçilen ülkeyle ilişki +12 (tekrarda azalan) |
| Güvenlik Paktı | Diplomasi | 80 | 48 ay | 24 ay çift yönlü savaş yasağı; bozma cezalı |

Yeni sinerji olayları: **Tahvil Sahipleri Ayakta** (borçlanma sonrası), **Seferberliğin
Faturası** (seferberlik bitince), **Elçinin Kayıp Valizi** (elçi heyeti sonrası).

## Kontroller

| Tuş / buton | İşlev |
|---|---|
| Boşluk | Duraklat / Devam |
| 1 / 2 / 3 | Hız: Normal / Hızlı / Çok hızlı |
| S | Hızlı kayıt (slot 1) |
| ESC | Hedef seçimini iptal / ana menü |
| Fare tekerleği | Sağ panelde kaydırma |
| Harita tekerleği ± | Yakınlaştır / uzaklaştır |
| Sağ tuş sürükleme | Haritayı kaydır |

## Kayıt / Yükleme

- 3 kayıt slotu, `kayitlar/slot1..3.json` dosyalarında saklanır.
- Ana menüden veya oyun içinde (Kayıt butonu / S tuşu) kaydedin.
- En iyi skor `kayitlar/en_iyi.json` dosyasında tutulur.

## İpuçları

- İlk oyun için **Britanya** veya **Prusya** önerilir. Osmanlı ve Qing zor moddur.
- Gıda arzı düşünce refah çöker; çiftlik sayısını gözden kaçırma.
- Vergiyi fazla yükseltirsen radikalizm tırmanır; radikalizm yüksekken reform risklidir.
- İnşaat sırası: çiftlik/maden → fabrika → demiryolu/liman.
- **Yeni:** Kasanız sıkışırsa İç Borçlanma cankurtaranıdır ama taksitleri unutmayın.
  Savaş açarken Seferberlik + Yıldırım Taarruzu ilk yılda büyük fark yaratır (ayda
  1 yetenek kuralına dikkat).

## Teknik Özet

- `data.py` — veri paketi: 9 ülke, 39 eyalet (+harita konumları), 11 mal, 12 bina,
  24 teknoloji, 7 hukuk kategorisi, 7 çıkar grubu, 30 olay, 10 yetenek, 3 zorluk.
- `engine.py` — aylık simülasyon çekirdeği (pazar, nüfus, bütçe, hukuk, savaş, AI,
  yetenek zamanlayıcıları). UI'ya dokunmaz. Kayıt/yükleme JSON.
- `ui.py` — pygame arayüzü: menü, harita, 7 sekme, sliderlar, olay modali, sonuç.
- `main.py` — oyun döngüsü, hız kontrolü, klavye kısayolları.

## Sürüm Notları / Bilinen Farklar

- Bütçe ölçeği orijinal HTML sürümüne göre yeniden dengelendi (aylık gelir ~30–120
  bandına indirildi); bina/olay/yetenek maliyetleriyle tutarlı.
- Oyuncu yetenekleri kullanabilir; AI ülkeleri kullanmaz (basitlik kararı) — AI
  dengesi zorluk seviyesinden gelir.
