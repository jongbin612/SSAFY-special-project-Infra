import { useRef, useEffect, useState, useCallback } from 'react';
import { Pose, POSE_CONNECTIONS } from '@mediapipe/pose';
import * as cam from '@mediapipe/camera_utils';
import {
  drawConnectors,
  drawLandmarks,
  type NormalizedLandmarkList,
} from '@mediapipe/drawing_utils';
import { drawLine } from '@/lib/utils';
import { toast } from 'sonner';
import type Webcam from 'react-webcam';

// 타입 정의
interface PoseResults {
  poseLandmarks: NormalizedLandmarkList | undefined;
}

interface Point {
  x: number;
  y: number;
}

interface UseMediapipeProps {
  webcamRef: React.RefObject<Webcam | null>;
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  onPoseDetected?: (landmarks: NormalizedLandmarkList) => void;
}

interface UseMediapipeReturn {
  isLoading: boolean;
  error: string | null;
}

const useMediapipe = ({
  webcamRef,
  canvasRef,
  onPoseDetected,
}: UseMediapipeProps): UseMediapipeReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const poseRef = useRef<Pose | null>(null);
  const cameraRef = useRef<cam.Camera | null>(null);
  const onPoseDetectedRef = useRef(onPoseDetected);

  // onPoseDetected 콜백을 ref로 업데이트
  useEffect(() => {
    onPoseDetectedRef.current = onPoseDetected;
  }, [onPoseDetected]);

  // Helper function to convert normalized coordinates to pixel coordinates
  const toPixelCoord = useCallback(
    (point: { x: number; y: number }, width: number, height: number): Point => ({
      x: point.x * width,
      y: point.y * height,
    }),
    [],
  );

  const onResults = useCallback(
    (results: PoseResults) => {
      const canvasElement = canvasRef.current;
      const webcamVideo = webcamRef.current?.video;

      if (!canvasElement || !webcamVideo || !results.poseLandmarks) {
        return;
      }

      const landmarks = results.poseLandmarks;
      const canvasCtx = canvasElement.getContext('2d');

      if (!canvasCtx) {
        return;
      }

      // Clear and setup canvas
      canvasCtx.save();
      canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
      canvasCtx.globalCompositeOperation = 'source-over';

      // 얼굴 부분을 제외한 포즈 연결선과 랜드마크 그리기
      // 얼굴 부분 랜드마크 인덱스: 0-10 (코, 눈, 귀 등)
      const bodyLandmarks = landmarks.filter((_, index) => index > 10);
      const bodyConnections = POSE_CONNECTIONS.filter(([start, end]) => start > 10 && end > 10);

      // 몸체 부분만 연결선 그리기
      drawConnectors(canvasCtx, landmarks, bodyConnections, {
        color: '#fff',
        lineWidth: 4,
      });

      // 몸체 부분만 랜드마크 그리기
      drawLandmarks(canvasCtx, bodyLandmarks, {
        color: '#fff',
        lineWidth: 2,
      });

      // Draw pose analysis indicators
      const { width, height } = canvasElement;

      // Shoulder level indicator
      const leftShoulder = landmarks[11];
      const rightShoulder = landmarks[12];
      const shoulderColor = 'green';
      const leftShoulderPixel = toPixelCoord(leftShoulder, width, height);
      const rightShoulderPixel = toPixelCoord(rightShoulder, width, height);

      drawLine(
        canvasCtx,
        leftShoulderPixel.x,
        leftShoulderPixel.y,
        rightShoulderPixel.x,
        rightShoulderPixel.y,
        shoulderColor,
        4,
      );

      // Back straightness indicator
      const midShoulder: Point = {
        x: (leftShoulder.x + rightShoulder.x) / 2,
        y: (leftShoulder.y + rightShoulder.y) / 2,
      };
      const midHip: Point = {
        x: (landmarks[23].x + landmarks[24].x) / 2,
        y: (landmarks[23].y + landmarks[24].y) / 2,
      };
      const midKnee: Point = {
        x: (landmarks[25].x + landmarks[26].x) / 2,
        y: (landmarks[25].y + landmarks[26].y) / 2,
      };

      const backColor = 'green';
      const midShoulderPixel = toPixelCoord(midShoulder, width, height);
      const midHipPixel = toPixelCoord(midHip, width, height);
      const midKneePixel = toPixelCoord(midKnee, width, height);

      drawLine(
        canvasCtx,
        midShoulderPixel.x,
        midShoulderPixel.y,
        midHipPixel.x,
        midHipPixel.y,
        backColor,
        4,
      );
      drawLine(
        canvasCtx,
        midHipPixel.x,
        midHipPixel.y,
        midKneePixel.x,
        midKneePixel.y,
        backColor,
        4,
      );

      canvasCtx.restore();

      // 포즈 감지 콜백 호출
      if (onPoseDetectedRef.current) {
        onPoseDetectedRef.current(landmarks);
      }
    },
    [toPixelCoord, canvasRef, webcamRef],
  );

  // Canvas 크기 설정을 위한 별도 useEffect
  useEffect(() => {
    if (!canvasRef.current || !webcamRef.current?.video) return;

    const video = webcamRef.current.video;
    const canvas = canvasRef.current;

    // 비디오 메타데이터가 로드된 후에 canvas 크기 설정
    const handleLoadedMetadata = () => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    };

    if (video.readyState >= 1) {
      handleLoadedMetadata();
    } else {
      video.addEventListener('loadedmetadata', handleLoadedMetadata);
      return () => video.removeEventListener('loadedmetadata', handleLoadedMetadata);
    }
  }, [canvasRef, webcamRef]);

  // MediaPipe 초기화 및 정리
  useEffect(() => {
    const initializePose = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const pose = new Pose({
          locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
        });

        pose.setOptions({
          modelComplexity: 1,
          smoothLandmarks: true,
          enableSegmentation: false,
          smoothSegmentation: false,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        pose.onResults(onResults);
        poseRef.current = pose;

        // 웹캠이 준비될 때까지 대기
        const video = webcamRef.current?.video;
        if (video) {
          const camera = new cam.Camera(video, {
            onFrame: async () => {
              if (webcamRef.current?.video && poseRef.current) {
                await poseRef.current.send({ image: webcamRef.current.video });
              }
            },
            width: 640,
            height: 640, // 1:1 비율로 변경
          });

          await camera.start();
          cameraRef.current = camera;
        }
      } catch {
        const errorMessage = '포즈 인식 초기화에 실패했습니다. 페이지를 새로고침해 주세요.';
        setError(errorMessage);
        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    initializePose();

    // Cleanup function
    return () => {
      if (cameraRef.current) {
        cameraRef.current.stop();
        cameraRef.current = null;
      }
      if (poseRef.current) {
        poseRef.current.close();
        poseRef.current = null;
      }
    };
  }, [onResults, webcamRef]);

  return {
    isLoading,
    error,
  };
};

export default useMediapipe;
