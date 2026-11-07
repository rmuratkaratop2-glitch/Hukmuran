# -*- coding: utf-8 -*-
"""
ui.py — HÜKMÜMRAN pygame arayüzü
Menü (ülke+zorluk seçimi), oyun ekranı (harita + 7 sekme), olay modali, sonuç ekranı.
"""
import math
import os
import json

import pygame

import data as D
import engine as E

# ---------------- sabitler ----------------
W, H = 1280, 800
FPS = 60
HIZ_MS = [0, 1000, 250, 80]

# renk paleti (koyu, dönemin mürekkep tonları)
ARKA = (24, 22, 20)
PANEL = (36, 33, 30)
PANEL2 = (46, 42, 38)
CIZGI = (70, 64, 56)
YAZI = (225, 218, 205)
SOLUK = (150, 143, 130)
ALTIN = (212, 175, 85)
YESIL = (110, 170, 110)
KIRMIZI = (200, 90, 80)
MAVI = (110, 150, 200)
TURUNCU = (210, 150, 80)
MOR = (160, 120, 190)
DENIZ = (26, 32, 44)

FONTLAR = {}


def fontYukle():
    FONTLAR["kucuk"] = pygame.font.SysFont("tahoma,segoeui,arial", 13)
    FONTLAR["normal"] = pygame.font.SysFont("tahoma,segoeui,arial", 15)
    FONTLAR["orta"] = pygame.font.SysFont("tahoma,segoeui,arial", 18)
    FONTLAR["buyuk"] = pygame.font.SysFont("tahoma,segoeui,arial", 24, bold=True)
    FONTLAR["dev"] = pygame.font.SysFont("tahoma,segoeui,arial", 40, bold=True)


def F(ad):
    return FONTLAR.get(ad) or FONTLAR["normal"]


# ---------------- metin yardımcıları ----------------
def satirlaraBol(metin, font, genislik):
    satirlar = []
    for parca in str(metin).split("\n"):
        kelimeler = parca.split(" ")
        satir = ""
        for k in kelimeler:
            dene = (satir + " " + k).strip()
            if font.size(dene)[0] <= genislik or not satir:
                satir = dene
            else:
                satirlar.append(satir)
                satir = k
        satirlar.append(satir)
    return satirlar


def yaziCiz(yuzey, metin, font, renk, x, y, genislik=None):
    """Tek satır; genislik verilirse taşarsa kırpar. Kullanılan yükseklik döner."""
    if genislik:
        while metin and font.size(metin)[0] > genislik:
            metin = metin[:-1]
    img = font.render(metin, True, renk)
    yuzey.blit(img, (x, y))
    return img.get_height()


def paragrafCiz(yuzey, metin, font, renk, x, y, genislik, satirAraligi=1.25):
    satirlar = satirlaraBol(metin, font, genislik)
    aralik = int(font.get_height() * satirAraligi)
    for i, satir in enumerate(satirlar):
        yuzey.blit(font.render(satir, True, renk), (x, y + i * aralik))
    return len(satirlar) * aralik


# ---------------- widget motoru ----------------
class Ui:
    """Her çerçevede yeniden doldurulan tıklanabilir alan listesi."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.butonlar = []   # (rect, cb, enabled, hover_text)
        self.bolgeler = []   # (rect, cb) — panel tıkları (harita vb.)
        self.kaydirma = {}   # panel anahtarı → scroll offset
        self.hoverTip = None  # (pos, metin)

    def buton(self, yuzey, rect, metin, cb, etkin=True, secili=False, renk=None, hover=None, font="normal"):
        pygame.draw.rect(yuzey, PANEL2 if not secili else (60, 54, 40), rect, border_radius=4)
        pygame.draw.rect(yuzey, ALTIN if secili else (CIZGI if etkin else (45, 42, 38)), rect, 2, border_radius=4)
        r = pygame.Rect(rect)
        satirlar = satirlaraBol(metin, F(font), r.width - 12)
        toplam = len(satirlar) * F(font).get_height()
        yy = r.y + (r.height - toplam) // 2
        c = (YAZI if etkin else (95, 90, 82))
        if renk:
            c = renk if etkin else (95, 90, 82)
        for s in satirlar:
            img = F(font).render(s, True, c)
            yuzey.blit(img, (r.x + 6, yy))
            yy += F(font).get_height()
        if etkin:
            self.butonlar.append((pygame.Rect(rect), cb, True, hover))
        elif hover:
            self.butonlar.append((pygame.Rect(rect), None, False, hover))
        return rect

    def etiket(self, yuzey, rect, metin, cb, hover=None, font="normal"):
        """Şeffaf tıklama bölgesi."""
        self.butonlar.append((pygame.Rect(rect), cb if cb else (lambda: None), True, hover))

    def kaydirAl(self, anahtar):
        return self.kaydirma.get(anahtar, 0)

    def kaydirAyarla(self, anahtar, deger):
        self.kaydirma[anahtar] = deger


UI = Ui()


class Slider:
    def __init__(self, x, y, w, deger, cb):
        self.rect = pygame.Rect(x, y, w, 18)
        self.deger = deger  # 0..1
        self.cb = cb
        self.surukle = False

    def ciz(self, yuzey, etiketMetni, renk=MAVI):
        r = self.rect
        pygame.draw.rect(yuzey, (55, 50, 45), (r.x, r.y + 7, r.width, 4), border_radius=2)
        doldur = int(r.width * self.deger)
        pygame.draw.rect(yuzey, renk, (r.x, r.y + 7, doldur, 4), border_radius=2)
        hx = r.x + doldur
        pygame.draw.circle(yuzey, (230, 224, 210), (hx, r.y + 9), 7)
        pygame.draw.circle(yuzey, renk, (hx, r.y + 9), 5)
        if etiketMetni:
            yaziCiz(yuzey, etiketMetni, F("kucuk"), SOLUK, r.x, r.y - 16)

    def olay(self, e, mouse):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(mouse) or pygame.Rect(self.rect.x - 6, self.rect.y - 6, self.rect.width + 12, self.rect.height + 12).collidepoint(mouse):
                self.surukle = True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.surukle = False
        if self.surukle and e.type == pygame.MOUSEMOTION:
            oran = (mouse[0] - self.rect.x) / max(self.rect.width, 1)
            yeni = min(1.0, max(0.0, oran))
            if abs(yeni - self.deger) > 0.005:
                self.deger = yeni
                if self.cb:
                    self.cb(yeni)


# ---------------- uygulama durumu ----------------
class App:
    def __init__(self):
        self.ekran = "menu"      # menu | oyun | sonuc
        self.state = None        # engine state
        self.hiz = 1
        self.acc = 0.0
        self.seciliEy = None
        self.sekme = "ozet"
        self.mesaj = None        # (metin, kalan_saniye)
        self.seciliYetenek = None  # hedef gerekli yetenek bekleyen
        self.menuZorluk = "normal"
        self.menuSeciliUlke = None
        self.menuNasil = False
        self.kayitListesi = []
        self.scroll = {}
        self.sliderlar = []      # her çerçeve yeniden kurulur
        self.haritaZoom = 1.0
        self.haritaPan = [0, 0]
        self.haritaSurukle = None
        self.enIyiSkor = self._enIyiOku()

    def _enIyiOku(self):
        yol = os.path.join(E.SAVE_KLASOR, "en_iyi.json")
        try:
            with open(yol, "r", encoding="utf-8") as f:
                return json.load(f).get("skor", 0.0)
        except Exception:
            return 0.0

    def _enIyiYaz(self, skor):
        try:
            os.makedirs(E.SAVE_KLASOR, exist_ok=True)
            with open(os.path.join(E.SAVE_KLASOR, "en_iyi.json"), "w", encoding="utf-8") as f:
                json.dump({"skor": skor}, f)
        except Exception:
            pass

    # ---- akış ----
    def yeniOyun(self, ulkeId):
        self.state = E.yeniOyun(ulkeId, self.menuZorluk)
        self.hiz = 1
        self.acc = 0
        self.seciliEy = None
        self.sekme = "ozet"
        self.ekran = "oyun"
        self.mesajla("Oyun başladı: " + self.state["ulkeler"][ulkeId]["ad"])

    def kaydet(self, slot):
        if not self.state:
            return
        E.kaydet(self.state, slot)
        self.mesajla("Kaydedildi (Slot %d)." % slot)

    def yukle(self, slot):
        s, hata = E.yukle(slot)
        if hata:
            self.mesajla(hata)
            return
        self.state = s
        self.hiz = 1 if not s["oyunBitti"] else 0
        self.ekran = "oyun" if not s["oyunBitti"] else "sonuc"
        self.seciliEy = None
        self.mesajla("Kayıt yüklendi.")

    def anaMenu(self):
        self.ekran = "menu"
        self.state = None
        self.kayitListesi = E.kayitMetasi()

    def mesajla(self, metin):
        self.mesaj = [metin, 4.0]

    # ---- tick ----
    def guncelle(self, dt):
        if self.mesaj:
            self.mesaj[1] -= dt
            if self.mesaj[1] <= 0:
                self.mesaj = None
        if self.ekran != "oyun" or not self.state:
            return
        ms = HIZ_MS[self.hiz] if 0 <= self.hiz < len(HIZ_MS) else 0
        olayAcik = bool(self.state["olaylar"]["aktif"])
        if ms <= 0 or olayAcik or self.state["oyunBitti"]:
            return
        self.acc += dt * 1000.0
        guvenlik = 0
        while self.acc >= ms and guvenlik < 8:
            self.acc -= ms
            E.tick(self.state)
            guvenlik += 1
            if self.state["olaylar"]["aktif"] or self.state["oyunBitti"]:
                self.acc = 0
                break


APP = None


def skorHesapla(s):
    Fk = D.SKOR_FORMULU
    ozet = s["sonOzet"]
    u = s["ulkeler"][s["oyuncuUlke"]]

    def norm(v, ref):
        if not v or v <= 0 or not ref:
            return 0.0
        return min(v / ref, 1.5)

    def hukukIlerleme():
        toplam, sayac = 0.0, 0
        for kat, secenekler in D.KANUNLAR.items():
            mevcut = u["kanunlar"].get(kat)
            idx = next((i for i, x in enumerate(secenekler) if x["id"] == mevcut), 0)
            if idx > 0:
                toplam += idx / max(len(secenekler) - 1, 1)
                sayac += 1
        return toplam / sayac if sayac else 0.0

    p = {}
    p["gsyhPuan"] = norm(ozet["gsyh"], Fk["gsyhReferans"]) * Fk["gsyh"]
    p["refahPuan"] = ozet["refahOrt"] * Fk["refah"]
    p["duzenPuan"] = (1 - ozet["radikalizm"]) * Fk["duzen"]
    p["eyaletPuan"] = norm(ozet["eyaletSayisi"], Fk["eyaletReferans"]) * Fk["eyalet"]
    p["hukukPuan"] = hukukIlerleme() * Fk["hukuk"]
    p["teknolojiPuan"] = norm(len(u["teknoloji"]["tamamlanan"]), Fk["teknolojiReferans"]) * Fk["teknoloji"]
    p["prestijPuan"] = ozet["prestij"] * Fk["prestij"]
    toplam = sum(p.values())
    itibar = ("Geri Kalmış Devlet" if toplam < 0.3 else
              "Modernleşen Devlet" if toplam < 0.5 else
              "Büyük Güç" if toplam < 0.7 else "HÜKMÜMRAN")
    p["toplam"] = toplam
    p["itibar"] = itibar
    return p


# ---------------- çizim: menü ----------------
def menuCiz(yuzey):
    yuzey.fill(ARKA)
    # başlık
    baslik = F("dev").render("HÜKMÜMRAN", True, ALTIN)
    yuzey.blit(baslik, (W // 2 - baslik.get_width() // 2, 40))
    alt = F("orta").render("Sanayi Çağı · 1836–1936 · Python Sürümü", True, SOLUK)
    yuzey.blit(alt, (W // 2 - alt.get_width() // 2, 96))

    # zorluk seçimi
    yaziCiz(yuzey, "Zorluk", F("orta"), YAZI, 120, 150)
    zx = 120
    for zid, z in D.ZORLUKLAR.items():
        r = pygame.Rect(zx, 180, 150, 34)
        UI.buton(yuzey, r, z["ad"], (lambda zid=zid: setattr(APP, "menuZorluk", zid)),
                 etkin=True, secili=(APP.menuZorluk == zid))
        # açıklama altına küçük
        paragrafCiz(yuzey, z["aciklama"], F("kucuk"), SOLUK, zx, 218, 150)
        zx += 165

    # ülke kartları 3×3
    yaziCiz(yuzey, "Bir Devlet Seçin", F("orta"), YAZI, 120, 260)
    kartW, kartH = 340, 92
    for i, u in enumerate(D.ULKELER):
        col, row = i % 3, i // 3
        r = pygame.Rect(120 + col * (kartW + 14), 292 + row * (kartH + 12), kartW, kartH)
        secili = (APP.menuSeciliUlke == u["id"])
        pygame.draw.rect(yuzey, (44, 40, 36) if not secili else (58, 52, 40), r, border_radius=6)
        pygame.draw.rect(yuzey, ALTIN if secili else CIZGI, r, 2, border_radius=6)
        pygame.draw.circle(yuzey, pygame.Color(u["renk"]), (r.x + 26, r.y + 26), 13)
        yaziCiz(yuzey, u["ad"], F("orta"), YAZI, r.x + 48, r.y + 12, kartW - 60)
        paragrafCiz(yuzey, u["ozet"], F("kucuk"), SOLUK, r.x + 48, r.y + 40, kartW - 60)
        prestij = u.get("prestijBaslangic", 0.3)
        zorEtiket = "Kolay" if prestij >= 0.6 else ("Zor" if prestij <= 0.35 else "Orta")
        rc = KIRMIZI if zorEtiket == "Zor" else (YESIL if zorEtiket == "Kolay" else TURUNCU)
        yaziCiz(yuzey, zorEtiket, F("kucuk"), rc, r.x + kartW - 52, r.y + 12)
        UI.etiket(yuzey, r, u["ad"], (lambda uid=u["id"]: setattr(APP, "menuSeciliUlke", uid)))

    # başlat + kayıtlar + nasıl oynanır
    altY = 292 + 3 * (kartH + 12) + 8
    UI.buton(yuzey, pygame.Rect(120, altY, 240, 44), "YENİ OYUN BAŞLAT", (lambda: APP.yeniOyun(APP.menuSeciliUlke) if APP.menuSeciliUlke else APP.mesajla("Önce bir devlet seçin.")),
             etkin=bool(APP.menuSeciliUlke), renk=(220, 200, 150), font="orta")
    UI.buton(yuzey, pygame.Rect(375, altY, 150, 44), "Nasıl Oynanır?", (lambda: setattr(APP, "menuNasil", not APP.menuNasil)), font="orta")

    # kayıt slotları
    kx = 560
    yaziCiz(yuzey, "Kayıtlar", F("orta"), YAZI, kx, altY - 4)
    kayitlar = {k["slot"]: k for k in E.kayitMetasi()}
    for slot in (1, 2, 3):
        k = kayitlar.get(slot)
        metin = "Slot %d: %s (%s)" % (slot, k["ulkeAd"], k["yil"]) if k else "Slot %d: boş" % slot
        ry = altY + 26 * slot - 10
        yaziCiz(yuzey, metin, F("kucuk"), YAZI if k else SOLUK, kx, ry)
        if k and not k["bitmis"]:
            UI.buton(yuzey, pygame.Rect(kx + 240, ry - 3, 70, 22), "Yükle", (lambda s=slot: APP.yukle(s)), font="kucuk")

    # nasıl oynanır paneli
    if APP.menuNasil:
        r = pygame.Rect(120, altY + 60, W - 240, 200)
        pygame.draw.rect(yuzey, PANEL, r, border_radius=8)
        pygame.draw.rect(yuzey, CIZGI, r, 2, border_radius=8)
        metin = ("AMAÇ: 1936'da en yüksek skoru yap. Skor = GSYH + refah + düşük radikalizm + eyalet + hukuk + teknoloji + prestij.\n"
                 "HARİTA: Eyaletlere tıklayın; sol altta inşaat paneli açılır. Tekerlek: yakınlaştır, sağ tuşla sürükle: kaydır.\n"
                 "SEKMELER: Özet · Ekonomi (vergi/harcama slider) · Hukuk (reform) · Teknoloji (araştırma) · Diplomasi · YETENEKLER (yeni!) · Günlük.\n"
                 "YETENEKLER: Altınla aktif güç kullanın; ayda 1 yetenek. Savaş gerektirenler ve hedef isteyenler işaretlidir.\n"
                 "TUŞLAR: Boşluk duraklat/devam · 1/2/3 hız · S hızlı kayıt · ESC menü.")
        paragrafCiz(yuzey, metin, F("kucuk"), YAZI, r.x + 14, r.y + 12, r.width - 28)

    # alt bilgi
    yaziCiz(yuzey, "Victoria 3 esinli büyük strateji · Tarayıcı sürümünden Python/pygame'e taşınmıştır", F("kucuk"), SOLUK, 120, H - 34)


# ---------------- çizim: harita ----------------
def haritaNokta(ey):
    """Harita dünya noktası → ekran noktası."""
    a = APP
    mx, my = ey["mx"], ey["my"]
    olcek = 0.66 * a.haritaZoom
    cx, cy = 10 + 690 // 2, 70 + 545 // 2
    return (int(cx + (mx - 500) * olcek + a.haritaPan[0]),
            int(cy + (my - 330) * olcek + a.haritaPan[1]))


def haritaCiz(yuzey):
    a = APP
    s = a.state
    alan = pygame.Rect(10, 70, 690, 545)
    pygame.draw.rect(yuzey, DENIZ, alan, border_radius=6)
    pygame.draw.rect(yuzey, CIZGI, alan, 2, border_radius=6)
    # parke grid
    for gx in range(alan.x + 40, alan.right, 60):
        pygame.draw.line(yuzey, (31, 38, 50), (gx, alan.y + 4), (gx, alan.bottom - 4))
    for gy in range(alan.y + 40, alan.bottom, 60):
        pygame.draw.line(yuzey, (31, 38, 50), (alan.x + 4, gy), (alan.right - 4, gy))

    yuzey.set_clip(alan)
    # pakt çizgileri
    oyuncu = s["ulkeler"][s["oyuncuUlke"]]
    for hedefId in oyuncu.get("paktlar", {}):
        hedefEy = next((e for e in D.EYALETLER if e["id"] == (s["ulkeler"][hedefId]["eyaletler"] or [None])[0]), None)
        oyuncuEy = next((e for e in D.EYALETLER if e["id"] == (oyuncu["eyaletler"] or [None])[0]), None)
        if hedefEy and oyuncuEy:
            p1, p2 = haritaNokta(oyuncuEy), haritaNokta(hedefEy)
            pygame.draw.line(yuzey, MOR, p1, p2, 2)
    # ittifak çizgileri
    for hedefId in oyuncu["ittifaklar"]:
        hedefUlke = s["ulkeler"].get(hedefId)
        hedefEy = next((e for e in D.EYALETLER if e["id"] == (hedefUlke["eyaletler"] or [None])[0]), None)
        oyuncuEy = next((e for e in D.EYALETLER if e["id"] == (oyuncu["eyaletler"] or [None])[0]), None)
        if hedefEy and oyuncuEy:
            p1, p2 = haritaNokta(oyuncuEy), haritaNokta(hedefEy)
            pygame.draw.line(yuzey, YESIL, p1, p2, 2)

    mouse = pygame.mouse.get_pos()
    for ey in D.EYALETLER:
        es = s["eyaletler"].get(ey["id"])
        if not es:
            continue
        ulke = s["ulkeler"].get(es["ulkeId"])
        renk = pygame.Color(ulke["renk"]) if ulke else pygame.Color("#555555")
        px, py = haritaNokta(ey)
        r = int((9 + 26 * math.sqrt(min(ey["nufus"], 30_000_000) / 30_000_000)) * (0.8 + 0.2 * a.haritaZoom))
        secili = (a.seciliEy == ey["id"])
        hover = pygame.Rect(px - r - 3, py - r - 3, (r + 3) * 2, (r + 3) * 2).collidepoint(mouse)
        # savaş halinde kenar
        savas = any(x["rakip"] == s["oyuncuUlke"] for x in ulke["savaslar"]) if ulke else False
        pygame.draw.circle(yuzey, renk, (px, py), r)
        pygame.draw.circle(yuzey, (240, 235, 220) if secili else ((250, 90, 70) if savas else (20, 18, 16)), (px, py), r, 3 if secili else 2)
        if hover:
            pygame.draw.circle(yuzey, (255, 255, 255), (px, py), r + 4, 1)
        adImg = F("kucuk").render(ey["ad"], True, (235, 230, 218))
        yuzey.blit(adImg, (px - adImg.get_width() // 2, py + r + 2))
        # tıklama bölgesi
        UI.butonlar.append((pygame.Rect(px - r - 2, py - r - 2, (r + 2) * 2, (r + 2) * 2),
                            (lambda eid=ey["id"]: setattr(APP, "seciliEy", eid)), True, None))
    yuzey.set_clip(None)

    # harita kontrolleri
    zx = alan.right - 92
    UI.buton(yuzey, pygame.Rect(zx, alan.y + 8, 26, 24), "+", (lambda: setattr(APP, "haritaZoom", min(2.2, APP.haritaZoom * 1.15))), font="orta")
    UI.buton(yuzey, pygame.Rect(zx + 30, alan.y + 8, 26, 24), "−", (lambda: setattr(APP, "haritaZoom", max(0.7, APP.haritaZoom / 1.15))), font="orta")
    UI.buton(yuzey, pygame.Rect(zx + 60, alan.y + 8, 32, 24), "Sıfır", (lambda: (setattr(APP, "haritaZoom", 1.0), APP.haritaPan.__setitem__(0, 0), APP.haritaPan.__setitem__(1, 0))), font="kucuk")
    yaziCiz(yuzey, "Ovalar: yeşil çizgi ittifak, mor çizgi pakt, kırmızı kenar savaş", F("kucuk"), SOLUK, alan.x + 10, alan.bottom - 20)


# ---------------- çizim: üst şerit ----------------
def ustSeritCiz(yuzey):
    a = APP
    s = a.state
    u = s["ulkeler"][s["oyuncuUlke"]]
    ozet = s["sonOzet"]
    uref = D.ulke_bul(s["oyuncuUlke"])
    r = pygame.Rect(0, 0, W, 62)
    pygame.draw.rect(yuzey, PANEL, r)
    pygame.draw.line(yuzey, CIZGI, (0, 61), (W, 61))

    x = 12
    pygame.draw.circle(yuzey, pygame.Color(uref["renk"]), (x + 14, 31), 14)
    x += 36
    yaziCiz(yuzey, uref["ad"], F("orta"), YAZI, x, 6, 270)
    yaziCiz(yuzey, "%d/%02d" % (s["yil"], s["ay"]), F("kucuk"), SOLUK, x, 30)

    # metrikler
    def metrik(x, etiket, degerMetni, renk):
        yaziCiz(yuzey, etiket, F("kucuk"), SOLUK, x, 8)
        yaziCiz(yuzey, degerMetni, F("normal"), renk, x, 24)
        return x + 118

    b = s.get("sonButce") or {}
    net = b.get("net", 0)
    x = 330
    x = metrik(x, "Kasa", "%d  altın (%+.1f/ay)" % (u["para"], net), ALTIN if net >= 0 else KIRMIZI)
    x = metrik(x, "Borç", "%d" % ozet["borc"], KIRMIZI if ozet["borc"] > 0 else SOLUK)
    x = metrik(x, "GSYH", "%d" % ozet["gsyh"], YAZI)
    x = metrik(x, "Nüfus", "%.1fM" % (ozet["nufus"] / 1e6), YAZI)
    # refah/radikal/prestij barları
    def bar(x, etiket, deger, renk):
        yaziCiz(yuzey, etiket, F("kucuk"), SOLUK, x, 8)
        pygame.draw.rect(yuzey, (55, 50, 45), (x, 28, 90, 8), border_radius=3)
        pygame.draw.rect(yuzey, renk, (x, 28, int(90 * min(1, max(0, deger))), 8), border_radius=3)
        return x + 104

    x = bar(x, "Refah", ozet["refahOrt"], YESIL)
    x = bar(x, "Radikal", ozet["radikalizm"], KIRMIZI)
    bar(x, "Prestij", ozet["prestij"], MAVI)

    # hız kontrolleri
    hx = W - 268
    UI.buton(yuzey, pygame.Rect(hx, 14, 44, 32), "II" if a.hiz != 0 else ">", (lambda: setattr(APP, "hiz", 0 if APP.hiz != 0 else (s.get("kayitliHiz") or 1))), secili=(a.hiz == 0), font="orta")
    for i, ad in ((1, "1×"), (2, "2×"), (3, "3×")):
        UI.buton(yuzey, pygame.Rect(hx + 48 + (i - 1) * 38, 14, 34, 32), ad, (lambda i=i: setattr(APP, "hiz", i)), secili=(a.hiz == i))
    UI.buton(yuzey, pygame.Rect(W - 92, 14, 40, 32), "Kayıt", (lambda: APP.kaydet(1)), font="kucuk")
    UI.buton(yuzey, pygame.Rect(W - 48, 14, 40, 32), "Menü", (lambda: APP.anaMenu()), font="kucuk")

    # savaş bandı
    if u["savaslar"]:
        savas = u["savaslar"][0]
        rakip = s["ulkeler"].get(savas["rakip"])
        if rakip:
            metin = "SAVAŞ: %s — ilerleme %+.0f (%s) · süre %d ay" % (
                rakip["ad"], savas["ilerleme"], savas.get("strateji", "kusatma"), savas["sure"])
            pygame.draw.rect(yuzey, (60, 25, 22), (330, 44, 560, 18), border_radius=4)
            pygame.draw.rect(yuzey, (120, 50, 40), (330, 44, 560, 18), 1, border_radius=4)
            yaziCiz(yuzey, metin, F("kucuk"), (240, 160, 150), 340, 46)


# ---------------- çizim: sol panel (eyalet + inşaat) ----------------
def eyaletPaneliCiz(yuzey):
    a = APP
    s = a.state
    alan = pygame.Rect(10, 623, 690, 168)
    pygame.draw.rect(yuzey, PANEL, alan, border_radius=6)
    pygame.draw.rect(yuzey, CIZGI, alan, 2, border_radius=6)
    u = s["ulkeler"][s["oyuncuUlke"]]

    if not a.seciliEy:
        paragrafCiz(yuzey, "Haritadan bir eyalet seçin — inşaat ve eyalet bilgileri burada açılır.\n"
                            "Hızlı yol: Özet sekmesinden eyalet listenize de ulaşabilirsiniz.", F("normal"), SOLUK, alan.x + 14, alan.y + 14, alan.width - 28)
        return
    es = s["eyaletler"].get(a.seciliEy)
    ed = D.eyalet_bul(a.seciliEy)
    if not es:
        return
    bizim = es["ulkeId"] == s["oyuncuUlke"]
    uref = D.ulke_bul(es["ulkeId"]) or {}
    x = alan.x + 14
    yaziCiz(yuzey, es["ad"] + ("  ·  " + uref.get("ad", "?") if not bizim else "  (bizim)"), F("orta"), YAZI if bizim else TURUNCU, x, alan.y + 10)
    yaziCiz(yuzey, "Nüfus: %.2fM   Kaynaklar: %s   %s" % (es["nufus"] / 1e6, ", ".join(ed.get("kaynaklar", [])) or "—", ed.get("cografiNot", "")), F("kucuk"), SOLUK, x, alan.y + 34, alan.width - 28)

    # binalar özeti
    binaMetni = []
    for bid, liste in es["binalar"].items():
        b = D.bina_bul(bid)
        insaat = sum(1 for i2 in liste if i2["insaatKalan"] > 0)
        binaMetni.append("%s×%d%s" % (b["ad"] if b else bid, len(liste), (" (inşaat %d)" % insaat if insaat else "")))
    paragrafCiz(yuzey, "Binalar: " + (", ".join(binaMetni) or "yok"), F("kucuk"), YAZI, x, alan.y + 54, alan.width - 28)

    if not bizim:
        return
    # inşaat butonları (2 satır)
    yaziCiz(yuzey, "İnşa et:", F("kucuk"), SOLUK, x, alan.y + 78)
    bx, by = x + 62, alan.y + 74
    for b in D.BINALAR:
        adet = len(es["binalar"].get(b["id"], []))
        maliyet = round(b["maliyet"] * (1 + 0.35 * adet))
        metin = "%s (%d altın)" % (b["ad"], maliyet)
        w = F("kucuk").size(metin)[0] + 14
        if bx + w > alan.right - 14:
            bx = x + 62
            by += 28
        if by > alan.bottom - 30:
            yaziCiz(yuzey, "…", F("kucuk"), SOLUK, bx, by)
            break
        UI.buton(yuzey, pygame.Rect(bx, by, w, 24), metin,
                 (lambda bid=b["id"]: binaInsaa(bid)), font="kucuk",
                 hover=b["aciklama"] + " · İşgücü: %s tabakası" % b.get("tabakaIhtiyaci", "alt"))
        bx += w + 8


def binaInsaa(binaId):
    a = APP
    sonuc = E.binaInsaaBaslat(a.state, a.seciliEy, binaId)
    if sonuc.get("hata"):
        APP.mesajla(sonuc["hata"])
    elif sonuc.get("tamam"):
        APP.mesajla("İnşaat başladı: %d altın, %d ay." % (sonuc["maliyet"], sonuc["sure"]))


# ---------------- çizim: sağ panel + sekmeler ----------------
SEKMELER = [("ozet", "Özet"), ("ekonomi", "Ekonomi"), ("hukuk", "Hukuk"), ("teknoloji", "Teknoloji"),
            ("diplomasi", "Diplomasi"), ("yetenek", "Yetenekler"), ("gunluk", "Günlük")]

SAG = pygame.Rect(708, 70, 562, 721)


def sekmelerCiz(yuzey):
    x = SAG.x
    for sid, ad in SEKMELER:
        w = 78
        UI.buton(yuzey, pygame.Rect(x, SAG.y, w, 30), ad, (lambda s2=sid: (setattr(APP, "sekme", s2), APP.scroll.__setitem__(s2, 0))),
                 secili=(APP.sekme == sid), font="kucuk")
        x += w + 4


def panelBasla(yuzey, baslik):
    alan = pygame.Rect(SAG.x, SAG.y + 34, SAG.width, SAG.height - 34)
    pygame.draw.rect(yuzey, PANEL, alan, border_radius=6)
    pygame.draw.rect(yuzey, CIZGI, alan, 2, border_radius=6)
    if baslik:
        yaziCiz(yuzey, baslik, F("orta"), ALTIN, alan.x + 14, alan.y + 10)
    return alan


def icerikKaydir(yuzey, alan, anahtar, icerikYuksekligi):
    """Scroll yönetimi; içerik çizim fonksiyonuna başlangıç y döner."""
    kaydir = UI.kaydirAl("sag_" + anahtar)
    enFazla = max(0, icerikYuksekligi - alan.height + 20)
    kaydir = min(kaydir, enFazla)
    return kaydir


def ozetSekme(yuzey):
    a = APP
    s = a.state
    alan = panelBasla(yuzey, "İmparatorluk Özeti")
    ozet = s["sonOzet"]
    u = s["ulkeler"][s["oyuncuUlke"]]
    uref = D.ulke_bul(s["oyuncuUlke"])
    y = alan.y + 44 - UI.kaydirAl("sag_ozet")
    icerikH = 0

    # skor önizleme
    skor = skorHesapla(s)
    skorR = pygame.Rect(alan.x + 12, y, alan.width - 24, 88)
    pygame.draw.rect(yuzey, PANEL2, skorR, border_radius=6)
    yaziCiz(yuzey, "Skor önizleme: %.2f — %s" % (skor["toplam"], skor["itibar"]), F("normal"), ALTIN, skorR.x + 10, y + 8)
    metin = "GSYH %.2f · Refah %.2f · Düzen %.2f · Eyalet %.2f\nHukuk %.2f · Teknoloji %.2f · Prestij %.2f" % (
        skor["gsyhPuan"], skor["refahPuan"], skor["duzenPuan"], skor["eyaletPuan"],
        skor["hukukPuan"], skor["teknolojiPuan"], skor["prestijPuan"])
    paragrafCiz(yuzey, metin, F("kucuk"), SOLUK, skorR.x + 10, y + 32, skorR.width - 20)
    y += 100

    # aktif etkiler
    ya = s.get("yetenekAktif", {})
    if ya:
        yaziCiz(yuzey, "Aktif yetenek etkileri:", F("kucuk"), MOR, alan.x + 14, y)
        y += 18
        for k, kalan in ya.items():
            yb = D.YETENEKLER and next((x2 for x2 in D.YETENEKLER if x2["id"] == k), None)
            ad = yb["ad"] if yb else k
            yaziCiz(yuzey, "• %s — %d ay kaldı" % (ad, kalan), F("kucuk"), YAZI, alan.x + 22, y)
            y += 17
    bek = s.get("beklemeler", {})
    if bek:
        yaziCiz(yuzey, "Beklemedeki yetenekler:", F("kucuk"), SOLUK, alan.x + 14, y)
        y += 18
        for k, kalan in sorted(bek.items()):
            yb = next((x2 for x2 in D.YETENEKLER if x2["id"] == k), None)
            ad = yb["ad"] if yb else k
            yaziCiz(yuzey, "• %s — %d ay" % (ad, kalan), F("kucuk"), SOLUK, alan.x + 22, y)
            y += 17
    y += 6

    # hukuk geçişleri
    for kat, g in u["kanunGecisleri"].items():
        sec = next((x2 for x2 in D.KANUNLAR.get(kat, []) if x2["id"] == g["yeniDeger"]), None)
        yaziCiz(yuzey, "REFORM: %s → %s (%d ay)" % (kat, sec["ad"] if sec else g["yeniDeger"], g["kalanAy"]), F("kucuk"), TURUNCU, alan.x + 14, y)
        y += 18

    # eyalet listesi (tıkla → haritada seç)
    y += 4
    yaziCiz(yuzey, "Eyaletler (%d)" % len(u["eyaletler"]), F("normal"), YAZI, alan.x + 14, y)
    y += 24
    for eyId in u["eyaletler"]:
        es = s["eyaletler"].get(eyId)
        if not es:
            continue
        ed = D.eyalet_bul(eyId) or {}
        r = pygame.Rect(alan.x + 12, y, alan.width - 24, 24)
        sec = (a.seciliEy == eyId)
        if sec:
            pygame.draw.rect(yuzey, (58, 52, 40), r, border_radius=4)
        yaziCiz(yuzey, es["ad"], F("kucuk"), YAZI, r.x + 8, y + 4, 150)
        yaziCiz(yuzey, "%.1fM nüfus" % (es["nufus"] / 1e6), F("kucuk"), SOLUK, r.x + 160, y + 4)
        binaSay = sum(len(v) for v in es["binalar"].values())
        yaziCiz(yuzey, "%d bina" % binaSay, F("kucuk"), SOLUK, r.x + 280, y + 4)
        yaziCiz(yuzey, ", ".join(ed.get("kaynaklar", [])) or "—", F("kucuk"), SOLUK, r.x + 360, y + 4)
        UI.etiket(yuzey, r, es["ad"], (lambda eid=eyId: setattr(APP, "seciliEy", eid)))
        y += 26
        icerikH = y

    # scroll alanı
    UI.kaydirma["sag_ozet_limit"] = max(0, y - alan.y)


def sliderKur(x, y, w, deger0_1, cb):
    sl = Slider(x, y, w, deger0_1, cb)
    APP.sliderlar.append(sl)
    return sl


def ekonomiSekme(yuzey):
    a = APP
    s = a.state
    alan = panelBasla(yuzey, "Bütçe ve Pazar")
    u = s["ulkeler"][s["oyuncuUlke"]]
    b = s.get("sonButce") or {}
    y = alan.y + 44 - UI.kaydirAl("sag_ekonomi")

    yaziCiz(yuzey, "Gelir: %.1f  altın/ay   Gider: %.1f  altın/ay   Net: %+.1f  altın/ay   Faiz: %.1f" % (
        b.get("gelir", 0), b.get("gider", 0), b.get("net", 0), b.get("faiz", 0)), F("normal"),
        YAZI if b.get("net", 0) >= 0 else KIRMIZI, alan.x + 14, y)
    y += 30

    # vergiler
    yaziCiz(yuzey, "Vergiler", F("orta"), YAZI, alan.x + 14, y)
    y += 26
    adlar = {"alt": "Alt Tabaka", "orta": "Orta Tabaka", "ust": "Üst Tabaka"}
    for t in ("alt", "orta", "ust"):
        yaziCiz(yuzey, adlar[t], F("kucuk"), SOLUK, alan.x + 14, y + 2)
        deger = u["vergiler"][t]
        sl = sliderKur(alan.x + 120, y + 4, 260, deger, (lambda v, t=t: E.vergiAyarla(s, t, v)))
        sl.ciz(yuzey, None, TURUNCU)
        yaziCiz(yuzey, "%d%%" % round(deger * 100), F("kucuk"), YAZI, alan.x + 392, y + 2)
        y += 34
    y += 6

    # harcamalar
    yaziCiz(yuzey, "Harcamalar", F("orta"), YAZI, alan.x + 14, y)
    y += 26
    hadlar = {"yonetim": "Yönetim (vergi verimi)", "ordu": "Ordu (askeri güç)", "egitim": "Eğitim (araştırma hızı)", "refah": "Refah (mutluluk)"}
    for k in ("yonetim", "ordu", "egitim", "refah"):
        yaziCiz(yuzey, hadlar[k], F("kucuk"), SOLUK, alan.x + 14, y + 2)
        deger = u["harcamalar"][k]
        sl = sliderKur(alan.x + 190, y + 4, 190, deger, (lambda v, k=k: E.harcamaAyarla(s, k, v)))
        sl.ciz(yuzey, None, MAVI)
        yaziCiz(yuzey, "%d%%" % round(deger * 100), F("kucuk"), YAZI, alan.x + 392, y + 2)
        y += 34
    y += 10

    # pazar
    yaziCiz(yuzey, "Ulusal Pazar", F("orta"), YAZI, alan.x + 14, y)
    y += 26
    for m in D.MALLAR:
        fiyat = s["pazar"]["fiyatlar"].get(m["id"], m["bazFiyat"])
        arz = s["pazar"]["arz"].get(m["id"], 0)
        talep = s["pazar"]["talep"].get(m["id"], 0)
        oran = (arz / talep) if talep > 0.01 else 2
        renk = YESIL if oran >= 1.1 else (KIRMIZI if oran < 0.8 else YAZI)
        yaziCiz(yuzey, "%-18s %5.1f altın   arz/talep %.2f" % (m["ad"], fiyat, oran), F("kucuk"), renk, alan.x + 22, y)
        y += 19
    UI.kaydirma["sag_ekonomi_limit"] = max(0, y - alan.y)


def hukukSekme(yuzey):
    a = APP
    s = a.state
    alan = panelBasla(yuzey, "Hukuk ve Reformlar")
    u = s["ulkeler"][s["oyuncuUlke"]]
    y = alan.y + 44 - UI.kaydirAl("sag_hukuk")
    katAdlari = {"oyHakki": "Oy Hakkı", "devletTipi": "Devlet Yapısı", "ekonomi": "Ekonomi", "diniSistem": "Din–Devlet İlişkisi",
                 "orduModeli": "Ordu Modeli", "egitim": "Eğitim", "medeniHukuk": "Medeni Hukuk"}
    for kat, secenekler in D.KANUNLAR.items():
        mevcut = u["kanunlar"].get(kat)
        gecis = u["kanunGecisleri"].get(kat)
        yaziCiz(yuzey, katAdlari.get(kat, kat), F("normal"), ALTIN, alan.x + 14, y)
        y += 22
        bx = alan.x + 14
        for sec in secenekler:
            metin = sec["ad"]
            w = min(260, F("kucuk").size(metin)[0] + 18)
            if bx + w > alan.right - 14:
                bx = alan.x + 14
                y += 30
            etkin = not gecis
            secili = (mevcut == sec["id"])
            bekliyor = gecis and gecis["yeniDeger"] == sec["id"]
            UI.buton(yuzey, pygame.Rect(bx, y, w, 26), metin + (" [+]" if secili else "") + (" [%d ay]" % gecis["kalanAy"] if bekliyor else ""),
                     (lambda k=kat, sid=sec["id"]: hukukDegistir(k, sid)), etkin=etkin, secili=secili or bekliyor,
                     hover=sec["aciklama"], font="kucuk")
            bx += w + 8
        y += 34
    UI.kaydirma["sag_hukuk_limit"] = max(0, y - alan.y)


def hukukDegistir(kategori, deger):
    sonuc = E.kanunDegistir(APP.state, kategori, deger)
    if sonuc.get("mesaj"):
        APP.mesajla(sonuc["mesaj"])


def teknolojiSekme(yuzey):
    a = APP
    s = a.state
    alan = panelBasla(yuzey, "Teknoloji")
    u = s["ulkeler"][s["oyuncuUlke"]]
    y = alan.y + 44 - UI.kaydirAl("sag_teknoloji")
    # aktif araştırma
    aktif = u["teknoloji"]["aktif"]
    if aktif:
        t = D.tech_bul(aktif["id"])
        oran = aktif["kalanIlerleme"] / max(aktif["maliyet"], 1)
        pygame.draw.rect(yuzey, PANEL2, (alan.x + 12, y, alan.width - 24, 40), border_radius=6)
        yaziCiz(yuzey, "Araştırılıyor: %s (%.0f/%d)" % (t["ad"] if t else aktif["id"], aktif["kalanIlerleme"], aktif["maliyet"]), F("kucuk"), YAZI, alan.x + 20, y + 4)
        pygame.draw.rect(yuzey, (55, 50, 45), (alan.x + 20, y + 24, alan.width - 40, 8), border_radius=3)
        pygame.draw.rect(yuzey, MAVI, (alan.x + 20, y + 24, int((alan.width - 40) * min(1, oran)), 8), border_radius=3)
        y += 50
    kolAdlari = {"sanayi": "Sanayi", "toplum": "Toplum", "ordu": "Ordu"}
    kolRenk = {"sanayi": TURUNCU, "toplum": YESIL, "ordu": KIRMIZI}
    kolX = {"sanayi": alan.x + 14, "toplum": alan.x + 196, "ordu": alan.x + 378}
    kolY = {k: y for k in kolAdlari}
    for k, ad in kolAdlari.items():
        yaziCiz(yuzey, ad, F("normal"), kolRenk[k], kolX[k], kolY[k])
        kolY[k] += 26
    for t in D.TEKNOLOJILER:
        tamam = t["id"] in u["teknoloji"]["tamamlanan"]
        onkosulTamam = all(o in u["teknoloji"]["tamamlanan"] for o in t["onkosul"])
        calisiyor = aktif and aktif["id"] == t["id"]
        x = kolX[t["kol"]]
        yy = kolY[t["kol"]]
        metin = t["ad"] if len(t["ad"]) <= 24 else t["ad"][:23] + "…"
        renk = YESIL if tamam else (YAZI if onkosulTamam else (95, 90, 82))
        if calisiyor:
            renk = MAVI
        satirlar = satirlaraBol(metin, F("kucuk"), 160)
        for i, sr in enumerate(satirlar):
            yuzey.blit(F("kucuk").render(("[x] " if tamam else "[>] " if onkosulTamam else "[ ] " if not calisiyor else "[~] ") + (sr if i == 0 else "   " + sr), True, renk), (x, yy + i * 15))
        if not tamam and onkosulTamam and not aktif:
            UI.etiket(yuzey, pygame.Rect(x - 2, yy - 2, 164, len(satirlar) * 15 + 4), t["ad"],
                      (lambda tid=t["id"]: techBaslat(tid)), hover=t["etkiMetni"] + " · maliyet %d" % t["maliyet"])
        elif not tamam:
            UI.etiket(yuzey, pygame.Rect(x - 2, yy - 2, 164, len(satirlar) * 15 + 4), t["ad"], None,
                      hover=("Ön koşul: " + ", ".join((D.tech_bul(o) or {"ad": o})["ad"] for o in t["onkosul"])) if not onkosulTamam else t["etkiMetni"])
        kolY[t["kol"]] += max(1, len(satirlar)) * 16 + 4
    y = max(kolY.values())
    UI.kaydirma["sag_teknoloji_limit"] = max(0, y - alan.y)


def techBaslat(tid):
    sonuc = E.teknolojiBaslat(APP.state, tid)
    if sonuc.get("hata"):
        APP.mesajla(sonuc["hata"])


def diplomasiSekme(yuzey):
    a = APP
    s = a.state
    alan = panelBasla(yuzey, "Diplomasi")
    u = s["ulkeler"][s["oyuncuUlke"]]
    y = alan.y + 44 - UI.kaydirAl("sag_diplomasi")

    # savaş yönetimi
    if u["savaslar"]:
        yaziCiz(yuzey, "Savaş Yönetimi", F("orta"), KIRMIZI, alan.x + 14, y)
        y += 26
        savas = u["savaslar"][0]
        rakip = s["ulkeler"].get(savas["rakip"])
        pygame.draw.rect(yuzey, PANEL2, (alan.x + 12, y, alan.width - 24, 66), border_radius=6)
        yaziCiz(yuzey, "%s karşıtı savaş — amaç: %s" % (rakip["ad"] if rakip else "?",
                 s["eyaletler"][savas["amacEyalet"]]["ad"] if savas.get("amacEyalet") in s["eyaletler"] else "—"), F("kucuk"), YAZI, alan.x + 20, y + 6)
        pygame.draw.rect(yuzey, (55, 50, 45), (alan.x + 20, y + 26, alan.width - 40, 10), border_radius=3)
        iler = int((alan.width - 40) * (savas["ilerleme"] + 100) / 200)
        pygame.draw.rect(yuzey, KIRMIZI if savas["ilerleme"] < 0 else YESIL, (alan.x + 20, y + 26, iler, 10), border_radius=3)
        yaziCiz(yuzey, "strateji: %s · süre %d ay" % (savas.get("strateji"), savas["sure"]), F("kucuk"), SOLUK, alan.x + 20, y + 44)
        y += 76
        for sid, ad, hover in (("yildirma", "Yıldırma", "Hızlı ve riskli: +5/ay, %18 ihtimalle −11"),
                               ("kusatma", "Kuşatma", "Yavaş ve güvenli: +2.5/ay"),
                               ("inkitab", "İnkitab", "Savunma: cepheyi tutar")):
            UI.buton(yuzey, pygame.Rect(alan.x + 14 + (["yildirma", "kusatma", "inkitab"].index(sid)) * 130, y, 124, 28), ad,
                     (lambda sid=sid: E.savasStrateji(s, sid) and APP.mesajla("Strateji: " + ad)), secili=(savas.get("strateji") == sid), hover=hover)
        y += 36
        UI.buton(yuzey, pygame.Rect(alan.x + 14, y, 180, 28), "Beyaz Barış Öner", (lambda: (lambda r: APP.mesajla(r.get("mesaj") or r.get("hata") or ""))(E.savasSonaErdir(s))), hover="Savaşı sonuçsuz kapat")
        y += 42

    yaziCiz(yuzey, "Devletler", F("orta"), YAZI, alan.x + 14, y)
    y += 26
    for vid in [v["id"] for v in D.ULKELER if v["id"] != s["oyuncuUlke"]]:
        hedef = s["ulkeler"].get(vid)
        if not hedef:
            continue
        vref = D.ulke_bul(vid) or {}
        iliski = hedef["iliskiler"].get(s["oyuncuUlke"], 0)
        savasVar = any(x["rakip"] == vid for x in u["savaslar"])
        paktVar = vid in u.get("paktlar", {})
        ittifakVar = vid in u["ittifaklar"]
        r = pygame.Rect(alan.x + 12, y, alan.width - 24, 58)
        pygame.draw.rect(yuzey, PANEL2, r, border_radius=6)
        pygame.draw.circle(yuzey, pygame.Color(vref.get("renk", "#777")), (r.x + 16, r.y + 16), 9)
        yaziCiz(yuzey, vref.get("ad", vid), F("kucuk"), YAZI, r.x + 32, r.y + 4, 200)
        durum = "SAVAŞ" if savasVar else ("PAKT" if paktVar else ("İTTİFAK" if ittifakVar else ""))
        if durum:
            yaziCiz(yuzey, durum, F("kucuk"), KIRMIZI if savasVar else MOR, r.x + 240, r.y + 4)
        renk = YESIL if iliski > 25 else (KIRMIZI if iliski < -25 else SOLUK)
        yaziCiz(yuzey, "İlişki: %+d" % iliski, F("kucuk"), renk, r.x + 320, r.y + 4)
        bx = r.x + 8
        by = r.y + 28
        butonlar = [("İlişki+ (5 altın)", "iyi_iliski", "5 altın karşılığı ilişki +10"),
                    ("İttifak", "ittifak", "İlişki ≥ 55 gerekir"),
                    ("Hudut Talebi", "hudut_talebi", "Güçlüysen eyalet isteyebilirsin; reddedilirse ilişki düşer"),
                    ("Savaş İlan", "savas_ilan", "Amaç eyalet: rakibin ilk eyaleti")]
        for ad, tur, hover in butonlar:
            w = F("kucuk").size(ad)[0] + 14
            etkin = not savasVar
            UI.buton(yuzey, pygame.Rect(bx, by, w, 24), ad,
                     (lambda vid=vid, tur=tur: diploEylem(vid, tur)), etkin=etkin, hover=hover, font="kucuk")
            bx += w + 6
        y += 66
    UI.kaydirma["sag_diplomasi_limit"] = max(0, y - alan.y)


def diploEylem(hedefId, tur):
    sonuc = E.diplomasiEylem(APP.state, hedefId, tur)
    if sonuc.get("hata"):
        APP.mesajla(sonuc["hata"])
    elif sonuc.get("mesaj"):
        APP.mesajla(sonuc["mesaj"])


def yetenekSekme(yuzey):
    a = APP
    s = a.state
    alan = panelBasla(yuzey, "Yetenekler — Devlet Başkanı Güçleri (YENİ)")
    u = s["ulkeler"][s["oyuncuUlke"]]
    y = alan.y + 44 - UI.kaydirAl("sag_yetenek")

    yaziCiz(yuzey, "Ayda 1 yetenek · altın maliyeti · kullanım sonrası bekleme süresi başlar", F("kucuk"), SOLUK, alan.x + 14, y)
    y += 24
    if s.get("aylikYetenekKullanildi"):
        yaziCiz(yuzey, "Bu ay yetenek hakkı kullanıldı.", F("kucuk"), TURUNCU, alan.x + 14, y)
        y += 20

    kartW = (alan.width - 40) // 2
    kartH = 118
    for i, yb in enumerate(D.YETENEKLER):
        col, row = i % 2, i // 2
        r = pygame.Rect(alan.x + 12 + col * (kartW + 14), y + row * (kartH + 10), kartW, kartH)
        kalan = s["beklemeler"].get(yb["id"], 0)
        aktif = s["yetenekAktif"].get(yb["id"], 0)
        kilitMetni = E.yetenekKilitMetni(s, yb)
        savasGerek = yb["id"] in ("rapid_offensive", "defensive_line") and not u["savaslar"]
        kullanilabilir = (kalan == 0 and not kilitMetni and not savasGerek and not s.get("aylikYetenekKullanildi"))

        pygame.draw.rect(yuzey, PANEL2 if kullanilabilir else (34, 31, 28), r, border_radius=8)
        pygame.draw.rect(yuzey, ALTIN if kullanilabilir else CIZGI, r, 2, border_radius=8)
        # kategori renk noktası
        katRenk = {"Askeri": KIRMIZI, "Ekonomi": ALTIN, "Toplum": YESIL, "Diplomasi": MAVI}[yb["kategori"]]
        pygame.draw.circle(yuzey, katRenk, (r.x + 16, r.y + 16), 7)
        yaziCiz(yuzey, yb["ad"], F("normal"), YAZI if kullanilabilir else (110, 104, 94), r.x + 30, r.y + 6, kartW - 40)
        durumMetni = []
        if aktif:
            durumMetni.append("AKTİF %d ay" % aktif)
        if kalan:
            durumMetni.append("bekleme %d ay" % kalan)
        if kilitMetni:
            durumMetni.append(kilitMetni)
        if savasGerek:
            durumMetni.append("savaş gerekli")
        if s.get("aylikYetenekKullanildi") and kullanilabilir:
            durumMetni.append("bu ay hakkın bitti")
        paragrafCiz(yuzey, yb["aciklama"], F("kucuk"), SOLUK, r.x + 10, r.y + 28, kartW - 20)
        yaziCiz(yuzey, yb["etkiMetni"], F("kucuk"), MOR, r.x + 10, r.y + 62, kartW - 20)
        maliyet = round(yb["maliyet"] * (s.get("zorlukAyar") or {}).get("yetenekMaliyet", 1.0))
        yaziCiz(yuzey, ("Maliyet: %d altın" % maliyet if maliyet else "Ücretsiz (borç yaratır)"), F("kucuk"), ALTIN, r.x + 10, r.y + kartH - 26)
        hedefGerek = yb["id"] in ("envoy_mission", "security_pact")
        btnMetin = "Kullan" + (" → ülke seç" if hedefGerek else "")
        UI.buton(yuzey, pygame.Rect(r.right - 110, r.bottom - 30, 100, 24), btnMetin,
                 (lambda yid=yb["id"]: yetenekTikla(yid)), etkin=kullanilabilir, font="kucuk",
                 hover=" | ".join(durumMetni) or yb["etkiMetni"])
        if durumMetni:
            yaziCiz(yuzey, "; ".join(durumMetni)[:60], F("kucuk"), TURUNCU, r.x + 110, r.y + kartH - 26, kartW - 224)

    y += ((len(D.YETENEKLER) + 1) // 2) * (kartH + 10) + 10

    # hedef seçim modu
    if a.seciliYetenek:
        hr = pygame.Rect(alan.x + 12, y, alan.width - 24, 150)
        pygame.draw.rect(yuzey, (40, 36, 30), hr, border_radius=8)
        pygame.draw.rect(yuzey, MAVI, hr, 2, border_radius=8)
        yb = E.yetenekBul(a.seciliYetenek)
        yaziCiz(yuzey, "Hedef seç: %s" % (yb["ad"] if yb else "?"), F("normal"), YAZI, hr.x + 12, y + 8)
        yaziCiz(yuzey, "İptal için ESC", F("kucuk"), SOLUK, hr.right - 110, y + 10)
        UI.etiket(yuzey, pygame.Rect(hr.right - 120, y + 6, 108, 20), "iptal", (lambda: setattr(APP, "seciliYetenek", None)))
        bx, by = hr.x + 12, hr.y + 32
        for vid in [v["id"] for v in D.ULKELER if v["id"] != s["oyuncuUlke"]]:
            metin = (D.ulke_bul(vid) or {}).get("ad", vid)
            w = min(170, F("kucuk").size(metin)[0] + 14)
            if bx + w > hr.right - 12:
                bx = hr.x + 12
                by += 30
            UI.buton(yuzey, pygame.Rect(bx, by, w, 26), metin, (lambda vid=vid: yetenekHedefli(vid)), font="kucuk")
            bx += w + 8
    UI.kaydirma["sag_yetenek_limit"] = max(0, y + 160 - alan.y)


def yetenekTikla(yetenekId):
    a = APP
    yb = E.yetenekBul(yetenekId)
    if not yb:
        return
    if yetenekId in ("envoy_mission", "security_pact"):
        a.seciliYetenek = yetenekId
        a.mesajla("Hedef ülke seçin.")
        return
    sonuc = E.yetenekKullan(a.state, yetenekId)
    a.mesajla(sonuc["mesaj"])


def yetenekHedefli(hedefId):
    a = APP
    if not a.seciliYetenek:
        return
    sonuc = E.yetenekKullan(a.state, a.seciliYetenek, hedefId)
    a.mesajla(sonuc["mesaj"])
    if sonuc.get("tamam"):
        a.seciliYetenek = None


def gunlukSekme(yuzey):
    s = APP.state
    alan = panelBasla(yuzey, "Devlet Günlüğü")
    kaydir = UI.kaydirAl("sag_gunluk")
    gunluk = list(reversed(s.get("gunluk", [])))
    y = alan.y + 14 - kaydir
    turRenk = {"bilgi": YAZI, "uyari": TURUNCU, "kriz": KIRMIZI}
    for g in gunluk[-120:]:
        renk = turRenk.get(g["tur"], YAZI)
        satirlar = satirlaraBol("%d/%02d — %s" % (g["yil"], g["ay"], g["metin"]), F("kucuk"), alan.width - 30)
        for sr in satirlar:
            yuzey.blit(F("kucuk").render(sr, True, renk), (alan.x + 14, y))
            y += 16
        y += 3
    UI.kaydirma["sag_gunluk_limit"] = max(0, y - alan.y)


# ---------------- olay modali ----------------
def olayModalCiz(yuzey):
    s = APP.state
    olayId = s["olaylar"]["aktif"]
    if not olayId:
        return
    olay = next((o for o in D.OLAYLAR if o["id"] == olayId), None)
    if not olay:
        s["olaylar"]["aktif"] = None
        return
    kararti = pygame.Surface((W, H), pygame.SRCALPHA)
    kararti.fill((0, 0, 0, 170))
    yuzey.blit(kararti, (0, 0))
    kartW, kartH = 620, 380
    r = pygame.Rect(W // 2 - kartW // 2, H // 2 - kartH // 2, kartW, kartH)
    pygame.draw.rect(yuzey, PANEL, r, border_radius=10)
    pygame.draw.rect(yuzey, ALTIN, r, 3, border_radius=10)
    yaziCiz(yuzey, "OLAY", F("kucuk"), TURUNCU, r.x + 20, r.y + 14)
    yaziCiz(yuzey, olay["baslik"], F("buyuk"), YAZI, r.x + 20, r.y + 34, kartW - 40)
    paragrafCiz(yuzey, olay["metin"], F("normal"), YAZI, r.x + 20, r.y + 74, kartW - 40)
    oy = r.y + 170
    for i, sec in enumerate(olay["secenekler"]):
        btn = pygame.Rect(r.x + 20, oy, kartW - 40, 52)
        UI.buton(yuzey, btn, sec["metin"], (lambda i2=i: olaySec(i2)), font="kucuk", hover="Bu seçeneği uygula")
        oy += 62
    yaziCiz(yuzey, "Simülasyon olay kararı verilene kadar duraklatıldı.", F("kucuk"), SOLUK, r.x + 20, r.bottom - 30)


def olaySec(indeks):
    s = APP.state
    E.olaySecim(s, s["olaylar"]["aktif"], indeks)


# ---------------- sonuç ekranı ----------------
def sonucCiz(yuzey):
    s = APP.state
    yuzey.fill(ARKA)
    skor = skorHesapla(s)
    baslik = F("dev").render("DÖNEM SONA ERDİ — 1936", True, ALTIN)
    yuzey.blit(baslik, (W // 2 - baslik.get_width() // 2, 90))
    itibar = F("buyuk").render(skor["itibar"], True, YAZI)
    yuzey.blit(itibar, (W // 2 - itibar.get_width() // 2, 160))
    pu = F("dev").render("Skor: %.2f" % skor["toplam"], True, (240, 220, 160))
    yuzey.blit(pu, (W // 2 - pu.get_width() // 2, 210))
    if skor["toplam"] > APP.enIyiSkor:
        APP._enIyiYaz(skor["toplam"])
        APP.enIyiSkor = skor["toplam"]
        yeni = F("orta").render("YENİ EN İYİ SKOR!", True, YESIL)
        yuzey.blit(yeni, (W // 2 - yeni.get_width() // 2, 270))
    else:
        eski = F("kucuk").render("En iyi skorun: %.2f" % APP.enIyiSkor, True, SOLUK)
        yuzey.blit(eski, (W // 2 - eski.get_width() // 2, 270))

    # kırılım tablosu
    satirlar = [
        ("GSYH", skor["gsyhPuan"]), ("Refah", skor["refahPuan"]), ("Düzen (radikalizm eksikliği)", skor["duzenPuan"]),
        ("Eyalet sayısı", skor["eyaletPuan"]), ("Hukuk ilerlemesi", skor["hukukPuan"]),
        ("Teknoloji", skor["teknolojiPuan"]), ("Prestij", skor["prestijPuan"]),
    ]
    y = 330
    for ad, deger in satirlar:
        yaziCiz(yuzey, ad, F("normal"), YAZI, W // 2 - 220, y)
        yaziCiz(yuzey, "%.2f" % deger, F("normal"), ALTIN, W // 2 + 150, y)
        y += 30
    ozet = s["sonOzet"]
    y += 10
    metin = "Nüfus %.1fM · Eyalet %d · GSYH %d · Refah %.2f · Radikalizm %.2f · Teknoloji %d · Prestij %.2f" % (
        ozet["nufus"] / 1e6, ozet["eyaletSayisi"], ozet["gsyh"], ozet["refahOrt"], ozet["radikalizm"],
        len(s["ulkeler"][s["oyuncuUlke"]]["teknoloji"]["tamamlanan"]), ozet["prestij"])
    paragrafCiz(yuzey, metin, F("kucuk"), SOLUK, W // 2 - 330, y, 660)
    UI.buton(yuzey, pygame.Rect(W // 2 - 110, H - 90, 220, 46), "ANA MENÜ", (lambda: APP.anaMenu()), font="orta", renk=(220, 200, 150))


# ---------------- ana çizim ----------------
def oyunCiz(yuzey):
    a = APP
    yuzey.fill(ARKA)
    ustSeritCiz(yuzey)
    haritaCiz(yuzey)
    eyaletPaneliCiz(yuzey)
    sekmelerCiz(yuzey)
    sekmeFonk = {"ozet": ozetSekme, "ekonomi": ekonomiSekme, "hukuk": hukukSekme, "teknoloji": teknolojiSekme,
                 "diplomasi": diplomasiSekme, "yetenek": yetenekSekme, "gunluk": gunlukSekme}
    sekmeFonk.get(a.sekme, ozetSekme)(yuzey)

    # alt durum çubuğu
    alt = pygame.Rect(0, H - 9, W, 9)
    pygame.draw.rect(yuzey, PANEL, alt)
    if a.mesaj:
        kutu = F("normal").size(a.mesaj[0])[0] + 24
        mr = pygame.Rect(W // 2 - kutu // 2, H - 66, kutu, 28)
        pygame.draw.rect(yuzey, (50, 46, 36), mr, border_radius=6)
        pygame.draw.rect(yuzey, ALTIN, mr, 1, border_radius=6)
        yaziCiz(yuzey, a.mesaj[0], F("normal"), YAZI, mr.x + 12, mr.y + 5)

    if a.state["oyunBitti"]:
        a.ekran = "sonuc"
    olayModalCiz(yuzey)


def hoverTipCiz(yuzey):
    mouse = pygame.mouse.get_pos()
    for rect, cb, etkin, hover in UI.butonlar:
        if hover and rect.collidepoint(mouse):
            satirlar = satirlaraBol(hover, F("kucuk"), 340)
            w = max(F("kucuk").size(s2)[0] for s2 in satirlar) + 16
            h = len(satirlar) * 15 + 10
            x = min(mouse[0] + 12, W - w - 4)
            y = min(mouse[1] + 14, H - h - 4)
            pygame.draw.rect(yuzey, (18, 16, 14), (x, y, w, h), border_radius=5)
            pygame.draw.rect(yuzey, CIZGI, (x, y, w, h), 1, border_radius=5)
            for i, sr in enumerate(satirlar):
                yuzey.blit(F("kucuk").render(sr, True, YAZI), (x + 8, y + 5 + i * 15))
            break
