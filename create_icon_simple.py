#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit İkon Oluşturucu - PIL gerektirmez
PyQt5 ile kırmızı yuvarlak üzerine beyaz RPo yazısı
"""

from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt

def create_icon_pixmap(size=256):
    """Kırmızı daire içinde beyaz RPo ikonu oluştur"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Kırmızı daire
    painter.setPen(QPen(QColor("#C62828"), max(2, size // 32)))
    painter.setBrush(QColor("#E53935"))
    margin = 2
    painter.drawEllipse(margin, margin, size - margin*2, size - margin*2)

    # Beyaz "RPo" yazısı
    painter.setPen(QColor("white"))
    font = QFont("Arial", int(size * 0.3), QFont.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "RPo")

    painter.end()
    return pixmap

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Farklı boyutlarda pixmap oluştur
    icon = QIcon()
    for size in [256, 128, 64, 48, 32, 16]:
        pixmap = create_icon_pixmap(size)
        icon.addPixmap(pixmap)

    # PNG olarak kaydet (Windows ICO'ya dönüştürür)
    pixmap_256 = create_icon_pixmap(256)
    pixmap_256.save("radio_icon.png")

    print("✓ İkon oluşturuldu: radio_icon.png")
    print("  Uygulama tarafından otomatik yüklenecek")
