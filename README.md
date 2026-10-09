# PDF Đơn Sắc — Làm Rõ Chữ (Web App + API)

Ứng dụng web tiếng Việt chuyển PDF màu sang đơn sắc xám hoặc đen-trắng, tự động cân bằng tương phản và tăng độ nét. Có API HTTP để tích hợp vào ứng dụng khác.

## Chạy thử trên máy tính

Yêu cầu Python 3.10 trở lên.

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

macOS/Linux:
```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Mở `http://127.0.0.1:8000`. Tài liệu API: `http://127.0.0.1:8000/docs`.

## Triển khai thành website công khai bằng Render

Gói này đã có `render.yaml` và `Dockerfile` để hỗ trợ triển khai.

1. Giải nén ZIP.
2. Tạo kho lưu trữ Git trên GitHub và tải toàn bộ nội dung thư mục này lên kho (repository phải chứa `render.yaml`, `Dockerfile`, `main.py`, `requirements.txt` và thư mục `static`).
3. Đăng nhập Render, chọn tạo **Blueprint** và kết nối kho GitHub vừa tạo.
4. Xem cấu hình từ `render.yaml`, sau đó nhấn triển khai.
5. Khi trạng thái dịch vụ là Live, mở URL `https://<ten-dich-vu>.onrender.com` do Render cung cấp. Kiểm tra `/api/health` và `/docs`.

Lưu ý: cần tài khoản Render và GitHub; bạn phải tự xác nhận quyền truy cập và triển khai trong tài khoản của mình. Gói miễn phí, nếu khả dụng, có thể ngủ khi không hoạt động và khởi động chậm ở lần truy cập tiếp theo. Chính sách và giới hạn của nhà cung cấp có thể thay đổi.

## API

- `GET /api/health` — kiểm tra trạng thái.
- `POST /api/convert` — tải lên PDF và nhận PDF đã xử lý.

Ví dụ:

```bash
curl -X POST https://YOUR-SITE.onrender.com/api/convert \
  -F "file=@tai-lieu.pdf" \
  -F "mode=grayscale" \
  -F "dpi=220" \
  -F "contrast=1.5" \
  -F "sharpness=1.7" \
  --output tai-lieu-don-sac.pdf
```

Các trường:
- `file`: PDF (bắt buộc; giới hạn mặc định 50 MB).
- `mode`: `grayscale` (đơn sắc xám, giữ sắc độ) hoặc `bw` (đen/trắng nhị phân).
- `dpi`: 100–350, mặc định 220.
- `contrast`: 0.5–3.0, mặc định 1.5.
- `sharpness`: 0.5–3.0, mặc định 1.7.
- `threshold`: 0–255, mặc định 180; chỉ ảnh hưởng khi `mode=bw`.

## Bảo mật trước khi dùng rộng rãi

API chưa có xác thực người dùng, giới hạn tốc độ hoặc quota. Trước khi dùng công khai với nhiều người, nên bổ sung chống lạm dụng, theo dõi lỗi, giới hạn số trang và tài nguyên xử lý. Không tải lên tài liệu nhạy cảm nếu chưa đánh giá chính sách lưu trữ/xử lý của nhà cung cấp.

## Lưu ý chất lượng

Mỗi trang PDF được render thành ảnh độ phân giải đã chọn rồi đóng gói lại thành PDF. Do đó, chữ trong PDF đầu ra có thể không còn chọn/tìm kiếm được; PDF nhiều trang hoặc DPI cao có thể tạo tệp lớn hơn. Luôn giữ bản gốc.
