# 🗂️ Deprecated Files Archive

**Oluşturulma Tarihi:** 26 Kasım 2025  
**Amaç:** Bu klasör, projenin eski ve artık kullanılmayan dosyalarını düzenli bir şekilde saklamak için oluşturulmuştur.

---

## 📁 Klasör Yapısı

### 1. `demos/` - Eski Demo Scriptleri
Geliştirme aşamasında test ve demo amaçlı yazılmış, artık kullanılmayan Python scriptleri.

**Dosyalar:**
- `demo_phase2.py` - Phase 2 geliştirme döneminde yazılmış demo scripti
- `demo_phase3.py` - Phase 3 geliştirme döneminde yazılmış demo scripti

**Not:** Ana uygulama giriş noktası artık `SchedularV3/main.py` dosyasıdır.

---

### 2. `old_tests/` - Eski Test Dosyaları
Projenin erken geliştirme dönemlerinde yazılmış, artık `tests/` klasöründeki pytest test suite'i tarafından yenilenen test dosyaları.

**Dosyalar:**
- `automated_gui_test.py` - GUI otomatik test scripti (pytest-qt ile değiştirildi)
- `comprehensive_test_suite.py` - Kapsamlı test paketi (artık pytest framework kullanılıyor)
- `test_gui_integration.py` - GUI entegrasyon testleri (aktif test suite'e dahil edildi)
- `test_isik_integration.py` - Işık University entegrasyon testleri (aktif test suite'e dahil edildi)

**Not:** Güncel test dosyaları `SchedularV3/tests/` klasöründe bulunmaktadır. 33/33 test başarılı.

---

### 3. `old_docs/` - Eski Dökümanlar
Güncelliğini yitirmiş dökümanlar ve tamamlanmış phase raporları.

**Dosyalar:**
- `CHANGELOG_Phase3_Enhancements.md` - Phase 3 değişiklik günlüğü (artık PHASES_PROGRESS.md kullanılıyor)
- `PHASE_1_COMPLETE.md` - Phase 1 tamamlama raporu (artık PHASES_PROGRESS.md içinde)
- `CURRENT_SESSION_SNAPSHOT.md` - Eski oturum özeti (artık TODO.md kullanılıyor)
- `PHASE_8_REMAINING_TASKS.md` - Phase 8 kalan görevler (artık TODO.md kullanılıyor)

**Not:** Güncel dökümanlar:
- `SchedularV3/README.md` - Ana proje dokümanı
- `SchedularV3/TODO.md` - Aktif görev listesi (2713 satır, %73 tamamlanmış)
- `SchedularV3/PHASES_PROGRESS.md` - Phase ilerleme takibi
- `SchedularV3/docs/ARCHITECTURE_COMPLETE_REPORT.md` - Kapsamlı mimari raporu (800+ satır)

---

### 4. `old_scripts/` - Eski Python Scriptleri
Projenin kök dizininde bulunan, artık kullanılmayan yardımcı scriptler.

**Dosyalar:**
- `sef.py` - Eski yardımcı script
- `temp_models.py` - Geçici model denemeleri
- `isik_university_programs.py` - Işık University program verileri (artık `SchedularV3/core/isik_university_data.py` kullanılıyor)

**Not:** Güncel veri modelleri `SchedularV3/core/models.py` dosyasında tanımlıdır.

---

### 5. `output_files/` - Eski Test Çıktıları
Geliştirme ve test aşamalarında üretilmiş, artık gerekli olmayan çıktı dosyaları.

**Dosyalar:**
- `comprehensive_test_2025-11-26_13-50-35.json` - Eski test çıktısı
- `comprehensive_test_2025-11-26_13-50-35.txt` - Eski test raporu
- `gui_test_report_2025-11-26_13-43-01.json` - Eski GUI test çıktısı
- `gui_test_report_2025-11-26_13-43-01.txt` - Eski GUI test raporu

**Not:** Güncel test çıktıları `SchedularV3/output/` klasöründe saklanmaktadır.

---

### 6. `old_resources/` - Eski Kaynak Dosyaları
Eski PDF raporları, JPG görüntüleri ve diğer kaynak dosyaları.

**Dosyalar:**
- `final_selection_matrices.pdf` - Eski seçim matrisleri raporu
- `program1.jpg` - `program5.jpg` - Eski program görüntüleri (5 adet)
- `conflict_report.txt` - Eski çakışma raporu

**Not:** Güncel raporlar GUI üzerinden PDF, JPEG ve Excel formatlarında export edilmektedir (Phase 9 - Reporting & Export).

---

## 🎯 Bu Dosyalar Neden Taşındı?

1. **Kod Kalitesi:** Ana proje dizinini temiz ve düzenli tutmak
2. **Karışıklığı Önleme:** Aktif geliştirme dosyaları ile eski dosyaları karıştırmamak
3. **Tarihsel Değer:** Eski dosyaları silmek yerine arşivlemek (gelecekte referans için)
4. **Clean Architecture:** Mimari refactoring öncesi temiz bir başlangıç noktası sağlamak

---

## ⚠️ Uyarı

Bu klasördeki dosyalar **artık kullanılmamaktadır** ve proje çalışması için gerekli değildir. 

- ❌ Bu dosyaları import etmeyin veya referans göstermeyin
- ❌ Yeni kod geliştirirken bu dosyaları kullanmayın
- ✅ Sadece tarihsel referans veya debugging amacıyla inceleyebilirsiniz
- ✅ Eğer tamamen emin değilseniz, bu klasörü silmeyin (disk alanı sorunu yoksa)

---

## 📊 İstatistikler

- **Toplam Taşınan Dosya:** 21+
- **Demos:** 2 dosya
- **Old Tests:** 4 dosya
- **Old Docs:** 4 dosya
- **Old Scripts:** 3 dosya
- **Output Files:** 4 dosya
- **Old Resources:** 7 dosya

---

## 🔄 Aktif Proje Bilgileri

**Ana Proje:** `SchedularV3/`
- **Durum:** Aktif Geliştirme (Phase 7 & 8: %85-92 tamamlanmış)
- **Python Dosyaları:** 60+
- **Kod Satırı:** ~15,000+
- **Algoritmalar:** 15+ (DFS, BFS, A*, GA, SA, PSO, vb.)
- **Test Coverage:** 33/33 passing, %65 coverage
- **GUI Framework:** PyQt6
- **Database:** SQLite

**Sonraki Hedefler:**
- Phase 7.5: Transcript Import (60% tamamlandı)
- Phase 9: Reporting & Export (PDF, JPEG, Excel)
- Phase 10: Polish & Testing

---

## 📝 Notlar

Bu arşiv, projenin tarihsel gelişimini göstermektedir. Proje başlangıçta `demo_phase2.py` ve `demo_phase3.py` gibi basit demo scriptleriyle başlamış, şimdi 15,000+ satır koddan oluşan profesyonel bir PyQt6 uygulamasına dönüşmüştür.

**Önemli:** Clean Architecture refactoring planı (5 haftalık) `docs/ARCHITECTURE_COMPLETE_REPORT.md` dosyasında detaylı olarak belgelenmiştir. Bu refactoring tamamlandığında, bu arşivdeki dosyalar tamamen güvenle silinebilir.

---

**Oluşturan:** GitHub Copilot  
**Tarih:** 26 Kasım 2025
