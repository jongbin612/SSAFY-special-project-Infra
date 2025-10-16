# app/services/body_type_service.py

import io
import os
import time
from typing import Any, Dict

import torch
from huggingface_hub import login
from PIL import Image
from transformers import AutoImageProcessor, ResNetForImageClassification

from app.core.config import get_settings

settings = get_settings()


class BodyTypeService:
    """체형 분석 서비스"""

    def __init__(self):
        self.processor = None
        self.model = None
        self.hf_token = settings.hf_token
        self.load_model()

    def load_model(self):
        """Hugging Face 토큰을 사용하여 모델 로드"""
        try:
            print("Loading body type classification model with HF token...")

            # Hugging Face 토큰으로 로그인
            login(token=self.hf_token)
            print("Successfully logged in to Hugging Face")

            model_name = "glazzova/body_type"

            # 로컬 경로가 있으면 로컬에서, 없으면 토큰으로 다운로드
            local_model_path = "./models/body_type"

            if os.path.exists(local_model_path):
                print(f"Loading from local path: {local_model_path}")

                self.processor = AutoImageProcessor.from_pretrained(
                    local_model_path, local_files_only=True, use_fast=False
                )

                self.model = ResNetForImageClassification.from_pretrained(local_model_path, local_files_only=True)
            else:
                print(f"Downloading from Hugging Face: {model_name}")

                self.processor = AutoImageProcessor.from_pretrained(model_name, token=self.hf_token, use_fast=False)

                self.model = ResNetForImageClassification.from_pretrained(model_name, token=self.hf_token)

            if torch.cuda.is_available():
                self.model = self.model.cuda()
                print("Model loaded on GPU")
            else:
                print("Model loaded on CPU")

            print("✅ Model loaded successfully")
            print(f"Model classes: {self.model.config.id2label}")

        except Exception as e:
            print(f"Failed to load model: {e}")
            raise

    def analyze_body_type(self, image_bytes: bytes) -> Dict[str, Any]:
        """체형 분석 수행"""
        start_time = time.time()

        # 바이트를 PIL Image로 변환
        image = Image.open(io.BytesIO(image_bytes))

        # RGB로 변환
        if image.mode != "RGB":
            image = image.convert("RGB")

        # 이미지 전처리
        inputs = self.processor(image, return_tensors="pt")

        # GPU로 이동 (사용 가능한 경우)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # 예측 수행
        with torch.no_grad():
            logits = self.model(**inputs).logits

        # 결과 처리
        predicted_label = logits.argmax(-1).item()
        body_type = self.model.config.id2label[predicted_label]

        # 모든 클래스별 확률 계산
        probabilities = torch.nn.functional.softmax(logits, dim=-1)

        # 모든 클래스별 확률을 딕셔너리로 변환
        all_predictions = {}
        for idx, prob in enumerate(probabilities[0]):
            class_name = self.model.config.id2label[idx]
            all_predictions[class_name] = float(prob.cpu().item())

        elapsed_time = time.time() - start_time

        return {
            "predicted_body_type": body_type,
            "confidence": float(probabilities[0][predicted_label].cpu().item()),
            "all_predictions": all_predictions,
            "processing_time_seconds": round(elapsed_time, 3),
            "image_size": f"{image.width}x{image.height}",
        }
