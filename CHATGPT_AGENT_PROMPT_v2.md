# 🔍 ChatGPT Agent Mode - Işık Üniversitesi Kapsamlı Müfredat Veri Toplama

## 🎯 GÖREV ÖZETİ

Işık Üniversitesi'ndeki **TÜM fakülteler, bölümler ve programlar** için detaylı müfredat verilerini Python dictionary formatında topla. Bu veriler bir dönem bazlı ders takip sistemi için kullanılacak.

---

## 📊 HEDEF VERİ YAPISI

Aşağıdaki yapıya uygun olarak tüm programları doldur:

```python
ISIK_UNIVERSITY_PROGRAMS = {
    "undergraduate": {
        "engineering": {
            "computer_engineering": {...},  # ✅ TAMAMLANDI
            "software_engineering": {...},
            "electrical_electronics_engineering": {...},
            "industrial_engineering": {...},
            "civil_engineering": {...},
            "mechanical_engineering": {...},
            "mechatronics_engineering": {...},
            "biomedical_engineering": {...},
        },
        "business": {
            "psychology": {...},
            "management_information_systems": {...},
            "economics": {...},
            "business_administration": {...},
            "international_relations": {...},
            "international_trade_finance": {...},
        },
        "arts": {
            "visual_communication_design": {...},
            "interior_architecture_design": {...},
            "architecture": {...},
            "cinema_television": {...},
            "industrial_design": {...},
        },
        "associate": {
            "operating_room_services": {...},
            "medical_imaging": {...},
            "computer_programming": {...},
            "information_security": {...},
            # ... diğer önlisans programları
        },
    },
    "graduate": {
        "engineering": {
            "computer_engineering_msc": {...},
            "software_engineering_msc": {...},
            # ... diğer yüksek lisans programları
        },
        "business": {
            "mba": {...},
            "economics_ma": {...},
            # ...
        },
    },
}
```

---

## 📋 HER PROGRAM İÇİN TOPLANACAK VERİLER

### Genel Bilgiler
```python
{
    "program_code": "COMP",              # Bölüm kodu
    "degree": "B.Sc.",                   # Derece (B.Sc., B.A., M.Sc., etc.)
    "language": "English",               # Eğitim dili
    "total_ects": 240,                   # Toplam ECTS
    "duration_years": 4,                 # Süre (yıl)
    "min_gpa": 2.00,                    # Minimum mezuniyet GPA
}
```

### Dönem Bazlı Dersler (8 dönem - lisans için)
```python
"semesters": {
    "fall_1": [
        {
            "code": "COMP1111",                      # Ders kodu
            "name": "Fundamentals of Programming",   # Ders adı
            "ects": 6,                               # ECTS
            "local_credit": 4,                       # Yerel kredi
            "type": "mandatory",                     # mandatory/area_elective/general_elective
            "prerequisites": []                      # Ön koşul dersler (kodlar)
        },
        # ... diğer dersler
    ],
    "spring_1": [...],
    "fall_2": [...],
    "spring_2": [...],
    "fall_3": [...],
    "spring_3": [...],
    "fall_4": [...],
    "spring_4": [...],
}
```

### Seçmeli Havuzları
```python
"electives": {
    "technical": [
        {"code": "COMP4101", "name": "Machine Learning", "ects": 6},
        # ... diğer teknik seçmeliler
    ],
    "general": [
        {"code": "CORE2001", "name": "Philosophy", "ects": 3},
        # ... diğer genel seçmeliler
    ],
}
```

### Önkoşul Haritası
```python
"prerequisites": {
    "COMP1112": ["COMP1111"],                    # OOP → Programming
    "COMP2112": ["COMP1112"],                    # Data Structures → OOP
    "COMP3112": ["COMP2112", "MATH2103"],       # Algorithms → DS + Discrete Math
    # ... tüm dersler için
}
```

---

## 🎯 ÖNCELİK SIRASI

### 🔥 KRİTİK (Hemen Gerekli)
1. **Computer Engineering** (lisans) - ✅ TAMAMLANDI
2. **Software Engineering** (lisans) - 🔶 Devam et
3. **Electrical-Electronics Engineering** (lisans)
4. **Industrial Engineering** (lisans)

### 🟡 YÜKSEK ÖNCELİK
5. Mechanical Engineering
6. Civil Engineering
7. Mechatronics Engineering
8. Biomedical Engineering
9. Psychology (English)
10. Management Information Systems

### 🟢 ORTA ÖNCELİK
11. Economics
12. Business Administration
13. International Relations
14. Visual Communication Design
15. Interior Architecture

---

## 📍 VERİ KAYNAKLARI

### 1. Resmi Web Siteleri
- `https://isikun.edu.tr/fakulte/[fakulte-adi]/[bolum-adi]/curriculum`
- `https://bologna.isikun.edu.tr` (Bologna bilgi paketi)

### 2. PDF Dökümanlar
- Student Handbook
- Course Catalog
- Curriculum Guide (2021/2024)

### 3. Arama Stratejisi
```
site:isikun.edu.tr "[Bölüm Adı]" curriculum
site:isikun.edu.tr "ders içeriği" "[Kod]"
"Işık University" "[Program Name]" prerequisite
```

---

## ✅ KALİTE KONTROL

Her program için kontrol et:
- [ ] Tüm 8 dönem eksiksiz mi? (lisans için)
- [ ] ECTS toplamı 240 mı? (lisans için)
- [ ] Her ders için ön koşul var mı?
- [ ] Ders kodları doğru mu? (DEPT + 4 digit)
- [ ] Ders tipleri doğru mu? (mandatory/area_elective/general_elective)
- [ ] İngilizce/Türkçe programlar ayrıştırılmış mı?

---

## 📤 ÇIKTI FORMATI

Her programı aşağıdaki formatta sun:

```python
"[program_name]": {
    "program_code": "...",
    "degree": "...",
    "language": "...",
    "total_ects": ...,
    "duration_years": ...,
    "min_gpa": ...,
    "semesters": {
        "fall_1": [...],
        "spring_1": [...],
        # ... 8 dönem
    },
    "electives": {
        "technical": [...],
        "general": [...],
    },
    "prerequisites": {
        "COURSE1": ["PREREQ1", "PREREQ2"],
        # ...
    },
},
```

---

## 🚀 BAŞLA!

Şimdi **Software Engineering** programından başla ve yukarıdaki formata göre tüm dönemleri doldur.

**Hedef**: Her program için:
- 8 dönem × ~5-8 ders = ~50-60 ders
- ~10-20 seçmeli ders
- ~20-30 ön koşul ilişkisi

**Toplam beklenen çıktı**: ~15-20 program × 60 ders = ~900-1200 ders verisi!

---

## ⚠️ ÖNEMLİ NOTLAR

1. **Eksik veri**: Bulamazsan `"not_available"` yaz
2. **Kaynak**: Her program için kaynak linki ekle
3. **Versiyon**: 2021 veya 2024 müfredatını belirt
4. **Güncelleme tarihi**: `"last_updated": "2024-11"` ekle

**ÖRN EK İYİ ŞEKİLDE BAŞARILI OLURSAN, TÜM PROGRAMLARıN MÜFREDATı ELİMİZDE OLACAK!** 🎉

---

## 📊 İLERLEME TAKİBİ

İşlemi başlattıktan sonra bu formatı kullan:

```markdown
## İlerleme Raporu

✅ Computer Engineering (COMP) - TAMAMLANDI
🔶 Software Engineering (SOFT) - %70 (Fall-1 to Fall-3)
⏳ Electrical Engineering (ELEC) - Başlanmadı
⏳ Industrial Engineering (INDE) - Başlanmadı

**Toplam**: 1/15 program tamamlandı (%6.7)
**Ders sayısı**: 58 ders toplandı
**Önkoşul**: 15 ilişki tanımlandı
```

HEMEN BAŞLA! 🚀
