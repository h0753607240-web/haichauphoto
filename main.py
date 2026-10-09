from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import fitz
import io
import os

app = FastAPI(title="PDF Monochrome & Clarity API", version="1.0.0", description="Convert PDF pages to monochrome and enhance text clarity.")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "PDF Monochrome & Clarity API", "version": "1.0.0"}

@app.post("/api/convert")
async def convert_pdf(
    file: UploadFile = File(...),
    mode: str = Form("grayscale"),  # grayscale | bw
    dpi: int = Form(220),
    contrast: float = Form(1.5),
    sharpness: float = Form(1.7),
    threshold: int = Form(180),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Vui lòng tải lên tệp PDF.")
    if mode not in ("grayscale", "bw"):
        raise HTTPException(400, "mode chỉ nhận grayscale hoặc bw.")
    if dpi < 100 or dpi > 350:
        raise HTTPException(400, "DPI phải trong khoảng 100–350.")
    if not 0.5 <= contrast <= 3.0 or not 0.5 <= sharpness <= 3.0:
        raise HTTPException(400, "contrast và sharpness phải trong khoảng 0.5–3.0.")
    if not 0 <= threshold <= 255:
        raise HTTPException(400, "threshold phải trong khoảng 0–255.")
    data = await file.read()
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"Tệp vượt quá giới hạn {MAX_UPLOAD_MB} MB.")
    if not data.startswith(b"%PDF"):
        raise HTTPException(400, "Tệp tải lên không phải PDF hợp lệ.")
    try:
        src = fitz.open(stream=data, filetype="pdf")
        out = fitz.open()
        matrix = fitz.Matrix(dpi / 72, dpi / 72)
        for page in src:
            pix = page.get_pixmap(matrix=matrix, alpha=False, colorspace=fitz.csGRAY)
            image = Image.frombytes("L", [pix.width, pix.height], pix.samples)
            image = ImageOps.autocontrast(image, cutoff=1)
            image = ImageEnhance.Contrast(image).enhance(contrast)
            image = ImageEnhance.Sharpness(image).enhance(sharpness)
            if mode == "bw":
                image = image.point(lambda p: 255 if p >= threshold else 0, mode="1").convert("L")
            # Embed each processed page as a high-resolution image in a PDF page of original dimensions.
            buf = io.BytesIO()
            image.save(buf, format="PNG", optimize=True)
            new_page = out.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(new_page.rect, stream=buf.getvalue())
        result = out.tobytes(deflate=True, garbage=4)
        out.close(); src.close()
    except Exception as exc:
        raise HTTPException(422, f"Không thể xử lý PDF: {str(exc)[:180]}") from exc
    stem = os.path.splitext(os.path.basename(file.filename))[0]
    output_name = f"{stem}_don-sac_ro-chu.pdf"
    return StreamingResponse(io.BytesIO(result), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{output_name}"', "X-Processed-Pages": str(len(fitz.open(stream=data, filetype="pdf")))})

app.mount("/", StaticFiles(directory="static", html=True), name="static")
