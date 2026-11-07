# -*- coding: utf-8 -*-
"""
data.py — HÜKMÜMRAN veri paketi (Python portu)
Dönem: 1836–1936. Tüm metinler Türkçe.
Yapı: dönem, mallar, binalar, teknolojiler, hukuklar, kulüpler, ülkeler,
      eyaletler (+ harita konumları), olaylar, YETENEKLER (yeni), skor formülü.
"""
import math
import random

DONEM = {"baslangicYil": 1836, "bitisYil": 1936}

# ---------------- MALLAR ----------------
MALLAR = [
    {"id": "tahil",  "ad": "Tahıl",          "bazFiyat": 4,  "kategori": "gida"},
    {"id": "et",     "ad": "Et",             "bazFiyat": 8,  "kategori": "gida"},
    {"id": "balik",  "ad": "Balık",          "bazFiyat": 6,  "kategori": "gida"},
    {"id": "kumas",  "ad": "Kumaş",          "bazFiyat": 12, "kategori": "sanayi"},
    {"id": "camur",  "ad": "Cam ve Tuğla",   "bazFiyat": 9,  "kategori": "sanayi"},
    {"id": "kokart", "ad": "Çelik",          "bazFiyat": 18, "kategori": "sanayi"},
    {"id": "demir",  "ad": "Demir Cevheri",  "bazFiyat": 10, "kategori": "ham"},
    {"id": "komur",  "ad": "Kömür",          "bazFiyat": 7,  "kategori": "ham"},
    {"id": "ahsap",  "ad": "Ağaç",           "bazFiyat": 5,  "kategori": "ham"},
    {"id": "silah",  "ad": "Silah",          "bazFiyat": 28, "kategori": "askeri"},
    {"id": "motor",  "ad": "Motor",          "bazFiyat": 34, "kategori": "sanayi"},
]

# ---------------- BİNALAR ----------------
BINALAR = [
    {"id": "ciftlik", "ad": "Çiftlik", "maliyet": 80, "insaatSuresi": 5, "isgucu": 2500, "tabakaIhtiyaci": "alt",
     "girdiler": {}, "ciktilar": {"tahil": 8, "et": 2},
     "aciklama": "Tahıl ve et üretir. Her eyaletin gıda temelinin belkemiği."},
    {"id": "maden", "ad": "Maden", "maliyet": 180, "insaatSuresi": 8, "isgucu": 1500, "tabakaIhtiyaci": "alt",
     "girdiler": {}, "ciktilar": {"demir": 3, "komur": 3},
     "aciklama": "Demir cevheri ve kömür çıkarır; sanayinin hammaddesi."},
    {"id": "ormancilik", "ad": "Ormancılık Kampı", "maliyet": 70, "insaatSuresi": 4, "isgucu": 1000, "tabakaIhtiyaci": "alt",
     "girdiler": {}, "ciktilar": {"ahsap": 5},
     "aciklama": "Ağaç üretir; inşaat ve silah sanayii için gerekli."},
    {"id": "tekstil_fabrikasi", "ad": "Tekstil Fabrikası", "maliyet": 220, "insaatSuresi": 8, "isgucu": 900, "tabakaIhtiyaci": "orta",
     "girdiler": {}, "ciktilar": {"kumas": 4},
     "aciklama": "Kumaş dokur; sanayileşmenin klasik ilk adımı."},
    {"id": "gida_fabrikasi", "ad": "Gıda Fabrikası", "maliyet": 160, "insaatSuresi": 6, "isgucu": 500, "tabakaIhtiyaci": "orta",
     "girdiler": {"tahil": 3, "balik": 2}, "ciktilar": {"et": 4},
     "aciklama": "Tahıl ve balığı işlenmiş gıdaya (konserve, salamura) çevirir."},
    {"id": "cam_fabrikasi", "ad": "Cam ve Tuğla Fabrikası", "maliyet": 200, "insaatSuresi": 7, "isgucu": 450, "tabakaIhtiyaci": "orta",
     "girdiler": {"komur": 2, "ahsap": 1}, "ciktilar": {"camur": 4},
     "aciklama": "Kömür ve ağacı yapı malzemesine dönüştürür."},
    {"id": "demir_fabrikasi", "ad": "Demir Fabrikası", "maliyet": 320, "insaatSuresi": 10, "isgucu": 600, "tabakaIhtiyaci": "orta",
     "girdiler": {"demir": 3, "komur": 3}, "ciktilar": {"kokart": 3},
     "aciklama": "Cevheri yüksek fırında çeliğe işler; ağır sanayinin kalbi."},
    {"id": "silah_fabrikasi", "ad": "Silah Fabrikası", "maliyet": 380, "insaatSuresi": 10, "isgucu": 500, "tabakaIhtiyaci": "orta",
     "girdiler": {"kokart": 2, "ahsap": 2}, "ciktilar": {"silah": 2},
     "aciklama": "Çelik ve ağaçtan ateşli silah üretir; ordunun gıdası."},
    {"id": "motor_fabrikasi", "ad": "Motor Fabrikası", "maliyet": 450, "insaatSuresi": 12, "isgucu": 500, "tabakaIhtiyaci": "orta",
     "girdiler": {"kokart": 2, "demir": 2}, "ciktilar": {"motor": 1.5},
     "aciklama": "Buhar ve içten yanmalı motor üretir; dönemin zirve teknolojisi."},
    {"id": "demiryolu", "ad": "Demiryolu Hattı", "maliyet": 300, "insaatSuresi": 10, "isgucu": 800, "tabakaIhtiyaci": "orta",
     "girdiler": {}, "ciktilar": {},
     "aciklama": "Eyaletin tüm üretimini verimliştirir (%8) ve iş gücü sağlar."},
    {"id": "liman", "ad": "Liman", "maliyet": 180, "insaatSuresi": 7, "isgucu": 600, "tabakaIhtiyaci": "orta",
     "girdiler": {}, "ciktilar": {"balik": 3},
     "aciklama": "Balıkçılık ve ticaret: üretimi %5 verimliştirir."},
    {"id": "insa_sehri", "ad": "İnşa Sektörü", "maliyet": 150, "insaatSuresi": 5, "isgucu": 1500, "tabakaIhtiyaci": "alt",
     "girdiler": {}, "ciktilar": {"camur": 2, "ahsap": 1},
     "aciklama": "Kentleşme ve altyapı için iş gücü ve yapı malzemesi üretir."},
]

# ---------------- YARDIMCI (teknoloji/olay etkileri) ----------------
def _uretim(u, carpan):
    if u and "teknolojiBonusu" in u:
        u["teknolojiBonusu"]["uretim"] *= carpan

def _vergiVerim(u, carpan):
    if u and "teknolojiBonusu" in u:
        u["teknolojiBonusu"]["vergiVerimliligi"] *= carpan

def _refah(u, ekle):
    if u and "teknolojiBonusu" in u:
        u["teknolojiBonusu"]["refah"] += ekle

def _askeri(u, carpan):
    if u and "teknolojiBonusu" in u:
        u["teknolojiBonusu"]["askeri"] *= carpan

def _kulupAyar(u, kulupId, degisim):
    if not u or "kulupler" not in u:
        return
    if isinstance(u["kulupler"].get(kulupId), (int, float)):
        u["kulupler"][kulupId] = max(-1.0, min(1.0, u["kulupler"][kulupId] + degisim))

def _tumHalk(s, u, fn):
    if not u:
        return
    for eyId in u.get("eyaletler", []):
        ey = s.get("eyaletler", {}).get(eyId)
        if not ey:
            continue
        for p in ey["populations"]:
            fn(p)

def _c_refah(p, d):
    p["refah"] = max(0.0, p["refah"] - d)

def _c_rad(p, d):
    p["radikalizm"] = max(0.0, min(1.0, p["radikalizm"] + d))

# ---------------- TEKNOLOJİLER ----------------
TEKNOLOJILER = [
    # -- Sanayi ve Üretim --
    {"id": "su_gucu", "ad": "Su Gücü ve Mekanizasyon", "kol": "sanayi", "maliyet": 10, "onkosul": [],
     "etkiMetni": "Üretim +%6.", "etki": lambda u, s: _uretim(u, 1.06)},
    {"id": "buhar_makinesi", "ad": "Buhar Makinesi", "kol": "sanayi", "maliyet": 14, "onkosul": ["su_gucu"],
     "etkiMetni": "Üretim +%8.", "etki": lambda u, s: _uretim(u, 1.08)},
    {"id": "kok_endustrisi", "ad": "Kok Endüstrisi", "kol": "sanayi", "maliyet": 14, "onkosul": ["buhar_makinesi"],
     "etkiMetni": "Üretim +%5.", "etki": lambda u, s: _uretim(u, 1.05)},
    {"id": "haddegirme", "ad": "Haddegirme ve Döküm", "kol": "sanayi", "maliyet": 16, "onkosul": ["kok_endustrisi"],
     "etkiMetni": "Üretim +%7.", "etki": lambda u, s: _uretim(u, 1.07)},
    {"id": "demiryolu_agi", "ad": "Demiryolu Ağı", "kol": "sanayi", "maliyet": 18, "onkosul": ["buhar_makinesi"],
     "etkiMetni": "Üretim +%6, vergi verimliliği +%5.",
     "etki": lambda u, s: (_uretim(u, 1.06), _vergiVerim(u, 1.05))},
    {"id": "kimya", "ad": "Endüstriyel Kimya", "kol": "sanayi", "maliyet": 18, "onkosul": ["kok_endustrisi"],
     "etkiMetni": "Üretim +%6.", "etki": lambda u, s: _uretim(u, 1.06)},
    {"id": "elektrik", "ad": "Elektriklendirme", "kol": "sanayi", "maliyet": 22, "onkosul": ["haddegirme"],
     "etkiMetni": "Üretim +%10.", "etki": lambda u, s: _uretim(u, 1.10)},
    {"id": "montaj_hatti", "ad": "Montaj Hattı", "kol": "sanayi", "maliyet": 26, "onkosul": ["elektrik", "kimya"],
     "etkiMetni": "Üretim +%12.", "etki": lambda u, s: _uretim(u, 1.12)},
    # -- Toplum ve Devlet --
    {"id": "matbaa_gazete", "ad": "Serbest Matbaa ve Gazete", "kol": "toplum", "maliyet": 8, "onkosul": [],
     "etkiMetni": "Vergi verimliliği +%5.", "etki": lambda u, s: _vergiVerim(u, 1.05)},
    {"id": "nufus_sayimi", "ad": "Modern Nüfus Sayımı", "kol": "toplum", "maliyet": 10, "onkosul": ["matbaa_gazete"],
     "etkiMetni": "Vergi verimliliği +%6.", "etki": lambda u, s: _vergiVerim(u, 1.06)},
    {"id": "devlet_okullari_tech", "ad": "Kamusal Eğitim Ağı", "kol": "toplum", "maliyet": 14, "onkosul": ["matbaa_gazete"],
     "etkiMetni": "Refah +%4.", "etki": lambda u, s: _refah(u, 0.04)},
    {"id": "kamusal_saglik", "ad": "Kamusal Sağlık Hizmeti", "kol": "toplum", "maliyet": 16, "onkosul": ["devlet_okullari_tech"],
     "etkiMetni": "Refah +%5.", "etki": lambda u, s: _refah(u, 0.05)},
    {"id": "bankacilik", "ad": "Modern Bankacılık", "kol": "toplum", "maliyet": 14, "onkosul": ["nufus_sayimi"],
     "etkiMetni": "Üretim +%5, vergi verimliliği +%4.",
     "etki": lambda u, s: (_uretim(u, 1.05), _vergiVerim(u, 1.04))},
    {"id": "anayasa_hukuku", "ad": "Anayasal Hukuk Geleneği", "kol": "toplum", "maliyet": 18, "onkosul": ["matbaa_gazete"],
     "etkiMetni": "Refah +%3, reformlar daha az direnç görür.", "etki": lambda u, s: _refah(u, 0.03)},
    {"id": "sendikalasma", "ad": "Sendikalaşma Hakkı", "kol": "toplum", "maliyet": 18, "onkosul": ["anayasa_hukuku"],
     "etkiMetni": "Refah +%4; sendika coşar, sermaye kırgın.",
     "etki": lambda u, s: (_refah(u, 0.04), _kulupAyar(u, "sendika", 0.15), _kulupAyar(u, "sermaye", -0.10))},
    {"id": "kadin_egitimi", "ad": "Kızların Eğitimi", "kol": "toplum", "maliyet": 16, "onkosul": ["devlet_okullari_tech"],
     "etkiMetni": "Refah +%4.", "etki": lambda u, s: _refah(u, 0.04)},
    # -- Askeri --
    {"id": "tufek_hatlari", "ad": "Tüfek Hatları", "kol": "ordu", "maliyet": 10, "onkosul": [],
     "etkiMetni": "Askeri güç +%10.", "etki": lambda u, s: _askeri(u, 1.10)},
    {"id": "top_dokumhane", "ad": "Top Dökümhanesi", "kol": "ordu", "maliyet": 12, "onkosul": ["tufek_hatlari"],
     "etkiMetni": "Askeri güç +%10.", "etki": lambda u, s: _askeri(u, 1.10)},
    {"id": "standartlastirma", "ad": "Silah Standardizasyonu", "kol": "ordu", "maliyet": 12, "onkosul": ["tufek_hatlari"],
     "etkiMetni": "Askeri güç +%5.", "etki": lambda u, s: _askeri(u, 1.05)},
    {"id": "askeri_okullar", "ad": "Askeri Akademiler", "kol": "ordu", "maliyet": 14, "onkosul": ["top_dokumhane"],
     "etkiMetni": "Askeri güç +%8.", "etki": lambda u, s: _askeri(u, 1.08)},
    {"id": "demiryolu_lojistigi", "ad": "Demiryolu Lojistiği", "kol": "ordu", "maliyet": 16, "onkosul": ["askeri_okullar", "demiryolu_agi"],
     "etkiMetni": "Askeri güç +%12.", "etki": lambda u, s: _askeri(u, 1.12)},
    {"id": "zirhli_donanma", "ad": "Zırhlı Donanma", "kol": "ordu", "maliyet": 20, "onkosul": ["haddegirme"],
     "etkiMetni": "Askeri güç +%10.", "etki": lambda u, s: _askeri(u, 1.10)},
    {"id": "telgraf", "ad": "Askeri Telgraf Ağı", "kol": "ordu", "maliyet": 14, "onkosul": ["demiryolu_lojistigi"],
     "etkiMetni": "Askeri güç +%8.", "etki": lambda u, s: _askeri(u, 1.08)},
    {"id": "makineli_tufek", "ad": "Makineli Tüfek", "kol": "ordu", "maliyet": 22, "onkosul": ["telgraf", "standartlastirma"],
     "etkiMetni": "Askeri güç +%15.", "etki": lambda u, s: _askeri(u, 1.15)},
]

# ---------------- HUKUKLAR ----------------
KANUNLAR = {
    "oyHakki": [
        {"id": "tabakasal", "ad": "Tabakasal Oy", "aciklama": "Yalnızca üst tabaka seçer."},
        {"id": "census", "ad": "Sayım Oyları", "aciklama": "Üst ve orta tabaka seçer."},
        {"id": "evrensel_erkek", "ad": "Evrensel Erkek Oyu", "aciklama": "Tüm erkek vatandaşlar seçer."},
        {"id": "evrensel", "ad": "Evrensel Oy", "aciklama": "Tüm yetişkin vatandaşlar seçer."},
    ],
    "devletTipi": [
        {"id": "mutlakiyet", "ad": "Mutlakiyet", "aciklama": "Padişah/kral istediğini yapar; reformlar zor geçer."},
        {"id": "mesrutiyet", "ad": "Meşrutiyet", "aciklama": "Anayasalı monarşi; meclis reformları hızlandırır."},
        {"id": "parlamenter", "ad": "Parlamenter Sistem", "aciklama": "Hükümet meclise karşı sorumlu."},
    ],
    "ekonomi": [
        {"id": "geleneksel", "ad": "Geleneksel Ekonomi", "aciklama": "Loncalar ve imtiyazlar; yavaş ama istikrarlı."},
        {"id": "devletci", "ad": "Devletçi Sanayileşme", "aciklama": "Devlet fabrikaları planlar ve kurdurur."},
        {"id": "serbest", "ad": "Serbest Ticaret", "aciklama": "Gümrük gelirini azaltır, üretimi hızlandırır."},
    ],
    "diniSistem": [
        {"id": "teokrasi", "ad": "Dini Hukuk Düzeni", "aciklama": "Cemaatler kendi hukukunda yaşar; ruhani sınıf güçlü."},
        {"id": "millisinir", "ad": "Eşit Vatandaşlık (Cizye Kaldırılır)", "aciklama": "Din farkı gözetmeden vergi ve askerlik."},
        {"id": "laiklik", "ad": "Laiklik", "aciklama": "Hukuk dinden ayrılır; ruhani sınıf tepki gösterir."},
    ],
    "orduModeli": [
        {"id": "derebeyi", "ad": "Derebeyi Askerleri", "aciklama": "Yerel birlikler; ucuz ama zayıf ve sadakatsiz."},
        {"id": "zorunlu_askerlik", "ad": "Zorunlu Askerlik", "aciklama": "Geniş ve modern ordu; köylü nüfus yüklenir."},
        {"id": "mesleki", "ad": "Mesleki Ordu", "aciklama": "Küçük, eğitimli, pahalı profesyonel ordu."},
    ],
    "egitim": [
        {"id": "kilise_okullari", "ad": "Geleneksel Okullar", "aciklama": "Medrese/kilise okulları; din adamlarının gözetiminde."},
        {"id": "devlet_okullari", "ad": "Devlet Okulları", "aciklama": "Seküler müfredat; memur ve teknisyen yetiştirir."},
        {"id": "zorunlu_egitim", "ad": "Zorunlu Eğitim", "aciklama": "Her çocuk okula gider; uzun vadede refah ve teknoloji kazanımı."},
    ],
    "medeniHukuk": [
        {"id": "geleneksel", "ad": "Geleneksel Medeni Hukuk", "aciklama": "Cemaat temelli aile ve miras hukuku."},
        {"id": "uygar_medeni", "ad": "Uygar Medeni Kanun", "aciklama": "Tek düzenli medeni hukuk (Code Civil tarzı)."},
        {"id": "tam_esitlik", "ad": "Tam Eşitlik", "aciklama": "Cinsiyet ve din farkı gözetmeyen hukuk."},
    ],
}

# ---------------- ÇIKAR GRUPLARI ----------------
KULUPLER = [
    {"id": "asiret", "ad": "Aşiret ve Etnik Gruplar", "tabakalar": ["alt"],
     "aciklama": "Yerel geleneklere bağlı kırsal nüfus; merkeziyetçiliğe ve yeni hukuklara tepkilidir."},
    {"id": "ordu", "ad": "Ordu", "tabakalar": ["orta", "alt"],
     "aciklama": "Subay kadrosu; orduda modernleşme ve güçlü bütçe ister, siyasete karışmaktan çekinmez."},
    {"id": "aydin", "ad": "Aydınlar", "tabakalar": ["orta"],
     "aciklama": "Gazeteci, öğretmen, hekim; anayasa, eğitim ve özgürlük talep eder."},
    {"id": "sermaye", "ad": "Sermaye Sahipleri", "tabakalar": ["orta", "ust"],
     "aciklama": "Tüccar ve fabrikatör; serbest ticaret ve düşük vergi ister."},
    {"id": "sendika", "ad": "İşçiler ve Sendikalar", "tabakalar": ["alt", "orta"],
     "aciklama": "Fabrika işçileri; ücret, iş güvenliği ve oy hakkı mücadelesi verir."},
    {"id": "ruhani", "ad": "Ruhani Sınıf", "tabakalar": ["orta", "ust"],
     "aciklama": "Din adamları; geleneksel hukuk düzeninin ve eğitim üzerindeki etkilerin savunucusu."},
    {"id": "memur", "ad": "Memur Sınıfı", "tabakalar": ["orta"],
     "aciklama": "Devlet makinesi; yönetim harcamasından pay ister, reformların uygulayıcısıdır."},
]

KULUP_LISTE = [k["id"] for k in KULUPLER]
TABAKA_LISTE = ["ust", "orta", "alt"]

# ---------------- ÜLKELER ----------------
ULKELER = [
    {"id": "osmanli", "ad": "Osmanlı İmparatorluğu", "renk": "#3d7a4f", "kisa": "OSM",
     "ozet": "II. Mahmud dönemi: yeniçeri ocağı kapatıldı (1826), merkeziyetçilik ve ıslahat yılları. Zor ama dönüştürücü bir başlangıç.",
     "prestijBaslangic": 0.45, "aiKarakter": "dengeli",
     "baslangicKanun": {"oyHakki": "tabakasal", "devletTipi": "mutlakiyet", "ekonomi": "geleneksel", "diniSistem": "teokrasi",
                        "orduModeli": "zorunlu_askerlik", "egitim": "kilise_okullari", "medeniHukuk": "geleneksel"}},
    {"id": "rusya", "ad": "Rus İmparatorluğu", "renk": "#4a5d8f", "kisa": "RUS",
     "ozet": "I. Nikola: otokrasi, Ortodoksluk ve milliyet ilkesi; serflerin dünyası ve dev bir kara ordusu.",
     "prestijBaslangic": 0.50, "aiKarakter": "agresif",
     "baslangicKanun": {"oyHakki": "tabakasal", "devletTipi": "mutlakiyet", "ekonomi": "geleneksel", "diniSistem": "teokrasi",
                        "orduModeli": "zorunlu_askerlik", "egitim": "kilise_okullari", "medeniHukuk": "geleneksel"}},
    {"id": "britanya", "ad": "Birleşik Krallık", "renk": "#8f2d2d", "kisa": "BRT",
     "ozet": "Victoria öncesi Whig çağı: 1832 Reform Yasası taze, sanayi dünya lideri, donanma hiç yenilmedi. Kolay başlangıç.",
     "prestijBaslangic": 0.65, "aiKarakter": "dengeli",
     "baslangicKanun": {"oyHakki": "census", "devletTipi": "mesrutiyet", "ekonomi": "serbest", "diniSistem": "laiklik",
                        "orduModeli": "mesleki", "egitim": "kilise_okullari", "medeniHukuk": "uygar_medeni"}},
    {"id": "fransa", "ad": "Fransa Krallığı", "renk": "#7a6d8f", "kisa": "FRA",
     "ozet": "Temmuz Monarşisi: Louis-Philippe burjuva tahtında; 1848'in gölgeleri yaklaşıyor. Code Civil yürürlükte.",
     "prestijBaslangic": 0.55, "aiKarakter": "dengeli",
     "baslangicKanun": {"oyHakki": "census", "devletTipi": "mesrutiyet", "ekonomi": "geleneksel", "diniSistem": "laiklik",
                        "orduModeli": "zorunlu_askerlik", "egitim": "kilise_okullari", "medeniHukuk": "uygar_medeni"}},
    {"id": "prusya", "ad": "Prusya Krallığı", "renk": "#4f4a42", "kisa": "PRS",
     "ozet": "Zollverein (1834) Alman ekonomisini birleştiriyor; okullu ve ordulu devlet. Sanayileşme için mükemmel zemin.",
     "prestijBaslangic": 0.45, "aiKarakter": "agresif",
     "baslangicKanun": {"oyHakki": "tabakasal", "devletTipi": "mutlakiyet", "ekonomi": "geleneksel", "diniSistem": "teokrasi",
                        "orduModeli": "zorunlu_askerlik", "egitim": "devlet_okullari", "medeniHukuk": "geleneksel"}},
    {"id": "avusturya", "ad": "Avusturya İmparatorluğu", "renk": "#a08a3c", "kisa": "AVS",
     "ozet": "Metternich düzeni: çok uluslu imparatorluk, sansür ve denge siyaseti; 1848 fırtınasının tam ortasında duracak.",
     "prestijBaslangic": 0.50, "aiKarakter": "dengeli",
     "baslangicKanun": {"oyHakki": "tabakasal", "devletTipi": "mutlakiyet", "ekonomi": "geleneksel", "diniSistem": "teokrasi",
                        "orduModeli": "zorunlu_askerlik", "egitim": "kilise_okullari", "medeniHukuk": "geleneksel"}},
    {"id": "abd", "ad": "Amerika Birleşik Devletleri", "renk": "#4f6f4f", "kisa": "ABD",
     "ozet": "Jackson dönemi: genişleyen cephe, patlayan pazar ekonomisi — ve her yıl derinleşen kölelik krizi.",
     "prestijBaslangic": 0.40, "aiKarakter": "bariscil",
     "baslangicKanun": {"oyHakki": "census", "devletTipi": "parlamenter", "ekonomi": "serbest", "diniSistem": "laiklik",
                        "orduModeli": "mesleki", "egitim": "devlet_okullari", "medeniHukuk": "uygar_medeni"}},
    {"id": "japonya", "ad": "Japonya (Tokugawa Şogunluğu)", "renk": "#8f5a2d", "kisa": "JPN",
     "ozet": "Sakoku düzeni sürüyor; Edo dünyanın en büyük kentlerinden biri. Batı gemileri ufukta belirdiğinde karar sizin olacak.",
     "prestijBaslangic": 0.30, "aiKarakter": "bariscil",
     "baslangicKanun": {"oyHakki": "tabakasal", "devletTipi": "mutlakiyet", "ekonomi": "geleneksel", "diniSistem": "teokrasi",
                        "orduModeli": "derebeyi", "egitim": "kilise_okullari", "medeniHukuk": "geleneksel"}},
    {"id": "qing", "ad": "Qing İmparatorluğu", "renk": "#7a8f5a", "kisa": "QNG",
     "ozet": "Daoguang dönemi: dünyanın en kalabalık ekonomisi ama Afyon krizi büyüyor. Devasa nüfus, kırılgan devlet. Zor mod.",
     "prestijBaslangic": 0.40, "aiKarakter": "dengeli",
     "baslangicKanun": {"oyHakki": "tabakasal", "devletTipi": "mutlakiyet", "ekonomi": "geleneksel", "diniSistem": "teokrasi",
                        "orduModeli": "derebeyi", "egitim": "kilise_okullari", "medeniHukuk": "geleneksel"}},
]

# ---------------- EYALETLER (~40) ----------------
# mx,my: stilize harita konumu (0..1000 × 0..660 koordinat alanı)
EYALETLER = [
    # OSMANLI
    {"id": "rumeli", "ulkeId": "osmanli", "ad": "Rumeli", "nufus": 2600000, "kaynaklar": ["tahil", "ahsap"], "mx": 352, "my": 392,
     "baslangicBinalar": {"ciftlik": 4, "ormancilik": 2, "insa_sehri": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 1900000, "refah": 0.42},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 300000, "refah": 0.50},
        {"kulup": "memur", "tabaka": "orta", "sayi": 250000, "refah": 0.48},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 150000, "refah": 0.52}],
     "cografiNot": "Balkanlar; ticaret yollarının kesişimi."},
    {"id": "istanbul", "ulkeId": "osmanli", "ad": "İstanbul", "nufus": 350000, "kaynaklar": ["balik", "kumas"], "mx": 391, "my": 418,
     "baslangicBinalar": {"ciftlik": 1, "liman": 2, "tekstil_fabrikasi": 1, "silah_fabrikasi": 1},
     "populations": [
        {"kulup": "memur", "tabaka": "orta", "sayi": 120000, "refah": 0.50},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 80000, "refah": 0.55},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 130000, "refah": 0.45},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 20000, "refah": 0.50}],
     "cografiNot": "Başkent; boğaz ticaretinin kilidi."},
    {"id": "anadolu", "ulkeId": "osmanli", "ad": "Anadolu", "nufus": 4500000, "kaynaklar": ["tahil", "et", "komur"], "mx": 438, "my": 428,
     "baslangicBinalar": {"ciftlik": 8, "maden": 2, "insa_sehri": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 3400000, "refah": 0.40},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 400000, "refah": 0.48},
        {"kulup": "memur", "tabaka": "orta", "sayi": 300000, "refah": 0.47},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 200000, "refah": 0.50},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 200000, "refah": 0.50}],
     "cografiNot": "İmparatorluğun tahıl ambarı ve kömür yatakları."},
    {"id": "suriye", "ulkeId": "osmanli", "ad": "Suriye", "nufus": 1800000, "kaynaklar": ["tahil", "kumas"], "mx": 452, "my": 492,
     "baslangicBinalar": {"ciftlik": 3, "tekstil_fabrikasi": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 1350000, "refah": 0.42},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 250000, "refah": 0.50},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 200000, "refah": 0.52}],
     "cografiNot": "Kumaş dokumacılığının merkezi."},
    {"id": "misir", "ulkeId": "osmanli", "ad": "Mısır", "nufus": 3500000, "kaynaklar": ["tahil", "kumas"], "mx": 405, "my": 560,
     "baslangicBinalar": {"ciftlik": 6, "tekstil_fabrikasi": 1, "insa_sehri": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 2800000, "refah": 0.38},
        {"kulup": "memur", "tabaka": "orta", "sayi": 400000, "refah": 0.46},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 300000, "refah": 0.50}],
     "cografiNot": "Kavalalı'nın modernleşme laboratuvarı; pamuk zenginliği."},
    {"id": "bagdat", "ulkeId": "osmanli", "ad": "Bağdat", "nufus": 1200000, "kaynaklar": ["tahil", "et"], "mx": 516, "my": 508,
     "baslangicBinalar": {"ciftlik": 3},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 900000, "refah": 0.40},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 180000, "refah": 0.48},
        {"kulup": "memur", "tabaka": "orta", "sayi": 120000, "refah": 0.46}],
     "cografiNot": "Mezopotamya vilayeti; aşiret yapısı güçlü."},
    # RUSYA
    {"id": "polonya", "ulkeId": "rusya", "ad": "Polonya (Vistula Ülkesi)", "nufus": 4500000, "kaynaklar": ["tahil", "ahsap"], "mx": 428, "my": 262,
     "baslangicBinalar": {"ciftlik": 6, "ormancilik": 2, "tekstil_fabrikasi": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 3300000, "refah": 0.40},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 500000, "refah": 0.48},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 400000, "refah": 0.50},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 300000, "refah": 0.50}],
     "cografiNot": "1831 ayaklanması taze; huzursuz vilayet."},
    {"id": "moskova", "ulkeId": "rusya", "ad": "Moskova", "nufus": 4000000, "kaynaklar": ["tahil", "ahsap", "komur"], "mx": 548, "my": 172,
     "baslangicBinalar": {"ciftlik": 5, "maden": 2, "ormancilik": 2, "tekstil_fabrikasi": 2},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 2900000, "refah": 0.38},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 450000, "refah": 0.50},
        {"kulup": "memur", "tabaka": "orta", "sayi": 350000, "refah": 0.47},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 300000, "refah": 0.48}],
     "cografiNot": "Eski başkent, tekstil sanayii merkezi."},
    {"id": "petersburg", "ulkeId": "rusya", "ad": "Petersburg", "nufus": 800000, "kaynaklar": ["balik", "ahsap"], "mx": 470, "my": 140,
     "baslangicBinalar": {"liman": 2, "ormancilik": 1, "silah_fabrikasi": 1},
     "populations": [
        {"kulup": "memur", "tabaka": "orta", "sayi": 250000, "refah": 0.50},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 200000, "refah": 0.52},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 350000, "refah": 0.40}],
     "cografiNot": "İmparatorluk başkenti; saray ve donanma."},
    {"id": "kazan", "ulkeId": "rusya", "ad": "Kazan", "nufus": 2500000, "kaynaklar": ["tahil", "komur"], "mx": 622, "my": 212,
     "baslangicBinalar": {"ciftlik": 4, "maden": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 2000000, "refah": 0.38},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 300000, "refah": 0.48},
        {"kulup": "memur", "tabaka": "orta", "sayi": 200000, "refah": 0.46}],
     "cografiNot": "Volga ticaretinin kapısı."},
    {"id": "kafkasya", "ulkeId": "rusya", "ad": "Kafkasya", "nufus": 1500000, "kaynaklar": ["demir", "et"], "mx": 572, "my": 380,
     "baslangicBinalar": {"ciftlik": 2, "maden": 2},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 1200000, "refah": 0.36},
        {"kulup": "memur", "tabaka": "orta", "sayi": 200000, "refah": 0.45},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 100000, "refah": 0.50}],
     "cografiNot": "Kafkasya Savaşı sürüyor; dağ halkları direnişte."},
    {"id": "sibirya", "ulkeId": "rusya", "ad": "Sibirya", "nufus": 1200000, "kaynaklar": ["ahsap", "komur", "demir"], "mx": 726, "my": 150,
     "baslangicBinalar": {"ormancilik": 4, "maden": 2},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 950000, "refah": 0.42},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 150000, "refah": 0.50},
        {"kulup": "memur", "tabaka": "orta", "sayi": 100000, "refah": 0.46}],
     "cografiNot": "Sonsuz orman ve maden; sürgün diyarı."},
    # BRİTANYA
    {"id": "londra", "ulkeId": "britanya", "ad": "Londra", "nufus": 1900000, "kaynaklar": ["balik", "kumas"], "mx": 148, "my": 244,
     "baslangicBinalar": {"liman": 3, "tekstil_fabrikasi": 2, "demiryolu": 1, "insa_sehri": 1},
     "populations": [
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 500000, "refah": 0.58},
        {"kulup": "sendika", "tabaka": "alt", "sayi": 700000, "refah": 0.50},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 300000, "refah": 0.55},
        {"kulup": "memur", "tabaka": "orta", "sayi": 250000, "refah": 0.52},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 150000, "refah": 0.45}],
     "cografiNot": "Dünyanın finans başkenti."},
    {"id": "midlands", "ulkeId": "britanya", "ad": "Midlands", "nufus": 2200000, "kaynaklar": ["komur", "demir"], "mx": 122, "my": 190,
     "baslangicBinalar": {"maden": 4, "demir_fabrikasi": 2, "motor_fabrikasi": 1, "silah_fabrikasi": 1, "demiryolu": 1},
     "populations": [
        {"kulup": "sendika", "tabaka": "alt", "sayi": 1200000, "refah": 0.48},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 400000, "refah": 0.56},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 300000, "refah": 0.52},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 300000, "refah": 0.45}],
     "cografiNot": "Sanayi devriminin kalbi: demir, kömür, buhar."},
    {"id": "iskocya", "ulkeId": "britanya", "ad": "İskoçya", "nufus": 2300000, "kaynaklar": ["komur", "balik"], "mx": 108, "my": 118,
     "baslangicBinalar": {"maden": 3, "liman": 2, "gida_fabrikasi": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 1400000, "refah": 0.44},
        {"kulup": "sendika", "tabaka": "alt", "sayi": 400000, "refah": 0.48},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 300000, "refah": 0.54},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 200000, "refah": 0.52}],
     "cografiNot": "Glasgow gemi yapımı ve kömür havzaları."},
    {"id": "irlanda", "ulkeId": "britanya", "ad": "İrlanda", "nufus": 7800000, "kaynaklar": ["tahil", "et"], "mx": 52, "my": 188,
     "baslangicBinalar": {"ciftlik": 9},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 6800000, "refah": 0.36},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 500000, "refah": 0.45},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 300000, "refah": 0.50},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 200000, "refah": 0.50}],
     "cografiNot": "Patatese bağımlı kalabalık kırsal; kıtlık riski yüksek."},
    # FRANSA
    {"id": "ile_de_france", "ulkeId": "fransa", "ad": "Île-de-France", "nufus": 2800000, "kaynaklar": ["tahil", "kumas"], "mx": 226, "my": 372,
     "baslangicBinalar": {"ciftlik": 4, "tekstil_fabrikasi": 2, "insa_sehri": 1},
     "populations": [
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 600000, "refah": 0.55},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 400000, "refah": 0.54},
        {"kulup": "memur", "tabaka": "orta", "sayi": 350000, "refah": 0.52},
        {"kulup": "sendika", "tabaka": "alt", "sayi": 700000, "refah": 0.50},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 750000, "refah": 0.47}],
     "cografiNot": "Paris: devrimlerin şehri."},
    {"id": "kuzey_fransa", "ulkeId": "fransa", "ad": "Kuzey Fransa", "nufus": 3200000, "kaynaklar": ["komur", "kumas"], "mx": 212, "my": 318,
     "baslangicBinalar": {"maden": 3, "tekstil_fabrikasi": 3},
     "populations": [
        {"kulup": "sendika", "tabaka": "alt", "sayi": 1500000, "refah": 0.48},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 500000, "refah": 0.54},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 1000000, "refah": 0.45},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 200000, "refah": 0.52}],
     "cografiNot": "Lille tekstil havzası ve kömür."},
    {"id": "aquitaine", "ulkeId": "fransa", "ad": "Akitanya", "nufus": 3000000, "kaynaklar": ["tahil", "balik"], "mx": 190, "my": 432,
     "baslangicBinalar": {"ciftlik": 5, "liman": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 2100000, "refah": 0.46},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 400000, "refah": 0.52},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 300000, "refah": 0.50},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 200000, "refah": 0.50}],
     "cografiNot": "Bordeaux şarabı ve liman ticareti."},
    {"id": "provence", "ulkeId": "fransa", "ad": "Provence", "nufus": 2500000, "kaynaklar": ["balik", "kumas"], "mx": 254, "my": 438,
     "baslangicBinalar": {"liman": 2, "ciftlik": 3, "tekstil_fabrikasi": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 1700000, "refah": 0.46},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 400000, "refah": 0.52},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 250000, "refah": 0.50},
        {"kulup": "memur", "tabaka": "orta", "sayi": 150000, "refah": 0.50}],
     "cografiNot": "Marsilya: Akdeniz'in kapısı."},
    # PRUSYA
    {"id": "berlin", "ulkeId": "prusya", "ad": "Berlin", "nufus": 900000, "kaynaklar": ["kumas", "komur"], "mx": 342, "my": 282,
     "baslangicBinalar": {"tekstil_fabrikasi": 2, "silah_fabrikasi": 1, "insa_sehri": 1},
     "populations": [
        {"kulup": "memur", "tabaka": "orta", "sayi": 250000, "refah": 0.52},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 250000, "refah": 0.55},
        {"kulup": "sendika", "tabaka": "alt", "sayi": 250000, "refah": 0.50},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 150000, "refah": 0.53}],
     "cografiNot": "Ordu ve bürokrasi başkenti."},
    {"id": "ren_bolgesi", "ulkeId": "prusya", "ad": "Ren Bölgesi", "nufus": 2800000, "kaynaklar": ["komur", "demir"], "mx": 296, "my": 288,
     "baslangicBinalar": {"maden": 4, "demir_fabrikasi": 2, "motor_fabrikasi": 1},
     "populations": [
        {"kulup": "sendika", "tabaka": "alt", "sayi": 1200000, "refah": 0.48},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 500000, "refah": 0.55},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 900000, "refah": 0.46},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 200000, "refah": 0.52}],
     "cografiNot": "Ruhr: Avrupa'nın gelecekteki sanayi motoru."},
    {"id": "dogu_prusya", "ulkeId": "prusya", "ad": "Doğu Prusya", "nufus": 2200000, "kaynaklar": ["tahil", "ahsap"], "mx": 404, "my": 232,
     "baslangicBinalar": {"ciftlik": 5, "ormancilik": 2},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 1700000, "refah": 0.42},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 250000, "refah": 0.50},
        {"kulup": "memur", "tabaka": "orta", "sayi": 250000, "refah": 0.48}],
     "cografiNot": "Junker toprak aristokrasisinin kalesi."},
    {"id": "silezya", "ulkeId": "prusya", "ad": "Silezya", "nufus": 2500000, "kaynaklar": ["komur", "demir"], "mx": 386, "my": 312,
     "baslangicBinalar": {"maden": 3, "demir_fabrikasi": 1, "tekstil_fabrikasi": 1},
     "populations": [
        {"kulup": "sendika", "tabaka": "alt", "sayi": 1200000, "refah": 0.47},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 900000, "refah": 0.44},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 400000, "refah": 0.53}],
     "cografiNot": "Madenciliğin eski merkezi; dokumacı yoksulluğu 1844'te patlayacak."},
    # AVUSTURYA
    {"id": "viyana", "ulkeId": "avusturya", "ad": "Viyana", "nufus": 1000000, "kaynaklar": ["kumas"], "mx": 336, "my": 356,
     "baslangicBinalar": {"tekstil_fabrikasi": 2, "silah_fabrikasi": 1, "insa_sehri": 1},
     "populations": [
        {"kulup": "memur", "tabaka": "orta", "sayi": 300000, "refah": 0.52},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 250000, "refah": 0.55},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 200000, "refah": 0.53},
        {"kulup": "sendika", "tabaka": "alt", "sayi": 250000, "refah": 0.48}],
     "cografiNot": "Metternich'in sarayı, Avrupa diplomasisinin sahne ışığı."},
    {"id": "bohemya", "ulkeId": "avusturya", "ad": "Bohemya", "nufus": 4000000, "kaynaklar": ["komur", "demir"], "mx": 312, "my": 326,
     "baslangicBinalar": {"maden": 4, "demir_fabrikasi": 2, "tekstil_fabrikasi": 2},
     "populations": [
        {"kulup": "sendika", "tabaka": "alt", "sayi": 1800000, "refah": 0.47},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 1400000, "refah": 0.44},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 500000, "refah": 0.53},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 300000, "refah": 0.50}],
     "cografiNot": "İmparatorluğun sanayi atölyesi; Çek milliyetçiliği yükseliyor."},
    {"id": "macaristan", "ulkeId": "avusturya", "ad": "Macaristan", "nufus": 5000000, "kaynaklar": ["tahil", "et"], "mx": 420, "my": 358,
     "baslangicBinalar": {"ciftlik": 7, "insa_sehri": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 3800000, "refah": 0.42},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 500000, "refah": 0.50},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 400000, "refah": 0.50},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 300000, "refah": 0.50}],
     "cografiNot": "Magyar soylular Viyana'yla pazarlıkta; 1848'e hazırlanın."},
    {"id": "galicya", "ulkeId": "avusturya", "ad": "Galiçya", "nufus": 3000000, "kaynaklar": ["tahil", "ahsap"], "mx": 452, "my": 316,
     "baslangicBinalar": {"ciftlik": 4, "ormancilik": 2},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 2400000, "refah": 0.38},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 350000, "refah": 0.48},
        {"kulup": "memur", "tabaka": "orta", "sayi": 250000, "refah": 0.46}],
     "cografiNot": "İmparatorluğun yoksul kuzeydoğusu."},
    # ABD (stilize Yeni Dünya sütunu)
    {"id": "kuzeydogu", "ulkeId": "abd", "ad": "Kuzeydoğu", "nufus": 4500000, "kaynaklar": ["kumas", "balik", "demir"], "mx": 96, "my": 560,
     "baslangicBinalar": {"tekstil_fabrikasi": 3, "liman": 2, "demir_fabrikasi": 1, "motor_fabrikasi": 1},
     "populations": [
        {"kulup": "sendika", "tabaka": "alt", "sayi": 1600000, "refah": 0.52},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 800000, "refah": 0.58},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 500000, "refah": 0.56},
        {"kulup": "memur", "tabaka": "orta", "sayi": 300000, "refah": 0.54},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 1300000, "refah": 0.50}],
     "cografiNot": "New England fabrikaları ve New York limanı."},
    {"id": "guney", "ulkeId": "abd", "ad": "Güney", "nufus": 5500000, "kaynaklar": ["tahil", "et"], "mx": 60, "my": 616,
     "baslangicBinalar": {"ciftlik": 8, "gida_fabrikasi": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 3600000, "refah": 0.40},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 900000, "refah": 0.56},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 500000, "refah": 0.50},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 300000, "refah": 0.52},
        {"kulup": "memur", "tabaka": "orta", "sayi": 200000, "refah": 0.50}],
     "cografiNot": "Pamuk tarlaları ve kölelik düzeni; ulusal krizin çekirdeği."},
    {"id": "ortabati", "ulkeId": "abd", "ad": "Ortabatı", "nufus": 3500000, "kaynaklar": ["tahil", "komur"], "mx": 160, "my": 560,
     "baslangicBinalar": {"ciftlik": 6, "maden": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 2800000, "refah": 0.50},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 300000, "refah": 0.55},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 250000, "refah": 0.53},
        {"kulup": "memur", "tabaka": "orta", "sayi": 150000, "refah": 0.52}],
     "cografiNot": "Buğday kuşağı; göçmen akını sürüyor."},
    {"id": "bati", "ulkeId": "abd", "ad": "Batı Cephesi", "nufus": 500000, "kaynaklar": ["demir", "ahsap"], "mx": 224, "my": 606,
     "baslangicBinalar": {"ormancilik": 2, "maden": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 350000, "refah": 0.50},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 80000, "refah": 0.55},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 70000, "refah": 0.53}],
     "cografiNot": "Sınır hattı; altın humması kapıda."},
    # JAPONYA
    {"id": "edo", "ulkeId": "japonya", "ad": "Edo", "nufus": 1200000, "kaynaklar": ["balik", "kumas"], "mx": 956, "my": 250,
     "baslangicBinalar": {"liman": 1, "ciftlik": 2, "tekstil_fabrikasi": 1},
     "populations": [
        {"kulup": "memur", "tabaka": "orta", "sayi": 400000, "refah": 0.50},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 250000, "refah": 0.52},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 500000, "refah": 0.46},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 50000, "refah": 0.50}],
     "cografiNot": "Şogunluk başkenti; milyonluk kent ekonomisi."},
    {"id": "osaka", "ulkeId": "japonya", "ad": "Osaka", "nufus": 900000, "kaynaklar": ["kumas", "balik"], "mx": 930, "my": 316,
     "baslangicBinalar": {"liman": 1, "tekstil_fabrikasi": 1, "gida_fabrikasi": 1},
     "populations": [
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 300000, "refah": 0.52},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 500000, "refah": 0.45},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 100000, "refah": 0.50}],
     "cografiNot": "Japonya'nın ticaret mutfası."},
    {"id": "satsuma", "ulkeId": "japonya", "ad": "Satsuma ve Chōshū", "nufus": 2500000, "kaynaklar": ["tahil", "balik"], "mx": 906, "my": 384,
     "baslangicBinalar": {"ciftlik": 4, "liman": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 2000000, "refah": 0.42},
        {"kulup": "memur", "tabaka": "orta", "sayi": 250000, "refah": 0.48},
        {"kulup": "ruhani", "tabaka": "orta", "sayi": 250000, "refah": 0.48}],
     "cografiNot": "Güçlü dış hanlıklar; restorasyonun fitilini tutacaklar."},
    # QING
    {"id": "pekin", "ulkeId": "qing", "ad": "Pekin", "nufus": 1500000, "kaynaklar": ["tahil", "kumas"], "mx": 838, "my": 236,
     "baslangicBinalar": {"ciftlik": 3, "tekstil_fabrikasi": 1, "insa_sehri": 1},
     "populations": [
        {"kulup": "memur", "tabaka": "orta", "sayi": 400000, "refah": 0.48},
        {"kulup": "asiret", "tabaka": "alt", "sayi": 800000, "refah": 0.40},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 300000, "refah": 0.50}],
     "cografiNot": "İmparatorluk sarayı ve bürokrasisi."},
    {"id": "yangtze", "ulkeId": "qing", "ad": "Yangtze Havzası", "nufus": 30000000, "kaynaklar": ["tahil", "kumas", "komur"], "mx": 856, "my": 308,
     "baslangicBinalar": {"ciftlik": 12, "tekstil_fabrikasi": 3, "maden": 2},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 24000000, "refah": 0.38},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 2500000, "refah": 0.48},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 2000000, "refah": 0.48},
        {"kulup": "memur", "tabaka": "orta", "sayi": 1500000, "refah": 0.47}],
     "cografiNot": "Dünyanın en üretken tarım havzası; devasa nüfus."},
    {"id": "guangdong", "ulkeId": "qing", "ad": "Guangdong", "nufus": 22000000, "kaynaklar": ["tahil", "balik"], "mx": 838, "my": 392,
     "baslangicBinalar": {"ciftlik": 8, "liman": 2, "gida_fabrikasi": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 17500000, "refah": 0.40},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 2200000, "refah": 0.50},
        {"kulup": "aydin", "tabaka": "orta", "sayi": 1500000, "refah": 0.48},
        {"kulup": "memur", "tabaka": "orta", "sayi": 800000, "refah": 0.47}],
     "cografiNot": "Kanton limanı: tek resmî ticaret kapısı; afyon sızıyor."},
    {"id": "mancurya", "ulkeId": "qing", "ad": "Mançurya", "nufus": 3000000, "kaynaklar": ["tahil", "ahsap", "komur"], "mx": 884, "my": 166,
     "baslangicBinalar": {"ciftlik": 3, "ormancilik": 2, "maden": 1},
     "populations": [
        {"kulup": "asiret", "tabaka": "alt", "sayi": 2300000, "refah": 0.42},
        {"kulup": "memur", "tabaka": "orta", "sayi": 400000, "refah": 0.47},
        {"kulup": "sermaye", "tabaka": "orta", "sayi": 300000, "refah": 0.48}],
     "cografiNot": "Hanedanın ata yurdu; Rus nüfuzu artıyor."},
]

# ---- olay etki/koşul fonksiyonları (OLAYLAR'dan ÖNCE tanımlı olmalı) ----
def _e_1848_taviz(s, u):
    _kulupAyar(u, "aydin", 0.20)
    _kulupAyar(u, "ordu", -0.10)
    _tumHalk(s, u, lambda p: p.__setitem__("radikalizm", max(0.0, p["radikalizm"] - 0.08)))
    if u["kanunlar"]["devletTipi"] == "mutlakiyet":
        u["kanunGecisleri"].setdefault("devletTipi", {"yeniDeger": "mesrutiyet", "kalanAy": 12})

def _e_meiji_destekle(s, u):
    _kulupAyar(u, "memur", 0.15)
    _kulupAyar(u, "asiret", -0.20)
    _kulupAyar(u, "ordu", 0.10)
    if "orduModeli" not in u["kanunGecisleri"] and u["kanunlar"]["orduModeli"] == "derebeyi":
        u["kanunGecisleri"]["orduModeli"] = {"yeniDeger": "zorunlu_askerlik", "kalanAy": 12}
    if "egitim" not in u["kanunGecisleri"]:
        u["kanunGecisleri"]["egitim"] = {"yeniDeger": "devlet_okullari", "kalanAy": 18}

def _e_isyan_reform(s, u):
    _tumHalk(s, u, lambda p: p.__setitem__("radikalizm", max(0.0, p["radikalizm"] - 0.10)))
    sira = ["tabakasal", "census", "evrensel_erkek", "evrensel"]
    if "oyHakki" not in u["kanunGecisleri"]:
        k = u["kanunlar"]["oyHakki"]
        i = sira.index(k) if k in sira else -1
        if 0 <= i < len(sira) - 1:
            u["kanunGecisleri"]["oyHakki"] = {"yeniDeger": sira[i + 1], "kalanAy": 10}

def _e_goc_kabul(s, u):
    if u.get("eyaletler"):
        ey = s["eyaletler"].get(u["eyaletler"][0])
        if ey and ey["populations"]:
            ey["populations"][0]["sayi"] += 20000
    _kulupAyar(u, "sermaye", 0.05)

def _e_tahvil(s):
    # İç Borçlanma'dan 6–12 ay sonra %60 şans; oyunda bir kez
    st = s.get("son_tahvil_tick")
    return bool(st is not None and 6 <= (s["tick"] - st) <= 12
                and "tahvil_sahipleri" not in s["olaylar"]["gecmis"]
                and random.random() < 0.60)

def _e_tahvil_reddet(s, u):
    u["prestij"] = max(0.0, u["prestij"] - 0.03)
    s["beklemeler"]["war_bonds"] = s["beklemeler"].get("war_bonds", 0) + 24

def _e_seferberlik_fatura(s):
    return bool(s.get("son_seferberlik_bitis_tick") == s["tick"]
                and "seferberlik_faturasi" not in s["olaylar"]["gecmis"])

def _e_elci_valizi(s):
    st = s.get("son_elci_tick")
    return bool(st is not None and 1 <= (s["tick"] - st) <= 3
                and "elci_valizi" not in s["olaylar"]["gecmis"]
                and random.random() < 0.25)

def _e_valiz_ort(s, u):
    u["para"] = max(0, u["para"] - 40)
    hedef = s.get("son_elci_hedef")
    if hedef and hedef in s["ulkeler"].get(s["oyuncuUlke"], {}).get("iliskiler", {}):
        u["iliskiler"][hedef] = max(-100, min(100, u["iliskiler"][hedef] + 4))

# ---------------- OLAYLAR ----------------
# tur: 'yetenek' olayları 8% kapıya takılmadan, kendi koşuluyla her ay kontrol edilir.
def _e_kolera(s):
    return s["yil"] >= 1836 and (s["tick"] % 97) == 13

def _e_afyon(s):
    return s["oyuncuUlke"] == "qing" and 1839 <= s["yil"] <= 1842

def _e_tanzimat(s):
    u = s["ulkeler"].get("osmanli")
    return (s["oyuncuUlke"] == "osmanli" and 1839 <= s["yil"] <= 1845
            and bool(u) and u["kanunlar"]["diniSistem"] == "teokrasi")

def _e_1848(s):
    return (s["oyuncuUlke"] in ("fransa", "avusturya", "prusya") and 1848 <= s["yil"] <= 1850)

def _e_kirim(s):
    return (s["oyuncuUlke"] in ("osmanli", "rusya") and 1853 <= s["yil"] <= 1856)

def _e_meiji(s):
    return s["oyuncuUlke"] == "japonya" and 1868 <= s["yil"] <= 1875

def _e_taiping(s):
    return s["oyuncuUlke"] == "qing" and 1850 <= s["yil"] <= 1864

def _e_icsavas(s):
    return s["oyuncuUlke"] == "abd" and 1861 <= s["yil"] <= 1865

def _e_berlin(s):
    return s["oyuncuUlke"] == "osmanli" and 1878 <= s["yil"] <= 1880

def _e_duyun(s):
    u = s["ulkeler"].get("osmanli")
    return s["oyuncuUlke"] == "osmanli" and s["yil"] >= 1881 and bool(u) and u.get("borc", 0) > 80

def _e_suez(s):
    return s["oyuncuUlke"] == "osmanli" and 1869 <= s["yil"] <= 1875

def _e_isyan(s):
    u = s["ulkeler"].get(s["oyuncuUlke"])
    return bool(u and s.get("sonOzet") and s["sonOzet"].get("radikalizm", 0) > 0.65)

def _e_grev(s):
    u = s["ulkeler"].get(s["oyuncuUlke"])
    return bool(u and u["kanunlar"]["ekonomi"] != "geleneksel" and u["kulupler"].get("sendika", 0) < -0.25 and s["yil"] >= 1860)

def _e_banka(s):
    u = s["ulkeler"].get(s["oyuncuUlke"])
    return bool(u and u.get("borc", 0) > 100 and s["yil"] >= 1857)

def _e_sergi(s):
    u = s["ulkeler"].get(s["oyuncuUlke"])
    return bool(u and len(u["teknoloji"]["tamamlanan"]) >= 4)

def _e_sansur(s):
    u = s["ulkeler"].get(s["oyuncuUlke"])
    return bool(u and u["kanunlar"]["devletTipi"] == "mutlakiyet" and s["yil"] >= 1840)

def _e_subay(s):
    u = s["ulkeler"].get(s["oyuncuUlke"])
    return bool(u and u["kulupler"].get("ordu", 0) < -0.30)

def _e_goc(s):
    return bool(s.get("sonOzet") and s["sonOzet"].get("refahOrt", 0) > 0.50 and (s["tick"] % 83) == 40)

def _e_demiryolu_hummasi(s):
    u = s["ulkeler"].get(s["oyuncuUlke"])
    if not u:
        return False
    sayi = 0
    for eyId in u["eyaletler"]:
        ey = s["eyaletler"].get(eyId)
        if ey and "demiryolu" in ey["binalar"]:
            sayi += len(ey["binalar"]["demiryolu"])
    return sayi >= 3

def _e_universite(s):
    u = s["ulkeler"].get(s["oyuncuUlke"])
    return bool(u and u["kanunlar"]["egitim"] != "kilise_okullari")

def _e_kitlik(s):
    pz = s.get("pazar", {})
    try:
        return pz["talep"]["tahil"] > 0 and (pz["arz"]["tahil"] / pz["talep"]["tahil"]) < 0.75
    except Exception:
        return False

def _e_milis(s):
    return (s["tick"] % 71) == 25

def _e_nufus(s):
    return bool(s.get("sonOzet") and s["sonOzet"].get("refahOrt", 0) > 0.60 and (s["tick"] % 89) == 55)

def _e_etnik(s):
    return bool(s.get("sonOzet") and s["sonOzet"].get("radikalizm", 0) > 0.45
                and s["oyuncuUlke"] in ("osmanli", "avusturya", "rusya"))

def _e_buhar_gemisi(s):
    u = s["ulkeler"].get(s["oyuncuUlke"])
    return bool(u and "buhar_makinesi" in u["teknoloji"]["tamamlanan"])

def _e_kodifikasyon(s):
    u = s["ulkeler"].get(s["oyuncuUlke"])
    return bool(u and u["kanunlar"]["medeniHukuk"] == "geleneksel" and s["yil"] >= 1850)

def _e_istihbarat(s):
    return (s["tick"] % 67) == 33

OLAYLAR = [
    {"id": "kolera_salgini", "tur": "genel", "baslik": "Kolera Salgını",
     "metin": "Liman kentinde kolera çıktı; mahalleler boşalıyor, pazarlar duruyor. Hekimler karantina istiyor, tüccarlar maliyetten yakınıyor.",
     "kosul": _e_kolera,
     "secenekler": [
        {"metin": "Sıkı karantina uygula (20 altın)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 20)),
                               _tumHalk(s, u, lambda p: _c_refah(p, 0.02)))},
        {"metin": "Kayıtsız devam et",
         "etki": lambda s, u: (_tumHalk(s, u, lambda p: (_c_refah(p, 0.08), _c_rad(p, 0.05))),
                               _kulupAyar(u, "sermaye", -0.05))}]},
    {"id": "afyon_savasi", "tur": "genel", "baslik": "Afyon Krizi (1839)",
     "metin": "Kanton açıklarında afyon imhası gerginliği savaşa çevirdi; denizaşırı bir güç filosu göndermeye hazırlanıyor. İmparatorluk ekonomisi gümüş akıntısıyla sarsılıyor.",
     "kosul": _e_afyon,
     "secenekler": [
        {"metin": "Direnci göğüsle (ordu yorgunluğu, prestij kazancı)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 60)),
                               u.__setitem__("prestij", min(1, u["prestij"] + 0.05)),
                               _kulupAyar(u, "ordu", 0.10))},
        {"metin": "Tazminat ödeyip kapıları aç",
         "etki": lambda s, u: (u.__setitem__("borc", u.get("borc", 0) + 120),
                               u.__setitem__("prestij", max(0, u["prestij"] - 0.10)),
                               _kulupAyar(u, "aydin", -0.05))}]},
    {"id": "tanzimat_fermani", "tur": "genel", "baslik": "Tanzimat Fermanı (1839)",
     "metin": "Bürokratlar kâğıt uzatıyor: can, mal ve namus güvencesi, düzenli vergi, adil askerlik. Yeni hukuk düzeninin ilanı bekleniyor.",
     "kosul": _e_tanzimat,
     "secenekler": [
        {"metin": "Fermanı ilan et: eşit vatandaşlık yolunda ilk adım",
         "etki": lambda s, u: (_tumHalk(s, u, lambda p: p.__setitem__("refah", min(1, p["refah"] + 0.04))),
                               _kulupAyar(u, "aydin", 0.15), _kulupAyar(u, "ruhani", -0.15), _kulupAyar(u, "memur", 0.05))},
        {"metin": "Ertelenmesin: gelenek düzeni sarsılmasın",
         "etki": lambda s, u: (_kulupAyar(u, "ruhani", 0.10), _kulupAyar(u, "aydin", -0.15))}]},
    {"id": "1848_dalgasi", "tur": "genel", "baslik": "1848 Baharı",
     "metin": "Paris'te barikatlar kuruldu; dalga Viyana'ya, Berlin'e, Milano'ya sıçradı. Sokaklar anayasa ve özgürlük istiyor; saray tereddütte.",
     "kosul": _e_1848,
     "secenekler": [
        {"metin": "Taviz ver: anayasal yola gir", "etki": _e_1848_taviz},
        {"metin": "Orduyla bastır",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 70)),
                               _kulupAyar(u, "ordu", 0.15), _kulupAyar(u, "aydin", -0.20),
                               _tumHalk(s, u, lambda p: _c_rad(p, 0.06)))}]},
    {"id": "kirim_savasi", "tur": "genel", "baslik": "Kırım Bunalımı (1853)",
     "metin": "Kutsal Topraklar üzerindeki hak iddiaları büyük güçleri karşı karşıya getirdi. Boğazlar ve denge tehlikede; müttefik arayışı başladı.",
     "kosul": _e_kirim,
     "secenekler": [
        {"metin": "Cephede karar kıl (ordu harcaması şart)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 80)),
                               u.__setitem__("prestij", min(1, u["prestij"] + 0.04)),
                               _kulupAyar(u, "ordu", 0.10))},
        {"metin": "Diplomasiyle geri çekil",
         "etki": lambda s, u: (u.__setitem__("prestij", max(0, u["prestij"] - 0.05)),
                               _kulupAyar(u, "aydin", 0.05))}]},
    {"id": "meiji_restorasyonu", "tur": "genel", "baslik": "İmparatorluk Restorasyonu (1868)",
     "metin": "Edo düştü; genç imparator \"zengin ülke, güçlü ordu\" yolunu açıyor. Şogunluk düzeni mi, hızlı modernleşme mi?",
     "kosul": _e_meiji,
     "secenekler": [
        {"metin": "Restorasyonu destekle: feodal düzen tasfiyesi", "etki": _e_meiji_destekle},
        {"metin": "Şogunluk düzenini koru",
         "etki": lambda s, u: (_kulupAyar(u, "asiret", 0.10), _kulupAyar(u, "aydin", -0.15))}]},
    {"id": "taiping_isyani", "tur": "genel", "baslik": "Taiping İsyanı (1850)",
     "metin": "Güneyde milyonları sürükleyen bir isyan patladı; vergi koleksiyonu çöktü, kentler el değiştiriyor.",
     "kosul": _e_taiping,
     "secenekler": [
        {"metin": "Ordularını seferber et (maliyetli bastırma)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 120)),
                               _kulupAyar(u, "ordu", 0.10),
                               _tumHalk(s, u, lambda p: _c_rad(p, -0.03)))},
        {"metin": "Vergi aflarıyla halkı yatıştır",
         "etki": lambda s, u: (u["vergiler"].__setitem__("alt", min(u["vergiler"].get("alt", 0.3), 0.2)),
                               _tumHalk(s, u, lambda p: _c_rad(p, -0.06)))}]},
    {"id": "amerikan_ic_savasi", "tur": "genel", "baslik": "Birlik Krizi (1861)",
     "metin": "Güney ayrılık ilan etti; birlik dağılıyor ya da savaşa yürüyor. Sanayi Kuzey'in, tarım Güney'in elinde.",
     "kosul": _e_icsavas,
     "secenekler": [
        {"metin": "Birliği koru — savaş bedeli ödensin",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 100)),
                               u.__setitem__("borc", u.get("borc", 0) + 100),
                               u.__setitem__("prestij", min(1, u["prestij"] + 0.05)),
                               _kulupAyar(u, "aydin", 0.10))},
        {"metin": "Uzlaşma yoluyla ayrılmayı kabul et",
         "etki": lambda s, u: (u.__setitem__("prestij", max(0, u["prestij"] - 0.12)),
                               _kulupAyar(u, "aydin", -0.20))}]},
    {"id": "berlin_kongresi", "tur": "genel", "baslik": "Berlin Kongresi (1878)",
     "metin": "Büyük güçler masaya oturdu; imparatorluğun toprak bütünlüğü kâğıt üzerinde yeniden çiziliyor. Savaşı kazanan değil, diplomasi yürüten kazanıyor.",
     "kosul": _e_berlin,
     "secenekler": [
        {"metin": "Masada taviz vererek barışı koru",
         "etki": lambda s, u: (u.__setitem__("prestij", max(0, u["prestij"] - 0.06)),
                               _kulupAyar(u, "ordu", -0.10))},
        {"metin": "Tavizi reddet: yeni savaş riski",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 60)),
                               _kulupAyar(u, "ordu", 0.15), _kulupAyar(u, "asiret", 0.05))}]},
    {"id": "duyun_umumiye", "tur": "genel", "baslik": "Borç Yönetimi Krizi (1881)",
     "metin": "Hazine borç servisinden yorgun; alacaklılar ortak bir borç idaresi kurup gelirlerin denetimini istiyor.",
     "kosul": _e_duyun,
     "secenekler": [
        {"metin": "Borç idaresini kabul: itibar korunur, egemenlik pazarlık konusu olur",
         "etki": lambda s, u: (u.__setitem__("borc", u.get("borc", 0) * 0.5),
                               u.__setitem__("prestij", max(0, u["prestij"] - 0.08)),
                               _kulupAyar(u, "sermaye", 0.05), _kulupAyar(u, "aydin", -0.10))},
        {"metin": "Tek taraflı moratoryum ilan et",
         "etki": lambda s, u: (u.__setitem__("borc", u.get("borc", 0) * 0.7),
                               u.__setitem__("prestij", max(0, u["prestij"] - 0.15)),
                               _kulupAyar(u, "sermaye", -0.20))}]},
    {"id": "suez_imtiyazi", "tur": "genel", "baslik": "Kanal İmtiyazı (1869)",
     "metin": "İki denizi bağlayan kanal tamamlandı; hisseleri ve imtiyazları masada. Egemenlik mi, para mı?",
     "kosul": _e_suez,
     "secenekler": [
        {"metin": "Hisseleri yabancı yatırımcıya sat (kasa dolar)",
         "etki": lambda s, u: (u.__setitem__("para", u["para"] + 120),
                               _kulupAyar(u, "sermaye", 0.05), _kulupAyar(u, "aydin", -0.05))},
        {"metin": "Hisseleri devlet alıkoyar (egemenlik tercihi)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 60)),
                               u.__setitem__("prestij", min(1, u["prestij"] + 0.05)),
                               _kulupAyar(u, "aydin", 0.10))}]},
    {"id": "isyan_kosullari", "tur": "genel", "baslik": "Sokaklar Kaynıyor",
     "metin": "Radikalizm eşiği aştı; barikatlar kuruluyor, memurlar görevden kaçıyor. Ya reform, ya demir yumruk.",
     "kosul": _e_isyan,
     "secenekler": [
        {"metin": "Orduyu meydana indir (70 altın, radikalizm düşer)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 70)),
                               _tumHalk(s, u, lambda p: _c_rad(p, -0.15)),
                               _kulupAyar(u, "ordu", 0.10), _kulupAyar(u, "aydin", -0.10))},
        {"metin": "Halkın taleplerini kararlaştır: oy hakkı reformu başlat", "etki": _e_isyan_reform}]},
    {"id": "grev_dalgasi", "tur": "genel", "baslik": "Grev Dalgası",
     "metin": "Fabrika ıslıkları sustu; işçiler ücret ve çalışma saatleri için meydanda. Sermaye kaygılı.",
     "kosul": _e_grev,
     "secenekler": [
        {"metin": "Ücret artışına aracılık et",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 30)),
                               _kulupAyar(u, "sendika", 0.15), _kulupAyar(u, "sermaye", -0.10),
                               _tumHalk(s, u, lambda p: p.__setitem__("refah", min(1, p["refah"] + 0.05)) if p["tabaka"] == "alt" else None))},
        {"metin": "Fabrikaları polisle açtır",
         "etki": lambda s, u: (_kulupAyar(u, "sendika", -0.20), _kulupAyar(u, "sermaye", 0.10),
                               _tumHalk(s, u, lambda p: _c_rad(p, 0.08) if p["tabaka"] == "alt" else None))}]},
    {"id": "banka_krizi", "tur": "genel", "baslik": "Banka Krizi",
     "metin": "Bir büyük banka kapısına kilit vurdu; panik borsaya ve kasalara sıçradı. Merkez hazinesi müdahaleyi tartışıyor.",
     "kosul": _e_banka,
     "secenekler": [
        {"metin": "Hazineden kurtarma paketi (80 altın)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 80)), _kulupAyar(u, "sermaye", 0.15))},
        {"metin": "Batmasına izin ver",
         "etki": lambda s, u: (_kulupAyar(u, "sermaye", -0.25), _kulupAyar(u, "sendika", -0.10),
                               _tumHalk(s, u, lambda p: _c_rad(p, 0.05)))}]},
    {"id": "endustri_sergisi", "tur": "genel", "baslik": "Endüstri Sergisi",
     "metin": "Dünyanın icatları sergide: buharlı motorlar, dokuma tezgâhları, telegraf. Sergiye katılım itibar ve bilgi demek.",
     "kosul": _e_sergi,
     "secenekler": [
        {"metin": "Görkemli pavilyon kur (40 altın, prestij +)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 40)),
                               u.__setitem__("prestij", min(1, u["prestij"] + 0.06)),
                               _kulupAyar(u, "aydin", 0.05))},
        {"metin": "Sadece gözlemci ol",
         "etki": lambda s, u: _kulupAyar(u, "sermaye", 0.02)}]},
    {"id": "gazete_sansuru", "tur": "genel", "baslik": "Gazete Polemiği",
     "metin": "Muhalif gazeteler hükümeti hedef aldı; sansür masası mı, basın özgürlüğü mü?",
     "kosul": _e_sansur,
     "secenekler": [
        {"metin": "Sansür uygula",
         "etki": lambda s, u: (_kulupAyar(u, "aydin", -0.20), _kulupAyar(u, "ruhani", 0.05),
                               _tumHalk(s, u, lambda p: _c_rad(p, 0.03)))},
        {"metin": "Basına serbestlik tanı",
         "etki": lambda s, u: (_kulupAyar(u, "aydin", 0.15), _kulupAyar(u, "ruhani", -0.05))}]},
    {"id": "ordu_reform_baskisi", "tur": "genel", "baslik": "Subayların Mektubu",
     "metin": "Generaller eskimiş teçhizat ve boş kasa dertli; ordu reformu talebi masada.",
     "kosul": _e_subay,
     "secenekler": [
        {"metin": "Ordu bütçesini artır",
         "etki": lambda s, u: (u["harcamalar"].__setitem__("ordu", min(1.0, u["harcamalar"].get("ordu", 0.4) + 0.2)),
                               _kulupAyar(u, "ordu", 0.15))},
        {"metin": "Mektubu cevapsız bırak",
         "etki": lambda s, u: _kulupAyar(u, "ordu", -0.10)}]},
    {"id": "goc_dalgasi", "tur": "genel", "baslik": "Göç Dalgası",
     "metin": "Komşu topraklardan on binlerce insan kaçıp sınırda toplanıyor; ekonomiye can mı, kaosa mı getirecekler?",
     "kosul": _e_goc,
     "secenekler": [
        {"metin": "Göçmenleri kabul et (nüfus ve iş gücü artar)", "etki": _e_goc_kabul},
        {"metin": "Sınırları kapat",
         "etki": lambda s, u: (_kulupAyar(u, "asiret", 0.05), _kulupAyar(u, "sermaye", -0.05))}]},
    {"id": "demiryolu_hummasi", "tur": "genel", "baslik": "Demiryolu Humması",
     "metin": "Yatırımcılar hat hisselerine akın ediyor; spekülatif balon mu, gerçek dönüşüm mü?",
     "kosul": _e_demiryolu_hummasi,
     "secenekler": [
        {"metin": "Devlet garantisi ver (hazine riske girer, sermaye coşar)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 50)), _kulupAyar(u, "sermaye", 0.15))},
        {"metin": "Spekülasyona soğuk bak",
         "etki": lambda s, u: (_kulupAyar(u, "sermaye", -0.05), _kulupAyar(u, "memur", 0.05))}]},
    {"id": "universite_kurulusu", "tur": "genel", "baslik": "Büyük Üniversite Kuruluşu",
     "metin": "Aydınlar modern bir üniversite için bağış topladı; devlet himayesi bekleniyor.",
     "kosul": _e_universite,
     "secenekler": [
        {"metin": "Devlet himayesi sağla (30 altın, aydın memnuniyeti)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 30)),
                               _kulupAyar(u, "aydin", 0.15), _kulupAyar(u, "memur", 0.05))},
        {"metin": "Bağışlarla idare etsinler",
         "etki": lambda s, u: _kulupAyar(u, "aydin", -0.03)}]},
    {"id": "kitlik_riski", "tur": "genel", "baslik": "Kıtlık Sınırlarında",
     "metin": "Tahıl fiyatları tırmanıyor; ambarlar boş, halk endişeli. İthalat mı, serbest bırakma mı?",
     "kosul": _e_kitlik,
     "secenekler": [
        {"metin": "Acil tahıl ithalatı (50 altın)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 50)),
                               s["pazar"]["arz"].__setitem__("tahil", s["pazar"]["arz"].get("tahil", 0) + 100))},
        {"metin": "Pazar kendini düzenlesin",
         "etki": lambda s, u: _tumHalk(s, u, lambda p: (_c_refah(p, 0.05), _c_rad(p, 0.04)))}]},
    {"id": "milis_gerilimi", "tur": "genel", "baslik": "Sınır Olayı",
     "metin": "Sınır kasabasında silahlı çatışma çıktı; komşu devlet nota verdi. Yumuşatma mı, caydırıcılık mı?",
     "kosul": _e_milis,
     "secenekler": [
        {"metin": "Sınırı takviye et (ordu gösterisi, 30 altın)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 30)), _kulupAyar(u, "ordu", 0.10))},
        {"metin": "Diplomatik açıklamayla yatıştır",
         "etki": lambda s, u: u.__setitem__("prestij", max(0, u["prestij"] - 0.02))}]},
    {"id": "nufus_patlamasi", "tur": "genel", "baslik": "Yeni Nesil",
     "metin": "Refah yükselirken doğumlar arttı; kentler gençleşiyor. Okullar ve meskenler için plan yapmak lazım.",
     "kosul": _e_nufus,
     "secenekler": [
        {"metin": "Yeni kent planlamasına bütçe ayır (40 altın)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 40)),
                               _tumHalk(s, u, lambda p: p.__setitem__("refah", min(1, p["refah"] + 0.03))),
                               _kulupAyar(u, "memur", 0.05))},
        {"metin": "Pazar koşullarına bırak",
         "etki": lambda s, u: _kulupAyar(u, "sermaye", 0.05)}]},
    {"id": "etnik_gerilim", "tur": "genel", "baslik": "Cemaat Gerilimi",
     "metin": "İki cemaat arasında kan davası büyüyor; önde gelenler arabulucu olmayı öneriyor. Eşit vatandaşlık mı, eski düzen mi?",
     "kosul": _e_etnik,
     "secenekler": [
        {"metin": "Cemaat temsilcileriyle ortak komisyon kur",
         "etki": lambda s, u: (_kulupAyar(u, "ruhani", 0.05), _kulupAyar(u, "aydin", 0.05),
                               _tumHalk(s, u, lambda p: _c_rad(p, -0.04)))},
        {"metin": "Olayları yalnızca güvenlik güçleriyle yönet",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 25)),
                               _kulupAyar(u, "asiret", -0.10),
                               _tumHalk(s, u, lambda p: _c_rad(p, 0.03)))}]},
    {"id": "buhar_gemisi_yarisi", "tur": "genel", "baslik": "Atlas Yarışı",
     "metin": "Buharlı gemi şirketleri okyanus rekoru için yarışıyor; devlet bayrağı taşıyan kazanacak. Donanma ve ticaret itibarı masada.",
     "kosul": _e_buhar_gemisi,
     "secenekler": [
        {"metin": "Ulusal şirketi sübvansiyonla destekle (35 altın)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 35)),
                               u.__setitem__("prestij", min(1, u["prestij"] + 0.04)),
                               _kulupAyar(u, "sermaye", 0.08))},
        {"metin": "Yarışa karışma",
         "etki": lambda s, u: _kulupAyar(u, "sermaye", -0.03)}]},
    {"id": "hukuk_kodifikasyonu", "tur": "genel", "baslik": "Kanunlaştırma Seferberliği",
     "metin": "Hukukçular dağınık emirleri tek kanun derlemesinde toplamak istiyor; bürokrasi ve ruhani sınıf karşı karşıya.",
     "kosul": _e_kodifikasyon,
     "secenekler": [
        {"metin": "Kanunlaştırma komisyonu kur",
         "etki": lambda s, u: (_kulupAyar(u, "memur", 0.10), _kulupAyar(u, "ruhani", -0.08),
                               u["kanunGecisleri"].setdefault("medeniHukuk", {"yeniDeger": "uygar_medeni", "kalanAy": 20}))},
        {"metin": "Geleneksel hukuk korunmalı",
         "etki": lambda s, u: (_kulupAyar(u, "ruhani", 0.08), _kulupAyar(u, "aydin", -0.08))}]},
    {"id": "istihbarat_agi", "tur": "genel", "baslik": "İstihbarat Ağı Teklifi",
     "metin": "İçişleri bürokratları gizli bir istihbarat ağı kurmayı teklif ediyor; reform karşıtlarını izlerken memnuniyetsizlik de büyüyecek.",
     "kosul": _e_istihbarat,
     "secenekler": [
        {"metin": "Ağı kur (25 altın)",
         "etki": lambda s, u: (u.__setitem__("para", max(0, u["para"] - 25)),
                               _kulupAyar(u, "memur", 0.08), _kulupAyar(u, "aydin", -0.08),
                               _tumHalk(s, u, lambda p: _c_rad(p, 0.02)))},
        {"metin": "Açık devlet ilkesini savun",
         "etki": lambda s, u: (_kulupAyar(u, "aydin", 0.08), _kulupAyar(u, "memur", -0.05))}]},
    # ---- YENİ: yetenek sinerjili olaylar (8% kapısını bypass eder) ----
    {"id": "tahvil_sahipleri", "tur": "yetenek", "baslik": "Tahvil Sahipleri Ayakta",
     "metin": "İç borçlanmanın tahvil sahipleri hükümet sarayının kapısına dayandı: \"Faiz ya taksit.\" Kasalar boş, gazeteler uğulduyor.",
     "kosul": _e_tahvil,
     "secenekler": [
        {"metin": "Faizi kabul et (borç +60, güvenilir devlet)",
         "etki": lambda s, u: (u.__setitem__("borc", u.get("borc", 0) + 60),
                               _tumHalk(s, u, lambda p: _c_rad(p, 0.02)),
                               u.__setitem__("prestij", min(1, u["prestij"] + 0.01)))},
        {"metin": "Reddet ve burun çevir (İç Borçlanma beklemesi +24 ay)", "etki": _e_tahvil_reddet}]},
    {"id": "seferberlik_faturasi", "tur": "yetenek", "baslik": "Seferberliğin Faturası",
     "metin": "Silahlar kundaklandı ama tarlalarda erkek eksikliği hasadı tehdit ediyor. Köy ağaları saraya dilekçe yolladı.",
     "kosul": _e_seferberlik_fatura,
     "secenekler": [
        {"metin": "Ücretli terhis (50 altın)",
         "etki": lambda s, u: u.__setitem__("para", max(0, u["para"] - 50))},
        {"metin": "Boş ver, kendi hallerinde",
         "etki": lambda s, u: _tumHalk(s, u, lambda p: (_c_refah(p, 0.04), _c_rad(p, 0.03)))}]},
    {"id": "elci_valizi", "tur": "yetenek", "baslik": "Elçinin Kayıp Valizi",
     "metin": "Elçinin hediye valizi gümrükte kayboldu; hedef ülkenin gazeteleri skandalı manşet yaptı.",
     "kosul": _e_elci_valizi,
     "secenekler": [
        {"metin": "Skandalı ört, yeniden gönder (40 altın, ilişki +4)", "etki": _e_valiz_ort},
        {"metin": "Gümrük müdürünü azlet (prestij -, radikalizm -)",
         "etki": lambda s, u: (u.__setitem__("prestij", max(0, u["prestij"] - 0.02)),
                               _tumHalk(s, u, lambda p: _c_rad(p, -0.02)))}]},
]

# ---------------- YETENEKLER (YENİ SİSTEM) ----------------
# kilit: {"prestij": x} veya {} — sağlanmıyorsa buton pasif ve sebebini gösterir.
YETENEKLER = [
    # --- ASKERİ ---
    {"id": "mobilization", "ad": "Genel Seferberlik", "kategori": "Askeri", "ikon": "kalkan",
     "aciklama": "Orduyu tam teçhizatla savaşa hazırlar; kısa süreli askeri güç patlaması sağlar. Depolar boşalır, silah tüccarları altın sayar.",
     "maliyet": 100, "bekleme": 36, "sure": 12, "kilit": {},
     "etkiMetni": "12 ay boyunca askeri güç ×1.20."},
    {"id": "rapid_offensive", "ad": "Yıldırım Taarruzu", "kategori": "Askeri", "ikon": "kilic",
     "aciklama": "Cephede planlı bir genel taarruz başlatır; savaş ilerlemesini garanti biçimde ileri taşır — ama cephe kayıpları halka ağır gelir.",
     "maliyet": 90, "bekleme": 30, "sure": 0, "kilit": {"prestij": 0.45},
     "etkiMetni": "Savaş ilerlemesi +8 (anlık); radikalizm +0.02. Savaş gerektirir."},
    {"id": "defensive_line", "ad": "Tahkimat Hattı", "kategori": "Askeri", "ikon": "sur",
     "aciklama": "Sınır boyunca siper ve tahkimat örer; düşmanın cephede kazanmış olduğu ilerlemeyi yavaşlatır.",
     "maliyet": 70, "bekleme": 30, "sure": 12, "kilit": {},
     "etkiMetni": "12 ay boyunca düşmanın aylık ilerleme kazanımı ×0.6. Savaş gerektirir."},
    # --- EKONOMİ ---
    {"id": "war_bonds", "ad": "İç Borçlanma", "kategori": "Ekonomi", "ikon": "tahvil",
     "aciklama": "Yurttaşlara ve tüccarlara tahvil satar; kasayı anında doldurur ama taksitler yıllarca bütçeyi yorar.",
     "maliyet": 0, "bekleme": 48, "sure": 24, "kilit": {},
     "etkiMetni": "Anında +150 altın ve +150 borç; 24 ay boyunca −8 altın/ay taksit."},
    {"id": "trade_agreements", "ad": "Ticaret Anlaşmaları", "kategori": "Ekonomi", "ikon": "gemi",
     "aciklama": "Komşu pazarlarla tercih gümrük anlaşmaları imzalar; aylık ticaret gelirini iki yıl boyunca artırır.",
     "maliyet": 120, "bekleme": 36, "sure": 24, "kilit": {"prestij": 0.40},
     "etkiMetni": "24 ay boyunca bütçeye +7 altın/ay."},
    {"id": "infrastructure_drive", "ad": "Altyapı Seferberliği", "kategori": "Ekonomi", "ikon": "vinç",
     "aciklama": "Yol, köprü ve tersane kervanlarına devlet desteği; bütün yapım işleri hızlanır.",
     "maliyet": 100, "bekleme": 36, "sure": 24, "kilit": {},
     "etkiMetni": "24 ay boyunca tüm inşaatlar %25 hızlanır."},
    # --- TOPLUM ---
    {"id": "education_campaign", "ad": "Aydınlanma Hamlesi", "kategori": "Toplum", "ikon": "kitap",
     "aciklama": "Okul ve matbaa ağına acil yatırım; devletin ilerleme üretimi hızlanır.",
     "maliyet": 90, "bekleme": 36, "sure": 24, "kilit": {},
     "etkiMetni": "24 ay boyunca aylık araştırma ilerlemesi +0.5."},
    {"id": "national_festival", "ad": "Ulusal Bayram", "kategori": "Toplum", "ikon": "fener",
     "aciklama": "Bütün ülke bayram eder; halkın devlete güveni artar, radikaller meydanlarda sessizleşir.",
     "maliyet": 60, "bekleme": 24, "sure": 12, "kilit": {},
     "etkiMetni": "12 ay boyunca radikalizm −0.005/ay; refah +0.03 ve prestij +0.01 anında."},
    # --- DİPLOMASİ ---
    {"id": "envoy_mission", "ad": "Elçi Heyeti", "kategori": "Diplomasi", "ikon": "elci",
     "aciklama": "Hediyeler ve nüfuz dolu bir elçi heyeti gönderilir; seçtiğin ülkeyle ilişkiler düzelir.",
     "maliyet": 50, "bekleme": 18, "sure": 0, "kilit": {},
     "etkiMetni": "Seçilen ülkeyle ilişki +12 (aynı hedefe tekrarda azalır, alt sınır +4)."},
    {"id": "security_pact", "ad": "Güvenlik Paktı", "kategori": "Diplomasi", "ikon": "pakt",
     "aciklama": "Güçlü bir komşuyla saldırmazlık anlaşması gizli maddelerle mühürlenir; iki devlet birbirine savaş ilan edemez.",
     "maliyet": 80, "bekleme": 48, "sure": 24, "kilit": {"prestij": 0.45},
     "etkiMetni": "Seçilen ülkeyle 24 ay çift yönlü savaş yasağı; ilişki +8. Bozma: prestij −0.05."},
]

YETENEK_KATEGORILERI = ["Askeri", "Ekonomi", "Toplum", "Diplomasi"]

# zorluk ayarları: AI çarpanı ve oyuncu yetenek maliyeti çarpanı
ZORLUKLAR = {
    "kolay":  {"ad": "Kolay",  "aiGelir": 0.70, "aiSaldirganlik": 0.7, "yetenekMaliyet": 0.80,
               "aciklama": "AI zayıf ve pasif; yetenekler %20 ucuz."},
    "normal": {"ad": "Normal", "aiGelir": 1.00, "aiSaldirganlik": 1.0, "yetenekMaliyet": 1.00,
               "aciklama": "Dengeli deneyim; oyunun kuraldışı tarafı yok."},
    "zor":    {"ad": "Zor",    "aiGelir": 1.35, "aiSaldirganlik": 1.3, "yetenekMaliyet": 1.25,
               "aciklama": "AI zengin ve saldırgan; yetenekler %25 pahalı."},
}

# ---------------- SKOR ----------------
SKOR_FORMULU = {
    "gsyh": 0.20, "refah": 0.20, "duzen": 0.15, "eyalet": 0.10, "hukuk": 0.10, "teknoloji": 0.15, "prestij": 0.10,
    "gsyhReferans": 1200, "eyaletReferans": 7, "teknolojiReferans": 15,
}

def mal_bul(mal_id):
    for m in MALLAR:
        if m["id"] == mal_id:
            return m
    return None

def bina_bul(bina_id):
    for b in BINALAR:
        if b["id"] == bina_id:
            return b
    return None

def tech_bul(tech_id):
    for t in TEKNOLOJILER:
        if t["id"] == tech_id:
            return t
    return None

def ulke_bul(ulke_id):
    for u in ULKELER:
        if u["id"] == ulke_id:
            return u
    return None

def eyalet_bul(ey_id):
    for e in EYALETLER:
        if e["id"] == ey_id:
            return e
    return None

def kulup_bul(kulup_id):
    for k in KULUPLER:
        if k["id"] == kulup_id:
            return k
    return None
