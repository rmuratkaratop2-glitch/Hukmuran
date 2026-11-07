# -*- coding: utf-8 -*-
"""
test_engine.py — engine.py çekirdek birim testleri.

pygame GEREKTİRMEZ; yalnızca stdlib + data/engine kullanır.
Çalıştırma (proje klasöründe):
    python -m unittest test_engine -v
"""
import math
import tempfile
import unittest

import engine as E
import data as D


class TestClamp(unittest.TestCase):
    def test_sinirlar(self):
        self.assertEqual(E.clamp(5, 0, 10), 5)
        self.assertEqual(E.clamp(-5, 0, 10), 0)
        self.assertEqual(E.clamp(99, 0, 10), 10)

    def test_nan_ve_sonsuz(self):
        # clamp, sonlu olmayan her girdiyi güvenli alt sınıra çeker
        self.assertEqual(E.clamp(float("nan"), 0, 1), 0)
        self.assertEqual(E.clamp(float("inf"), 0, 1), 0)
        self.assertEqual(E.clamp(float("-inf"), 0, 1), 0)

    def test_gecersiz_tip(self):
        self.assertEqual(E.clamp("abc", 0, 1), 0)


class TestPazarFiyat(unittest.TestCase):
    def test_denge(self):
        baz = D.mal_bul("tahil")["bazFiyat"]
        self.assertAlmostEqual(E.pazarHedefFiyat("tahil", 100, 100), baz)

    def test_arz_fazlasi_tavan(self):
        baz = D.mal_bul("tahil")["bazFiyat"]
        self.assertAlmostEqual(E.pazarHedefFiyat("tahil", 1000, 10), baz * 2.0)

    def test_arz_azligi_taban(self):
        baz = D.mal_bul("tahil")["bazFiyat"]
        self.assertAlmostEqual(E.pazarHedefFiyat("tahil", 1, 1000), baz * 0.5)

    def test_bilinmeyen_mal(self):
        self.assertEqual(E.pazarHedefFiyat("yok", 1, 1), 5.0)


class TestVeriButunlugu(unittest.TestCase):
    def test_ulke_eyalet_eslesmesi(self):
        ulkeler = {u["id"] for u in D.ULKELER}
        for e in D.EYALETLER:
            self.assertIn(e["ulkeId"], ulkeler, e["id"])

    def test_bina_girdi_cikti_mallari(self):
        mallar = {m["id"] for m in D.MALLAR}
        for b in D.BINALAR:
            for mid in b.get("girdiler", {}):
                self.assertIn(mid, mallar, b["id"])
            for mid in b.get("ciktilar", {}):
                self.assertIn(mid, mallar, b["id"])

    def test_teknoloji_onkosul(self):
        ids = {t["id"] for t in D.TEKNOLOJILER}
        for t in D.TEKNOLOJILER:
            for dep in t.get("onkosul", []):
                self.assertIn(dep, ids, t["id"])


class TestYeniOyun(unittest.TestCase):
    def setUp(self):
        self.s = E.yeniOyun("osmanli", "normal")

    def test_temel_yapi(self):
        self.assertEqual(self.s["oyuncuUlke"], "osmanli")
        self.assertEqual(self.s["yil"], 1836)
        self.assertEqual(self.s["ay"], 1)
        self.assertEqual(len(self.s["ulkeler"]), len(D.ULKELER))
        self.assertEqual(len(self.s["eyaletler"]), len(D.EYALETLER))

    def test_oyuncu_eyalet_iliskisi(self):
        o = self.s["ulkeler"]["osmanli"]
        self.assertTrue(o["eyaletler"])
        for eid in o["eyaletler"]:
            self.assertEqual(self.s["eyaletler"][eid]["ulkeId"], "osmanli")

    def test_ozet_sonlu(self):
        ozet = self.s.get("sonOzet") or E.hesaplaOzet(self.s)
        for k, v in ozet.items():
            self.assertTrue(math.isfinite(float(v)), "%s sonlu değil: %r" % (k, v))


class TestTick(unittest.TestCase):
    def test_ay_ilerler(self):
        s = E.yeniOyun("osmanli")
        for _ in range(3):
            E.tick(s)
        self.assertEqual((s["yil"], s["ay"]), (1836, 4))

    def test_yil_donumu(self):
        s = E.yeniOyun("osmanli")
        for _ in range(12):
            E.tick(s)
        self.assertEqual((s["yil"], s["ay"]), (1837, 1))

    def test_tick_nan_uretmez(self):
        s = E.yeniOyun("osmanli")
        for _ in range(24):
            E.tick(s)
        ozet = E.hesaplaOzet(s)
        for k, v in ozet.items():
            self.assertTrue(math.isfinite(float(v)), "%s sonlu değil: %r" % (k, v))


class TestAksiyonlar(unittest.TestCase):
    def test_vergi_clamp(self):
        s = E.yeniOyun("osmanli")
        E.vergiAyarla(s, "alt", 5.0)
        self.assertEqual(s["ulkeler"]["osmanli"]["vergiler"]["alt"], 0.9)
        E.vergiAyarla(s, "alt", -3.0)
        self.assertEqual(s["ulkeler"]["osmanli"]["vergiler"]["alt"], 0.0)

    def test_harcama_clamp(self):
        s = E.yeniOyun("osmanli")
        E.harcamaAyarla(s, "ordu", 9.9)
        self.assertEqual(s["ulkeler"]["osmanli"]["harcamalar"]["ordu"], 1.0)

    def test_vergi_gecersiz_tabaka(self):
        s = E.yeniOyun("osmanli")
        once = dict(s["ulkeler"]["osmanli"]["vergiler"])
        E.vergiAyarla(s, "yok", 0.5)
        self.assertEqual(s["ulkeler"]["osmanli"]["vergiler"], once)

    def test_bina_hazine_yetersiz(self):
        s = E.yeniOyun("osmanli")
        o = s["ulkeler"]["osmanli"]
        ey = s["eyaletler"][o["eyaletler"][0]]
        sonuc = E.binaInsaaBaslat(s, ey["id"], "silah_fabrikasi")
        self.assertIn("hata", sonuc)

    def test_bina_insaat_baslat(self):
        s = E.yeniOyun("osmanli")
        o = s["ulkeler"]["osmanli"]
        ey = s["eyaletler"][o["eyaletler"][0]]
        once = o["para"]
        sonuc = E.binaInsaaBaslat(s, ey["id"], "ciftlik")
        self.assertTrue(sonuc.get("tamam"))
        self.assertLess(o["para"], once)
        self.assertIn("ciftlik", ey["binalar"])


class TestKayitYukle(unittest.TestCase):
    def test_gidis_donus(self):
        s = E.yeniOyun("prusya", "zor")
        for _ in range(5):
            E.tick(s)
        eski_klasor = E.SAVE_KLASOR
        try:
            with tempfile.TemporaryDirectory() as tmp:
                E.SAVE_KLASOR = tmp
                E.kaydet(s, 2)
                s2, hata = E.yukle(2)
        finally:
            E.SAVE_KLASOR = eski_klasor
        self.assertIsNone(hata)
        self.assertEqual((s2["yil"], s2["ay"]), (s["yil"], s["ay"]))
        self.assertEqual(s2["oyuncuUlke"], "prusya")
        self.assertEqual(s2["ulkeler"]["prusya"]["para"], s["ulkeler"]["prusya"]["para"])


if __name__ == "__main__":
    unittest.main()
