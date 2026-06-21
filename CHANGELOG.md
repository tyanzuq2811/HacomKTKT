# Changelog

## 7.0.0

- Viết lại pipeline OCR theo grid-first, cell-level, batched recognition.
- Thêm orientation retry 180° bằng điểm OCR header.
- Thêm parser số Việt Nam/quốc tế và giữ nguyên giá trị 0.
- Thêm HSMT-vs-many-HSDT và HSDT-vs-HSDT.
- Thêm TF-IDF nearest-neighbor, RapidFuzz và BGE-M3 local.
- Thêm median/MAD/Robust-Z và IsolationForest.
- Thêm report constant-memory, ma trận giá và audit SHA-256.
- Thêm strict offline environment, egress guard và Docker networkless.
