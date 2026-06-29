# app/api/v1/analyze.py
# pmtking @copyright 2026 all rights reserved mohammad taheri# app/api/v1/analyze.py
# pmtking @copyright 2026 all rights reserved mohammad taheri

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import time
from app.services.face_service import FaceService

# ایجاد router
router = APIRouter()

# ایجاد سرویس
face_service = FaceService()


@router.post("/analyze")
async def analyze_face(file: UploadFile = File(...)):
    """
    آنالیز صورت و استخراج ۴۶۸ نقطه کلیدی
    
    - **file**: تصویر صورت (JPG, PNG, JPEG)
    
    بازگشت:
    - **status**: موفقیت یا خطا
    - **landmarks**: لیست نقاط کلیدی
    - **count**: تعداد نقاط استخراج شده
    - **processing_time**: زمان پردازش
    """
    start_time = time.time()
    
    try:
        # بررسی نوع فایل
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="فایل باید تصویر باشد"
            )
        
        # خواندن فایل
        content = await file.read()
        
        # آنالیز تصویر
        result = face_service.analyze_image(content)
        
        # محاسبه زمان
        processing_time = round(time.time() - start_time, 3)
        
        # بررسی نتیجه
        if result['status'] == 'error':
            return JSONResponse(
                status_code=404,
                content={
                    **result,
                    'processing_time': processing_time
                }
            )
        
        # بازگشت موفقیت‌آمیز
        return {
            **result,
            'processing_time': processing_time,
            'message': f"{result['count']} نقطه کلیدی استخراج شد"
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': f'خطا در پردازش: {str(e)}',
                'processing_time': round(time.time() - start_time, 3)
            }
        )


@router.get("/analyze/indices")
async def get_face_indices():
    """
    دریافت ایندکس‌های مهم نقاط صورت
    
    بازگشت:
    - **nose**: ایندکس‌های بینی
    - **lip**: ایندکس‌های لب
    - **jaw**: ایندکس‌های فک
    - **eye**: ایندکس‌های چشم
    """
    return face_service.detector.get_indices()