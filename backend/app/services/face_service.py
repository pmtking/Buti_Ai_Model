# app/services/face_service.py
# pmtking @copyright 2026 all rights reserved mohammad taheri

import cv2
import numpy as np
import tempfile
import os
from app.core.face_detector import FaceDetector
from app.utils.warping import FaceWarping
from app.utils.blending import FaceBlending


class FaceService:
    """سرویس مدیریت تشخیص و تغییر شکل صورت"""
    
    def __init__(self):
        self.detector = FaceDetector()
        self.warping = FaceWarping()
        self.blending = FaceBlending()
    
    def analyze_image(self, image_bytes: bytes) -> dict:
        """
        آنالیز تصویر و استخراج لندمارک‌ها
        
        Args:
            image_bytes: بایت‌های تصویر
            
        Returns:
            dict: شامل وضعیت و نقاط کلیدی
        """
        try:
            # ذخیره موقت تصویر
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            try:
                # استخراج لندمارک‌ها
                landmarks = self.detector.detect_landmarks(tmp_path)
                
                if landmarks is None:
                    return {
                        'status': 'error',
                        'message': 'چهره‌ای در تصویر شناسایی نشد'
                    }
                
                # دریافت ایندکس‌های مهم
                indices = self.detector.get_indices()
                
                # استخراج نقاط مهم
                nose_points = [landmarks[i] for i in indices['nose'] if i < len(landmarks)]
                lip_points = [landmarks[i] for i in indices['lip'] if i < len(landmarks)]
                
                return {
                    'status': 'success',
                    'landmarks': landmarks,
                    'count': len(landmarks),
                    'features': {
                        'nose': nose_points,
                        'lip': lip_points,
                        'nose_count': len(nose_points),
                        'lip_count': len(lip_points)
                    }
                }
                
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            return {
                'status': 'error',
                'message': f'خطا در پردازش تصویر: {str(e)}'
            }
    
    def edit_image(self, image_bytes: bytes, feature: str, intensity: float) -> dict:
        """
        تغییر شکل صورت
        
        Args:
            image_bytes: بایت‌های تصویر
            feature: نوع تغییر (nose, lip)
            intensity: شدت تغییر (0.0 تا 1.0)
            
        Returns:
            dict: شامل وضعیت و تصویر تغییر یافته
        """
        try:
            # خواندن تصویر
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    'status': 'error',
                    'message': 'تصویر معتبر نیست'
                }
            
            # ذخیره موقت برای تشخیص
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            try:
                # استخراج لندمارک‌ها
                landmarks = self.detector.detect_landmarks(tmp_path)
                
                if landmarks is None:
                    return {
                        'status': 'error',
                        'message': 'چهره‌ای در تصویر شناسایی نشد'
                    }
                
                # دریافت نقاط ویژه
                indices = self.detector.get_indices()
                
                # تبدیل نقاط به پیکسل
                h, w = image.shape[:2]
                points = []
                
                if feature == 'nose':
                    idx_list = indices['nose']
                elif feature == 'lip':
                    idx_list = indices['lip']
                else:
                    idx_list = indices['nose']
                
                for i in idx_list:
                    if i < len(landmarks):
                        x = int(landmarks[i]['x'] * w / 100)
                        y = int(landmarks[i]['y'] * h / 100)
                        points.append([x, y])
                
                # ایجاد ماسک
                mask = self.warping.create_mask(image, points)
                
                # اعمال تغییر
                if feature == 'nose':
                    warped = self.warping.warp_nose(image, points, intensity)
                elif feature == 'lip':
                    warped = self.warping.warp_lip(image, points, intensity)
                else:
                    warped = image
                
                # ترکیب
                result = self.blending.poisson_blending(image, warped, mask)
                
                # ذخیره نتیجه
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_out:
                    cv2.imwrite(tmp_out.name, result)
                    result_path = tmp_out.name
                
                return {
                    'status': 'success',
                    'image_path': result_path,
                    'message': f'تغییر {feature} با شدت {intensity:.2f} اعمال شد'
                }
                
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            return {
                'status': 'error',
                'message': f'خطا در تغییر شکل: {str(e)}'
            }