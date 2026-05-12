from  fastapi import FastAPI , File , UploadFile
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image
import  io
import base64

