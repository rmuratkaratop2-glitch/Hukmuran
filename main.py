# -*- coding: utf-8 -*-
"""
main.py — HÜKMÜMRAN Python/pygame sürümü giriş noktası
Çalıştırma: python main.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

import ui as U
from ui import App


def main():
    APP = App()
    U.APP = APP
    APP.anaMenu()
    pygame.init()
    ekran = pygame.display.set_mode((U.W, U.H))
    pygame.display.set_caption("HÜKMÜMRAN — Sanayi Çağı 1836–1936 (Python)")
    U.fontYukle()
    clock = pygame.time.Clock()
    APP.anaMenu()

    calisiyor = True
    while calisiyor:
        dt = clock.tick(U.FPS) / 1000.0
        mouse = pygame.mouse.get_pos()

        # ---- olaylar ----
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                calisiyor = False

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if APP.seciliYetenek:
                        APP.seciliYetenek = None
                    elif APP.ekran == "oyun":
                        APP.anaMenu()
                if APP.ekran == "oyun" and APP.state and not APP.state["olaylar"]["aktif"]:
                    if e.key == pygame.K_SPACE:
                        if APP.hiz == 0:
                            APP.hiz = 1
                        else:
                            APP.kayitliHiz = APP.hiz
                            APP.hiz = 0
                    if e.key == pygame.K_1:
                        APP.hiz = 1
                    if e.key == pygame.K_2:
                        APP.hiz = 2
                    if e.key == pygame.K_3:
                        APP.hiz = 3
                    if e.key == pygame.K_s:
                        APP.kaydet(1)
                if APP.ekran == "menu" and e.key == pygame.K_RETURN and APP.menuSeciliUlke:
                    APP.yeniOyun(APP.menuSeciliUlke)

            elif e.type == pygame.MOUSEWHEEL:
                # sağ panelde scroll
                if APP.ekran == "oyun":
                    sag = pygame.Rect(U.SAG.x, U.SAG.y + 34, U.SAG.width, U.SAG.height - 34)
                    if sag.collidepoint(mouse):
                        anahtar = "sag_" + APP.sekme
                        limit = U.UI.kaydirma.get(anahtar + "_limit", 0)
                        U.UI.kaydirAyarla(anahtar, max(0, min(limit, U.UI.kaydirAl(anahtar) - e.y * 40)))

            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 3 and APP.ekran == "oyun":
                    APP.haritaSurukle = mouse
                if e.button == 1:
                    # 1) slider yakalama (varsa üstünlük)
                    for sl in APP.sliderlar:
                        sl.olay(e, mouse)
                    if any(sl.surukle for sl in APP.sliderlar):
                        continue
                    # 2) UI buton tıkları — en üstte çizilen (son çizilen) öncelikli:
                    #    olay modali > sekmeler > panel butonları > harita > menü
                    for rect, cb, etkin, hover in reversed(U.UI.butonlar):
                        if etkin and cb and rect.collidepoint(mouse):
                            cb()
                            break

            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 3:
                    APP.haritaSurukle = None
                for sl in APP.sliderlar:
                    sl.olay(e, mouse)

            elif e.type == pygame.MOUSEMOTION:
                if APP.haritaSurukle and APP.ekran == "oyun":
                    dx = mouse[0] - APP.haritaSurukle[0]
                    dy = mouse[1] - APP.haritaSurukle[1]
                    APP.haritaPan[0] += dx
                    APP.haritaPan[1] += dy
                    APP.haritaSurukle = mouse

        # ---- güncelleme ----
        APP.guncelle(dt)

        # ---- çizim ----
        U.UI.reset()
        APP.sliderlar = []
        if APP.ekran == "menu":
            U.menuCiz(ekran)
        elif APP.ekran == "oyun":
            U.oyunCiz(ekran)
        elif APP.ekran == "sonuc":
            U.sonucCiz(ekran)
        U.hoverTipCiz(ekran)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
