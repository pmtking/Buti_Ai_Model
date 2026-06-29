# app/api/v1/edit.py
# pmtking @copyright 2026 all rights reserved mohammad taheri

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import time
import os
from app.services.face_service import FaceService

router = APIRouter()
face_service = FaceService()


@router.post("/edit")
async def edit_face(
    file: UploadFile = File(...),
    feature: str = Form("nose"),
    intensity: float = Form(0.5)
):
    """
    تغییر شکل صورت
    
    - **file**: تصویر صورت (JPG, PNG, JPEG)
    - **feature**: نوع تغییر (nose, lip)
    - **intensity**: شدت تغییر (0.0 تا 1.0)
    
    بازگشت:
    - تصویر تغییر یافته
    """
    start_time = time.time()
    
    try:
        # بررسی نوع فایل
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="فایل باید تصویر باشد"
            )
        
        # بررسی پارامترها
        if feature not in ['nose', 'lip']:
            raise HTTPException(
                status_code=400,
                detail="نوع تغییر باید nose یا lip باشد"
            )
        
        if intensity < 0 or intensity > 1:
            raise HTTPException(
                status_code=400,
                detail="شدت تغییر باید بین 0 و 1 باشد"
            )
        
        # خواندن فایل
        content = await file.read()
        
        # اعمال تغییر
        result = face_service.edit_image(content, feature, intensity)
        
        if result['status'] == 'error':
            return JSONResponse(
                status_code=404,
                content={
                    'status': 'error',
                    'message': result['message'],
                    'processing_time': round(time.time() - start_time, 3)
                }
            )
        
        # بازگرداندن تصویر
        return FileResponse(
            result['image_path'],
            media_type="image/jpeg",
            filename=f"edited_{feature}_{intensity:.2f}.jpg"
        )
        
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


@router.get("/edit/features")
async def get_edit_features():
    """
    دریافت ویژگی‌های قابل تغییر
    
    بازگشت:
    - لیست ویژگی‌های قابل تغییر
    """
    return {
        'features': [
            {
                'id': 'nose',
                'name': 'بینی',
                'description': 'تغییر فرم بینی',
                'min_intensity': 0.0,
                'max_intensity': 1.0
            },
            {
                'id': 'lip',
                'name': 'لب',
                'description': 'تغییر حجم لب',
                'min_intensity': 0.0,
                'max_intensity': 1.0
            }
        ]
    }