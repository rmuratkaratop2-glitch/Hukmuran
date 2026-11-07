# -*- coding: utf-8 -*-
"""
engine.py — HÜKMÜMRAN simülasyon çekirdeği (Python portu)
UI'ya DOKUNMAZ. data.py'yı çalışma anında okur.
Yeni: yetenek (güç) sistemi — oyuncu özel aktif güçler, altın + bekleme süresi ile.
Hiçbir fonksiyon NaN üretmez; tüm sayılar clamp/guard'lıdır.
"""
import math
import random
import json
import os

import data as D

ORDU_MODELI_CARPAN = {"derebeyi": 0.8, "zorunlu_askerlik": 1.25, "mesleki": 1.0}
KULUP_LISTE = D.KULUP_LISTE
TABAKA_LISTE = D.TABAKA_LISTE


def clamp(x, a, b):
    try:
        x = float(x)
        if not math.isfinite(x):
            return a
    except (TypeError, ValueError):
        return a
    return a if x < a else (b if x > b else x)


def rast(v):
    return random.random() < v


def tpl(d):
    return json.loads(json.dumps(d))


def simdiTarih(s):
    return "%d/%02d" % (s["yil"], s["ay"])


def gunlukEkle(s, metin, tur="bilgi"):
    if "gunluk" not in s or not isinstance(s["gunluk"], list):
        s["gunluk"] = []
    s["gunluk"].append({"yil": s["yil"], "ay": s["ay"], "metin": str(metin)[:200], "tur": tur or "bilgi"})
    if len(s["gunluk"]) > 200:
        del s["gunluk"][:len(s["gunluk"]) - 200]


def aktifYetenek(s, yetenekId):
    """Oyuncunun süreli yetenek etkisi aktif mi?"""
    return bool(s.get("yetenekAktif", {}).get(yetenekId))


# ---------------- türetilmiş değerler ----------------
def nufusToplam(s, ulkeId):
    n = 0
    u = s["ulkeler"].get(ulkeId)
    if not u:
        return 0
    for eyId in u["eyaletler"]:
        ey = s["eyaletler"].get(eyId)
        if not ey:
            continue
        for p in ey["populations"]:
            n += p["sayi"]
    return n


def askeriGuc(s, ulke):
    if not ulke:
        return 1.0
    n = nufusToplam(s, ulke["id"])
    model = ORDU_MODELI_CARPAN.get(ulke["kanunlar"]["orduModeli"], 1.0)
    bonus = (ulke.get("teknolojiBonusu") or {}).get("askeri", 1.0)
    mob = 1.20 if (ulke["id"] == s.get("oyuncuUlke") and aktifYetenek(s, "mobilization")) else 1.0
    return math.sqrt(max(n, 1)) * (0.5 + (ulke["harcamalar"].get("ordu", 0)) * 2) * model * bonus * mob


def refahOrt(s, ulkeId):
    top, agirlik = 0.0, 0.0
    u = s["ulkeler"].get(ulkeId)
    if not u:
        return 0.4
    for eyId in u["eyaletler"]:
        ey = s["eyaletler"].get(eyId)
        if not ey:
            continue
        for p in ey["populations"]:
            top += p["refah"] * p["sayi"]
            agirlik += p["sayi"]
    return clamp(top / agirlik, 0, 1) if agirlik > 0 else 0.4


def radikalizmOrt(s, ulkeId):
    top, agirlik = 0.0, 0.0
    u = s["ulkeler"].get(ulkeId)
    if not u:
        return 0.3
    for eyId in u["eyaletler"]:
        ey = s["eyaletler"].get(eyId)
        if not ey:
            continue
        for p in ey["populations"]:
            top += p["radikalizm"] * p["sayi"]
            agirlik += p["sayi"]
    return clamp(top / agirlik, 0, 1) if agirlik > 0 else 0.3


def kulupEtkisi(s, ulke):
    etki = {}
    d_kulupler = {k["id"]: k for k in D.KULUPLER}
    for k in KULUP_LISTE:
        tabakaAgirlik = 0
        for eyId in ulke["eyaletler"]:
            ey = s["eyaletler"].get(eyId)
            if not ey:
                continue
            kulup = d_kulupler[k]
            for p in ey["populations"]:
                if p["tabaka"] in kulup["tabakalar"]:
                    tabakaAgirlik += p["sayi"]
        mem = ulke["kulupler"].get(k, 0)
        if not isinstance(mem, (int, float)):
            mem = 0
        etki[k] = clamp(math.sqrt(tabakaAgirlik) / 50 * (0.5 + 0.5 * (mem + 1)), 0.02, 1)
    dt = ulke["kanunlar"]["devletTipi"]
    if dt == "mutlakiyet":
        etki["ordu"] *= 1.5
        etki["ruhani"] *= 1.4
        etki["aydin"] *= 0.7
    elif dt in ("meşrutiyet", "mesrutiyet"):
        etki["aydin"] *= 1.2
        etki["sermaye"] *= 1.2
    elif dt == "parlamenter":
        etki["aydin"] *= 1.4
        etki["sermaye"] *= 1.4
        etki["sendika"] *= 1.3
        etki["ruhani"] *= 0.7
    return etki


# ---------------- yeni oyun ----------------
def yeniOyun(ulkeId="osmanli", zorluk="normal"):
    s = {
        "surum": 2,
        "yil": D.DONEM["baslangicYil"], "ay": 1, "tick": 0,
        "oyuncuUlke": ulkeId, "zorluk": zorluk, "hiz": 1,
        "ulkeler": {}, "eyaletler": {},
        "pazar": {"fiyatlar": {}, "arz": {}, "talep": {}},
        "olaylar": {"aktif": None, "gecmis": []},
        "gunluk": [], "skorGecmisi": [],
        "oyunBitti": False, "sonOzet": None,
        "beklemeler": {}, "yetenekAktif": {},
        "elciSayac": {}, "savasYetenekIlerleme": 0,
        "aylikYetenekKullanildi": False,
        "son_tahvil_tick": None, "son_seferberlik_bitis_tick": None,
        "son_elci_tick": None, "son_elci_hedef": None,
        "zorlukAyar": D.ZORLUKLAR.get(zorluk, D.ZORLUKLAR["normal"]),
    }
    for m in D.MALLAR:
        s["pazar"]["fiyatlar"][m["id"]] = m["bazFiyat"]
    for u in D.ULKELER:
        eyIds = [e["id"] for e in D.EYALETLER if e["ulkeId"] == u["id"]]
        s["ulkeler"][u["id"]] = {
            "id": u["id"], "ad": u["ad"], "renk": u["renk"], "aiKarakter": u.get("aiKarakter", "dengeli"),
            "para": 300, "borc": 0, "prestij": u.get("prestijBaslangic", 0.3),
            "kanunlar": tpl(u.get("baslangicKanun", {})),
            "kanunGecisleri": {},
            "teknoloji": {"tamamlanan": [], "aktif": None},
            "teknolojiBonusu": {"uretim": 1, "refah": 0, "askeri": 1, "vergiVerimliligi": 1},
            "vergiler": {"alt": 0.3, "orta": 0.25, "ust": 0.2},
            "harcamalar": {"yonetim": 0.5, "ordu": 0.4, "egitim": 0.3, "refah": 0.2},
            "iliskiler": {}, "ittifaklar": [], "savaslar": [],
            "eyaletler": eyIds,
            "kulupler": {k: 0 for k in KULUP_LISTE},
            "paktlar": {},
            "aiKararAy": 1 + random.randint(0, 11),
        }
        for v in D.ULKELER:
            if v["id"] == u["id"]:
                continue
            s["ulkeler"][u["id"]]["iliskiler"][v["id"]] = 20 if {u["id"], v["id"]} == {"rusya", "avusturya"} else 0
    for e in D.EYALETLER:
        s["eyaletler"][e["id"]] = {
            "id": e["id"], "ulkeId": e["ulkeId"], "ad": e["ad"], "nufus": e["nufus"],
            "kaynaklar": list(e.get("kaynaklar", [])),
            "binalar": {},
            "populations": [
                {"kulup": p["kulup"], "tabaka": p["tabaka"],
                 "sayi": max(1, round(p["sayi"])),
                 "refah": clamp(p.get("refah", 0.5), 0, 1),
                 "radikalizm": clamp((1 - p.get("refah", 0.5)) * 0.8, 0, 1)}
                for p in e.get("populations", [])
            ],
            "istihdam": {"ust": 0, "orta": 0, "alt": 0},
        }
        bSet = {}
        for bid, adet in (e.get("baslangicBinalar") or {}).items():
            bSet[bid] = [{"seviye": 1, "insaatKalan": 0, "isgucuDoluluk": 0.7}
                         for _ in range(max(1, round(adet)))]
        s["eyaletler"][e["id"]]["binalar"] = bSet
    gunlukEkle(s, "Oyun başladı. " + (s["ulkeler"][ulkeId]["ad"] if ulkeId in s["ulkeler"] else ulkeId)
               + " yönetimi size emanet. Halkın refahı, hazinenin durumu ve meclisin havası kritik.")
    hesaplaOzet(s)
    return s


# ---------------- üretim & pazar ----------------
def pazarHedefFiyat(malId, arz, talep):
    m = D.mal_bul(malId)
    if not m:
        return 5.0
    oran = (arz / talep) if talep > 0.01 else 2.0
    hedef = m["bazFiyat"] * clamp(oran, 0.5, 2.0)
    return clamp(hedef, m["bazFiyat"] * 0.5, m["bazFiyat"] * 2.0)


def ulretimVePazar(s):
    for m in D.MALLAR:
        s["pazar"]["arz"][m["id"]] = 0.0
        s["pazar"]["talep"][m["id"]] = 0.0
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        return 0.0
    bonus = (oyuncu.get("teknolojiBonusu") or {}).get("uretim", 1.0)
    uretimDegeri = 0.0
    girdiIsteg = {}
    for eyId in oyuncu["eyaletler"]:
        ey = s["eyaletler"].get(eyId)
        if not ey:
            continue
        ey["istihdam"] = {"ust": 0.0, "orta": 0.0, "alt": 0.0}
        for bid in list(ey["binalar"].keys()):
            b = D.bina_bul(bid)
            if not b:
                continue
            for inst in ey["binalar"][bid]:
                if inst["insaatKalan"] > 0:
                    continue
                doluluk = clamp(inst["isgucuDoluluk"], 0.15, 1)
                carp = doluluk * bonus * inst["seviye"]
                for cid, cikti in (b["ciktilar"] or {}).items():
                    miktar = cikti * carp
                    s["pazar"]["arz"][cid] = s["pazar"]["arz"].get(cid, 0) + miktar
                    m = D.mal_bul(cid)
                    if m:
                        uretimDegeri += miktar * s["pazar"]["fiyatlar"].get(cid, m["bazFiyat"])
                for gid, girdi in (b["girdiler"] or {}).items():
                    girdiIsteg[gid] = girdiIsteg.get(gid, 0) + girdi * carp
                iht = b.get("tabakaIhtiyaci", "alt")
                ey["istihdam"][iht] = ey["istihdam"].get(iht, 0) + b.get("isgucu", 0) * doluluk
                if iht == "alt":
                    ey["istihdam"]["orta"] += b.get("isgucu", 0) * doluluk * 0.1
                    ey["istihdam"]["ust"] += b.get("isgucu", 0) * doluluk * 0.02
    nufus = nufusToplam(s, s["oyuncuUlke"])
    for m in D.MALLAR:
        if m["kategori"] == "gida":
            tuketim = nufus / 1000 * 2.2
        elif m["kategori"] == "ham":
            tuketim = nufus / 1000 * 0.4
        else:
            tuketim = nufus / 1000 * 0.8
        s["pazar"]["talep"][m["id"]] = s["pazar"]["talep"].get(m["id"], 0) + tuketim + girdiIsteg.get(m["id"], 0)
    for m in D.MALLAR:
        hedef = pazarHedefFiyat(m["id"], s["pazar"]["arz"][m["id"]], s["pazar"]["talep"][m["id"]])
        s["pazar"]["fiyatlar"][m["id"]] = s["pazar"]["fiyatlar"].get(m["id"], m["bazFiyat"]) * 0.75 + hedef * 0.25
    for eyId in oyuncu["eyaletler"]:
        ey = s["eyaletler"].get(eyId)
        if not ey:
            continue
        for bid in list(ey["binalar"].keys()):
            b = D.bina_bul(bid)
            if not b:
                continue
            for inst in ey["binalar"][bid]:
                if inst["insaatKalan"] > 0:
                    continue
                kisit = False
                for gid in (b["girdiler"] or {}):
                    arz = s["pazar"]["arz"].get(gid, 0)
                    tlp = s["pazar"]["talep"].get(gid, 0)
                    if tlp > 0 and arz / tlp < 0.7:
                        kisit = True
                if kisit:
                    inst["isgucuDoluluk"] = clamp(inst["isgucuDoluluk"] * 0.92, 0.15, 1)
                else:
                    inst["isgucuDoluluk"] = clamp(inst["isgucuDoluluk"] * 1.05 + 0.02, 0.15, 1)
    return uretimDegeri


def aiUretimKatsayisi(s, ulke):
    n = nufusToplam(s, ulke["id"])
    ek = ulke["kanunlar"]["ekonomi"]
    ekonomiCarp = {"geleneksel": 0.8, "devletçi": 1.0, "devletci": 1.0, "serbest": 1.15}.get(ek, 0.9)
    aiGelir = (s.get("zorlukAyar") or {}).get("aiGelir", 1.0)
    uretim = (ulke.get("teknolojiBonusu") or {}).get("uretim", 1.0)
    return n / 1000 * 0.9 * ekonomiCarp * uretim * aiGelir


# ---------------- nüfus & refah ----------------
def nufusGuncelle(s):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        return
    refahBonus = (oyuncu.get("teknolojiBonusu") or {}).get("refah", 0) + (oyuncu["harcamalar"].get("refah", 0) * 0.15)
    for eyId in oyuncu["eyaletler"]:
        ey = s["eyaletler"].get(eyId)
        if not ey:
            continue
        for p in ey["populations"]:
            vergiYuku = oyuncu["vergiler"].get(p["tabaka"], 0.2)
            hedef = 0.45 + refahBonus - vergiYuku * 0.5
            istihdamOrani = (ey["istihdam"].get(p["tabaka"], 0) / max(p["sayi"] / 1000, 0.001))
            hedef += clamp(istihdamOrani, 0, 0.6) * 0.25
            hedef = clamp(hedef, 0.05, 0.95)
            p["refah"] = clamp(p["refah"] * 0.9 + hedef * 0.1, 0, 1)
            p["radikalizm"] = clamp((1 - p["refah"]) * 0.9 + (0.1 if vergiYuku > 0.45 else 0), 0, 1)
            buyume = 0.0006 * (p["refah"] - 0.35) * 12
            p["sayi"] = max(50, round(p["sayi"] * (1 + buyume)))
        ey["nufus"] = sum(p["sayi"] for p in ey["populations"])


# ---------------- bütçe ----------------
def butceIsle(s):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        return {"gelir": 0, "gider": 0, "net": 0, "faiz": 0}
    tabakaGelir = {"ust": 0.0, "orta": 0.0, "alt": 0.0}
    for eyId in oyuncu["eyaletler"]:
        ey = s["eyaletler"].get(eyId)
        if not ey:
            continue
        for p in ey["populations"]:
            katsayi = 1.4 if p["tabaka"] == "ust" else (0.8 if p["tabaka"] == "orta" else 0.4)
            tabakaGelir[p["tabaka"]] += p["sayi"] / 1000 * katsayi
    yonetimVerim = clamp(0.4 + (oyuncu["harcamalar"].get("yonetim", 0.5) * 1.2), 0.3, 1) \
        * ((oyuncu.get("teknolojiBonusu") or {}).get("vergiVerimliligi", 1.0))
    # DENGE: dev yönetimli ülkelerde (Qing) kişi başı vergi tahsilatı tarihsel olarak düşüktür;
    # 8M referansın üstündeki nüfus için yumuşak dampen (nüfus/8M)^0.25 uygulanır.
    toplamNufus = sum(p["sayi"] for eyId in oyuncu["eyaletler"]
                      for p in (s["eyaletler"].get(eyId, {"populations": []})["populations"]))
    if toplamNufus > 8_000_000:
        yonetimVerim *= (8_000_000 / toplamNufus) ** 0.25
    gelir = 0.0
    # DENGE DÜZELTMESİ: orijinaldeki ×10 çarpanı gelirleri olay/yetenek/bina maliyetlerine
    # göre anlamsızlaştırıyordu (aylık ~10k+). ×0.015 ile aylık gelir ~10-80 bandına indirildi.
    for t in TABAKA_LISTE:
        gelir += tabakaGelir[t] * (oyuncu["vergiler"].get(t, 0.2)) * yonetimVerim * 0.015
    gelir += 4
    if oyuncu["kanunlar"]["ekonomi"] == "serbest":
        gelir -= 2
    gider = 0.0
    for k in ("yonetim", "ordu", "egitim", "refah"):
        gider += oyuncu["harcamalar"].get(k, 0) * 6
    faiz = oyuncu["borc"] * 0.02 / 12
    gider += faiz
    # YENİ: yeteneklerin aylık bütçe etkileri
    if aktifYetenek(s, "trade_agreements"):
        gelir += 7
    if aktifYetenek(s, "war_bonds"):
        gider += 8
    net = gelir - gider
    oyuncu["para"] = clamp(oyuncu["para"] + net, -1e9, 1e9)
    if net < 0 and oyuncu["para"] < 0:
        oyuncu["borc"] += -oyuncu["para"]
        oyuncu["para"] = 0
    elif net > 0 and oyuncu["borc"] > 0:
        odenen = min(net * 0.5, oyuncu["borc"])
        oyuncu["borc"] -= odenen
    gsyh = (s.get("sonOzet") or {}).get("gsyh", 10) or 10
    if oyuncu["borc"] > gsyh * 18:
        oyuncu["para"] = 0
        oyuncu["borc"] *= 0.6
        oyuncu["prestij"] = clamp(oyuncu["prestij"] - 0.1, 0, 1)
        gunlukEkle(s, "DEVLET İFLASI: borç yükü yeniden yapılandırıldı; prestij ağır darbe aldı.", "kriz")
    s["sonButce"] = {"gelir": gelir, "gider": gider, "net": net, "faiz": faiz}
    return s["sonButce"]


# ---------------- inşaat ----------------
def insaatIsle(s):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        return
    altyapi = aktifYetenek(s, "infrastructure_drive")
    for eyId in oyuncu["eyaletler"]:
        ey = s["eyaletler"].get(eyId)
        if not ey:
            continue
        for bid in list(ey["binalar"].keys()):
            for inst in ey["binalar"][bid]:
                if inst["insaatKalan"] > 0:
                    # YENİ: Altyapı Seferberliği → %25 hızlanma
                    if altyapi:
                        inst["insaatKalan"] -= 1.25
                    else:
                        inst["insaatKalan"] -= 1
                    if inst["insaatKalan"] <= 0:
                        inst["insaatKalan"] = 0
                        inst["isgucuDoluluk"] = 0.3
                        b = D.bina_bul(bid)
                        gunlukEkle(s, (b["ad"] if b else bid) + " tamamlandı — " + ey["ad"] + ".")


# ---------------- hukuk geçişi ----------------
def kanunGecisiIsle(s):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        return
    for kat in list(oyuncu["kanunGecisleri"].keys()):
        g = oyuncu["kanunGecisleri"][kat]
        g["kalanAy"] -= 1
        if g["kalanAy"] <= 0:
            oyuncu["kanunlar"][kat] = g["yeniDeger"]
            del oyuncu["kanunGecisleri"][kat]
            sec = None
            for x in D.KANUNLAR.get(kat, []):
                if x["id"] == g["yeniDeger"]:
                    sec = x
            gunlukEkle(s, "HUKUK YÜRÜRLÜKTE: " + (sec["ad"] if sec else g["yeniDeger"]) + ".")
            etki = kulupEtkisi(s, oyuncu)
            for k in KULUP_LISTE:
                oyuncu["kulupler"][k] = clamp((oyuncu["kulupler"].get(k, 0) * 0.85
                                               + (-0.05 if rast(0.5) else 0.05) - 0.03 * etki[k]), -1, 1)


# ---------------- teknoloji ----------------
def teknolojiIsle(s):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        return
    aktif = oyuncu["teknoloji"]["aktif"]
    if not aktif:
        return
    egitimIvmesi = 1 + oyuncu["harcamalar"].get("egitim", 0.3) * 0.5
    if aktifYetenek(s, "education_campaign"):
        egitimIvmesi += 0.5
    aktif["kalanIlerleme"] += egitimIvmesi
    if aktif["kalanIlerleme"] >= aktif["maliyet"]:
        oyuncu["teknoloji"]["tamamlanan"].append(aktif["id"])
        t = D.tech_bul(aktif["id"])
        if t:
            try:
                t["etki"](oyuncu, s)
            except Exception:
                pass
        gunlukEkle(s, "TEKNOLOJİ TAMAM: " + (t["ad"] if t else aktif["id"]) + ".")
        oyuncu["teknoloji"]["aktif"] = None


# ---------------- savaş & diplomasi ----------------
def savasIsle(s):
    for uId in list(s["ulkeler"].keys()):
        u = s["ulkeler"][uId]
        for savas in u["savaslar"][:]:
            rakip = s["ulkeler"].get(savas["rakip"])
            if not rakip:
                if savas in u["savaslar"]:
                    u["savaslar"].remove(savas)
                continue
            if uId != s["oyuncuUlke"] and savas["rakip"] != s["oyuncuUlke"]:
                savas["sure"] += 1
                if savas["sure"] > 24:
                    if savas in u["savaslar"]:
                        u["savaslar"].remove(savas)
                    rakip["savaslar"] = [x for x in rakip["savaslar"] if x["rakip"] != uId]
                continue
            gucBen = askeriGuc(s, u)
            gucRakip = askeriGuc(s, rakip)
            oran = gucBen / max(gucRakip, 0.01)
            degisim = 0.0
            strateji = savas.get("strateji", "kusatma")
            if strateji == "yildirma":
                degisim += 5
                if rast(0.18):
                    degisim -= 11
            elif strateji == "kusatma":
                degisim += 2.5
            else:  # inkitab (savunma)
                degisim -= 1
                if oran < 1:
                    degisim -= 1.5
            degisim *= clamp(oran, 0.4, 2.2)
            # YENİ: Tahkimat Hattı → oyuncu savunmadayken düşmanın pozitif kazanımı ×0.6
            if savas["rakip"] == s["oyuncuUlke"] and degisim > 0 and aktifYetenek(s, "defensive_line"):
                degisim *= 0.6
            savas["ilerleme"] = clamp(savas["ilerleme"] + degisim, -100, 100)
            savas["sure"] += 1
            if uId == s["oyuncuUlke"]:
                for eyId in u["eyaletler"]:
                    ey = s["eyaletler"].get(eyId)
                    if not ey:
                        continue
                    for p in ey["populations"]:
                        p["refah"] = clamp(p["refah"] - 0.002 * (2 if strateji == "yildirma" else 1), 0, 1)
            if savas["ilerleme"] >= 100:
                savasBitir(s, u, rakip, savas, True)
            elif savas["ilerleme"] <= -100:
                savasBitir(s, u, rakip, savas, False)
            elif savas["sure"] >= 60:
                savasSonu(s, u, rakip, savas, "beyaz")


def savasBitir(s, kazanan, kaybeden, savas, kazandi):
    if kazandi:
        amacId = savas.get("amacEyalet")
        if amacId and s["eyaletler"].get(amacId, {}).get("ulkeId") == kaybeden["id"]:
            s["eyaletler"][amacId]["ulkeId"] = kazanan["id"]
            kazanan["eyaletler"].append(amacId)
            kaybeden["eyaletler"] = [x for x in kaybeden["eyaletler"] if x != amacId]
        tazminat = max(0, min(kaybeden["para"], 60))
        kaybeden["para"] -= tazminat
        kazanan["para"] += tazminat
        kazanan["prestij"] = clamp(kazanan["prestij"] + 0.06, 0, 1)
        kaybeden["prestij"] = clamp(kaybeden["prestij"] - 0.08, 0, 1)
        if kazanan["id"] == s["oyuncuUlke"] or kaybeden["id"] == s["oyuncuUlke"]:
            if kazanan["id"] == s["oyuncuUlke"]:
                gunlukEkle(s, "SAVAŞ BİTTİ — " + kazanan["ad"] + " kazandı. Eyalet ve tazminat bize geçti.")
            else:
                gunlukEkle(s, "SAVAŞ BİTTİ — " + kazanan["ad"] + " kazandı. Kaybettiğimiz savaş: eyalet ve tazminat karşı tarafa geçti.", "kriz")
    else:
        savasSonu(s, kazanan, kaybeden, savas, "yenilgi")
    temizleSavas(kazanan, kaybeden, savas)


def savasSonu(s, u, rakip, savas, tur):
    if tur == "beyaz":
        if u["id"] == s["oyuncuUlke"] or rakip["id"] == s["oyuncuUlke"]:
            gunlukEkle(s, "Beyaz barış: " + u["ad"] + " — " + rakip["ad"] + " savaşı sonuçsuz kapandı.", "uyari")
        u["prestij"] = clamp(u["prestij"] - 0.01, 0, 1)
        rakip["prestij"] = clamp(rakip["prestij"] - 0.01, 0, 1)
    else:
        if u["id"] == s["oyuncuUlke"] or rakip["id"] == s["oyuncuUlke"]:
            gunlukEkle(s, "YENİLGİ: " + u["ad"] + " savaşı " + rakip["ad"] + "'a karşı kaybetti; tazminat ödüyor.",
                       "kriz" if u["id"] == s["oyuncuUlke"] else "bilgi")
        tazminat = max(0, min(u["para"], 50))
        u["para"] -= tazminat
        rakip["para"] += tazminat
        u["prestij"] = clamp(u["prestij"] - 0.08, 0, 1)
        rakip["prestij"] = clamp(rakip["prestij"] + 0.05, 0, 1)
    temizleSavas(u, rakip, savas)


def temizleSavas(u, rakip, savas):
    u["savaslar"] = [x for x in u["savaslar"] if x is not savas]
    rakip["savaslar"] = [x for x in rakip["savaslar"] if x["rakip"] != u["id"]]
    u["iliskiler"][rakip["id"]] = clamp(u["iliskiler"].get(rakip["id"], 0) - 20, -100, 100)
    rakip["iliskiler"][u["id"]] = clamp(rakip["iliskiler"].get(u["id"], 0) - 20, -100, 100)


# ---------------- AI kararları ----------------
def aiKararlari(s):
    aktifAiSavasi = sum(len(u["savaslar"]) for uid, u in s["ulkeler"].items() if uid != s["oyuncuUlke"])
    for u in D.ULKELER:
        us = s["ulkeler"].get(u["id"])
        if not us or us["id"] == s["oyuncuUlke"]:
            continue
        if (s["tick"] + us["aiKararAy"]) % 12 != 0:
            continue
        for hedefId in list(us["iliskiler"].keys()):
            ekle = -0.5 if us["aiKarakter"] == "agresif" else 0.5
            us["iliskiler"][hedefId] = clamp(us["iliskiler"][hedefId] * 0.95 + ekle, -100, 100)
        karakter = us["aiKarakter"]
        if karakter == "bariscil":
            continue
        if aktifAiSavasi >= 2:
            continue
        gucBen = askeriGuc(s, us)
        hedefler = []
        for v in D.ULKELER:
            if v["id"] == us["id"]:
                continue
            vs = s["ulkeler"].get(v["id"])
            if not vs:
                continue
            if v["id"] in us["ittifaklar"]:
                continue
            # YENİ: oyuncuyla güvenlik paktı varsa AI saldıramaz
            if v["id"] == s["oyuncuUlke"] and us["id"] in s["ulkeler"][s["oyuncuUlke"]].get("paktlar", {}):
                continue
            # mükerrer savaş engeli: aynı rakiple zaten savaştaysa hedef listesine alma
            if any(x["rakip"] == v["id"] for x in us["savaslar"]):
                continue
            hedefler.append({"id": v["id"], "iliski": us["iliskiler"].get(v["id"], 0), "guc": askeriGuc(s, vs)})
        saldirganlik = (s.get("zorlukAyar") or {}).get("aiSaldirganlik", 1.0)
        for h in hedefler:
            if h["iliski"] < -55 and gucBen > h["guc"] * 1.3 and (karakter == "agresif" or rast(0.4 * saldirganlik)):
                rakip = s["ulkeler"][h["id"]]
                amac = (rakip["eyaletler"][0] if rakip["eyaletler"] else None)
                us["savaslar"].append({"rakip": h["id"], "ilerleme": 0, "strateji": "kusatma", "sure": 0, "amacEyalet": amac})
                rakip["savaslar"].append({"rakip": us["id"], "ilerleme": 0, "strateji": "kusatma", "sure": 0, "amacEyalet": None})
                us["iliskiler"][h["id"]] = -100
                rakip["iliskiler"][us["id"]] = -100
                aktifAiSavasi += 1
                if h["id"] == s["oyuncuUlke"]:
                    gunlukEkle(s, "SAVAŞ İLANI: " + us["ad"] + " bize savaş ilan etti! Strateji belirleyin.", "kriz")
                break
        if karakter != "agresif" and rast(0.25):
            oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
            if oyuncu and us["iliskiler"].get(s["oyuncuUlke"], 0) > 55 \
                    and s["oyuncuUlke"] not in us["ittifaklar"] and us["id"] not in oyuncu["ittifaklar"]:
                gunlukEkle(s, "İttifak teklifi: " + us["ad"] + " ittifak öneriyor. (Diplomasi sekmesinden yanıtlayın)", "uyari")
        us["para"] += aiUretimKatsayisi(s, us) * 0.003
        if us["teknoloji"]["aktif"]:
            us["teknoloji"]["aktif"]["kalanIlerleme"] += 1
            if us["teknoloji"]["aktif"]["kalanIlerleme"] >= us["teknoloji"]["aktif"]["maliyet"]:
                t = D.tech_bul(us["teknoloji"]["aktif"]["id"])
                if t:
                    try:
                        t["etki"](us, s)
                    except Exception:
                        pass
                us["teknoloji"]["tamamlanan"].append(us["teknoloji"]["aktif"]["id"])
                us["teknoloji"]["aktif"] = None
        else:
            mevcut = [t for t in D.TEKNOLOJILER
                      if t["id"] not in us["teknoloji"]["tamamlanan"]
                      and all(o in us["teknoloji"]["tamamlanan"] for o in t["onkosul"])]
            if mevcut:
                t = random.choice(mevcut)
                us["teknoloji"]["aktif"] = {"id": t["id"], "maliyet": t["maliyet"], "kalanIlerleme": 0}


# ---------------- olaylar ----------------
def olayKontrol(s):
    if s["olaylar"]["aktif"]:
        return
    # 1) YETENEK olayları — kendi koşuluyla her ay (8% kapısını bypass eder)
    for o in D.OLAYLAR:
        if o.get("tur") != "yetenek":
            continue
        if o["id"] in s["olaylar"]["gecmis"]:
            continue
        try:
            tetiklendi = o["kosul"](s)
        except Exception:
            tetiklendi = False
        if tetiklendi:
            s["olaylar"]["aktif"] = o["id"]
            return
    # 2) Genel olaylar — %8 aylık şans
    if rast(0.08):
        adaylar = []
        for o in D.OLAYLAR:
            if o["id"] in s["olaylar"]["gecmis"] or o.get("tur") == "yetenek":
                continue
            try:
                if o["kosul"](s):
                    adaylar.append(o)
            except Exception:
                pass
        if adaylar:
            s["olaylar"]["aktif"] = random.choice(adaylar)["id"]


# ---------------- yetenek sistemi (YENİ) ----------------
def yetenekBul(yetenekId):
    for x in D.YETENEKLER:
        if x["id"] == yetenekId:
            return x
    return None


def yetenekKilitMetni(s, y):
    """Kilit koşulu sağlanmıyorsa sebep metni; sağlanıyorsa None."""
    u = s["ulkeler"].get(s["oyuncuUlke"])
    if not u:
        return "Devlet yok."
    for kosul, deger in (y.get("kilit") or {}).items():
        if kosul == "prestij" and u["prestij"] < deger:
            return "Prestij %.2f gerekli — şu an %.2f" % (deger, u["prestij"])
    return None


def yetenekKullan(s, yetenekId, hedefUlkeId=None):
    """Oyuncu yetenek kullanımı. Döner: {"tamam": bool, "mesaj": str}"""
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    y = yetenekBul(yetenekId)
    if not oyuncu or not y:
        return {"tamam": False, "mesaj": "Geçersiz istek."}
    # bekleme
    if s["beklemeler"].get(yetenekId, 0) > 0:
        return {"tamam": False, "mesaj": "%s: beklemesi sürüyor (%d ay)." % (y["ad"], s["beklemeler"][yetenekId])}
    # ayda 1 yetenek kuralı
    if s.get("aylikYetenekKullanildi"):
        return {"tamam": False, "mesaj": "Bu ay zaten bir yetenek kullanıldı — gelecek aya kadar bekle."}
    # kilit
    kilitMetni = yetenekKilitMetni(s, y)
    if kilitMetni:
        return {"tamam": False, "mesaj": y["ad"] + ": " + kilitMetni}
    # savaş gerektiren yetenekler
    savasGerektiren = ("rapid_offensive", "defensive_line")
    if yetenekId in savasGerektiren and not oyuncu["savaslar"]:
        return {"tamam": False, "mesaj": y["ad"] + " aktif savaş gerektirir."}
    # maliyet (zorluk çarpanıyla)
    maliyet = round(y["maliyet"] * (s.get("zorlukAyar") or {}).get("yetenekMaliyet", 1.0))
    if maliyet > 0 and oyuncu["para"] < maliyet:
        return {"tamam": False, "mesaj": "Hazine yetersiz: %d altın gerekli, kasa %d." % (maliyet, round(oyuncu["para"]))}
    # İç Borçlanma güvenlik kilidi: taksitler sürerken ikinci borçlanma yok
    if yetenekId == "war_bonds" and s["yetenekAktif"].get("war_bonds", 0) > 0:
        return {"tamam": False, "mesaj": "Önceki tahvillerin taksitleri sürerken yeni borçlanma yapılamaz."}
    # hedef gerekli mi?
    if yetenekId == "security_pact":
        if not hedefUlkeId or hedefUlkeId == s["oyuncuUlke"]:
            return {"tamam": False, "mesaj": "Bir hedef ülke seçin."}
        if hedefUlkeId in oyuncu["ittifaklar"]:
            return {"tamam": False, "mesaj": "İttifak üyesiyle zaten savaş yasak."}
        if hedefUlkeId in oyuncu.get("paktlar", {}):
            return {"tamam": False, "mesaj": "Bu ülkeyle pakt zaten yürürlükte."}
    if yetenekId == "envoy_mission":
        if not hedefUlkeId or hedefUlkeId == s["oyuncuUlke"]:
            return {"tamam": False, "mesaj": "Bir hedef ülke seçin."}
    kazanc = 0
    # --- etki uygulama ---
    if yetenekId == "security_pact":
        oyuncu.setdefault("paktlar", {})[hedefUlkeId] = {"kalanAy": 24}
        hedef = s["ulkeler"].get(hedefUlkeId)
        if hedef:
            hedef["iliskiler"][s["oyuncuUlke"]] = clamp(hedef["iliskiler"].get(s["oyuncuUlke"], 0) + 8, -100, 100)
            oyuncu["iliskiler"][hedefUlkeId] = clamp(oyuncu["iliskiler"].get(hedefUlkeId, 0) + 8, -100, 100)
    elif yetenekId == "war_bonds":
        oyuncu["para"] += 150
        oyuncu["borc"] += 150
        s["yetenekAktif"]["war_bonds"] = 24
        s["son_tahvil_tick"] = s["tick"]
    elif yetenekId == "envoy_mission":
        hedef = s["ulkeler"].get(hedefUlkeId)
        if not hedef:
            return {"tamam": False, "mesaj": "Hedef ülke bulunamadı."}
        tekrar = s["elciSayac"].get(hedefUlkeId, 0)
        kazanc = max(4, 12 - 2 * tekrar)
        hedef["iliskiler"][s["oyuncuUlke"]] = clamp(hedef["iliskiler"].get(s["oyuncuUlke"], 0) + kazanc, -100, 100)
        oyuncu["iliskiler"][hedefUlkeId] = clamp(oyuncu["iliskiler"].get(hedefUlkeId, 0) + kazanc, -100, 100)
        s["elciSayac"][hedefUlkeId] = tekrar + 1
        s["son_elci_tick"] = s["tick"]
        s["son_elci_hedef"] = hedefUlkeId
    elif yetenekId == "rapid_offensive":
        if s.get("savasYetenekIlerleme", 0) >= 16:
            return {"tamam": False, "mesaj": "Bu savaşta yetenek kaynaklı ilerleme tavanı doldu (+16)."}
        oyuncu["savaslar"][0]["ilerleme"] = clamp(oyuncu["savaslar"][0]["ilerleme"] + 8, -100, 100)
        s["savasYetenekIlerleme"] = s.get("savasYetenekIlerleme", 0) + 8
        for eyId in oyuncu["eyaletler"]:
            ey = s["eyaletler"].get(eyId)
            if ey:
                for p in ey["populations"]:
                    p["radikalizm"] = clamp(p["radikalizm"] + 0.02, 0, 1)
    elif yetenekId == "national_festival":
        oyuncu["prestij"] = clamp(oyuncu["prestij"] + 0.01, 0, 1)
        for eyId in oyuncu["eyaletler"]:
            ey = s["eyaletler"].get(eyId)
            if ey:
                for p in ey["populations"]:
                    p["refah"] = clamp(p["refah"] + 0.03, 0, 1)
    # süreli etkiler (yukarıda özel işlenenler hariç)
    ozelIslenen = ("war_bonds", "envoy_mission", "rapid_offensive", "national_festival", "security_pact")
    if y["sure"] > 0 and yetenekId not in ozelIslenen:
        s["yetenekAktif"][yetenekId] = y["sure"]
    # bekleme + maliyet + ay bayrağı
    s["beklemeler"][yetenekId] = y["bekleme"]
    if maliyet > 0:
        oyuncu["para"] -= maliyet
    s["aylikYetenekKullanildi"] = True
    hedefMetni = ""
    if hedefUlkeId and hedefUlkeId in s["ulkeler"]:
        hedefMetni = " (" + s["ulkeler"][hedefUlkeId]["ad"] + " hedefli)"
    gunlukEkle(s, "YETENEK: " + y["ad"] + " kullanıldı" + hedefMetni + ".", "uyari")
    mesaj = y["ad"] + " yürürlükte."
    if yetenekId == "envoy_mission":
        mesaj = y["ad"] + ": ilişki +" + str(kazanc) + "."
    return {"tamam": True, "mesaj": mesaj}


def _yetenekTiklari(s):
    """Her tick: beklemeleri azalt, süreli etkileri işle/bitiştir."""
    for k in list(s["beklemeler"].keys()):
        if s["beklemeler"][k] > 0:
            s["beklemeler"][k] -= 1
            if s["beklemeler"][k] <= 0:
                del s["beklemeler"][k]
    ya = s.get("yetenekAktif", {})
    if ya.get("mobilization", 0) > 0:
        ya["mobilization"] -= 1
        if ya["mobilization"] <= 0:
            del ya["mobilization"]
            s["son_seferberlik_bitis_tick"] = s["tick"]
            gunlukEkle(s, "Genel Seferberlik süresi doldu; birlikler terhis ediliyor.")
    if ya.get("war_bonds", 0) > 0:
        ya["war_bonds"] -= 1
        if ya["war_bonds"] <= 0:
            del ya["war_bonds"]
            gunlukEkle(s, "Tahvil taksitleri tamamlandı; bütçedeki yük kalktı.")
    for k in ("trade_agreements", "infrastructure_drive", "education_campaign", "national_festival", "defensive_line"):
        if ya.get(k, 0) > 0:
            ya[k] -= 1
            if ya[k] <= 0:
                del ya[k]
                y = yetenekBul(k)
                gunlukEkle(s, "Etki süresi doldu: " + (y["ad"] if y else k) + ".")
    # pakt sayaçları
    for uId, u in s["ulkeler"].items():
        for hedefId in list(u.get("paktlar", {}).keys()):
            p = u["paktlar"][hedefId]
            p["kalanAy"] -= 1
            if p["kalanAy"] <= 0:
                del u["paktlar"][hedefId]
                if uId == s["oyuncuUlke"]:
                    gunlukEkle(s, "Güvenlik Paktı süresi doldu (" + s["ulkeler"].get(hedefId, {}).get("ad", hedefId) + ").", "uyari")
    # savaş bitince yetenek ilerleme sayacı sıfırlanır
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if oyuncu and not oyuncu["savaslar"] and s.get("savasYetenekIlerleme", 0) > 0:
        s["savasYetenekIlerleme"] = 0
    # Ulusal Bayram: kademeli radikalizm düşüşü
    if oyuncu and aktifYetenek(s, "national_festival"):
        for eyId in oyuncu["eyaletler"]:
            ey = s["eyaletler"].get(eyId)
            if ey:
                for p in ey["populations"]:
                    p["radikalizm"] = clamp(p["radikalizm"] - 0.005, 0, 1)


# ---------------- ana tick ----------------
def tick(s):
    if not s or s["oyunBitti"]:
        return
    s["tick"] += 1
    s["aylikYetenekKullanildi"] = False
    _yetenekTiklari(s)
    insaatIsle(s)
    s["sonUretimDegeri"] = ulretimVePazar(s) or 0
    nufusGuncelle(s)
    butceIsle(s)
    kanunGecisiIsle(s)
    teknolojiIsle(s)
    savasIsle(s)
    aiKararlari(s)
    olayKontrol(s)
    s["ay"] += 1
    if s["ay"] > 12:
        s["ay"] = 1
        s["yil"] += 1
    if s["ay"] == 12:
        ozet = hesaplaOzet(s)
        s["skorGecmisi"].append({"yil": s["yil"], "ay": s["ay"], "gsyh": ozet["gsyh"],
                                 "refahOrt": ozet["refahOrt"], "radikalizm": ozet["radikalizm"]})
        if len(s["skorGecmisi"]) > 120:
            s["skorGecmisi"].pop(0)
    if s["yil"] > D.DONEM["bitisYil"]:
        s["oyunBitti"] = True
    hesaplaOzet(s)


# ---------------- özet ----------------
def hesaplaOzet(s):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        ozet = {"gsyh": 0, "gelir": 0, "gider": 0, "borc": 0, "radikalizm": 0, "refahOrt": 0,
                "nufus": 0, "prestij": 0, "eyaletSayisi": 0}
        s["sonOzet"] = ozet
        return ozet
    ozet = {
        "gsyh": s.get("sonUretimDegeri", 0) or 0,
        "gelir": (s.get("sonButce") or {}).get("gelir", 0),
        "gider": (s.get("sonButce") or {}).get("gider", 0),
        "borc": oyuncu.get("borc", 0),
        "radikalizm": radikalizmOrt(s, oyuncu["id"]),
        "refahOrt": refahOrt(s, oyuncu["id"]),
        "nufus": nufusToplam(s, oyuncu["id"]),
        "prestij": oyuncu.get("prestij", 0),
        "eyaletSayisi": len(oyuncu["eyaletler"]),
    }
    s["sonOzet"] = ozet
    return ozet


# ---------------- oyuncu aksiyonları ----------------
def vergiAyarla(s, tabaka, oran):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu or tabaka not in TABAKA_LISTE:
        return
    oyuncu["vergiler"][tabaka] = clamp(oran, 0, 0.9)


def harcamaAyarla(s, kalem, oran):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu or kalem not in ("yonetim", "ordu", "egitim", "refah"):
        return
    oyuncu["harcamalar"][kalem] = clamp(oran, 0, 1)


def binaInsaaBaslat(s, eyaletId, binaTipId):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    ey = s["eyaletler"].get(eyaletId)
    b = D.bina_bul(binaTipId)
    if not oyuncu or not ey or not b:
        return {"hata": "Geçersiz istek."}
    if ey["ulkeId"] != oyuncu["id"]:
        return {"hata": "Bu eyalet bizim değil."}
    maliyet = round(b["maliyet"] * (1 + 0.35 * len(ey["binalar"].get(binaTipId, []))))
    if oyuncu["para"] < maliyet:
        return {"hata": "Hazine yetersiz: %d gerekli, kasa %d." % (maliyet, round(oyuncu["para"]))}
    oyuncu["para"] -= maliyet
    ey["binalar"].setdefault(binaTipId, []).append(
        {"seviye": 1, "insaatKalan": b.get("insaatSuresi", 6), "isgucuDoluluk": 0})
    gunlukEkle(s, b["ad"] + " inşası başladı — " + ey["ad"] + " (" + str(maliyet) + " ödendi).")
    return {"tamam": True, "maliyet": maliyet, "sure": b.get("insaatSuresi", 6)}


def kanunDegistir(s, kategori, yeniDeger):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        return {"tamam": False, "mesaj": "Devlet yok."}
    secenekler = D.KANUNLAR.get(kategori, [])
    sec = None
    for x in secenekler:
        if x["id"] == yeniDeger:
            sec = x
    if not sec:
        return {"tamam": False, "mesaj": "Bilinmeyen hukuk seçeneği."}
    if oyuncu["kanunlar"].get(kategori) == yeniDeger:
        return {"tamam": False, "mesaj": "Bu hukuk zaten yürürlükte."}
    if kategori in oyuncu["kanunGecisleri"]:
        return {"tamam": False, "mesaj": "Bu kategoride yürüyen bir reform var."}
    dt = oyuncu["kanunlar"]["devletTipi"]
    if kategori == "oyHakki":
        if dt == "mutlakiyet" and yeniDeger == "evrensel":
            return {"tamam": False, "mesaj": "Mutlakiyet rejiminde evrensel oy hakkı ilan edilemez — önce devlet yapısı değişmeli."}
        if dt in ("meşrutiyet", "mesrutiyet") and yeniDeger == "tabakasal":
            return {"tamam": False, "mesaj": "Meşrutiyette tabakasal oy hakkı geriye çekilemez."}
    if kategori == "devletTipi" and yeniDeger == "mutlakiyet" and dt in ("meşrutiyet", "mesrutiyet", "parlamenter"):
        return {"tamam": False, "mesaj": "Mutlakiyete dönüş yok — meclis buna asla onay vermez."}
    mevcutIdx = next((i for i, x in enumerate(secenekler) if x["id"] == oyuncu["kanunlar"].get(kategori)), -1)
    yeniIdx = next((i for i, x in enumerate(secenekler) if x["id"] == yeniDeger), -1)
    if mevcutIdx >= 0 and yeniIdx > mevcutIdx + 1:
        return {"tamam": False, "mesaj": "Reform kademeli yapılır: önce bir sonraki adım (「" + secenekler[mevcutIdx + 1]["ad"] + "」)."}
    etki = kulupEtkisi(s, oyuncu)
    karsiBloklar = {"diniSistem": ["ruhani", "asiret"], "medeniHukuk": ["ruhani", "asiret"],
                    "oyHakki": ["asiret", "ruhani"], "devletTipi": ["ordu", "ruhani"],
                    "ekonomi": ["sermaye", "asiret"], "orduModeli": ["ordu", "asiret"], "egitim": ["ruhani"]}
    blok = karsiBloklar.get(kategori, [])
    karsiGuc = 0.0
    for k in blok:
        mem = oyuncu["kulupler"].get(k, 0)
        if mem < -0.05:
            karsiGuc += etki[k] * (1 - mem)
    if yeniIdx > mevcutIdx and karsiGuc > 1.15 and rast(0.65):
        if blok:
            oyuncu["kulupler"][blok[0]] = clamp(oyuncu["kulupler"].get(blok[0], 0) - 0.1, -1, 1)
        adlar = ", ".join((D.kulup_bul(k) or {"ad": k})["ad"] for k in blok)
        return {"tamam": False, "mesaj": "Meclis reddetti: " + adlar + " bloğu güçlü muhalefet ediyor. Önce memnuniyetlerini artırın."}
    sure = clamp((6 + (yeniIdx - mevcutIdx) * 6) if yeniIdx > mevcutIdx else 4, 4, 24)
    oyuncu["kanunGecisleri"][kategori] = {"yeniDeger": yeniDeger, "kalanAy": int(sure)}
    gunlukEkle(s, "REFORM SÜRECİ: " + sec["ad"] + " — " + str(int(sure)) + " ay içinde meclisten geçmesi bekleniyor.", "uyari")
    return {"tamam": True, "kalanAy": int(sure), "mesaj": "Reform süreci başladı (" + str(int(sure)) + " ay)."}


def teknolojiBaslat(s, teknolojiId):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        return {"hata": "Devlet yok."}
    if oyuncu["teknoloji"]["aktif"]:
        t0 = D.tech_bul(oyuncu["teknoloji"]["aktif"]["id"])
        return {"hata": "Araştırma zaten sürüyor: " + (t0["ad"] if t0 else oyuncu["teknoloji"]["aktif"]["id"]) + "."}
    t = D.tech_bul(teknolojiId)
    if not t:
        return {"hata": "Bilinmeyen teknoloji."}
    if teknolojiId in oyuncu["teknoloji"]["tamamlanan"]:
        return {"hata": "Zaten tamamlanmış."}
    eksik = [o for o in t["onkosul"] if o not in oyuncu["teknoloji"]["tamamlanan"]]
    if eksik:
        return {"hata": "Ön koşullar eksik: " + ", ".join(eksik) + "."}
    oyuncu["teknoloji"]["aktif"] = {"id": teknolojiId, "maliyet": t["maliyet"], "kalanIlerleme": 0}
    gunlukEkle(s, "Araştırma başladı: " + t["ad"] + " (" + str(t["maliyet"]) + " ilerleme puanı).")
    return {"tamam": True}


def diplomasiEylem(s, hedefUlkeId, tur):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    hedef = s["ulkeler"].get(hedefUlkeId)
    if not oyuncu or not hedef or hedefUlkeId == s["oyuncuUlke"]:
        return {"hata": "Geçersiz hedef."}
    paktVar = (hedefUlkeId in oyuncu.get("paktlar", {})) or (s["oyuncuUlke"] in hedef.get("paktlar", {}))
    if tur == "iyi_iliski":
        oyuncu["iliskiler"][hedefUlkeId] = clamp(oyuncu["iliskiler"].get(hedefUlkeId, 0) + 10, -100, 100)
        hedef["iliskiler"][s["oyuncuUlke"]] = clamp(hedef["iliskiler"].get(s["oyuncuUlke"], 0) + 10, -100, 100)
        oyuncu["para"] = max(0, oyuncu["para"] - 5)
        gunlukEkle(s, "Diplomasi: " + hedef["ad"] + " ile ilişkiler iyileştirildi (+10).")
        return {"tamam": True, "mesaj": "İlişki +10."}
    if tur == "ittifak":
        if oyuncu["iliskiler"].get(hedefUlkeId, 0) < 55:
            return {"tamam": False, "mesaj": hedef["ad"] + " ittifaka sıcak bakmıyor (ilişki ≥ 55 gerekli)."}
        if hedefUlkeId in oyuncu["ittifaklar"]:
            return {"tamam": False, "mesaj": "Zaten ittifaktayız."}
        oyuncu["ittifaklar"].append(hedefUlkeId)
        hedef["ittifaklar"].append(s["oyuncuUlke"])
        gunlukEkle(s, "İTTİFAK: " + hedef["ad"] + " ile ittifak kuruldu.")
        return {"tamam": True, "mesaj": "İttifak kuruldu."}
    if tur == "hudut_talebi":
        oyuncu["prestij"] = clamp(oyuncu["prestij"] - 0.02, 0, 1)
        gucBen = askeriGuc(s, oyuncu)
        gucRakip = askeriGuc(s, hedef)
        if gucBen > gucRakip * 1.6 and rast(0.4):
            amacId = hedef["eyaletler"][-1] if hedef["eyaletler"] else None
            if amacId and s["eyaletler"].get(amacId):
                s["eyaletler"][amacId]["ulkeId"] = oyuncu["id"]
                oyuncu["eyaletler"].append(amacId)
                hedef["eyaletler"] = [x for x in hedef["eyaletler"] if x != amacId]
                hedef["iliskiler"][s["oyuncuUlke"]] = -100
                oyuncu["iliskiler"][hedefUlkeId] = -100
                gunlukEkle(s, "HUDUT TALEBİ kabul edildi: " + s["eyaletler"][amacId]["ad"] + " bize devredildi.")
                return {"tamam": True, "mesaj": s["eyaletler"][amacId]["ad"] + " teslim edildi."}
        hedef["iliskiler"][s["oyuncuUlke"]] = clamp(hedef["iliskiler"].get(s["oyuncuUlke"], 0) - 25, -100, 100)
        gunlukEkle(s, "HUDUT TALEBİ reddedildi: " + hedef["ad"] + " talebi reddetti; ilişkiler bozuldu.", "uyari")
        return {"tamam": False, "mesaj": "Talep reddedildi (ilişki −25)."}
    if tur == "savas_ilan":
        if paktVar:
            if hedefUlkeId in oyuncu.get("paktlar", {}):
                del oyuncu["paktlar"][hedefUlkeId]
            if s["oyuncuUlke"] in hedef.get("paktlar", {}):
                del hedef["paktlar"][s["oyuncuUlke"]]
            oyuncu["iliskiler"][hedefUlkeId] = -100
            hedef["iliskiler"][s["oyuncuUlke"]] = -100
            oyuncu["prestij"] = clamp(oyuncu["prestij"] - 0.05, 0, 1)
            gunlukEkle(s, "PAKT BOZULDU: " + hedef["ad"] + "'a ihanet edildi; prestij ve itibar ağır darbe aldı.", "kriz")
            return {"tamam": False, "mesaj": "Güvenlik Paktı bozuldu: ilişki −100, prestij −0.05. Savaş için bir sonraki ay tekrar deneyin."}
        if any(x["rakip"] == hedefUlkeId for x in oyuncu["savaslar"]):
            return {"tamam": False, "mesaj": "Zaten savaştayız."}
        if hedefUlkeId in oyuncu["ittifaklar"]:
            return {"tamam": False, "mesaj": "İttifak üyesine savaş ilan edilemez; önce ittifaktan çıkın."}
        amacId = (hedef["eyaletler"][0] if hedef["eyaletler"] else None)
        oyuncu["savaslar"].append({"rakip": hedefUlkeId, "ilerleme": 0, "strateji": "kusatma", "sure": 0, "amacEyalet": amacId})
        hedef["savaslar"].append({"rakip": s["oyuncuUlke"], "ilerleme": 0, "strateji": "kusatma", "sure": 0, "amacEyalet": None})
        oyuncu["iliskiler"][hedefUlkeId] = -100
        hedef["iliskiler"][s["oyuncuUlke"]] = -100
        s["savasYetenekIlerleme"] = 0
        amacAdi = s["eyaletler"][amacId]["ad"] if amacId and amacId in s["eyaletler"] else "—"
        gunlukEkle(s, "SAVAŞ İLANI: " + hedef["ad"] + "'a savaş ilan ettik. Amaç eyalet: " + amacAdi + ".", "kriz")
        return {"tamam": True, "mesaj": "Savaş ilan edildi."}
    return {"hata": "Bilinmeyen diplomasi eylemi."}


def savasStrateji(s, strateji):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        return {"hata": "Devlet yok."}
    if strateji not in ("yildirma", "kusatma", "inkitab"):
        return {"hata": "Bilinmeyen strateji."}
    for savas in oyuncu["savaslar"]:
        savas["strateji"] = strateji
    return {"tamam": True, "mesaj": "Savaş stratejisi: " + strateji + "."}


def savasSonaErdir(s):
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    if not oyuncu:
        return {"hata": "Devlet yok."}
    if not oyuncu["savaslar"]:
        return {"hata": "Aktif savaş yok."}
    savas = oyuncu["savaslar"][0]
    rakip = s["ulkeler"].get(savas["rakip"])
    if rakip:
        savasSonu(s, oyuncu, rakip, savas, "beyaz")
    else:
        oyuncu["savaslar"].pop(0)
    return {"tamam": True, "mesaj": "Beyaz barış önerildi ve kabul gördü."}


def olaySecim(s, olayId, secenekIndex):
    olay = None
    for o in D.OLAYLAR:
        if o["id"] == olayId:
            olay = o
    if not olay:
        return {"hata": "Olay bulunamadı."}
    idx = int(clamp(secenekIndex, 0, max(len(olay["secenekler"]) - 1, 0)))
    sec = olay["secenekler"][idx]
    oyuncu = s["ulkeler"].get(s["oyuncuUlke"])
    try:
        sec["etki"](s, oyuncu)
    except Exception:
        pass
    if s["olaylar"]["aktif"] == olayId:
        s["olaylar"]["aktif"] = None
    s["olaylar"]["gecmis"].append(olayId)
    if len(s["olaylar"]["gecmis"]) > 400:
        s["olaylar"]["gecmis"].pop(0)
    gunlukEkle(s, "Olay sonuçlandı: " + olay["baslik"] + " → " + sec["metin"], "uyari")
    return {"tamam": True}


# ---------------- kayıt / yükleme ----------------
SAVE_KLASOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kayitlar")


def kaydet(s, slot):
    os.makedirs(SAVE_KLASOR, exist_ok=True)
    yol = os.path.join(SAVE_KLASOR, "slot%d.json" % slot)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False)
    return {"tamam": True, "yol": yol}


def kayitMetasi():
    """Ana menü kayıt listesi için: [(slot, ülke adı, yıl, tarih-str)]"""
    sonuc = []
    if not os.path.isdir(SAVE_KLASOR):
        return sonuc
    for slot in (1, 2, 3):
        yol = os.path.join(SAVE_KLASOR, "slot%d.json" % slot)
        if os.path.exists(yol):
            try:
                with open(yol, "r", encoding="utf-8") as f:
                    d = json.load(f)
                u = d.get("ulkeler", {}).get(d.get("oyuncuUlke", ""), {})
                sonuc.append({"slot": slot, "ulkeAd": u.get("ad", d.get("oyuncuUlke", "?")),
                              "yil": d.get("yil", "?"), "bitmis": d.get("oyunBitti", False)})
            except Exception:
                sonuc.append({"slot": slot, "ulkeAd": "?", "yil": "?", "bitmis": False})
    return sonuc


def yukle(slot):
    yol = os.path.join(SAVE_KLASOR, "slot%d.json" % slot)
    if not os.path.exists(yol):
        return None, "Bu slotta kayıt yok."
    with open(yol, "r", encoding="utf-8") as f:
        s = json.load(f)
    s.setdefault("beklemeler", {})
    s.setdefault("yetenekAktif", {})
    s.setdefault("elciSayac", {})
    s.setdefault("savasYetenekIlerleme", 0)
    s.setdefault("aylikYetenekKullanildi", False)
    s.setdefault("son_tahvil_tick", None)
    s.setdefault("son_seferberlik_bitis_tick", None)
    s.setdefault("son_elci_tick", None)
    s.setdefault("son_elci_hedef", None)
    s.setdefault("zorlukAyar", D.ZORLUKLAR.get(s.get("zorluk", "normal"), D.ZORLUKLAR["normal"]))
    s.setdefault("olaylar", {"aktif": None, "gecmis": []})
    s["olaylar"].setdefault("gecmis", [])
    s.setdefault("pazar", {"fiyatlar": {}, "arz": {}, "talep": {}})
    for m in D.MALLAR:
        if not isinstance(s["pazar"]["fiyatlar"].get(m["id"]), (int, float)) or not math.isfinite(s["pazar"]["fiyatlar"].get(m["id"], 0)):
            s["pazar"]["fiyatlar"][m["id"]] = m["bazFiyat"]
        s["pazar"]["arz"].setdefault(m["id"], 0)
        s["pazar"]["talep"].setdefault(m["id"], 0)
    for uId, u in s["ulkeler"].items():
        u.setdefault("paktlar", {})
        u.setdefault("vergiler", {"alt": 0.3, "orta": 0.25, "ust": 0.2})
        u.setdefault("harcamalar", {"yonetim": 0.5, "ordu": 0.4, "egitim": 0.3, "refah": 0.2})
        u.setdefault("kanunlar", tpl(D.ULKELER[0]["baslangicKanun"]) if D.ULKELER else {})
        for t in TABAKA_LISTE:
            u["vergiler"].setdefault(t, 0.2)
        for k in ("yonetim", "ordu", "egitim", "refah"):
            u["harcamalar"].setdefault(k, 0.2)
        u.setdefault("teknoloji", {"tamamlanan": [], "aktif": None})
        u["teknoloji"].setdefault("tamamlanan", [])
        u["teknoloji"].setdefault("aktif", None)
        u.setdefault("teknolojiBonusu", {"uretim": 1, "refah": 0, "askeri": 1, "vergiVerimliligi": 1})
        u.setdefault("kanunGecisleri", {})
        u.setdefault("kulupler", {k: 0 for k in KULUP_LISTE})
        u.setdefault("savaslar", [])
        u.setdefault("ittifaklar", [])
        u.setdefault("iliskiler", {})
        u.setdefault("eyaletler", [])
    for eId, ey in s["eyaletler"].items():
        ey.setdefault("istihdam", {"ust": 0, "orta": 0, "alt": 0})
        ey.setdefault("populations", [])
    s["oyunBitti"] = bool(s.get("oyunBitti"))
    hesaplaOzet(s)
    return s, None
