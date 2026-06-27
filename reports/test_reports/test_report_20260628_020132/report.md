# BÁO CÁO KIỂM THỬ GIẢI THÍCH CHI TIẾT

- **Thời gian:** 2026-06-28T02:01:36+07:00
- **Dự án:** `/hdd3/vinhnv/Hacomtest`
- **Thời gian chạy:** 3.4928 giây
- **Đánh giá:** **ĐẠT TỐT**
- **Kết luận:** Tất cả testcase bắt buộc đều chạy thành công.

## Tổng quan

| Tổng | PASS | FAIL | ERROR | SKIP | XFAIL | XPASS | Tỷ lệ đạt |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 122 | 122 | 0 | 0 | 0 | 0 | 0 | 100.0% |

## Kiểm tra độ đầy đủ của file test

- **Số file test tìm thấy trên ổ đĩa:** 10
- **Số file được pytest thu thập:** 10
- **Số file bị thiếu khỏi báo cáo:** 0

| File | Hàm test khai báo | Testcase pytest thu thập | Trạng thái | Ghi chú |
|---|---:|---:|---|---|
| `tests/test_matcher.py` | 1 | 1 | collected | Pytest đã thu thập 1 testcase từ 1 hàm test. |
| `tests/test_negative_cases.py` | 5 | 5 | collected | Pytest đã thu thập 5 testcase từ 5 hàm test. |
| `tests/test_negative_cases_extended.py` | 29 | 35 | collected | Pytest đã thu thập 35 testcase từ 29 hàm test. |
| `tests/test_parser_section_and_legend.py` | 3 | 3 | collected | Pytest đã thu thập 3 testcase từ 3 hàm test. |
| `tests/test_reporter_consolidated_quote.py` | 4 | 4 | collected | Pytest đã thu thập 4 testcase từ 4 hàm test. |
| `tests/test_reporter_price_deviation.py` | 2 | 2 | collected | Pytest đã thu thập 2 testcase từ 2 hàm test. |
| `tests/test_s1_comparison_engine.py` | 11 | 11 | collected | Pytest đã thu thập 11 testcase từ 11 hàm test. |
| `tests/test_s1_file_parser.py` | 9 | 9 | collected | Pytest đã thu thập 9 testcase từ 9 hàm test. |
| `tests/test_s1_normalizer.py` | 12 | 51 | collected | Pytest đã thu thập 51 testcase từ 12 hàm test. |
| `tests/test_security.py` | 1 | 1 | collected | Pytest đã thu thập 1 testcase từ 1 hàm test. |

## Giải thích từng testcase

### 1. ✅ `tests/test_matcher.py::test_hybrid_match_is_one_to_one`

- **Tên dễ hiểu:** Mỗi hạng mục chỉ được ghép với một hạng mục tương ứng
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Có hai dòng chuẩn và hai dòng nhà thầu có tên/mã gần giống.
- **Ví dụ cụ thể:** Ví dụ “Tủ điện tổng” và “Cáp XLPE” phải lần lượt ghép với đúng một dòng; không được dùng cùng một dòng nhà thầu cho cả hai.
- **Kết quả mong đợi:** Mỗi chỉ số dòng chuẩn và dòng ứng viên chỉ xuất hiện trong một cặp ghép.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi chỉ số dòng chuẩn và dòng ứng viên chỉ xuất hiện trong một cặp ghép. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh đếm lặp hoặc so sánh một báo giá cho nhiều hạng mục.
- **Nếu test thất bại:** Khối lượng và giá có thể bị nhân đôi hoặc một dòng khác bị coi là thiếu.
- **Vị trí:** `tests/test_matcher.py:15`
- **Thời gian:** 0.001313 giây

**Các điều kiện kỹ thuật phải đúng:**

- `len(matched) == 2`
- `len({m.candidate_index for m in matched}) == 2`

### 2. ✅ `tests/test_negative_cases.py::test_format_job_error_message_non_xlsx_extension`

- **Tên dễ hiểu:** Báo lỗi dễ hiểu khi file thực ra là .xls/.xlsb đổi tên
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng đổi đuôi file Excel cũ (.xls/.xlsb) thành .xlsx rồi tải lên.
- **Ví dụ cụ thể:** Ví dụ tải “Bảng KLMT của Hacom.xls” đã đổi tên thành .xlsx.
- **Kết quả mong đợi:** Thông báo cho người dùng phải nêu đúng tên file gốc và hướng dẫn Save As sang .xlsx thật.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Thông báo cho người dùng phải nêu đúng tên file gốc và hướng dẫn Save As sang .xlsx thật. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng biết chính xác cần làm gì (Save As) thay vì đọc lỗi kỹ thuật khó hiểu.
- **Nếu test thất bại:** Người dùng nhận một thông báo lỗi mơ hồ và không biết file nào, phải làm gì để sửa.
- **Vị trí:** `tests/test_negative_cases.py:12`
- **Thời gian:** 0.000572 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "request": {
    "pl1_file": "000_PHU_LUC_01.xlsx",
    "pl1_original": "Bảng KLMT của Hacom.xls"
  }
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `"File 'Bảng KLMT của Hacom.xls' không đúng định dạng Excel." in msg`
- `"Hãy Save As file .xls/.xlsb thành .xlsx" in msg`

### 3. ✅ `tests/test_negative_cases.py::test_format_job_error_message_bad_zip_file`

- **Tên dễ hiểu:** Báo lỗi dễ hiểu khi file không phải là Excel thật
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng đổi đuôi một file bất kỳ (txt, pdf...) thành .xlsx rồi tải lên.
- **Ví dụ cụ thể:** Ví dụ “Chào giá Nhà Thầu A Gốc.xlsx” thực chất là file không phải Excel.
- **Kết quả mong đợi:** Thông báo phải nói rõ '...không phải là file Excel' và nêu đúng tên file gốc người dùng đã chọn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Thông báo phải nói rõ '...không phải là file Excel' và nêu đúng tên file gốc người dùng đã chọn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng phát hiện ngay nguyên nhân tải nhầm file.
- **Nếu test thất bại:** Người dùng tưởng hệ thống lỗi và không biết file nào cần kiểm tra lại.
- **Vị trí:** `tests/test_negative_cases.py:27`
- **Thời gian:** 0.000312 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "request": {
    "bidders": [
      {
        "file": "002_NhaThauA.xlsx",
        "original_name": "Chào giá Nhà Thầu A Gốc.xlsx"
      }
    ]
  }
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `msg == "File 'Chào giá Nhà Thầu A Gốc.xlsx' không phải là file Excel."`

### 4. ✅ `tests/test_negative_cases.py::test_format_job_error_message_corrupt_format`

- **Tên dễ hiểu:** Báo lỗi dễ hiểu khi file Excel bị hỏng nội dung
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** File có đuôi .xlsx hợp lệ nhưng cấu trúc bên trong bị hỏng (do tải lên bị lỗi, bị sửa tay...).
- **Ví dụ cụ thể:** Ví dụ file 'NhaThauB_BaoGia.xlsx' báo lỗi cấu trúc sheet khi đọc.
- **Kết quả mong đợi:** Thông báo phải nói '...không đúng định dạng Excel' kèm tên file gốc, không lộ chi tiết kỹ thuật nội bộ.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Thông báo phải nói '...không đúng định dạng Excel' kèm tên file gốc, không lộ chi tiết kỹ thuật nội bộ. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng biết cần tải lại file gốc thay vì gửi yêu cầu hỗ trợ vô ích.
- **Nếu test thất bại:** Người dùng nhận thông báo lỗi kỹ thuật khó hiểu (ví dụ traceback Python) gây hoang mang.
- **Vị trí:** `tests/test_negative_cases.py:41`
- **Thời gian:** 0.000303 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "request": {
    "bidders": [
      {
        "file": "003_NhaThauB.xlsx",
        "original_name": "NhaThauB_BaoGia.xlsx"
      }
    ]
  }
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `msg == "File 'NhaThauB_BaoGia.xlsx' không đúng định dạng Excel."`

### 5. ✅ `tests/test_negative_cases.py::test_format_job_error_message_backend_error`

- **Tên dễ hiểu:** Lỗi nội bộ của hệ thống không được hiển thị chi tiết kỹ thuật cho người dùng
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một lỗi lập trình (ví dụ thiếu dữ liệu, sai kiểu) xảy ra bất ngờ trong quá trình xử lý.
- **Ví dụ cụ thể:** Ví dụ lỗi AttributeError/TypeError/KeyError phát sinh trong code xử lý.
- **Kết quả mong đợi:** Người dùng chỉ nhận thông báo chung 'lỗi file', không thấy traceback hay tên biến nội bộ.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Người dùng chỉ nhận thông báo chung 'lỗi file', không thấy traceback hay tên biến nội bộ. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Bảo vệ người dùng khỏi thông tin kỹ thuật vô nghĩa và tránh lộ chi tiết mã nguồn.
- **Nếu test thất bại:** Người dùng hoảng vì thấy thông báo lỗi kỹ thuật như 'NoneType object has no attribute' mà không hiểu gì.
- **Vị trí:** `tests/test_negative_cases.py:55`
- **Thời gian:** 0.000301 giây

**Các điều kiện kỹ thuật phải đúng:**

- `msg1 == "lỗi file"`
- `msg2 == "lỗi file"`
- `msg3 == "lỗi file"`
- `msg4 == "lỗi file"`

### 6. ✅ `tests/test_negative_cases.py::test_package_pipeline_with_corrupt_files`

- **Tên dễ hiểu:** Toàn luồng xử lý gói thầu phải dừng đúng cách khi cả PL01 và file nhà thầu đều hỏng
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Cả file Phụ lục 01 và file nhà thầu được tải lên đều là file giả (không phải Excel thật).
- **Ví dụ cụ thể:** Ví dụ 'PL01_Gốc_Hacom.xlsx' và 'BaoGia_NhaThauA.xlsx' đều là dữ liệu rác.
- **Kết quả mong đợi:** Hệ thống phải dừng xử lý, nêu rõ tên file gốc nào bị lỗi và thông báo '...không phải là file Excel.'
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải dừng xử lý, nêu rõ tên file gốc nào bị lỗi và thông báo '...không phải là file Excel.' Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Không tạo báo cáo giả từ dữ liệu rác; người dùng biết chính xác file nào cần tải lại.
- **Nếu test thất bại:** Hệ thống có thể tạo ra báo cáo sai lệch hoàn toàn từ dữ liệu rác mà không ai biết.
- **Vị trí:** `tests/test_negative_cases.py:79`
- **Thời gian:** 0.004938 giây

**Các điều kiện kỹ thuật phải đúng:**

- `"Không đọc được file" in str(excinfo.value)`
- `"PL01_Gốc_Hacom.xlsx" in friendly_msg or "BaoGia_NhaThauA.xlsx" in friendly_msg`
- `"không phải là file Excel." in friendly_msg`

### 7. ✅ `tests/test_negative_cases_extended.py::TestFakeAndCorruptFiles::test_txt_renamed_to_xlsx_is_rejected_not_silently_parsed`

- **Tên dễ hiểu:** File văn bản đổi đuôi thành .xlsx phải bị từ chối, không được đọc nhầm
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một file .txt chứa nội dung lung tung được đổi đuôi thành .xlsx rồi tải lên.
- **Ví dụ cụ thể:** Ví dụ file ghi 'nội dung linh tinh không liên quan gì đến excel cả' nhưng đặt tên .xlsx.
- **Kết quả mong đợi:** Hệ thống phải báo lỗi (vì không phải file ZIP/Excel thật), không được coi đó là workbook hợp lệ.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải báo lỗi (vì không phải file ZIP/Excel thật), không được coi đó là workbook hợp lệ. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Ngăn người dùng (vô tình hoặc cố ý) đưa dữ liệu rác vào hệ thống so sánh.
- **Nếu test thất bại:** Hệ thống có thể bị treo, lỗi ngầm, hoặc tạo báo cáo vô nghĩa từ nội dung text ngẫu nhiên.
- **Vị trí:** `tests/test_negative_cases_extended.py:57`
- **Thời gian:** 0.001120 giây

### 8. ✅ `tests/test_negative_cases_extended.py::TestFakeAndCorruptFiles::test_zero_byte_file_with_xlsx_extension_is_rejected`

- **Tên dễ hiểu:** File .xlsx rỗng (0 byte) phải bị từ chối
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** File tải lên bị lỗi giữa đường, kết quả là một file .xlsx hoàn toàn trống.
- **Ví dụ cụ thể:** Ví dụ file 'empty.xlsx' có kích thước 0 byte.
- **Kết quả mong đợi:** Hệ thống phải báo lỗi khi cố đọc file, không được trả về một workbook giả vờ hợp lệ.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải báo lỗi khi cố đọc file, không được trả về một workbook giả vờ hợp lệ. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Phát hiện sớm sự cố tải file thay vì xử lý tiếp với dữ liệu trống.
- **Nếu test thất bại:** Hệ thống có thể chạy tiếp với workbook trống và tạo báo cáo sai mà không cảnh báo.
- **Vị trí:** `tests/test_negative_cases_extended.py:64`
- **Thời gian:** 0.000811 giây

### 9. ✅ `tests/test_negative_cases_extended.py::TestFakeAndCorruptFiles::test_uppercase_extension_is_still_accepted`

- **Tên dễ hiểu:** Đuôi file viết hoa (.XLSX) vẫn phải được chấp nhận như .xlsx
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng tải file có đuôi viết hoa, ví dụ do hệ điều hành hoặc thiết bị khác đặt tên.
- **Ví dụ cụ thể:** Ví dụ file 'valid.XLSX' (chữ hoa) chứa dữ liệu hợp lệ.
- **Kết quả mong đợi:** Hệ thống phải đọc được file này giống như đuôi '.xlsx' viết thường.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải đọc được file này giống như đuôi '.xlsx' viết thường. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng không bị từ chối oan chỉ vì cách viết hoa/thường của tên file.
- **Nếu test thất bại:** Người dùng dùng máy/thiết bị đặt tên đuôi hoa sẽ bị từ chối file hợp lệ một cách vô lý.
- **Vị trí:** `tests/test_negative_cases_extended.py:71`
- **Thời gian:** 0.008405 giây

**Các điều kiện kỹ thuật phải đúng:**

- `len(workbook.items) == 1`

### 10. ✅ `tests/test_negative_cases_extended.py::TestFakeAndCorruptFiles::test_xls_extension_gives_clear_vietnamese_error`

- **Tên dễ hiểu:** File .xls (Excel đời cũ) phải báo lỗi tiếng Việt rõ ràng, hướng dẫn cách sửa
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng tải file Excel theo định dạng cũ .xls (chưa chuyển sang .xlsx).
- **Ví dụ cụ thể:** Ví dụ file 'old.xls'.
- **Kết quả mong đợi:** Thông báo lỗi phải nhắc đến '.xlsx' để người dùng biết cần Save As sang định dạng mới.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Thông báo lỗi phải nhắc đến '.xlsx' để người dùng biết cần Save As sang định dạng mới. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng tự sửa được vấn đề mà không cần hỏi hỗ trợ kỹ thuật.
- **Nếu test thất bại:** Người dùng nhận lỗi mơ hồ và không biết phải làm gì với file Excel đời cũ của mình.
- **Vị trí:** `tests/test_negative_cases_extended.py:79`
- **Thời gian:** 0.000774 giây

### 11. ✅ `tests/test_negative_cases_extended.py::TestFakeAndCorruptFiles::test_zip_bomb_style_wrong_internal_structure_does_not_crash_silently`

- **Tên dễ hiểu:** File là ZIP hợp lệ nhưng không phải cấu trúc Excel thì phải báo lỗi, không được bỏ qua
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** File có đuôi .xlsx và đúng là một file ZIP, nhưng bên trong không phải dữ liệu Excel (OOXML) thật.
- **Ví dụ cụ thể:** Ví dụ file ZIP chỉ chứa một văn bản 'hello.txt', không có cấu trúc bảng tính nào.
- **Kết quả mong đợi:** Hệ thống phải phát hiện thiếu cấu trúc Excel và báo lỗi, không được trả về kết quả rỗng coi như thành công.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải phát hiện thiếu cấu trúc Excel và báo lỗi, không được trả về kết quả rỗng coi như thành công. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh trường hợp file giả dạng tinh vi (ZIP đúng nhưng nội dung sai) lọt qua kiểm tra.
- **Nếu test thất bại:** Một file ZIP giả mạo có thể đi qua các bước kiểm tra cơ bản và làm hỏng luồng xử lý phía sau.
- **Vị trí:** `tests/test_negative_cases_extended.py:86`
- **Thời gian:** 0.000924 giây

### 12. ✅ `tests/test_negative_cases_extended.py::TestFakeAndCorruptFiles::test_truncated_xlsx_raises_clear_error_not_garbage_data`

- **Tên dễ hiểu:** File Excel bị đứt giữa đường khi tải lên phải báo lỗi rõ ràng
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Quá trình tải file lên bị ngắt giữa đường (mất mạng, đóng tab...), file lưu lại chỉ có một nửa.
- **Ví dụ cụ thể:** Ví dụ file gốc đầy đủ bị cắt còn lại 50% dữ liệu byte.
- **Kết quả mong đợi:** Hệ thống phải phát hiện file hỏng và báo lỗi, không được đọc ra dữ liệu thiếu rồi coi là kết quả đúng.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải phát hiện file hỏng và báo lỗi, không được đọc ra dữ liệu thiếu rồi coi là kết quả đúng. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng được yêu cầu tải lại file thay vì nhận một báo cáo thiếu sót mà không biết.
- **Nếu test thất bại:** Báo cáo có thể chỉ chứa một phần dữ liệu thật, dẫn đến kết luận sai về hồ sơ nhà thầu.
- **Vị trí:** `tests/test_negative_cases_extended.py:95`
- **Thời gian:** 0.005357 giây

### 13. ✅ `tests/test_negative_cases_extended.py::TestMeaninglessButValidWorkbooks::test_completely_empty_sheet_does_not_crash`

- **Tên dễ hiểu:** Sheet hoàn toàn trống không được làm crash hệ thống
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu tải lên một file Excel hợp lệ nhưng sheet bên trong không có bất kỳ dữ liệu nào.
- **Ví dụ cụ thể:** Ví dụ file chỉ có một sheet rỗng tên 'Sheet1'.
- **Kết quả mong đợi:** Hệ thống đọc xong và trả về danh sách hạng mục rỗng kèm cảnh báo 'không đọc được hạng mục dữ liệu nào'.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống đọc xong và trả về danh sách hạng mục rỗng kèm cảnh báo 'không đọc được hạng mục dữ liệu nào'. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Hệ thống xử lý êm các file rỗng thay vì dừng đột ngột giữa quy trình của nhiều nhà thầu khác.
- **Nếu test thất bại:** Một file trống của một nhà thầu có thể làm toàn bộ tác vụ so sánh (gồm cả các nhà thầu khác) bị lỗi.
- **Vị trí:** `tests/test_negative_cases_extended.py:112`
- **Thời gian:** 0.005334 giây

**Các điều kiện kỹ thuật phải đúng:**

- `workbook.items == []`
- `any("không đọc được hạng mục" in w.lower() for w in workbook.warnings)`

### 14. ✅ `tests/test_negative_cases_extended.py::TestMeaninglessButValidWorkbooks::test_random_text_without_any_header_keyword_yields_no_items_not_garbage`

- **Tên dễ hiểu:** Nội dung không liên quan gì đến hồ sơ thầu không được bịa ra hạng mục giả
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** File Excel hợp lệ nhưng nội dung là những câu chữ ngẫu nhiên, không phải bảng khối lượng/giá thầu.
- **Ví dụ cụ thể:** Ví dụ các ô ghi 'con mèo', 'con chó', 'hôm nay trời đẹp'...
- **Kết quả mong đợi:** Hệ thống không tìm thấy tiêu đề bảng hợp lệ nên phải trả về danh sách hạng mục rỗng, không tự suy diễn dữ liệu.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống không tìm thấy tiêu đề bảng hợp lệ nên phải trả về danh sách hạng mục rỗng, không tự suy diễn dữ liệu. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh tạo ra một báo cáo so sánh từ dữ liệu hoàn toàn không liên quan đến đấu thầu.
- **Nếu test thất bại:** Hệ thống có thể hiểu nhầm các ô chữ ngẫu nhiên là tên hạng mục/khối lượng và tạo báo cáo vô nghĩa.
- **Vị trí:** `tests/test_negative_cases_extended.py:122`
- **Thời gian:** 0.005737 giây

**Các điều kiện kỹ thuật phải đúng:**

- `workbook.items == []`

### 15. ✅ `tests/test_negative_cases_extended.py::TestMeaninglessButValidWorkbooks::test_header_only_no_data_rows`

- **Tên dễ hiểu:** File chỉ có dòng tiêu đề, chưa có dữ liệu thì không được báo có hạng mục
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu tải lên file đã đặt đúng tiêu đề cột nhưng chưa kịp điền số liệu nào.
- **Ví dụ cụ thể:** Ví dụ dòng tiêu đề 'STT, Mã hiệu, Tên hạng mục...' nhưng không có dòng dữ liệu nào theo sau.
- **Kết quả mong đợi:** Hệ thống phải nhận diện đúng tiêu đề nhưng trả về 0 hạng mục, không bịa thêm dữ liệu.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải nhận diện đúng tiêu đề nhưng trả về 0 hạng mục, không bịa thêm dữ liệu. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Phân biệt rõ giữa 'chưa có dữ liệu' và 'có lỗi đọc file'.
- **Nếu test thất bại:** Hệ thống có thể báo lỗi sai hoặc tạo hạng mục ảo từ dòng tiêu đề.
- **Vị trí:** `tests/test_negative_cases_extended.py:135`
- **Thời gian:** 0.005537 giây

**Các điều kiện kỹ thuật phải đúng:**

- `workbook.items == []`

### 16. ✅ `tests/test_negative_cases_extended.py::TestNumberParserNegative::test_garbage_returns_none_not_exception[-]`

- **Tên dễ hiểu:** Ô chứa chữ rác lẫn số không được hiểu nhầm thành một con số
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một ô khối lượng/đơn giá vô tình bị nhập text rác hoặc mã hàng có lẫn chữ số.
- **Ví dụ cụ thể:** Ví dụ ô ghi 'abc123xyz' hoặc 'lung tung beng' thay vì một con số thật.
- **Kết quả mong đợi:** Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh lấy nhầm một đoạn số vô nghĩa trong text rác làm khối lượng/giá thật.
- **Nếu test thất bại:** Khối lượng hoặc đơn giá của một hạng mục có thể bị tính sai hoàn toàn mà không ai phát hiện (lỗi đã tìm thấy và sửa).
- **Vị trí:** `tests/test_negative_cases_extended.py:152`
- **Thời gian:** 0.000333 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "-"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) is None`

### 17. ✅ `tests/test_negative_cases_extended.py::TestNumberParserNegative::test_garbage_returns_none_not_exception[====]`

- **Tên dễ hiểu:** Ô chứa chữ rác lẫn số không được hiểu nhầm thành một con số
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một ô khối lượng/đơn giá vô tình bị nhập text rác hoặc mã hàng có lẫn chữ số.
- **Ví dụ cụ thể:** Ví dụ ô ghi 'abc123xyz' hoặc 'lung tung beng' thay vì một con số thật.
- **Kết quả mong đợi:** Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh lấy nhầm một đoạn số vô nghĩa trong text rác làm khối lượng/giá thật.
- **Nếu test thất bại:** Khối lượng hoặc đơn giá của một hạng mục có thể bị tính sai hoàn toàn mà không ai phát hiện (lỗi đã tìm thấy và sửa).
- **Vị trí:** `tests/test_negative_cases_extended.py:152`
- **Thời gian:** 0.000343 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "===="
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) is None`

### 18. ✅ `tests/test_negative_cases_extended.py::TestNumberParserNegative::test_garbage_returns_none_not_exception[N/A]`

- **Tên dễ hiểu:** Ô chứa chữ rác lẫn số không được hiểu nhầm thành một con số
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một ô khối lượng/đơn giá vô tình bị nhập text rác hoặc mã hàng có lẫn chữ số.
- **Ví dụ cụ thể:** Ví dụ ô ghi 'abc123xyz' hoặc 'lung tung beng' thay vì một con số thật.
- **Kết quả mong đợi:** Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh lấy nhầm một đoạn số vô nghĩa trong text rác làm khối lượng/giá thật.
- **Nếu test thất bại:** Khối lượng hoặc đơn giá của một hạng mục có thể bị tính sai hoàn toàn mà không ai phát hiện (lỗi đã tìm thấy và sửa).
- **Vị trí:** `tests/test_negative_cases_extended.py:152`
- **Thời gian:** 0.000335 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "N/A"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) is None`

### 19. ✅ `tests/test_negative_cases_extended.py::TestNumberParserNegative::test_garbage_returns_none_not_exception[None]`

- **Tên dễ hiểu:** Ô chứa chữ rác lẫn số không được hiểu nhầm thành một con số
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một ô khối lượng/đơn giá vô tình bị nhập text rác hoặc mã hàng có lẫn chữ số.
- **Ví dụ cụ thể:** Ví dụ ô ghi 'abc123xyz' hoặc 'lung tung beng' thay vì một con số thật.
- **Kết quả mong đợi:** Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh lấy nhầm một đoạn số vô nghĩa trong text rác làm khối lượng/giá thật.
- **Nếu test thất bại:** Khối lượng hoặc đơn giá của một hạng mục có thể bị tính sai hoàn toàn mà không ai phát hiện (lỗi đã tìm thấy và sửa).
- **Vị trí:** `tests/test_negative_cases_extended.py:152`
- **Thời gian:** 0.000332 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": null
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) is None`

### 20. ✅ `tests/test_negative_cases_extended.py::TestNumberParserNegative::test_garbage_returns_none_not_exception[]`

- **Tên dễ hiểu:** Ô chứa chữ rác lẫn số không được hiểu nhầm thành một con số
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một ô khối lượng/đơn giá vô tình bị nhập text rác hoặc mã hàng có lẫn chữ số.
- **Ví dụ cụ thể:** Ví dụ ô ghi 'abc123xyz' hoặc 'lung tung beng' thay vì một con số thật.
- **Kết quả mong đợi:** Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh lấy nhầm một đoạn số vô nghĩa trong text rác làm khối lượng/giá thật.
- **Nếu test thất bại:** Khối lượng hoặc đơn giá của một hạng mục có thể bị tính sai hoàn toàn mà không ai phát hiện (lỗi đã tìm thấy và sửa).
- **Vị trí:** `tests/test_negative_cases_extended.py:152`
- **Thời gian:** 0.000340 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": ""
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) is None`

### 21. ✅ `tests/test_negative_cases_extended.py::TestNumberParserNegative::test_garbage_returns_none_not_exception[abc123xyz]`

- **Tên dễ hiểu:** Ô chứa chữ rác lẫn số không được hiểu nhầm thành một con số
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một ô khối lượng/đơn giá vô tình bị nhập text rác hoặc mã hàng có lẫn chữ số.
- **Ví dụ cụ thể:** Ví dụ ô ghi 'abc123xyz' hoặc 'lung tung beng' thay vì một con số thật.
- **Kết quả mong đợi:** Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh lấy nhầm một đoạn số vô nghĩa trong text rác làm khối lượng/giá thật.
- **Nếu test thất bại:** Khối lượng hoặc đơn giá của một hạng mục có thể bị tính sai hoàn toàn mà không ai phát hiện (lỗi đã tìm thấy và sửa).
- **Vị trí:** `tests/test_negative_cases_extended.py:152`
- **Thời gian:** 0.000377 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "abc123xyz"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) is None`

### 22. ✅ `tests/test_negative_cases_extended.py::TestNumberParserNegative::test_garbage_returns_none_not_exception[lung tung beng]`

- **Tên dễ hiểu:** Ô chứa chữ rác lẫn số không được hiểu nhầm thành một con số
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một ô khối lượng/đơn giá vô tình bị nhập text rác hoặc mã hàng có lẫn chữ số.
- **Ví dụ cụ thể:** Ví dụ ô ghi 'abc123xyz' hoặc 'lung tung beng' thay vì một con số thật.
- **Kết quả mong đợi:** Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm đọc số phải trả về 'không có giá trị' (None), không được tự suy ra số 123 từ chuỗi chữ đó. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh lấy nhầm một đoạn số vô nghĩa trong text rác làm khối lượng/giá thật.
- **Nếu test thất bại:** Khối lượng hoặc đơn giá của một hạng mục có thể bị tính sai hoàn toàn mà không ai phát hiện (lỗi đã tìm thấy và sửa).
- **Vị trí:** `tests/test_negative_cases_extended.py:152`
- **Thời gian:** 0.000369 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "lung tung beng"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) is None`

### 23. ✅ `tests/test_negative_cases_extended.py::TestNumberParserNegative::test_math_error_detects_klxdg_mismatch`

- **Tên dễ hiểu:** Phải phát hiện khi Khối lượng × Đơn giá không khớp với Thành tiền ghi trong file
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** File nhà thầu tự ghi cột 'thành tiền' nhưng số liệu không khớp với khối lượng nhân đơn giá.
- **Ví dụ cụ thể:** Ví dụ 10 (khối lượng) × 1.000 (đơn giá) = 10.000, nhưng cột thành tiền lại ghi 5.000.
- **Kết quả mong đợi:** Hệ thống phải tính ra mức chênh lệch và gắn cờ cảnh báo sai phép tính.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải tính ra mức chênh lệch và gắn cờ cảnh báo sai phép tính. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Phát hiện lỗi tính toán hoặc gian lận số liệu trong hồ sơ chào giá.
- **Nếu test thất bại:** Một khoản tiền sai có thể lọt vào báo cáo tổng hợp mà không bị phát hiện.
- **Vị trí:** `tests/test_negative_cases_extended.py:156`
- **Thời gian:** 0.000273 giây

**Các điều kiện kỹ thuật phải đúng:**

- `err is not None and err > 0`

### 24. ✅ `tests/test_negative_cases_extended.py::TestNumberParserNegative::test_math_error_none_when_any_input_missing`

- **Tên dễ hiểu:** Không được báo lỗi phép tính khi thiếu dữ liệu để tính
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một trong ba giá trị (khối lượng, đơn giá, thành tiền) bị bỏ trống.
- **Ví dụ cụ thể:** Ví dụ chỉ có khối lượng và đơn giá, không có thành tiền để so sánh.
- **Kết quả mong đợi:** Hệ thống phải trả về 'không xác định được lỗi' thay vì báo sai phép tính một cách giả tạo.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải trả về 'không xác định được lỗi' thay vì báo sai phép tính một cách giả tạo. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh tạo cảnh báo sai (báo động giả) khi đơn giản là thiếu dữ liệu để kiểm tra.
- **Nếu test thất bại:** Báo cáo có thể tràn ngập cảnh báo giả, làm người kiểm tra mất niềm tin vào hệ thống.
- **Vị trí:** `tests/test_negative_cases_extended.py:161`
- **Thời gian:** 0.000268 giây

**Các điều kiện kỹ thuật phải đúng:**

- `math_error(None, 1000, 5000) is None`
- `math_error(10, None, 5000) is None`
- `math_error(10, 1000, None) is None`

### 25. ✅ `tests/test_negative_cases_extended.py::TestTenderPackageNegative::test_no_bidder_files_raises_value_error`

- **Tên dễ hiểu:** Không cho phép chạy so sánh khi chưa có file nhà thầu nào
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng bấm chạy chức năng so sánh phụ lục nhưng chưa tải lên file nhà thầu nào.
- **Ví dụ cụ thể:** Ví dụ chỉ có file PL01, danh sách hồ sơ nhà thầu để trống.
- **Kết quả mong đợi:** Hệ thống phải dừng ngay và báo 'Cần ít nhất 1 hồ sơ nhà thầu để đối chiếu phụ lục'.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải dừng ngay và báo 'Cần ít nhất 1 hồ sơ nhà thầu để đối chiếu phụ lục'. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh chạy một tác vụ vô nghĩa (không có gì để so sánh) gây lãng phí thời gian xử lý.
- **Nếu test thất bại:** Hệ thống có thể chạy treo, lỗi mơ hồ, hoặc tạo báo cáo trống không rõ nguyên nhân.
- **Vị trí:** `tests/test_negative_cases_extended.py:172`
- **Thời gian:** 0.005496 giây

### 26. ✅ `tests/test_negative_cases_extended.py::TestTenderPackageNegative::test_no_appendix_at_all_raises_value_error`

- **Tên dễ hiểu:** Không cho phép chạy so sánh khi không có Phụ lục 01 lẫn Phụ lục 02
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng chỉ tải lên hồ sơ nhà thầu mà quên tải phụ lục làm căn cứ đối chiếu.
- **Ví dụ cụ thể:** Ví dụ chỉ có file 'bidder.xlsx', không có PL01 và PL02.
- **Kết quả mong đợi:** Hệ thống phải dừng ngay và báo 'Cần tải lên ít nhất một phụ lục: Phụ lục 01 hoặc Phụ lục 02'.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải dừng ngay và báo 'Cần tải lên ít nhất một phụ lục: Phụ lục 01 hoặc Phụ lục 02'. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng biết ngay cần bổ sung phụ lục, tránh chờ kết quả của một tác vụ vô nghĩa.
- **Nếu test thất bại:** Hệ thống không có cơ sở pháp lý/kỹ thuật nào để đối chiếu nhưng vẫn cố chạy, dẫn đến lỗi khó hiểu hoặc kết quả sai.
- **Vị trí:** `tests/test_negative_cases_extended.py:185`
- **Thời gian:** 0.004779 giây

### 27. ✅ `tests/test_negative_cases_extended.py::TestTenderPackageNegative::test_missing_pl2_file_on_disk_raises_clear_error`

- **Tên dễ hiểu:** Báo lỗi rõ ràng khi file Phụ lục 02 bị thiếu trên đĩa khi xử lý
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đường dẫn tới file Phụ lục 02 được truyền vào nhưng file thực tế không tồn tại (ví dụ do lỗi lưu file tạm).
- **Ví dụ cụ thể:** Ví dụ hệ thống được yêu cầu đọc 'khong_ton_tai.xlsx' nhưng file này không có thật trên đĩa.
- **Kết quả mong đợi:** Lỗi trả về phải nêu rõ đang xảy ra ở bước đọc PHỤ LỤC 02, không phải lỗi chung mơ hồ.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Lỗi trả về phải nêu rõ đang xảy ra ở bước đọc PHỤ LỤC 02, không phải lỗi chung mơ hồ. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người vận hành/hỗ trợ xác định nhanh đúng bước nào trong quy trình bị lỗi.
- **Nếu test thất bại:** Lỗi tệp tin chung chung khiến khó xác định do thiếu PL01, PL02 hay file nhà thầu.
- **Vị trí:** `tests/test_negative_cases_extended.py:198`
- **Thời gian:** 0.010268 giây

### 28. ✅ `tests/test_negative_cases_extended.py::TestTenderPackageNegative::test_pl2_without_recognizable_headers_does_not_crash_but_warns`

- **Tên dễ hiểu:** Khi file Phụ lục 02 không đúng mẫu (thiếu cột Thương hiệu/Xuất xứ), hệ thống vẫn phải chạy xong và cảnh báo rõ
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng tải nhầm một file Excel khác vào ô Phụ lục 02, không có cột yêu cầu vật tư/thương hiệu/xuất xứ.
- **Ví dụ cụ thể:** Ví dụ file chỉ có 'Cột A, Cột B, Cột C' không liên quan gì đến yêu cầu vật tư.
- **Kết quả mong đợi:** Báo cáo vẫn phải được tạo ra, nhưng phải có cảnh báo rõ là không đọc được yêu cầu nào từ Phụ lục 02.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Báo cáo vẫn phải được tạo ra, nhưng phải có cảnh báo rõ là không đọc được yêu cầu nào từ Phụ lục 02. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng biết ngay là đã tải nhầm file, không lầm tưởng rằng việc kiểm tra thương hiệu/xuất xứ đã được thực hiện đầy đủ.
- **Nếu test thất bại:** Người dùng có thể tưởng nhầm hồ sơ đã được kiểm tra đầy đủ thương hiệu/xuất xứ, trong khi thực tế bước đó chưa từng chạy.
- **Vị trí:** `tests/test_negative_cases_extended.py:212`
- **Thời gian:** 0.062113 giây

**Các điều kiện kỹ thuật phải đúng:**

- `out.report_path.exists()`
- `any("phụ lục 02" in w.lower() for w in out.result.warnings)`

### 29. ✅ `tests/test_negative_cases_extended.py::TestTenderPackageNegative::test_single_bidder_with_zero_items_produces_empty_but_valid_report`

- **Tên dễ hiểu:** Khi nhà thầu nộp file trống (không có hạng mục nào), hệ thống phải báo đầy đủ các hạng mục đó là 'thiếu'
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Có Phụ lục 01 quy định rõ các hạng mục cần chào giá, nhưng file nhà thầu hoàn toàn trống.
- **Ví dụ cụ thể:** Ví dụ PL01 yêu cầu 2 hạng mục, nhưng nhà thầu nộp file Excel có sheet trống không một dòng dữ liệu.
- **Kết quả mong đợi:** Báo cáo phải đếm đủ 2 hạng mục đó ở trạng thái 'thiếu' (MISSING), không được bỏ qua.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Báo cáo phải đếm đủ 2 hạng mục đó ở trạng thái 'thiếu' (MISSING), không được bỏ qua. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Phát hiện ngay trường hợp nhà thầu nộp nhầm/thiếu hồ sơ chào giá.
- **Nếu test thất bại:** Một hồ sơ thực chất trống rỗng có thể bị đánh giá nhầm là 'không có vấn đề gì' vì không có dữ liệu để so sánh.
- **Vị trí:** `tests/test_negative_cases_extended.py:237`
- **Thời gian:** 0.079366 giây

**Các điều kiện kỹ thuật phải đúng:**

- `out.report_path.exists()`
- `out.result.summary.missing_items == 2`

### 30. ✅ `tests/test_negative_cases_extended.py::TestTenderPackageNegative::test_single_bidder_disables_peer_price_comparison`

- **Tên dễ hiểu:** Khi chỉ có một nhà thầu duy nhất, hệ thống không được tự so sánh giá của họ với ai
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Chỉ có đúng một hồ sơ nhà thầu được nộp, không có nhà thầu thứ hai để đối chiếu giá.
- **Ví dụ cụ thể:** Ví dụ chỉ một nhà thầu 'NT duy nhất' chào giá cho các hạng mục trong PL01.
- **Kết quả mong đợi:** Audit của báo cáo phải ghi rõ 'không so sánh giá ngang hàng' kèm lý do, vì không có đối tượng thứ hai để so.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Audit của báo cáo phải ghi rõ 'không so sánh giá ngang hàng' kèm lý do, vì không có đối tượng thứ hai để so. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh đưa ra nhận định 'giá cao/giá thấp' khi không có cơ sở để so sánh, gây hiểu nhầm cho người đánh giá thầu.
- **Nếu test thất bại:** Một mức giá hợp lý có thể bị gắn nhãn bất thường một cách vô căn cứ chỉ vì so sánh sai logic.
- **Vị trí:** `tests/test_negative_cases_extended.py:257`
- **Thời gian:** 0.083098 giây

**Các điều kiện kỹ thuật phải đúng:**

- `out.result.audit["peer_price_comparison_enabled"] is False`
- `out.result.audit["peer_stats"]["reason"]`

### 31. ✅ `tests/test_negative_cases_extended.py::TestPL2ReaderNegative::test_pl2_wrong_extension_raises`

- **Tên dễ hiểu:** Phụ lục 02 sai định dạng (.xls) phải bị từ chối ngay từ đầu
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng tải file Phụ lục 02 ở định dạng Excel cũ chưa chuyển sang .xlsx.
- **Ví dụ cụ thể:** Ví dụ file 'pl2.xls'.
- **Kết quả mong đợi:** Hệ thống phải báo lỗi yêu cầu định dạng .xlsx, không cố đọc tiếp.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải báo lỗi yêu cầu định dạng .xlsx, không cố đọc tiếp. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh xử lý một file mà hệ thống chắc chắn không đọc đúng được.
- **Nếu test thất bại:** Hệ thống có thể cố đọc và trả về kết quả rác hoặc lỗi không rõ nguyên nhân.
- **Vị trí:** `tests/test_negative_cases_extended.py:279`
- **Thời gian:** 0.002053 giây

### 32. ✅ `tests/test_negative_cases_extended.py::TestPL2ReaderNegative::test_pl2_empty_workbook_returns_empty_with_warning`

- **Tên dễ hiểu:** Phụ lục 02 trống phải trả về danh sách yêu cầu rỗng kèm cảnh báo rõ ràng
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** File Phụ lục 02 hợp lệ về định dạng nhưng không có nội dung gì bên trong.
- **Ví dụ cụ thể:** Ví dụ file chỉ có một sheet trống.
- **Kết quả mong đợi:** Hệ thống trả về danh sách yêu cầu vật tư rỗng và một cảnh báo 'Không đọc được yêu cầu vật tư nào từ Phụ lục 02'.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống trả về danh sách yêu cầu vật tư rỗng và một cảnh báo 'Không đọc được yêu cầu vật tư nào từ Phụ lục 02'. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng biết chính xác lý do không có kiểm tra thương hiệu/xuất xứ nào được áp dụng.
- **Nếu test thất bại:** Việc thiếu Phụ lục 02 thực chất có thể bị hiểu lầm thành 'đã kiểm tra và không có vấn đề gì'.
- **Vị trí:** `tests/test_negative_cases_extended.py:285`
- **Thời gian:** 0.010293 giây

**Các điều kiện kỹ thuật phải đúng:**

- `requirements == []`
- `any("không đọc được yêu cầu" in w.lower() for w in warnings)`

### 33. ✅ `tests/test_negative_cases_extended.py::TestUploadValidationNegative::test_sanitize_strips_path_traversal`

- **Tên dễ hiểu:** Tên file độc hại kiểu '../../etc/passwd' phải bị làm sạch, không được ghi ra ngoài thư mục cho phép
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng (hoặc kẻ tấn công) đặt tên file tải lên chứa các ký tự '..' và '/' để cố thoát khỏi thư mục lưu file.
- **Ví dụ cụ thể:** Ví dụ tên file '../../../etc/passwd.xlsx'.
- **Kết quả mong đợi:** Tên file sau khi xử lý không còn chứa '..' hay dấu '/'.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tên file sau khi xử lý không còn chứa '..' hay dấu '/'. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Ngăn chặn kiểu tấn công Path Traversal ghi đè file hệ thống ngoài ý muốn.
- **Nếu test thất bại:** Kẻ tấn công có thể lợi dụng tên file để ghi đè hoặc truy cập file ngoài phạm vi cho phép của ứng dụng.
- **Vị trí:** `tests/test_negative_cases_extended.py:316`
- **Thời gian:** 0.000533 giây

**Các điều kiện kỹ thuật phải đúng:**

- `".." not in result`
- `"/" not in result and "\\" not in result`

### 34. ✅ `tests/test_negative_cases_extended.py::TestUploadValidationNegative::test_sanitize_strips_path_traversal_windows_style`

- **Tên dễ hiểu:** Tên file độc hại kiểu Windows '..\\..\\Windows\\...' cũng phải bị làm sạch
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Giống tấn công path traversal nhưng dùng dấu gạch chéo ngược kiểu đường dẫn Windows.
- **Ví dụ cụ thể:** Ví dụ tên file '..\\..\\Windows\\System32\\evil.xlsx'.
- **Kết quả mong đợi:** Tên file sau khi xử lý không còn chứa '..' hay dấu '\\'.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tên file sau khi xử lý không còn chứa '..' hay dấu '\\'. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Đảm bảo việc làm sạch tên file hoạt động trên cả hai kiểu đường dẫn Windows và Unix.
- **Nếu test thất bại:** Hệ thống chạy trên Windows có thể bị tấn công bằng kiểu đường dẫn đặc thù mà bộ lọc Unix bỏ sót.
- **Vị trí:** `tests/test_negative_cases_extended.py:321`
- **Thời gian:** 0.000721 giây

**Các điều kiện kỹ thuật phải đúng:**

- `"\\" not in result`
- `"/" not in result`
- `joined.parent == base`

### 35. ✅ `tests/test_negative_cases_extended.py::TestUploadValidationNegative::test_sanitize_empty_name_falls_back`

- **Tên dễ hiểu:** Tên file rỗng phải được thay bằng một tên mặc định hợp lệ
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Trường hợp hiếm khi trình duyệt gửi lên tên file rỗng hoặc không hợp lệ.
- **Ví dụ cụ thể:** Ví dụ tên file gửi lên là chuỗi rỗng ''.
- **Kết quả mong đợi:** Hệ thống phải tự đặt một tên file mặc định thay vì lưu file không tên.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải tự đặt một tên file mặc định thay vì lưu file không tên. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh lỗi hệ thống file khi gặp tên rỗng.
- **Nếu test thất bại:** Việc lưu file có thể thất bại với lỗi khó hiểu nếu tên file rỗng không được xử lý.
- **Vị trí:** `tests/test_negative_cases_extended.py:335`
- **Thời gian:** 0.000501 giây

**Các điều kiện kỹ thuật phải đúng:**

- `_sanitize("", "fallback.xlsx") == "fallback.xlsx"`

### 36. ✅ `tests/test_negative_cases_extended.py::TestUploadValidationNegative::test_save_upload_rejects_disallowed_extension`

- **Tên dễ hiểu:** Từ chối ngay các file có đuôi không được phép (ví dụ .exe) trước khi lưu vào đĩa
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng tải lên một file không phải Excel, ví dụ file thực thi.
- **Ví dụ cụ thể:** Ví dụ file 'evil.exe' được gửi tới chức năng chỉ chấp nhận .xlsx.
- **Kết quả mong đợi:** Yêu cầu phải bị từ chối với mã lỗi 400 (yêu cầu không hợp lệ) và không được lưu file đó vào đĩa.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Yêu cầu phải bị từ chối với mã lỗi 400 (yêu cầu không hợp lệ) và không được lưu file đó vào đĩa. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Ngăn người dùng tải lên các loại file nguy hiểm hoặc không liên quan vào máy chủ.
- **Nếu test thất bại:** Máy chủ có thể vô tình lưu trữ file thực thi hoặc file độc hại do không kiểm tra đuôi file.
- **Vị trí:** `tests/test_negative_cases_extended.py:338`
- **Thời gian:** 0.001673 giây

**Các điều kiện kỹ thuật phải đúng:**

- `excinfo.value.status_code == 400`

### 37. ✅ `tests/test_negative_cases_extended.py::TestUploadValidationNegative::test_save_upload_rejects_empty_file`

- **Tên dễ hiểu:** Từ chối file tải lên có dung lượng 0 byte
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng tải lên một file rỗng (ví dụ do lỗi mạng khi chọn file).
- **Ví dụ cụ thể:** Ví dụ file 'empty.xlsx' có nội dung trống.
- **Kết quả mong đợi:** Yêu cầu bị từ chối với thông báo 'File tải lên rỗng' và file tạm không được giữ lại trên đĩa.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Yêu cầu bị từ chối với thông báo 'File tải lên rỗng' và file tạm không được giữ lại trên đĩa. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Phát hiện sớm lỗi tải file, tránh xử lý tiếp với dữ liệu không có gì.
- **Nếu test thất bại:** Hệ thống có thể tạo một tác vụ xử lý cho một file trống, gây lãng phí và lỗi khó hiểu ở bước sau.
- **Vị trí:** `tests/test_negative_cases_extended.py:348`
- **Thời gian:** 0.001359 giây

**Các điều kiện kỹ thuật phải đúng:**

- `excinfo.value.status_code == 400`
- `not target.exists()`

### 38. ✅ `tests/test_negative_cases_extended.py::TestUploadValidationNegative::test_save_upload_rejects_file_over_limit`

- **Tên dễ hiểu:** Từ chối file tải lên vượt quá giới hạn dung lượng cho phép
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng tải lên một file có kích thước lớn hơn mức hệ thống cho phép.
- **Ví dụ cụ thể:** Ví dụ file 2KB được tải lên trong khi giới hạn cấu hình chỉ cho phép 1KB.
- **Kết quả mong đợi:** Yêu cầu bị từ chối với mã lỗi 413 (file quá lớn) và phần file đã ghi tạm phải được xoá sạch, không để lại rác trên đĩa.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Yêu cầu bị từ chối với mã lỗi 413 (file quá lớn) và phần file đã ghi tạm phải được xoá sạch, không để lại rác trên đĩa. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Bảo vệ máy chủ khỏi bị quá tải ổ đĩa do file tải lên quá lớn hoặc tấn công làm đầy dung lượng.
- **Nếu test thất bại:** Máy chủ có thể bị đầy ổ đĩa hoặc chậm dần theo thời gian do các file dở dang không bị dọn dẹp.
- **Vị trí:** `tests/test_negative_cases_extended.py:359`
- **Thời gian:** 0.001277 giây

**Các điều kiện kỹ thuật phải đúng:**

- `excinfo.value.status_code == 413`
- `not target.exists()`

### 39. ✅ `tests/test_negative_cases_extended.py::TestUploadValidationNegative::test_save_upload_accepts_valid_small_file`

- **Tên dễ hiểu:** File hợp lệ, đúng định dạng và trong giới hạn dung lượng phải được lưu thành công
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Trường hợp bình thường: người dùng tải lên một file Excel nhỏ, hợp lệ.
- **Ví dụ cụ thể:** Ví dụ file 'ok.xlsx' với nội dung hợp lệ và dung lượng nhỏ.
- **Kết quả mong đợi:** File phải được lưu đúng vào vị trí đích với nội dung giữ nguyên, không bị từ chối oan.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: File phải được lưu đúng vào vị trí đích với nội dung giữ nguyên, không bị từ chối oan. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Đảm bảo các bước kiểm tra an toàn (đuôi file, dung lượng) không chặn nhầm các yêu cầu hợp lệ.
- **Nếu test thất bại:** Các bộ lọc bảo mật quá chặt có thể vô tình chặn luôn cả người dùng hợp lệ, gây khó chịu khi sử dụng hệ thống.
- **Vị trí:** `tests/test_negative_cases_extended.py:372`
- **Thời gian:** 0.001280 giây

**Các điều kiện kỹ thuật phải đúng:**

- `target.exists()`
- `target.read_bytes() == b"valid content"`

### 40. ✅ `tests/test_negative_cases_extended.py::TestErrorMessageMapping::test_encrypted_or_unknown_underlying_error_falls_back_to_generic_excel_message`

- **Tên dễ hiểu:** File Excel có mật khẩu/mã hoá vẫn phải báo lỗi thân thiện, không lộ chi tiết kỹ thuật
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu nộp một file Excel được đặt mật khẩu bảo vệ, hệ thống không tự mở được.
- **Ví dụ cụ thể:** Ví dụ file 'BaoGia_C_CoMatKhau.xlsx' báo lỗi 'Workbook is encrypted and password-protected'.
- **Kết quả mong đợi:** Thông báo cho người dùng vẫn phải nêu đúng tên file gốc và nói 'không đúng định dạng Excel', không hiển thị câu lỗi kỹ thuật gốc.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Thông báo cho người dùng vẫn phải nêu đúng tên file gốc và nói 'không đúng định dạng Excel', không hiển thị câu lỗi kỹ thuật gốc. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng biết cần gỡ mật khẩu file trước khi tải lên, dù lỗi kỹ thuật bên dưới là loại lỗi hệ thống chưa từng gặp.
- **Nếu test thất bại:** Người dùng nhận một câu lỗi tiếng Anh kỹ thuật khó hiểu, không biết hướng xử lý.
- **Vị trí:** `tests/test_negative_cases_extended.py:382`
- **Thời gian:** 0.000374 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "request": {
    "bidders": [
      {
        "file": "004_NhaThauC.xlsx",
        "original_name": "BaoGia_C_CoMatKhau.xlsx"
      }
    ]
  }
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `"BaoGia_C_CoMatKhau.xlsx" in msg`
- `"không đúng định dạng Excel" in msg`

### 41. ✅ `tests/test_negative_cases_extended.py::TestErrorMessageMapping::test_unknown_request_mapping_still_returns_something_safe`

- **Tên dễ hiểu:** Hệ thống không bao giờ được 'câm lặng' hoặc crash khi gặp lỗi không xác định được tên file/nhà thầu
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một lỗi xảy ra nhưng không khớp với bất kỳ thông tin nào trong yêu cầu (ví dụ thiếu thông tin ngữ cảnh).
- **Ví dụ cụ thể:** Ví dụ lỗi nhắc tới 'unknown.xlsx' mà không có dữ liệu request nào để tham chiếu.
- **Kết quả mong đợi:** Hàm tạo thông báo lỗi vẫn phải trả về một chuỗi văn bản hợp lệ, không phải None và không ném thêm lỗi mới.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm tạo thông báo lỗi vẫn phải trả về một chuỗi văn bản hợp lệ, không phải None và không ném thêm lỗi mới. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Bảo đảm người dùng luôn nhận được một phản hồi nào đó, dù là trường hợp hiếm gặp nhất.
- **Nếu test thất bại:** Toàn bộ tác vụ có thể bị crash thêm lần hai ngay tại bước hiển thị lỗi, khiến người dùng không nhận được phản hồi nào cả.
- **Vị trí:** `tests/test_negative_cases_extended.py:394`
- **Thời gian:** 0.000766 giây

**Các điều kiện kỹ thuật phải đúng:**

- `msg`
- `"unknown.xlsx" in msg`

### 42. ✅ `tests/test_parser_section_and_legend.py::test_numbering_row_with_float_values_is_detected`

- **Tên dễ hiểu:** Nhận diện đúng dòng chú giải đánh số cột kể cả khi số ở dạng 1.0, 2.0
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhiều file Excel có một dòng ghi số thứ tự cột (1, 2, 3...) ngay dưới tiêu đề; khi đọc bằng máy, các số này có thể ở dạng '1.0', '2.0'.
- **Ví dụ cụ thể:** Ví dụ dòng '1, 2, 3, 4, 5, 6, 7, 8, 16=11+12+13+14+15' — chỉ là chú thích đánh số cột, không phải hàng hóa.
- **Kết quả mong đợi:** Hệ thống phải nhận ra đây là dòng chú giải và bỏ qua, không đọc nhầm thành một hạng mục tên là '2'.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống phải nhận ra đây là dòng chú giải và bỏ qua, không đọc nhầm thành một hạng mục tên là '2'. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh để dòng đánh số cột lọt vào báo cáo như một hạng mục giả rồi bị gắn cờ 'phát sinh' oan.
- **Nếu test thất bại:** Báo cáo có thể chứa hàng loạt 'hạng mục' rác tên là số, làm sai số liệu và gây nhiễu cho người đánh giá.
- **Vị trí:** `tests/test_parser_section_and_legend.py:20`
- **Thời gian:** 0.000534 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "row": [
    1.0,
    2.0,
    "3",
    4.0,
    5.0,
    6.0,
    7.0,
    8.0,
    "16=11+12+13+14+15"
  ]
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `_is_numbering_row(row) is True`

### 43. ✅ `tests/test_parser_section_and_legend.py::test_numbering_row_does_not_misfire_on_real_priced_row`

- **Tên dễ hiểu:** Không nhầm một hạng mục thật thành dòng đánh số cột
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một hàng hóa thật cũng có thể bắt đầu bằng số thứ tự 1, 2, 3, 4.
- **Ví dụ cụ thể:** Ví dụ '1 | Tủ điện tổng | Cái | 4 | Schneider' — là hạng mục thật, không phải dòng chú giải.
- **Kết quả mong đợi:** Hệ thống vẫn giữ lại dòng này như một hạng mục, không bỏ nhầm.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống vẫn giữ lại dòng này như một hạng mục, không bỏ nhầm. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Đảm bảo việc lọc dòng chú giải không vô tình xóa mất hàng hóa thật.
- **Nếu test thất bại:** Một hạng mục hợp lệ có thể biến mất khỏi báo cáo nếu bộ lọc quá tay.
- **Vị trí:** `tests/test_parser_section_and_legend.py:26`
- **Thời gian:** 0.000302 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "row": [
    1.0,
    "Tủ điện tổng",
    "Cái",
    4.0,
    "Schneider"
  ]
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `_is_numbering_row(row) is False`

### 44. ✅ `tests/test_parser_section_and_legend.py::test_legend_and_section_subtotal_excluded_from_comparable_items`

- **Tên dễ hiểu:** Dòng đánh số cột và tiêu đề mục có tổng phụ không được coi là hạng mục so sánh
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** File chào giá có dòng đánh số cột, có tiêu đề mục lớn (vd 'A. ĐẦU MỤC CÔNG VIỆC THEO KLMT') kèm một con số tổng phụ rất lớn ở cột thành tiền.
- **Ví dụ cụ thể:** Ví dụ tiêu đề mục 'A. ĐẦU MỤC...' có thành tiền 76 tỷ (là tổng của cả mục), không có đơn vị/khối lượng/đơn giá.
- **Kết quả mong đợi:** Dòng đánh số cột bị bỏ hẳn; tiêu đề mục được giữ lại nhưng đánh dấu là dòng tổng phụ (không đem ra so sánh như một hàng hóa).
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Dòng đánh số cột bị bỏ hẳn; tiêu đề mục được giữ lại nhưng đánh dấu là dòng tổng phụ (không đem ra so sánh như một hàng hóa). Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh việc các dòng tiêu đề/tổng phụ bị gắn cờ 'phát sinh' hoặc 'bất thường' một cách vô lý, gây nhiễu báo cáo.
- **Nếu test thất bại:** Báo cáo có thể đầy cảnh báo giả ở các dòng tiêu đề mục, khiến người đánh giá mất thời gian và giảm tin tưởng.
- **Vị trí:** `tests/test_parser_section_and_legend.py:46`
- **Thời gian:** 0.007212 giây

**Các điều kiện kỹ thuật phải đúng:**

- `"2" not in names and "2.0" not in names`
- `section is not None`
- `section.row_type is RowType.SUMMARY`
- `section.is_comparable is False`
- `len(comparable) == 1`
- `comparable[0].item_name == "Tủ điện tổng"`

### 45. ✅ `tests/test_reporter_consolidated_quote.py::test_summary_has_one_sheet_per_hangmuc_with_side_by_side_blocks`

- **Tên dễ hiểu:** Tự sinh file tổng hợp đúng format: mỗi hạng mục một sheet, các nhà thầu xếp cạnh nhau
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Có nhiều nhà thầu cùng chào giá; hệ thống gộp tất cả vào một file tổng hợp riêng, mỗi hạng mục (sheet gốc) là một trang, mỗi nhà thầu một khối cột nằm cạnh nhau — giống hệt bảng chào giá tổng hợp thực tế.
- **Ví dụ cụ thể:** Ví dụ hạng mục 'HT điện' thành một sheet riêng; trong đó bốn nhà thầu xếp cạnh nhau, mỗi nhà thầu có đủ các cột KL chào, mô tả/quy cách, mã hiệu, thương hiệu, xuất xứ, các thành phần đơn giá, ĐG tổng hợp và thành tiền.
- **Kết quả mong đợi:** Sheet mang đúng tên hạng mục gốc, dòng tiêu đề ghi đủ tên cả bốn nhà thầu, mỗi nhà thầu có cột 'ĐG tổng hợp' và 'Thành tiền NT chào' riêng, và TUYỆT ĐỐI không có cột phân tích phụ (Mức độ, Điểm bất thường).
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Sheet mang đúng tên hạng mục gốc, dòng tiêu đề ghi đủ tên cả bốn nhà thầu, mỗi nhà thầu có cột 'ĐG tổng hợp' và 'Thành tiền NT chào' riêng, và TUYỆT ĐỐI không có cột phân tích phụ (Mức độ, Điểm bất thường). Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người đánh giá thầu xem được toàn bộ nhà thầu trên đúng bảng quen thuộc của mình, không bị chèn thêm các cột kỹ thuật lạ.
- **Nếu test thất bại:** Nếu dựng sai cấu trúc, cột của nhà thầu này có thể lẫn sang nhà thầu khác, hoặc file lại xuất hiện các cột phân tích mà người dùng không muốn.
- **Vị trí:** `tests/test_reporter_consolidated_quote.py:55`
- **Thời gian:** 0.083976 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "prices": {
    "NT A": 100,
    "NT B": 105,
    "NT C": 95,
    "NT Lệch": 500
  },
  "all_headers": []
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `"1. HT điện" in wb.sheetnames`
- `"Điểm bất thường" not in joined`
- `"Mức độ" not in joined`
- `len(cols.get("ĐG tổng hợp", [])) == 4`
- `len(cols.get("Thành tiền NT chào", [])) == 4`
- `name in tier1`

### 46. ✅ `tests/test_reporter_consolidated_quote.py::test_summary_marks_deviating_price_cells_directly`

- **Tên dễ hiểu:** Đánh dấu trực tiếp lên ô giá của nhà thầu báo lệch nhiều trong file tổng hợp
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Trong file tổng hợp, một nhà thầu báo đơn giá cách biệt hẳn so với các nhà thầu còn lại cho cùng một hạng mục.
- **Ví dụ cụ thể:** Ví dụ ba nhà thầu báo 95, 100, 105; một nhà thầu báo 500 cho cùng hạng mục.
- **Kết quả mong đợi:** Đúng ô 'ĐG tổng hợp' (và 'Thành tiền NT chào') của nhà thầu báo 500 được tô màu cảnh báo và gắn ghi chú ngay trên ô, nêu rõ mức lệch so với trung vị; ô của các nhà thầu báo gần nhau không bị đánh dấu.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Đúng ô 'ĐG tổng hợp' (và 'Thành tiền NT chào') của nhà thầu báo 500 được tô màu cảnh báo và gắn ghi chú ngay trên ô, nêu rõ mức lệch so với trung vị; ô của các nhà thầu báo gần nhau không bị đánh dấu. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người xem chỉ cần rê chuột vào đúng ô giá bị đánh dấu để hiểu vì sao nó bất thường, ngay trên bảng tổng hợp.
- **Nếu test thất bại:** Một mức giá bất thường có thể bị bỏ lọt giữa hàng nghìn dòng, dẫn đến đánh giá thầu sai.
- **Vị trí:** `tests/test_reporter_consolidated_quote.py:83`
- **Thời gian:** 0.097256 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "prices": {
    "NT A": 100,
    "NT B": 105,
    "NT C": 95,
    "NT Lệch": 500
  },
  "data_row": null,
  "flagged": []
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `data_row is not None`
- `len(flagged) == 1`
- `value == 500`
- `has_fill`
- `"cao hơn" in comment_text`

### 47. ✅ `tests/test_reporter_consolidated_quote.py::test_summary_no_marks_when_prices_close`

- **Tên dễ hiểu:** File tổng hợp không đánh dấu khi các nhà thầu báo giá tương đương nhau
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Tất cả nhà thầu báo giá cho cùng hạng mục chỉ chênh nhau rất ít.
- **Ví dụ cụ thể:** Ví dụ ba nhà thầu báo 98, 100, 102.
- **Kết quả mong đợi:** Không ô giá nào trong file tổng hợp bị tô màu hay gắn ghi chú cảnh báo.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Không ô giá nào trong file tổng hợp bị tô màu hay gắn ghi chú cảnh báo. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh làm người xem rối mắt với cảnh báo thừa khi giá cả vẫn hợp lý.
- **Nếu test thất bại:** File tô màu tràn lan sẽ làm mất ý nghĩa của việc đánh dấu.
- **Vị trí:** `tests/test_reporter_consolidated_quote.py:114`
- **Thời gian:** 0.060558 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "prices": {
    "NT A": 100,
    "NT B": 102,
    "NT C": 98
  }
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `cell.comment is None`

### 48. ✅ `tests/test_reporter_consolidated_quote.py::test_summary_splits_multiple_hangmuc_into_separate_sheets`

- **Tên dễ hiểu:** Nhiều hạng mục được tách thành nhiều sheet riêng trong file tổng hợp
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Hồ sơ chào giá có nhiều hạng mục khác nhau (ví dụ hệ thống điện và hệ thống cấp thoát nước).
- **Ví dụ cụ thể:** Ví dụ mỗi nhà thầu có sheet 'HT điện' và sheet 'HT CTN'; file tổng hợp phải tạo đúng hai trang tương ứng.
- **Kết quả mong đợi:** File tổng hợp có một sheet riêng cho mỗi hạng mục, mang đúng tên hạng mục gốc.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: File tổng hợp có một sheet riêng cho mỗi hạng mục, mang đúng tên hạng mục gốc. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Giữ đúng cách tổ chức theo hạng mục như bảng chào giá gốc, dễ tra cứu từng phần.
- **Nếu test thất bại:** Nếu gộp hết vào một sheet hoặc đặt sai tên, người dùng khó đối chiếu với hồ sơ gốc.
- **Vị trí:** `tests/test_reporter_consolidated_quote.py:130`
- **Thời gian:** 0.064924 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "bidder_files": []
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `"1. HT điện" in wb.sheetnames`
- `"3. HT CTN" in wb.sheetnames`

### 49. ✅ `tests/test_reporter_price_deviation.py::test_price_matrix_marks_the_outlier_cell_directly`

- **Tên dễ hiểu:** Tự động tô màu và gắn ghi chú ngay trên ô giá khi nhà thầu báo giá lệch hẳn
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Bốn nhà thầu cùng báo giá một hạng mục: ba nhà thầu báo giá gần nhau, một nhà thầu báo giá cách biệt rất xa.
- **Ví dụ cụ thể:** Ví dụ ba nhà thầu báo 95, 100, 105; một nhà thầu báo 500 cho cùng một hạng mục 'Tủ điện tổng'.
- **Kết quả mong đợi:** Đúng ô giá của nhà thầu báo 500 (không phải một cột riêng) phải được tô màu cảnh báo và có ghi chú (hiện khi rê chuột) nêu rõ tên nhà thầu, giá trị, trung vị và mức lệch %; ô giá của các nhà thầu báo gần nhau thì không bị tô màu và không có ghi chú.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Đúng ô giá của nhà thầu báo 500 (không phải một cột riêng) phải được tô màu cảnh báo và có ghi chú (hiện khi rê chuột) nêu rõ tên nhà thầu, giá trị, trung vị và mức lệch %; ô giá của các nhà thầu báo gần nhau thì không bị tô màu và không có ghi chú. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người xem báo cáo chỉ cần rê chuột vào đúng ô giá bất thường để biết ngay vì sao nó bị đánh dấu, không cần dò một cột ghi chú riêng hay tự tính toán so sánh từng dòng.
- **Nếu test thất bại:** Một mức giá bất thường có thể bị bỏ lọt trong hàng nghìn dòng dữ liệu, dẫn đến đánh giá thầu sai mà không ai phát hiện kịp thời.
- **Vị trí:** `tests/test_reporter_price_deviation.py:33`
- **Thời gian:** 0.078567 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "prices": {
    "NT Gần 1": 100,
    "NT Gần 2": 105,
    "NT Gần 3": 95,
    "NT Lệch xa": 500
  },
  "bidder_files": []
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `"Ma trận đơn giá" in wb.sheetnames`
- `"Ghi chú chênh lệch" not in headers`
- `outlier_cell.fill is not None`
- `outlier_cell.fill.fgColor.rgb not in (None, "00000000")`
- `outlier_cell.comment is not None`
- `"NT Lệch xa" in outlier_cell.comment.text`
- `"cao hơn" in outlier_cell.comment.text`
- `normal_cell.fill is None or normal_cell.fill.fgColor.rgb in (None, "00000000")`
- `normal_cell.comment is None`

### 50. ✅ `tests/test_reporter_price_deviation.py::test_price_matrix_has_no_comment_when_all_bidders_close`

- **Tên dễ hiểu:** Không gắn ghi chú/tô màu giả khi tất cả nhà thầu báo giá tương đương nhau
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Các nhà thầu báo giá cho cùng một hạng mục chỉ chênh nhau rất ít, trong phạm vi bình thường.
- **Ví dụ cụ thể:** Ví dụ ba nhà thầu báo 98, 100, 102 cho cùng một hạng mục — mức chênh chỉ vài phần trăm.
- **Kết quả mong đợi:** Không ô giá nào trong dòng đó được tô màu cảnh báo hay gắn ghi chú, vì không có nhà thầu nào lệch đáng kể.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Không ô giá nào trong dòng đó được tô màu cảnh báo hay gắn ghi chú, vì không có nhà thầu nào lệch đáng kể. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người xem báo cáo không bị làm phiền bởi các cảnh báo không cần thiết khi giá cả vẫn trong mức hợp lý.
- **Nếu test thất bại:** Báo cáo có thể tô màu và cảnh báo tràn lan dù không có vấn đề thật, làm người dùng mất niềm tin vào tính năng cảnh báo.
- **Vị trí:** `tests/test_reporter_price_deviation.py:72`
- **Thời gian:** 0.057833 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "prices": {
    "NT A": 100,
    "NT B": 102,
    "NT C": 98
  },
  "bidder_files": []
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `cell.comment is None`

### 51. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce01_equal_quantity_has_no_warning`

- **Tên dễ hiểu:** Khối lượng bằng nhau thì không cảnh báo
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Phụ lục và nhà thầu ghi cùng một số lượng.
- **Ví dụ cụ thể:** Ví dụ PL01 = 100 mét cáp, nhà thầu = 100 mét cáp.
- **Kết quả mong đợi:** Độ chênh bằng 0% và trạng thái không phải WARNING/CRITICAL.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Độ chênh bằng 0% và trạng thái không phải WARNING/CRITICAL. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng không bị làm phiền bởi dữ liệu hoàn toàn khớp.
- **Nếu test thất bại:** Hệ thống có thể tạo cảnh báo giả cho hồ sơ đúng.
- **Vị trí:** `tests/test_s1_comparison_engine.py:95`
- **Thời gian:** 0.000563 giây

**Các điều kiện kỹ thuật phải đúng:**

- `row.quantity_delta == 0`
- `row.quantity_delta_pct == 0`
- `row.severity is Severity.OK`
- `row.flags == []`

### 52. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce02_quantity_difference_8_percent_is_warning`

- **Tên dễ hiểu:** Chênh khối lượng 8% phải tạo cảnh báo
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu ghi số lượng lệch vừa phải so với phụ lục.
- **Ví dụ cụ thể:** Ví dụ PL01 = 100, nhà thầu = 108; chênh 8%.
- **Kết quả mong đợi:** Hệ thống gắn mức WARNING theo ngưỡng đang cấu hình.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống gắn mức WARNING theo ngưỡng đang cấu hình. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người kiểm tra biết có sai khác cần xem lại nhưng chưa phải mức nghiêm trọng nhất.
- **Nếu test thất bại:** Sai số vừa phải có thể bị bỏ qua.
- **Vị trí:** `tests/test_s1_comparison_engine.py:112`
- **Thời gian:** 0.000425 giây

**Các điều kiện kỹ thuật phải đúng:**

- `row.quantity_delta == 8`
- `row.quantity_delta_pct == 0.08`
- `row.severity is Severity.WARNING`
- `any("khối lượng nhà thầu chào" in flag.lower() for flag in row.flags)`

### 53. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce03_quantity_difference_35_percent_is_critical`

- **Tên dễ hiểu:** Chênh khối lượng 35% phải là nghiêm trọng
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Số lượng nhà thầu khác rất xa yêu cầu.
- **Ví dụ cụ thể:** Ví dụ PL01 = 100, nhà thầu = 135; chênh 35%.
- **Kết quả mong đợi:** Hệ thống gắn CRITICAL hoặc mức nghiêm trọng tương đương.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống gắn CRITICAL hoặc mức nghiêm trọng tương đương. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Lỗi lớn được đưa lên ưu tiên xử lý.
- **Nếu test thất bại:** Sai khối lượng lớn có thể bị xem như cảnh báo nhẹ.
- **Vị trí:** `tests/test_s1_comparison_engine.py:129`
- **Thời gian:** 0.000367 giây

**Các điều kiện kỹ thuật phải đúng:**

- `row.quantity_delta_pct == 0.35`
- `row.severity is Severity.CRITICAL`
- `row.anomaly_score >= 24`

### 54. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce04_unit_mismatch_is_flagged`

- **Tên dễ hiểu:** Khác đơn vị phải được cảnh báo
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Tên hạng mục giống nhau nhưng đơn vị không tương thích.
- **Ví dụ cụ thể:** Ví dụ phụ lục dùng “m”, nhà thầu dùng “100m” hoặc “bộ”.
- **Kết quả mong đợi:** Hệ thống gắn cờ UNIT_MISMATCH và không coi số lượng là so sánh trực tiếp.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống gắn cờ UNIT_MISMATCH và không coi số lượng là so sánh trực tiếp. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh kết luận sai khi 5 đơn vị “100m” thực chất bằng 500m.
- **Nếu test thất bại:** Khối lượng có thể bị hiểu sai 100 lần.
- **Vị trí:** `tests/test_s1_comparison_engine.py:145`
- **Thời gian:** 0.000416 giây

**Các điều kiện kỹ thuật phải đúng:**

- `row.severity is not Severity.OK`
- `any("đơn vị tính" in flag.lower() for flag in row.flags)`
- `any("khối lượng" in flag.lower() for flag in row.flags)`

### 55. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce05_missing_item_is_critical`

- **Tên dễ hiểu:** Hạng mục bị thiếu phải là lỗi nghiêm trọng
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Phụ lục có yêu cầu nhưng hồ sơ nhà thầu không có dòng tương ứng.
- **Ví dụ cụ thể:** Ví dụ PL01 có máy bơm P-01 nhưng file nhà thầu không tìm thấy P-01 hoặc tên tương đương.
- **Kết quả mong đợi:** Kết quả phải có trạng thái MISSING và mức CRITICAL.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Kết quả phải có trạng thái MISSING và mức CRITICAL. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng thấy ngay nhà thầu chưa chào đủ phạm vi.
- **Nếu test thất bại:** Hồ sơ thiếu hàng hóa có thể được đánh giá nhầm là đầy đủ.
- **Vị trí:** `tests/test_s1_comparison_engine.py:162`
- **Thời gian:** 0.000321 giây

**Các điều kiện kỹ thuật phải đúng:**

- `row.severity is Severity.CRITICAL`
- `any("thiếu hạng mục" in flag.lower() for flag in row.flags)`

### 56. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce06_extra_item_is_warning`

- **Tên dễ hiểu:** Hạng mục phát sinh phải được thông báo
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu thêm một dòng không có trong phụ lục.
- **Ví dụ cụ thể:** Ví dụ thêm “Chi phí vận chuyển” hoặc một thiết bị ngoài danh mục.
- **Kết quả mong đợi:** Kết quả ghi EXTRA_ITEM ở mức cảnh báo để người dùng xem xét.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Kết quả ghi EXTRA_ITEM ở mức cảnh báo để người dùng xem xét. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Phát hiện chi phí hoặc phạm vi bổ sung.
- **Nếu test thất bại:** Khoản phát sinh có thể bị bỏ qua trong tổng giá.
- **Vị trí:** `tests/test_s1_comparison_engine.py:172`
- **Thời gian:** 0.000333 giây

**Các điều kiện kỹ thuật phải đúng:**

- `row.severity is Severity.WARNING`
- `any("phát sinh ngoài" in flag.lower() for flag in row.flags)`

### 57. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce07_different_sheet_is_note_not_warning`

- **Tên dễ hiểu:** Khác sheet chỉ là ghi chú khi nội dung vẫn khớp
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Hai file đặt cùng hạng mục ở các sheet có tên khác nhau.
- **Ví dụ cụ thể:** Ví dụ PL01 đặt “Tủ điện LV-G.1” ở sheet “Hạ thế”, nhà thầu đặt ở sheet “HT điện”. Tên, đơn vị và số lượng vẫn giống.
- **Kết quả mong đợi:** Hệ thống ghép thành công và chỉ ghi “khác sheet”, không tăng mức cảnh báo.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống ghép thành công và chỉ ghi “khác sheet”, không tăng mức cảnh báo. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Cho phép nhà thầu tổ chức workbook khác mà không bị chấm lỗi oan.
- **Nếu test thất bại:** Báo cáo có thể cảnh báo hàng loạt chỉ vì cách chia sheet khác nhau.
- **Vị trí:** `tests/test_s1_comparison_engine.py:182`
- **Thời gian:** 0.000370 giây

**Các điều kiện kỹ thuật phải đúng:**

- `row.severity is Severity.OK`
- `row.anomaly_score == 0`
- `row.flags == []`
- `any("khác sheet" in note.lower() for note in row.notes)`

### 58. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce08_single_bidder_does_not_compare_price_against_pl01`

- **Tên dễ hiểu:** Không so giá một nhà thầu với PL01 khi PL01 không phải bảng giá tham chiếu
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Chỉ có một nhà thầu và phụ lục yêu cầu.
- **Ví dụ cụ thể:** Ví dụ nhà thầu báo 2 triệu; PL01 chỉ có khối lượng và mô tả.
- **Kết quả mong đợi:** Không sinh PRICE_HIGH/PRICE_LOW ở giai đoạn đối chiếu phụ lục.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Không sinh PRICE_HIGH/PRICE_LOW ở giai đoạn đối chiếu phụ lục. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Kết luận giá phải dựa trên dữ liệu hợp lý.
- **Nếu test thất bại:** Nhà thầu có thể bị báo giá bất thường sai căn cứ.
- **Vị trí:** `tests/test_s1_comparison_engine.py:205`
- **Thời gian:** 0.000339 giây

**Các điều kiện kỹ thuật phải đúng:**

- `row.price_delta is None`
- `row.price_delta_pct is None`
- `not any("đơn giá" in flag.lower() for flag in row.flags)`

### 59. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce09_price_outlier_is_flagged_only_in_peer_stage`

- **Tên dễ hiểu:** Giá lệch chỉ được cảnh báo khi so giữa nhiều nhà thầu
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Có ít nhất ba giá cho cùng một hạng mục.
- **Ví dụ cụ thể:** Ví dụ NT1 = 100, NT2 = 105, NT3 = 200.
- **Kết quả mong đợi:** Giai đoạn peer comparison gắn cờ cho 200; giai đoạn PL01 không tạo cờ giá này.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Giai đoạn peer comparison gắn cờ cho 200; giai đoạn PL01 không tạo cờ giá này. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tách rõ đối chiếu yêu cầu và phân tích giá thị trường nội bộ.
- **Nếu test thất bại:** Cảnh báo giá có thể xuất hiện sai bước hoặc bị tính lặp.
- **Vị trí:** `tests/test_s1_comparison_engine.py:227`
- **Thời gian:** 0.000799 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "prices": {
    "NT1": 100000000.0,
    "NT2": 105000000.0,
    "NT3": 95000000.0,
    "NT4": 200000000.0
  },
  "rows": []
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `all(row.severity is Severity.OK for row in rows)`
- `nt4.consensus_price is not None`
- `nt4.severity in {Severity.WARNING, Severity.CRITICAL}`
- `any("đơn giá tổng hợp" in flag.lower() for flag in nt4.flags)`

### 60. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce10_formula_error_is_critical`

- **Tên dễ hiểu:** Lỗi công thức #REF! phải là nghiêm trọng
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một ô công thức trong workbook bị hỏng tham chiếu.
- **Ví dụ cụ thể:** Ví dụ thành tiền là =D5*#REF! hoặc ô hiển thị #REF!.
- **Kết quả mong đợi:** Hệ thống tạo FORMULA_ERROR ở mức CRITICAL và chỉ rõ sheet/dòng/ô.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống tạo FORMULA_ERROR ở mức CRITICAL và chỉ rõ sheet/dòng/ô. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng biết số tiền có thể không đáng tin.
- **Nếu test thất bại:** Báo cáo tài chính có thể dùng số liệu sai do công thức lỗi.
- **Vị trí:** `tests/test_s1_comparison_engine.py:267`
- **Thời gian:** 0.000351 giây

**Các điều kiện kỹ thuật phải đúng:**

- `row.severity is Severity.CRITICAL`
- `any("#ref" in flag.lower() for flag in row.flags)`

### 61. ✅ `tests/test_s1_comparison_engine.py::test_s1_ce11_configurable_quantity_threshold_is_used`

- **Tên dễ hiểu:** Ngưỡng cảnh báo cấu hình phải được áp dụng thật
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Quản trị viên đổi ngưỡng chênh khối lượng.
- **Ví dụ cụ thể:** Ví dụ giảm ngưỡng cảnh báo từ 5% xuống 3%; dữ liệu lệch 4% giờ phải cảnh báo.
- **Kết quả mong đợi:** Kết quả thay đổi theo cấu hình mới, không dùng giá trị viết cứng trong code.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Kết quả thay đổi theo cấu hình mới, không dùng giá trị viết cứng trong code. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Mỗi dự án có thể đặt tiêu chuẩn kiểm tra riêng.
- **Nếu test thất bại:** Giao diện cho phép đổi ngưỡng nhưng kết quả không thay đổi.
- **Vị trí:** `tests/test_s1_comparison_engine.py:283`
- **Thời gian:** 0.000352 giây

**Các điều kiện kỹ thuật phải đúng:**

- `row.quantity_delta_pct == 0.04`
- `row.severity is Severity.WARNING`

### 62. ✅ `tests/test_s1_file_parser.py::test_s1_fi01_parse_valid_xlsx_and_preserve_source_row`

- **Tên dễ hiểu:** Đọc file XLSX hợp lệ và giữ đúng số dòng nguồn
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Workbook có một hạng mục ở một dòng xác định.
- **Ví dụ cụ thể:** Ví dụ “Máy bơm” nằm ở dòng Excel 12.
- **Kết quả mong đợi:** Sau khi parse, ItemRecord vẫn ghi row_number = 12 và đúng tên sheet.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Sau khi parse, ItemRecord vẫn ghi row_number = 12 và đúng tên sheet. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Khi cảnh báo, người dùng mở đúng dòng trong file gốc.
- **Nếu test thất bại:** Báo cáo chỉ sai vị trí, khiến người dùng khó kiểm tra.
- **Vị trí:** `tests/test_s1_file_parser.py:43`
- **Thời gian:** 0.006308 giây

**Các điều kiện kỹ thuật phải đúng:**

- `workbook.read_engine in {"calamine", "openpyxl"}`
- `len(workbook.items) == 1`
- `item.sheet == "Điện"`
- `item.row_number == 2`
- `item.item_code == "M-01"`
- `item.item_name == "Cáp điện Cu/XLPE 4x10"`
- `item.bid_quantity == 10`
- `item.unit_price_total == 100`
- `item.bid_amount == 1_000`

### 63. ✅ `tests/test_s1_file_parser.py::test_s1_fi02_detect_multi_level_header`

- **Tên dễ hiểu:** Tự tìm tiêu đề nhiều tầng
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** File có vài dòng tên công trình và nhóm cột trước dòng tiêu đề thật.
- **Ví dụ cụ thể:** Ví dụ dòng 5 có STT/Mô tả, dòng 6 có Đơn vị/Khối lượng/Đơn giá.
- **Kết quả mong đợi:** Parser xác định đúng vùng tiêu đề và cột dữ liệu.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Parser xác định đúng vùng tiêu đề và cột dữ liệu. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Không phụ thuộc cứng vào việc header luôn nằm ở dòng 1.
- **Nếu test thất bại:** Toàn bộ cột có thể bị đọc sai khi nhà thầu dùng mẫu khác.
- **Vị trí:** `tests/test_s1_file_parser.py:61`
- **Thời gian:** 0.000721 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "rows": [
    [
      "BÁO GIÁ",
      null,
      null,
      null,
      null,
      null
    ],
    [
      "Thông tin công việc",
      null,
      null,
      "Khối lượng",
      "Đơn giá",
      "Thành tiền"
    ],
    [
      "Mã hiệu",
      "Tên hạng mục",
      "ĐVT",
      "Nhà thầu",
      "Tổng hợp",
      "Nhà thầu"
    ],
    [
      "M-01",
      "Tủ điện tổng",
      "Tủ",
      1,
      1000000,
      1000000
    ]
  ]
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `start == 1`
- `end == 2`
- `"item_code" in fixed.values()`
- `"item_name" in fixed.values()`
- `"unit" in fixed.values()`
- `"bid_quantity" in fixed.values()`
- `"unit_price_total" in fixed.values()`
- `"bid_amount" in fixed.values()`

### 64. ✅ `tests/test_s1_file_parser.py::test_s1_fi03_calamine_matrix_preserves_raw_rows`

- **Tên dễ hiểu:** Ma trận Calamine giữ nguyên dữ liệu thô
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đọc sheet trước khi chuyển thành hạng mục chuẩn hóa.
- **Ví dụ cụ thể:** Ví dụ các ô trống, số 0 và chuỗi mô tả phải còn đúng vị trí.
- **Kết quả mong đợi:** Số hàng/cột và giá trị ô quan trọng không bị thay đổi.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Số hàng/cột và giá trị ô quan trọng không bị thay đổi. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Bảo đảm bước đọc nhanh không làm biến dạng dữ liệu.
- **Nếu test thất bại:** Lỗi phát sinh ngay từ bước đầu và lan sang toàn bộ phép so sánh.
- **Vị trí:** `tests/test_s1_file_parser.py:82`
- **Thời gian:** 0.004896 giây

**Các điều kiện kỹ thuật phải đúng:**

- `matrices.engine in {"calamine", "openpyxl"}`
- `len(matrices.sheets) == 1`
- `matrices.sheets[0].name == "Điện"`
- `matrices.sheets[0].rows[1][0] == "M-01"`

### 65. ✅ `tests/test_s1_file_parser.py::test_s1_fi04_formula_ref_is_detected`

- **Tên dễ hiểu:** Bộ đọc file phát hiện #REF!
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Trong file có công thức lỗi.
- **Ví dụ cụ thể:** Ví dụ ô F20 chứa =SUM(#REF!).
- **Kết quả mong đợi:** Danh sách lỗi phải chứa vị trí ô và loại lỗi tham chiếu.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Danh sách lỗi phải chứa vị trí ô và loại lỗi tham chiếu. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Cảnh báo được tạo trước khi dùng số liệu để so sánh.
- **Nếu test thất bại:** Số tổng sai có thể được sử dụng như dữ liệu hợp lệ.
- **Vị trí:** `tests/test_s1_file_parser.py:94`
- **Thời gian:** 0.006357 giây

**Các điều kiện kỹ thuật phải đúng:**

- `any(issue.kind == "FORMULA_ERROR" and issue.cell == "G2" for issue in scan.issues)`
- `any(issue["cell"] == "G2" for issue in workbook.formula_issues)`
- `any("#REF" in warning.upper() for warning in workbook.warnings)`

### 66. ✅ `tests/test_s1_file_parser.py::test_s1_fi05_four_workbooks_are_loaded_in_parallel`

- **Tên dễ hiểu:** Bốn file được đọc song song và đủ kết quả
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Hệ thống nhận nhiều hồ sơ cùng lúc.
- **Ví dụ cụ thể:** Ví dụ bốn file nhỏ được giao cho bốn tác vụ đọc.
- **Kết quả mong đợi:** Kết quả có đủ bốn workbook và nội dung giống cách đọc tuần tự.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Kết quả có đủ bốn workbook và nội dung giống cách đọc tuần tự. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tăng tốc mà vẫn an toàn dữ liệu.
- **Nếu test thất bại:** Có thể xảy ra race condition, thiếu file hoặc lẫn kết quả.
- **Vị trí:** `tests/test_s1_file_parser.py:106`
- **Thời gian:** 0.029649 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "specs": []
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `set(result) == {"0", "1", "2", "3"}`
- `all(book.read_engine in {"calamine", "openpyxl"} for book in result.values())`
- `[result[str(i)].items[0].unit_price_total for i in range(4)] == [100, 101, 102, 103]`

### 67. ✅ `tests/test_s1_file_parser.py::test_s1_fi06_invalid_extension_is_rejected`

- **Tên dễ hiểu:** Từ chối định dạng không được hỗ trợ
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Người dùng đổi tên hoặc tải file không phải Excel.
- **Ví dụ cụ thể:** Ví dụ tải file .txt, .exe hoặc .pdf vào chức năng chỉ nhận workbook.
- **Kết quả mong đợi:** Hệ thống dừng sớm và trả thông báo định dạng hợp lệ, không cố parse.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống dừng sớm và trả thông báo định dạng hợp lệ, không cố parse. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng nhận lỗi rõ ràng và hệ thống tránh xử lý dữ liệu nguy hiểm.
- **Nếu test thất bại:** Có thể crash, treo job hoặc tạo báo cáo rỗng khó hiểu.
- **Vị trí:** `tests/test_s1_file_parser.py:125`
- **Thời gian:** 0.001053 giây

### 68. ✅ `tests/test_s1_file_parser.py::test_s1_fi07_corrupt_xlsx_returns_clear_error`

- **Tên dễ hiểu:** File XLSX hỏng phải trả lỗi dễ hiểu
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đuôi file là .xlsx nhưng nội dung ZIP bên trong bị hỏng.
- **Ví dụ cụ thể:** Ví dụ file bị cắt khi tải lên hoặc chỉ chứa vài byte.
- **Kết quả mong đợi:** Hệ thống báo rõ file không đọc được và nêu tên file, không nuốt lỗi.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hệ thống báo rõ file không đọc được và nêu tên file, không nuốt lỗi. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Người dùng biết cần tải lại file nào.
- **Nếu test thất bại:** Job chỉ báo “failed” chung chung hoặc treo không kết thúc.
- **Vị trí:** `tests/test_s1_file_parser.py:133`
- **Thời gian:** 0.001079 giây

### 69. ✅ `tests/test_s1_file_parser.py::test_s1_fi08_duplicate_code_rows_are_preserved_and_flagged`

- **Tên dễ hiểu:** Dòng trùng mã không bị xóa trong bước parse
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một mã xuất hiện nhiều lần trong cùng sheet.
- **Ví dụ cụ thể:** Ví dụ hai dòng M-01 có mô tả hoặc khối lượng khác nhau.
- **Kết quả mong đợi:** Parser giữ cả hai, sau đó auditor gắn cờ trùng mã.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Parser giữ cả hai, sau đó auditor gắn cờ trùng mã. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Vừa bảo toàn hồ sơ gốc vừa hỗ trợ phát hiện sai sót.
- **Nếu test thất bại:** Một dòng có thể bị ghi đè và biến mất.
- **Vị trí:** `tests/test_s1_file_parser.py:141`
- **Thời gian:** 0.008946 giây

**Các điều kiện kỹ thuật phải đúng:**

- `len(comparable) == 2`
- `all(item.normalized_code == "M-01" for item in comparable)`
- `any("mã hiệu trùng" in flag.lower() for item in comparable for flag in item.data_quality_flags)`

### 70. ✅ `tests/test_s1_file_parser.py::test_s1_fi09_component_without_price_is_not_false_error`

- **Tên dễ hiểu:** Dòng nhóm không có giá không bị báo lỗi giả
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Một dòng là tiêu đề hoặc cấu phần không yêu cầu đơn giá.
- **Ví dụ cụ thể:** Ví dụ “I. PHẦN ĐIỆN” chỉ dùng để phân nhóm.
- **Kết quả mong đợi:** Parser phân loại đúng row_type và không tạo lỗi thiếu giá.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Parser phân loại đúng row_type và không tạo lỗi thiếu giá. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Giảm cảnh báo rác trong báo cáo.
- **Nếu test thất bại:** Người dùng phải xem hàng trăm cảnh báo không có ý nghĩa.
- **Vị trí:** `tests/test_s1_file_parser.py:159`
- **Thời gian:** 0.007272 giây

**Các điều kiện kỹ thuật phải đúng:**

- `"Thiếu đơn giá tổng hợp" not in component.data_quality_flags`
- `"Thiếu thành tiền" not in component.data_quality_flags`

### 71. ✅ `tests/test_s1_normalizer.py::test_s1_nr01_parse_vietnamese_and_international_numbers[(1.000)--1000.0]`

- **Tên dễ hiểu:** Chuẩn hóa số Việt Nam và quốc tế
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Cùng một giá trị có thể được viết theo nhiều quy ước.
- **Ví dụ cụ thể:** Ví dụ “1.234.567,89”, “1,234,567.89” và “1 234 567,89”.
- **Kết quả mong đợi:** Tất cả phải được chuyển thành số thực đúng để có thể tính toán.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải được chuyển thành số thực đúng để có thể tính toán. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh sai giá trị khi nhận file từ nhiều nhà thầu.
- **Nếu test thất bại:** Một đơn giá có thể bị hiểu sai hàng nghìn lần.
- **Vị trí:** `tests/test_s1_normalizer.py:59`
- **Thời gian:** 0.000483 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "(1.000)",
  "expected": -1000.0
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) == pytest.approx(expected)`

### 72. ✅ `tests/test_s1_normalizer.py::test_s1_nr01_parse_vietnamese_and_international_numbers[-0.5--0.5]`

- **Tên dễ hiểu:** Chuẩn hóa số Việt Nam và quốc tế
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Cùng một giá trị có thể được viết theo nhiều quy ước.
- **Ví dụ cụ thể:** Ví dụ “1.234.567,89”, “1,234,567.89” và “1 234 567,89”.
- **Kết quả mong đợi:** Tất cả phải được chuyển thành số thực đúng để có thể tính toán.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải được chuyển thành số thực đúng để có thể tính toán. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh sai giá trị khi nhận file từ nhiều nhà thầu.
- **Nếu test thất bại:** Một đơn giá có thể bị hiểu sai hàng nghìn lần.
- **Vị trí:** `tests/test_s1_normalizer.py:59`
- **Thời gian:** 0.000474 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "-0.5",
  "expected": -0.5
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) == pytest.approx(expected)`

### 73. ✅ `tests/test_s1_normalizer.py::test_s1_nr01_parse_vietnamese_and_international_numbers[0-0.0]`

- **Tên dễ hiểu:** Chuẩn hóa số Việt Nam và quốc tế
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Cùng một giá trị có thể được viết theo nhiều quy ước.
- **Ví dụ cụ thể:** Ví dụ “1.234.567,89”, “1,234,567.89” và “1 234 567,89”.
- **Kết quả mong đợi:** Tất cả phải được chuyển thành số thực đúng để có thể tính toán.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải được chuyển thành số thực đúng để có thể tính toán. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh sai giá trị khi nhận file từ nhiều nhà thầu.
- **Nếu test thất bại:** Một đơn giá có thể bị hiểu sai hàng nghìn lần.
- **Vị trí:** `tests/test_s1_normalizer.py:59`
- **Thời gian:** 0.000381 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": 0,
  "expected": 0.0
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) == pytest.approx(expected)`

### 74. ✅ `tests/test_s1_normalizer.py::test_s1_nr01_parse_vietnamese_and_international_numbers[1 234 567-1234567.0]`

- **Tên dễ hiểu:** Chuẩn hóa số Việt Nam và quốc tế
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Cùng một giá trị có thể được viết theo nhiều quy ước.
- **Ví dụ cụ thể:** Ví dụ “1.234.567,89”, “1,234,567.89” và “1 234 567,89”.
- **Kết quả mong đợi:** Tất cả phải được chuyển thành số thực đúng để có thể tính toán.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải được chuyển thành số thực đúng để có thể tính toán. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh sai giá trị khi nhận file từ nhiều nhà thầu.
- **Nếu test thất bại:** Một đơn giá có thể bị hiểu sai hàng nghìn lần.
- **Vị trí:** `tests/test_s1_normalizer.py:59`
- **Thời gian:** 0.000430 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "1 234 567",
  "expected": 1234567.0
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) == pytest.approx(expected)`

### 75. ✅ `tests/test_s1_normalizer.py::test_s1_nr01_parse_vietnamese_and_international_numbers[1,234,567.89-1234567.89]`

- **Tên dễ hiểu:** Chuẩn hóa số Việt Nam và quốc tế
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Cùng một giá trị có thể được viết theo nhiều quy ước.
- **Ví dụ cụ thể:** Ví dụ “1.234.567,89”, “1,234,567.89” và “1 234 567,89”.
- **Kết quả mong đợi:** Tất cả phải được chuyển thành số thực đúng để có thể tính toán.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải được chuyển thành số thực đúng để có thể tính toán. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh sai giá trị khi nhận file từ nhiều nhà thầu.
- **Nếu test thất bại:** Một đơn giá có thể bị hiểu sai hàng nghìn lần.
- **Vị trí:** `tests/test_s1_normalizer.py:59`
- **Thời gian:** 0.000446 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "1,234,567.89",
  "expected": 1234567.89
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) == pytest.approx(expected)`

### 76. ✅ `tests/test_s1_normalizer.py::test_s1_nr01_parse_vietnamese_and_international_numbers[1.234.567,89-1234567.89]`

- **Tên dễ hiểu:** Chuẩn hóa số Việt Nam và quốc tế
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Cùng một giá trị có thể được viết theo nhiều quy ước.
- **Ví dụ cụ thể:** Ví dụ “1.234.567,89”, “1,234,567.89” và “1 234 567,89”.
- **Kết quả mong đợi:** Tất cả phải được chuyển thành số thực đúng để có thể tính toán.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải được chuyển thành số thực đúng để có thể tính toán. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh sai giá trị khi nhận file từ nhiều nhà thầu.
- **Nếu test thất bại:** Một đơn giá có thể bị hiểu sai hàng nghìn lần.
- **Vị trí:** `tests/test_s1_normalizer.py:59`
- **Thời gian:** 0.000959 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "1.234.567,89",
  "expected": 1234567.89
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) == pytest.approx(expected)`

### 77. ✅ `tests/test_s1_normalizer.py::test_s1_nr01_parse_vietnamese_and_international_numbers[1.500.000 VN\u0110-1500000.0]`

- **Tên dễ hiểu:** Chuẩn hóa số Việt Nam và quốc tế
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Cùng một giá trị có thể được viết theo nhiều quy ước.
- **Ví dụ cụ thể:** Ví dụ “1.234.567,89”, “1,234,567.89” và “1 234 567,89”.
- **Kết quả mong đợi:** Tất cả phải được chuyển thành số thực đúng để có thể tính toán.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải được chuyển thành số thực đúng để có thể tính toán. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tránh sai giá trị khi nhận file từ nhiều nhà thầu.
- **Nếu test thất bại:** Một đơn giá có thể bị hiểu sai hàng nghìn lần.
- **Vị trí:** `tests/test_s1_normalizer.py:59`
- **Thời gian:** 0.000417 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "1.500.000 VNĐ",
  "expected": 1500000.0
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `parse_number(raw) == pytest.approx(expected)`

### 78. ✅ `tests/test_s1_normalizer.py::test_s1_nr02_normalize_square_metre_variants[M2]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét vuông
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị diện tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m2, M2, m², m^2, “mét vuông”.
- **Kết quả mong đợi:** Tất cả phải trở thành một giá trị chuẩn là m².
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành một giá trị chuẩn là m². Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Các dòng cùng đơn vị vẫn ghép được dù cách viết khác nhau.
- **Nếu test thất bại:** Hệ thống có thể báo sai khác đơn vị hoặc không ghép được hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:79`
- **Thời gian:** 0.000335 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "M2"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m²"`

### 79. ✅ `tests/test_s1_normalizer.py::test_s1_nr02_normalize_square_metre_variants[m 2]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét vuông
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị diện tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m2, M2, m², m^2, “mét vuông”.
- **Kết quả mong đợi:** Tất cả phải trở thành một giá trị chuẩn là m².
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành một giá trị chuẩn là m². Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Các dòng cùng đơn vị vẫn ghép được dù cách viết khác nhau.
- **Nếu test thất bại:** Hệ thống có thể báo sai khác đơn vị hoặc không ghép được hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:79`
- **Thời gian:** 0.000340 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "m 2"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m²"`

### 80. ✅ `tests/test_s1_normalizer.py::test_s1_nr02_normalize_square_metre_variants[m2]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét vuông
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị diện tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m2, M2, m², m^2, “mét vuông”.
- **Kết quả mong đợi:** Tất cả phải trở thành một giá trị chuẩn là m².
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành một giá trị chuẩn là m². Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Các dòng cùng đơn vị vẫn ghép được dù cách viết khác nhau.
- **Nếu test thất bại:** Hệ thống có thể báo sai khác đơn vị hoặc không ghép được hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:79`
- **Thời gian:** 0.000360 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "m2"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m²"`

### 81. ✅ `tests/test_s1_normalizer.py::test_s1_nr02_normalize_square_metre_variants[m\xb2]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét vuông
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị diện tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m2, M2, m², m^2, “mét vuông”.
- **Kết quả mong đợi:** Tất cả phải trở thành một giá trị chuẩn là m².
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành một giá trị chuẩn là m². Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Các dòng cùng đơn vị vẫn ghép được dù cách viết khác nhau.
- **Nếu test thất bại:** Hệ thống có thể báo sai khác đơn vị hoặc không ghép được hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:79`
- **Thời gian:** 0.000338 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "m²"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m²"`

### 82. ✅ `tests/test_s1_normalizer.py::test_s1_nr02_normalize_square_metre_variants[m\xe9t vu\xf4ng]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét vuông
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị diện tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m2, M2, m², m^2, “mét vuông”.
- **Kết quả mong đợi:** Tất cả phải trở thành một giá trị chuẩn là m².
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành một giá trị chuẩn là m². Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Các dòng cùng đơn vị vẫn ghép được dù cách viết khác nhau.
- **Nếu test thất bại:** Hệ thống có thể báo sai khác đơn vị hoặc không ghép được hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:79`
- **Thời gian:** 0.000355 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "mét vuông"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m²"`

### 83. ✅ `tests/test_s1_normalizer.py::test_s1_nr02_normalize_square_metre_variants[m^2]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét vuông
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị diện tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m2, M2, m², m^2, “mét vuông”.
- **Kết quả mong đợi:** Tất cả phải trở thành một giá trị chuẩn là m².
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành một giá trị chuẩn là m². Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Các dòng cùng đơn vị vẫn ghép được dù cách viết khác nhau.
- **Nếu test thất bại:** Hệ thống có thể báo sai khác đơn vị hoặc không ghép được hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:79`
- **Thời gian:** 0.000340 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "m^2"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m²"`

### 84. ✅ `tests/test_s1_normalizer.py::test_s1_nr02_normalize_square_metre_variants[met vuong]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét vuông
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị diện tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m2, M2, m², m^2, “mét vuông”.
- **Kết quả mong đợi:** Tất cả phải trở thành một giá trị chuẩn là m².
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành một giá trị chuẩn là m². Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Các dòng cùng đơn vị vẫn ghép được dù cách viết khác nhau.
- **Nếu test thất bại:** Hệ thống có thể báo sai khác đơn vị hoặc không ghép được hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:79`
- **Thời gian:** 0.000340 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "met vuong"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m²"`

### 85. ✅ `tests/test_s1_normalizer.py::test_s1_nr03_normalize_cubic_metre_variants[M3]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét khối
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị thể tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m3, M3, m³, m^3, “mét khối”.
- **Kết quả mong đợi:** Tất cả phải trở thành m³.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành m³. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Dữ liệu thể tích từ nhiều nguồn được so sánh thống nhất.
- **Nếu test thất bại:** Có thể phát sinh cảnh báo đơn vị giả.
- **Vị trí:** `tests/test_s1_normalizer.py:88`
- **Thời gian:** 0.000331 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "M3"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m³"`

### 86. ✅ `tests/test_s1_normalizer.py::test_s1_nr03_normalize_cubic_metre_variants[m 3]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét khối
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị thể tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m3, M3, m³, m^3, “mét khối”.
- **Kết quả mong đợi:** Tất cả phải trở thành m³.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành m³. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Dữ liệu thể tích từ nhiều nguồn được so sánh thống nhất.
- **Nếu test thất bại:** Có thể phát sinh cảnh báo đơn vị giả.
- **Vị trí:** `tests/test_s1_normalizer.py:88`
- **Thời gian:** 0.000342 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "m 3"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m³"`

### 87. ✅ `tests/test_s1_normalizer.py::test_s1_nr03_normalize_cubic_metre_variants[m3]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét khối
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị thể tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m3, M3, m³, m^3, “mét khối”.
- **Kết quả mong đợi:** Tất cả phải trở thành m³.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành m³. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Dữ liệu thể tích từ nhiều nguồn được so sánh thống nhất.
- **Nếu test thất bại:** Có thể phát sinh cảnh báo đơn vị giả.
- **Vị trí:** `tests/test_s1_normalizer.py:88`
- **Thời gian:** 0.000339 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "m3"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m³"`

### 88. ✅ `tests/test_s1_normalizer.py::test_s1_nr03_normalize_cubic_metre_variants[m\xb3]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét khối
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị thể tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m3, M3, m³, m^3, “mét khối”.
- **Kết quả mong đợi:** Tất cả phải trở thành m³.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành m³. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Dữ liệu thể tích từ nhiều nguồn được so sánh thống nhất.
- **Nếu test thất bại:** Có thể phát sinh cảnh báo đơn vị giả.
- **Vị trí:** `tests/test_s1_normalizer.py:88`
- **Thời gian:** 0.000351 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "m³"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m³"`

### 89. ✅ `tests/test_s1_normalizer.py::test_s1_nr03_normalize_cubic_metre_variants[m\xe9t kh\u1ed1i]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét khối
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị thể tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m3, M3, m³, m^3, “mét khối”.
- **Kết quả mong đợi:** Tất cả phải trở thành m³.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành m³. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Dữ liệu thể tích từ nhiều nguồn được so sánh thống nhất.
- **Nếu test thất bại:** Có thể phát sinh cảnh báo đơn vị giả.
- **Vị trí:** `tests/test_s1_normalizer.py:88`
- **Thời gian:** 0.000352 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "mét khối"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m³"`

### 90. ✅ `tests/test_s1_normalizer.py::test_s1_nr03_normalize_cubic_metre_variants[m^3]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét khối
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị thể tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m3, M3, m³, m^3, “mét khối”.
- **Kết quả mong đợi:** Tất cả phải trở thành m³.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành m³. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Dữ liệu thể tích từ nhiều nguồn được so sánh thống nhất.
- **Nếu test thất bại:** Có thể phát sinh cảnh báo đơn vị giả.
- **Vị trí:** `tests/test_s1_normalizer.py:88`
- **Thời gian:** 0.000337 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "m^3"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m³"`

### 91. ✅ `tests/test_s1_normalizer.py::test_s1_nr03_normalize_cubic_metre_variants[met khoi]`

- **Tên dễ hiểu:** Chuẩn hóa mọi cách viết mét khối
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Đơn vị thể tích có nhiều kiểu ký hiệu.
- **Ví dụ cụ thể:** Ví dụ m3, M3, m³, m^3, “mét khối”.
- **Kết quả mong đợi:** Tất cả phải trở thành m³.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Tất cả phải trở thành m³. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Dữ liệu thể tích từ nhiều nguồn được so sánh thống nhất.
- **Nếu test thất bại:** Có thể phát sinh cảnh báo đơn vị giả.
- **Vị trí:** `tests/test_s1_normalizer.py:88`
- **Thời gian:** 0.000328 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "met khoi"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == "m³"`

### 92. ✅ `tests/test_s1_normalizer.py::test_s1_nr04_normalize_common_units[100m-100m]`

- **Tên dễ hiểu:** Chuẩn hóa các đơn vị phổ biến
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu có thể viết “chiếc”, “cái”, “BỘ”, “thiết bị” hoặc không dấu.
- **Ví dụ cụ thể:** Ví dụ “chiếc” được quy về “cái”, “BỘ” được quy về “bộ”.
- **Kết quả mong đợi:** Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tăng khả năng ghép đúng hạng mục.
- **Nếu test thất bại:** Cùng một đơn vị nhưng khác cách viết có thể bị hiểu là không khớp.
- **Vị trí:** `tests/test_s1_normalizer.py:97`
- **Thời gian:** 0.000360 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "100m",
  "expected": "100m"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == expected`

### 93. ✅ `tests/test_s1_normalizer.py::test_s1_nr04_normalize_common_units[B\u1ed8-b\u1ed9]`

- **Tên dễ hiểu:** Chuẩn hóa các đơn vị phổ biến
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu có thể viết “chiếc”, “cái”, “BỘ”, “thiết bị” hoặc không dấu.
- **Ví dụ cụ thể:** Ví dụ “chiếc” được quy về “cái”, “BỘ” được quy về “bộ”.
- **Kết quả mong đợi:** Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tăng khả năng ghép đúng hạng mục.
- **Nếu test thất bại:** Cùng một đơn vị nhưng khác cách viết có thể bị hiểu là không khớp.
- **Vị trí:** `tests/test_s1_normalizer.py:97`
- **Thời gian:** 0.000376 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "BỘ",
  "expected": "bộ"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == expected`

### 94. ✅ `tests/test_s1_normalizer.py::test_s1_nr04_normalize_common_units[C\xe1i-c\xe1i]`

- **Tên dễ hiểu:** Chuẩn hóa các đơn vị phổ biến
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu có thể viết “chiếc”, “cái”, “BỘ”, “thiết bị” hoặc không dấu.
- **Ví dụ cụ thể:** Ví dụ “chiếc” được quy về “cái”, “BỘ” được quy về “bộ”.
- **Kết quả mong đợi:** Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tăng khả năng ghép đúng hạng mục.
- **Nếu test thất bại:** Cùng một đơn vị nhưng khác cách viết có thể bị hiểu là không khớp.
- **Vị trí:** `tests/test_s1_normalizer.py:97`
- **Thời gian:** 0.000355 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "Cái",
  "expected": "cái"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == expected`

### 95. ✅ `tests/test_s1_normalizer.py::test_s1_nr04_normalize_common_units[T\u1ea5n-t\u1ea5n]`

- **Tên dễ hiểu:** Chuẩn hóa các đơn vị phổ biến
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu có thể viết “chiếc”, “cái”, “BỘ”, “thiết bị” hoặc không dấu.
- **Ví dụ cụ thể:** Ví dụ “chiếc” được quy về “cái”, “BỘ” được quy về “bộ”.
- **Kết quả mong đợi:** Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tăng khả năng ghép đúng hạng mục.
- **Nếu test thất bại:** Cùng một đơn vị nhưng khác cách viết có thể bị hiểu là không khớp.
- **Vị trí:** `tests/test_s1_normalizer.py:97`
- **Thời gian:** 0.000412 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "Tấn",
  "expected": "tấn"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == expected`

### 96. ✅ `tests/test_s1_normalizer.py::test_s1_nr04_normalize_common_units[chi\u1ebfc-c\xe1i]`

- **Tên dễ hiểu:** Chuẩn hóa các đơn vị phổ biến
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu có thể viết “chiếc”, “cái”, “BỘ”, “thiết bị” hoặc không dấu.
- **Ví dụ cụ thể:** Ví dụ “chiếc” được quy về “cái”, “BỘ” được quy về “bộ”.
- **Kết quả mong đợi:** Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tăng khả năng ghép đúng hạng mục.
- **Nếu test thất bại:** Cùng một đơn vị nhưng khác cách viết có thể bị hiểu là không khớp.
- **Vị trí:** `tests/test_s1_normalizer.py:97`
- **Thời gian:** 0.000367 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "chiếc",
  "expected": "cái"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == expected`

### 97. ✅ `tests/test_s1_normalizer.py::test_s1_nr04_normalize_common_units[kg-kg]`

- **Tên dễ hiểu:** Chuẩn hóa các đơn vị phổ biến
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu có thể viết “chiếc”, “cái”, “BỘ”, “thiết bị” hoặc không dấu.
- **Ví dụ cụ thể:** Ví dụ “chiếc” được quy về “cái”, “BỘ” được quy về “bộ”.
- **Kết quả mong đợi:** Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tăng khả năng ghép đúng hạng mục.
- **Nếu test thất bại:** Cùng một đơn vị nhưng khác cách viết có thể bị hiểu là không khớp.
- **Vị trí:** `tests/test_s1_normalizer.py:97`
- **Thời gian:** 0.000373 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "kg",
  "expected": "kg"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == expected`

### 98. ✅ `tests/test_s1_normalizer.py::test_s1_nr04_normalize_common_units[m\xe9t-m]`

- **Tên dễ hiểu:** Chuẩn hóa các đơn vị phổ biến
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu có thể viết “chiếc”, “cái”, “BỘ”, “thiết bị” hoặc không dấu.
- **Ví dụ cụ thể:** Ví dụ “chiếc” được quy về “cái”, “BỘ” được quy về “bộ”.
- **Kết quả mong đợi:** Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tăng khả năng ghép đúng hạng mục.
- **Nếu test thất bại:** Cùng một đơn vị nhưng khác cách viết có thể bị hiểu là không khớp.
- **Vị trí:** `tests/test_s1_normalizer.py:97`
- **Thời gian:** 0.000383 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "mét",
  "expected": "m"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == expected`

### 99. ✅ `tests/test_s1_normalizer.py::test_s1_nr04_normalize_common_units[t\u1ee7-t\u1ee7]`

- **Tên dễ hiểu:** Chuẩn hóa các đơn vị phổ biến
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu có thể viết “chiếc”, “cái”, “BỘ”, “thiết bị” hoặc không dấu.
- **Ví dụ cụ thể:** Ví dụ “chiếc” được quy về “cái”, “BỘ” được quy về “bộ”.
- **Kết quả mong đợi:** Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tăng khả năng ghép đúng hạng mục.
- **Nếu test thất bại:** Cùng một đơn vị nhưng khác cách viết có thể bị hiểu là không khớp.
- **Vị trí:** `tests/test_s1_normalizer.py:97`
- **Thời gian:** 0.000376 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "tủ",
  "expected": "tủ"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == expected`

### 100. ✅ `tests/test_s1_normalizer.py::test_s1_nr04_normalize_common_units[thi\u1ebft b\u1ecb-thi\u1ebft b\u1ecb]`

- **Tên dễ hiểu:** Chuẩn hóa các đơn vị phổ biến
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhà thầu có thể viết “chiếc”, “cái”, “BỘ”, “thiết bị” hoặc không dấu.
- **Ví dụ cụ thể:** Ví dụ “chiếc” được quy về “cái”, “BỘ” được quy về “bộ”.
- **Kết quả mong đợi:** Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi nhóm đồng nghĩa phải trả về cùng một đơn vị chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tăng khả năng ghép đúng hạng mục.
- **Nếu test thất bại:** Cùng một đơn vị nhưng khác cách viết có thể bị hiểu là không khớp.
- **Vị trí:** `tests/test_s1_normalizer.py:97`
- **Thời gian:** 0.000395 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "thiết bị",
  "expected": "thiết bị"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_unit(raw) == expected`

### 101. ✅ `tests/test_s1_normalizer.py::test_s1_nr05_normalize_item_codes[ AB_12 -AB-12]`

- **Tên dễ hiểu:** Chuẩn hóa mã vật tư
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Mã có thể chứa dấu chấm, gạch chéo hoặc khoảng trắng.
- **Ví dụ cụ thể:** Ví dụ M01, M.01 và M/01 đều trở thành M-01; ô công thức =A1 không được xem là mã.
- **Kết quả mong đợi:** Mã tương đương có cùng dạng chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mã tương đương có cùng dạng chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** So khớp mã ổn định giữa các biểu mẫu.
- **Nếu test thất bại:** Một hạng mục có thể bị coi là thiếu chỉ vì cách viết mã khác.
- **Vị trí:** `tests/test_s1_normalizer.py:116`
- **Thời gian:** 0.000505 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": " AB_12 ",
  "expected": "AB-12"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_code(raw) == expected`

### 102. ✅ `tests/test_s1_normalizer.py::test_s1_nr05_normalize_item_codes[-]`

- **Tên dễ hiểu:** Chuẩn hóa mã vật tư
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Mã có thể chứa dấu chấm, gạch chéo hoặc khoảng trắng.
- **Ví dụ cụ thể:** Ví dụ M01, M.01 và M/01 đều trở thành M-01; ô công thức =A1 không được xem là mã.
- **Kết quả mong đợi:** Mã tương đương có cùng dạng chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mã tương đương có cùng dạng chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** So khớp mã ổn định giữa các biểu mẫu.
- **Nếu test thất bại:** Một hạng mục có thể bị coi là thiếu chỉ vì cách viết mã khác.
- **Vị trí:** `tests/test_s1_normalizer.py:116`
- **Thời gian:** 0.000380 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "",
  "expected": ""
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_code(raw) == expected`

### 103. ✅ `tests/test_s1_normalizer.py::test_s1_nr05_normalize_item_codes[=A1-]`

- **Tên dễ hiểu:** Chuẩn hóa mã vật tư
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Mã có thể chứa dấu chấm, gạch chéo hoặc khoảng trắng.
- **Ví dụ cụ thể:** Ví dụ M01, M.01 và M/01 đều trở thành M-01; ô công thức =A1 không được xem là mã.
- **Kết quả mong đợi:** Mã tương đương có cùng dạng chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mã tương đương có cùng dạng chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** So khớp mã ổn định giữa các biểu mẫu.
- **Nếu test thất bại:** Một hạng mục có thể bị coi là thiếu chỉ vì cách viết mã khác.
- **Vị trí:** `tests/test_s1_normalizer.py:116`
- **Thời gian:** 0.000364 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "=A1",
  "expected": ""
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_code(raw) == expected`

### 104. ✅ `tests/test_s1_normalizer.py::test_s1_nr05_normalize_item_codes[M.01-M-01]`

- **Tên dễ hiểu:** Chuẩn hóa mã vật tư
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Mã có thể chứa dấu chấm, gạch chéo hoặc khoảng trắng.
- **Ví dụ cụ thể:** Ví dụ M01, M.01 và M/01 đều trở thành M-01; ô công thức =A1 không được xem là mã.
- **Kết quả mong đợi:** Mã tương đương có cùng dạng chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mã tương đương có cùng dạng chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** So khớp mã ổn định giữa các biểu mẫu.
- **Nếu test thất bại:** Một hạng mục có thể bị coi là thiếu chỉ vì cách viết mã khác.
- **Vị trí:** `tests/test_s1_normalizer.py:116`
- **Thời gian:** 0.000386 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "M.01",
  "expected": "M-01"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_code(raw) == expected`

### 105. ✅ `tests/test_s1_normalizer.py::test_s1_nr05_normalize_item_codes[M/01-M-01]`

- **Tên dễ hiểu:** Chuẩn hóa mã vật tư
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Mã có thể chứa dấu chấm, gạch chéo hoặc khoảng trắng.
- **Ví dụ cụ thể:** Ví dụ M01, M.01 và M/01 đều trở thành M-01; ô công thức =A1 không được xem là mã.
- **Kết quả mong đợi:** Mã tương đương có cùng dạng chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mã tương đương có cùng dạng chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** So khớp mã ổn định giữa các biểu mẫu.
- **Nếu test thất bại:** Một hạng mục có thể bị coi là thiếu chỉ vì cách viết mã khác.
- **Vị trí:** `tests/test_s1_normalizer.py:116`
- **Thời gian:** 0.000378 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "M/01",
  "expected": "M-01"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_code(raw) == expected`

### 106. ✅ `tests/test_s1_normalizer.py::test_s1_nr05_normalize_item_codes[M01-M-01]`

- **Tên dễ hiểu:** Chuẩn hóa mã vật tư
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Mã có thể chứa dấu chấm, gạch chéo hoặc khoảng trắng.
- **Ví dụ cụ thể:** Ví dụ M01, M.01 và M/01 đều trở thành M-01; ô công thức =A1 không được xem là mã.
- **Kết quả mong đợi:** Mã tương đương có cùng dạng chuẩn.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mã tương đương có cùng dạng chuẩn. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** So khớp mã ổn định giữa các biểu mẫu.
- **Nếu test thất bại:** Một hạng mục có thể bị coi là thiếu chỉ vì cách viết mã khác.
- **Vị trí:** `tests/test_s1_normalizer.py:116`
- **Thời gian:** 0.000367 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "M01",
  "expected": "M-01"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_code(raw) == expected`

### 107. ✅ `tests/test_s1_normalizer.py::test_s1_nr06_normalize_stt[ A-01 -A-01]`

- **Tên dễ hiểu:** Chuẩn hóa số thứ tự
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** STT có khoảng trắng, chữ cái hoặc ký hiệu phân cấp.
- **Ví dụ cụ thể:** Ví dụ “ I.1 ” trở thành I.1; công thức =ROW()-1 được bỏ qua.
- **Kết quả mong đợi:** STT hợp lệ được làm sạch, công thức không bị dùng làm khóa ghép.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: STT hợp lệ được làm sạch, công thức không bị dùng làm khóa ghép. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Giảm ghép nhầm dựa trên số thứ tự giả.
- **Nếu test thất bại:** Công thức Excel có thể bị hiểu nhầm là mã hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:132`
- **Thời gian:** 0.000373 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": " A-01 ",
  "expected": "A-01"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_stt(raw) == expected`

### 108. ✅ `tests/test_s1_normalizer.py::test_s1_nr06_normalize_stt[ I.1 -I.1]`

- **Tên dễ hiểu:** Chuẩn hóa số thứ tự
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** STT có khoảng trắng, chữ cái hoặc ký hiệu phân cấp.
- **Ví dụ cụ thể:** Ví dụ “ I.1 ” trở thành I.1; công thức =ROW()-1 được bỏ qua.
- **Kết quả mong đợi:** STT hợp lệ được làm sạch, công thức không bị dùng làm khóa ghép.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: STT hợp lệ được làm sạch, công thức không bị dùng làm khóa ghép. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Giảm ghép nhầm dựa trên số thứ tự giả.
- **Nếu test thất bại:** Công thức Excel có thể bị hiểu nhầm là mã hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:132`
- **Thời gian:** 0.000378 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": " I.1 ",
  "expected": "I.1"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_stt(raw) == expected`

### 109. ✅ `tests/test_s1_normalizer.py::test_s1_nr06_normalize_stt[-]`

- **Tên dễ hiểu:** Chuẩn hóa số thứ tự
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** STT có khoảng trắng, chữ cái hoặc ký hiệu phân cấp.
- **Ví dụ cụ thể:** Ví dụ “ I.1 ” trở thành I.1; công thức =ROW()-1 được bỏ qua.
- **Kết quả mong đợi:** STT hợp lệ được làm sạch, công thức không bị dùng làm khóa ghép.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: STT hợp lệ được làm sạch, công thức không bị dùng làm khóa ghép. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Giảm ghép nhầm dựa trên số thứ tự giả.
- **Nếu test thất bại:** Công thức Excel có thể bị hiểu nhầm là mã hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:132`
- **Thời gian:** 0.000358 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "",
  "expected": ""
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_stt(raw) == expected`

### 110. ✅ `tests/test_s1_normalizer.py::test_s1_nr06_normalize_stt[1.2.3-1.2.3]`

- **Tên dễ hiểu:** Chuẩn hóa số thứ tự
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** STT có khoảng trắng, chữ cái hoặc ký hiệu phân cấp.
- **Ví dụ cụ thể:** Ví dụ “ I.1 ” trở thành I.1; công thức =ROW()-1 được bỏ qua.
- **Kết quả mong đợi:** STT hợp lệ được làm sạch, công thức không bị dùng làm khóa ghép.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: STT hợp lệ được làm sạch, công thức không bị dùng làm khóa ghép. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Giảm ghép nhầm dựa trên số thứ tự giả.
- **Nếu test thất bại:** Công thức Excel có thể bị hiểu nhầm là mã hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:132`
- **Thời gian:** 0.000368 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "1.2.3",
  "expected": "1.2.3"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_stt(raw) == expected`

### 111. ✅ `tests/test_s1_normalizer.py::test_s1_nr06_normalize_stt[=ROW()-1-]`

- **Tên dễ hiểu:** Chuẩn hóa số thứ tự
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** STT có khoảng trắng, chữ cái hoặc ký hiệu phân cấp.
- **Ví dụ cụ thể:** Ví dụ “ I.1 ” trở thành I.1; công thức =ROW()-1 được bỏ qua.
- **Kết quả mong đợi:** STT hợp lệ được làm sạch, công thức không bị dùng làm khóa ghép.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: STT hợp lệ được làm sạch, công thức không bị dùng làm khóa ghép. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Giảm ghép nhầm dựa trên số thứ tự giả.
- **Nếu test thất bại:** Công thức Excel có thể bị hiểu nhầm là mã hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:132`
- **Thời gian:** 0.000362 giây

**Tham số thực tế của lần test này:**

```json
{
  "raw": "=ROW()-1",
  "expected": ""
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_stt(raw) == expected`

### 112. ✅ `tests/test_s1_normalizer.py::test_s1_nr07_normalize_vietnamese_names_and_symbols[C\xe1p \u0111i\u1ec7n 3\xd72.5 mm\xb2-cap dien 3x2 5 mm2]`

- **Tên dễ hiểu:** Chuẩn hóa tên có dấu và ký hiệu kỹ thuật
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Tên vật tư có thể viết có dấu/không dấu và dùng ký hiệu ×, ².
- **Ví dụ cụ thể:** Ví dụ “Cáp điện 3×2.5 mm²” phải cùng khóa với “cap dien 3x2 5 mm2”.
- **Kết quả mong đợi:** Hai chuỗi biểu diễn cùng vật tư phải cho kết quả chuẩn hóa giống nhau.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hai chuỗi biểu diễn cùng vật tư phải cho kết quả chuẩn hóa giống nhau. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tên kỹ thuật vẫn ghép được dù định dạng khác.
- **Nếu test thất bại:** Ký tự mũ hoặc dấu nhân bị mất có thể làm ghép sai vật tư.
- **Vị trí:** `tests/test_s1_normalizer.py:147`
- **Thời gian:** 0.000418 giây

**Tham số thực tế của lần test này:**

```json
{
  "left": "Cáp điện 3×2.5 mm²",
  "right": "cap dien 3x2 5 mm2"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_name(left) == normalize_name(right)`

### 113. ✅ `tests/test_s1_normalizer.py::test_s1_nr07_normalize_vietnamese_names_and_symbols[M\xe1y b\u01a1m n\u01b0\u1edbc sinh ho\u1ea1t-MAY BOM NUOC SINH HOAT]`

- **Tên dễ hiểu:** Chuẩn hóa tên có dấu và ký hiệu kỹ thuật
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Tên vật tư có thể viết có dấu/không dấu và dùng ký hiệu ×, ².
- **Ví dụ cụ thể:** Ví dụ “Cáp điện 3×2.5 mm²” phải cùng khóa với “cap dien 3x2 5 mm2”.
- **Kết quả mong đợi:** Hai chuỗi biểu diễn cùng vật tư phải cho kết quả chuẩn hóa giống nhau.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hai chuỗi biểu diễn cùng vật tư phải cho kết quả chuẩn hóa giống nhau. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tên kỹ thuật vẫn ghép được dù định dạng khác.
- **Nếu test thất bại:** Ký tự mũ hoặc dấu nhân bị mất có thể làm ghép sai vật tư.
- **Vị trí:** `tests/test_s1_normalizer.py:147`
- **Thời gian:** 0.000408 giây

**Tham số thực tế của lần test này:**

```json
{
  "left": "Máy bơm nước sinh hoạt",
  "right": "MAY BOM NUOC SINH HOAT"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_name(left) == normalize_name(right)`

### 114. ✅ `tests/test_s1_normalizer.py::test_s1_nr07_normalize_vietnamese_names_and_symbols[T\u1ee7 \u0111i\u1ec7n LV-G.1 + LV-G.2-TU DIEN LV G 1 LV G 2]`

- **Tên dễ hiểu:** Chuẩn hóa tên có dấu và ký hiệu kỹ thuật
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Tên vật tư có thể viết có dấu/không dấu và dùng ký hiệu ×, ².
- **Ví dụ cụ thể:** Ví dụ “Cáp điện 3×2.5 mm²” phải cùng khóa với “cap dien 3x2 5 mm2”.
- **Kết quả mong đợi:** Hai chuỗi biểu diễn cùng vật tư phải cho kết quả chuẩn hóa giống nhau.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hai chuỗi biểu diễn cùng vật tư phải cho kết quả chuẩn hóa giống nhau. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tên kỹ thuật vẫn ghép được dù định dạng khác.
- **Nếu test thất bại:** Ký tự mũ hoặc dấu nhân bị mất có thể làm ghép sai vật tư.
- **Vị trí:** `tests/test_s1_normalizer.py:147`
- **Thời gian:** 0.000417 giây

**Tham số thực tế của lần test này:**

```json
{
  "left": "Tủ điện LV-G.1 + LV-G.2",
  "right": "TU DIEN LV G 1 LV G 2"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `normalize_name(left) == normalize_name(right)`

### 115. ✅ `tests/test_s1_normalizer.py::test_s1_nr08_safe_amount_respects_explicit_zero`

- **Tên dễ hiểu:** Giữ nguyên thành tiền 0 khi 0 là dữ liệu thật
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Ô thành tiền có thể là 0 hoặc để trống.
- **Ví dụ cụ thể:** Ví dụ quantity=2, price=100, amount=0 phải giữ 0; amount trống mới tính thành 200.
- **Kết quả mong đợi:** Không thay số 0 bằng phép nhân dự phòng.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Không thay số 0 bằng phép nhân dự phòng. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Tôn trọng dữ liệu gốc và phân biệt 0 với thiếu dữ liệu.
- **Nếu test thất bại:** Tổng tiền có thể bị tự động tăng sai.
- **Vị trí:** `tests/test_s1_normalizer.py:163`
- **Thời gian:** 0.000268 giây

**Các điều kiện kỹ thuật phải đúng:**

- `safe_amount(2, 100, 0) == 0`
- `safe_amount(2, 100, None) == 200`

### 116. ✅ `tests/test_s1_normalizer.py::test_s1_nr09_percent_delta[100-100-0.0]`

- **Tên dễ hiểu:** Tính đúng phần trăm chênh lệch
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** So sánh giá trị nhà thầu với giá trị chuẩn.
- **Ví dụ cụ thể:** Ví dụ từ 100 lên 108 là +8%; từ 100 xuống 95 là -5%.
- **Kết quả mong đợi:** Hàm trả đúng dấu và đúng tỷ lệ.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm trả đúng dấu và đúng tỷ lệ. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Mức cảnh báo dựa trên con số chính xác.
- **Nếu test thất bại:** Hệ thống có thể phân loại sai WARNING/CRITICAL.
- **Vị trí:** `tests/test_s1_normalizer.py:169`
- **Thời gian:** 0.000393 giây

**Tham số thực tế của lần test này:**

```json
{
  "baseline": 100,
  "candidate": 100,
  "expected": 0.0
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `percent_delta(baseline, candidate) == pytest.approx(expected)`

### 117. ✅ `tests/test_s1_normalizer.py::test_s1_nr09_percent_delta[100-108-0.08]`

- **Tên dễ hiểu:** Tính đúng phần trăm chênh lệch
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** So sánh giá trị nhà thầu với giá trị chuẩn.
- **Ví dụ cụ thể:** Ví dụ từ 100 lên 108 là +8%; từ 100 xuống 95 là -5%.
- **Kết quả mong đợi:** Hàm trả đúng dấu và đúng tỷ lệ.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm trả đúng dấu và đúng tỷ lệ. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Mức cảnh báo dựa trên con số chính xác.
- **Nếu test thất bại:** Hệ thống có thể phân loại sai WARNING/CRITICAL.
- **Vị trí:** `tests/test_s1_normalizer.py:169`
- **Thời gian:** 0.000434 giây

**Tham số thực tế của lần test này:**

```json
{
  "baseline": 100,
  "candidate": 108,
  "expected": 0.08
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `percent_delta(baseline, candidate) == pytest.approx(expected)`

### 118. ✅ `tests/test_s1_normalizer.py::test_s1_nr09_percent_delta[100-95--0.05]`

- **Tên dễ hiểu:** Tính đúng phần trăm chênh lệch
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** So sánh giá trị nhà thầu với giá trị chuẩn.
- **Ví dụ cụ thể:** Ví dụ từ 100 lên 108 là +8%; từ 100 xuống 95 là -5%.
- **Kết quả mong đợi:** Hàm trả đúng dấu và đúng tỷ lệ.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Hàm trả đúng dấu và đúng tỷ lệ. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Mức cảnh báo dựa trên con số chính xác.
- **Nếu test thất bại:** Hệ thống có thể phân loại sai WARNING/CRITICAL.
- **Vị trí:** `tests/test_s1_normalizer.py:169`
- **Thời gian:** 0.000406 giây

**Tham số thực tế của lần test này:**

```json
{
  "baseline": 100,
  "candidate": 95,
  "expected": -0.05
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `percent_delta(baseline, candidate) == pytest.approx(expected)`

### 119. ✅ `tests/test_s1_normalizer.py::test_s1_nr10_hybrid_match_is_one_to_one`

- **Tên dễ hiểu:** Ghép hạng mục một-một
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Nhiều dòng có tên gần nhau.
- **Ví dụ cụ thể:** Ví dụ hai dòng chuẩn và hai dòng nhà thầu phải tạo đúng hai cặp, không dùng một dòng hai lần.
- **Kết quả mong đợi:** Mỗi dòng chỉ xuất hiện trong tối đa một cặp ghép.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Mỗi dòng chỉ xuất hiện trong tối đa một cặp ghép. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Không đếm lặp dữ liệu.
- **Nếu test thất bại:** Một giá hoặc khối lượng có thể bị gán cho nhiều hạng mục.
- **Vị trí:** `tests/test_s1_normalizer.py:186`
- **Thời gian:** 0.000508 giây

**Các điều kiện kỹ thuật phải đúng:**

- `len(paired) == 2`
- `len({match.reference_index for match in paired}) == 2`
- `len({match.candidate_index for match in paired}) == 2`

### 120. ✅ `tests/test_s1_normalizer.py::test_s1_nr11_exact_name_can_match_across_different_sheets`

- **Tên dễ hiểu:** Tên chính xác vẫn ghép được khi khác sheet
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Hai workbook đặt cùng vật tư ở hai sheet khác tên.
- **Ví dụ cụ thể:** Ví dụ tủ LV-G.1…LV-G.6 nằm ở “PHẦN TỦ HẠ THẾ” và “HT điện”.
- **Kết quả mong đợi:** Matcher tạo EXACT_NAME với điểm cao và ghi chú khác sheet.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Matcher tạo EXACT_NAME với điểm cao và ghi chú khác sheet. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Cấu trúc workbook không cản trở đối chiếu.
- **Nếu test thất bại:** Hạng mục đúng có thể bị báo thiếu.
- **Vị trí:** `tests/test_s1_normalizer.py:228`
- **Thời gian:** 0.000423 giây

**Dữ liệu ví dụ lấy trực tiếp từ code test:**

```json
{
  "item_name": "Tủ điện LV-G.1+LV-G.2+LV-G.3+LV-G.4+LV-G.5+LV-G.6"
}
```

**Các điều kiện kỹ thuật phải đúng:**

- `len(paired) == 1`
- `paired[0].kind is MatchKind.EXACT_NAME`
- `paired[0].score >= 0.95`
- `"khác tên sheet" in paired[0].reason.lower()`

### 121. ✅ `tests/test_s1_normalizer.py::test_s1_nr12_different_names_are_not_forced_into_exact_name_match`

- **Tên dễ hiểu:** Không ép hai tên khác nhau thành khớp chính xác
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Hai dòng không có mã và tên hoàn toàn khác.
- **Ví dụ cụ thể:** Ví dụ “Tủ điện phân phối tổng” và “Ống nước HDPE D110”.
- **Kết quả mong đợi:** Không được tạo cặp EXACT_NAME giữa hai dòng này.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Không được tạo cặp EXACT_NAME giữa hai dòng này. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Ngăn ghép nhầm vật tư.
- **Nếu test thất bại:** Giá và khối lượng của hai loại thiết bị khác nhau có thể bị so sánh với nhau.
- **Vị trí:** `tests/test_s1_normalizer.py:262`
- **Thời gian:** 0.063757 giây

**Các điều kiện kỹ thuật phải đúng:**

- `exact_pairs == []`

### 122. ✅ `tests/test_security.py::test_network_guard_blocks_external`

- **Tên dễ hiểu:** Chế độ riêng tư phải chặn kết nối Internet
- **Trạng thái:** PASS
- **Tình huống kiểm tra:** Hệ thống chạy local-only và một đoạn code cố truy cập máy chủ bên ngoài.
- **Ví dụ cụ thể:** Ví dụ OCR hoặc thư viện cố gọi một URL Internet để tải model/dữ liệu.
- **Kết quả mong đợi:** Network guard chặn yêu cầu bên ngoài nhưng vẫn cho phép xử lý nội bộ cần thiết.
- **Kết quả lần chạy:** ĐÃ ĐẠT. Trong lần chạy này, hệ thống đã đáp ứng yêu cầu: Network guard chặn yêu cầu bên ngoài nhưng vẫn cho phép xử lý nội bộ cần thiết. Nói đơn giản: ví dụ được nêu trong testcase đã cho kết quả đúng và không có điều kiện kiểm tra nào bị sai.
- **Ý nghĩa nghiệp vụ:** Hồ sơ dự thầu không bị gửi ra ngoài ngoài ý muốn.
- **Nếu test thất bại:** Dữ liệu nhạy cảm có nguy cơ rò rỉ hoặc hệ thống phụ thuộc Internet.
- **Vị trí:** `tests/test_security.py:7`
- **Thời gian:** 0.002974 giây
