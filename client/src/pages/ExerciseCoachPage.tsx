import { useNavigate, useParams } from 'react-router-dom';
import ExerciseInfoCard from '@components/exercise/ExerciseInfoCard';
import Webcam from 'react-webcam';
import { useRef, useState, useCallback, useEffect } from 'react';
import { type NormalizedLandmarkList } from '@mediapipe/drawing_utils';
import { Button } from '@/components/ui/button';
import { PauseIcon, PlayIcon, StopCircleIcon } from 'lucide-react';
import PoseWebCam from '@components/exercise/PoseWebCam';
import useMediapipe from '@/hooks/useMedeapipe';
import { getSessionDetail } from '@/apis/exercises';
import type { SessionDetail, SocketInfo } from '@/types/exercise';
import useSocket from '@/hooks/useSocket';
import { useTextToSpeech } from '@/hooks/useTextToSpeech';
import type { exerciseMessage } from '@/types/exercise';
import { toast } from 'sonner';
// 타입 정의

function ExerciseCoachPage() {
  const { sessionId: _sessionId } = useParams<{ sessionId: string }>();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const webcamRef = useRef<Webcam>(null);
  const socketRef = useRef<WebSocket>(null);
  const navigate = useNavigate();
  const [isStart, setIsStart] = useState(false);
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [socketInfo, setSocketInfo] = useState<SocketInfo | null>(null);
  const [isPause, setIsPause] = useState(false);

  const { speakText } = useTextToSpeech({
    voiceId: '4JJwo477JUAx3HV0T7n7',
    modelId: 'eleven_flash_v2_5',
  });

  const { isConnected, sendMessage } = useSocket({
    url: socketInfo?.websocket_url || '',
    socketRef: socketRef,
    autoConnect: !!socketInfo?.websocket_url,
  });
  // MediaPipe 커스텀 훅 사용

  const handleStart = useCallback(() => {
    setIsStart(true);
    speakText(
      `${session?.exercise.name} 레벨 ${session?.level.level}. ${session?.level.target_sets}세트 ${session?.level.target_reps}회씩 진행하겠습니다. 준비되시면 운동을 시작 해 주세요!`,
    );
  }, [session, speakText]);

  const handlePuase = useCallback(() => {
    if (isPause) {
      toast.success('운동을 재시작합니다.');
      speakText('운동을 재시작합니다.');
      sendMessage({ type: 'workout_resume', data: {} });
      setIsPause(false);
      return;
    }
    toast.error('운동을 일시 정지합니다.');
    speakText('운동을 일시 정지합니다.');
    sendMessage({ type: 'workout_pause', data: {} });
    setIsPause(true);
  }, [isPause, speakText, sendMessage]);

  const handleStop = useCallback(() => {
    toast.error('운동을 종료합니다.');
    speakText('운동을 종료합니다. 다음에는 끝까지 해봐요!');
    sendMessage({
      type: 'workout_stop',
      data: {
        total_reps: 10,
        duration_seconds: 120.0,
        total_calories_burned: 60.0,
      },
    });
    setIsStart(false);
    navigate(`/exercise/coach/${_sessionId}/result`);
  }, [sendMessage, speakText, _sessionId, navigate]);

  // 포즈 감지 콜백 - useRef를 사용하여 안정화
  const isStartRef = useRef(isStart);
  const sendMessageRef = useRef(sendMessage);

  // ref 업데이트
  useEffect(() => {
    isStartRef.current = isStart;
  }, [isStart]);

  useEffect(() => {
    sendMessageRef.current = sendMessage;
  }, [sendMessage]);

  // 포즈 감지 콜백 - 의존성 없이 안정화
  const handlePoseDetected = useCallback(
    (_landmarks: NormalizedLandmarkList) => {
      if (isStartRef.current && sendMessageRef.current && !isPause && isConnected) {
        sendMessageRef.current({
          type: 'mediapipe_coordinates',
          data: {
            landmarks: _landmarks.map((landmark) => [
              landmark.x,
              landmark.y,
              landmark.z,
              landmark.visibility,
            ]),
          },
        });
      }
    },
    [isPause, isConnected], // 의존성 배열을 비워서 재생성 방지
  );
  if (socketRef.current && isConnected) {
    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data) as exerciseMessage;
      if (data.type === 'workout_completed') {
        setIsPause(true);
        speakText('수고하셨습니다. 결과를 확인해 주세요.');
        navigate(`/exercise/coach/${_sessionId}/result`);
        return;
      }
      if (data.type === 'rep_success') {
        if (data.data.rep_detected) {
          if (data.data.set_completed) {
            toast.success(data.data.feedback_message);
            speakText(data.data.feedback_message);
            setSession(data.data.session);
            sendMessage({ type: 'workout_pause', data: {} });
            setIsPause(true);
            setTimeout(() => {
              toast.success('휴식 시간 끝! 운동을 재시작합니다.');
              speakText('휴식 시간 끝! 운동을 재시작합니다.');
              sendMessage({ type: 'workout_resume', data: {} });
              setIsPause(false);
            }, data.data.session.level.rest_seconds * 1000);
            return;
          }
          toast.success(`${data.data.session.current_set_reps}회 성공`);
          speakText(`${data.data.session.current_set_reps}개`);
          setSession(data.data.session);
        }
        if (data.data.failed_detected) {
          toast.error(data.data.feedback_message);
          speakText(data.data.feedback_message);
          setSession(data.data.session);
        }
      }
    };
  }

  const { isLoading, error } = useMediapipe({
    webcamRef,
    canvasRef,
    onPoseDetected: handlePoseDetected,
  });
  useEffect(() => {
    if (!_sessionId) return;
    getSessionDetail(_sessionId)
      .then((data) => {
        setSession(data.session);
        setSocketInfo(data.socket_info);
      })
      .catch(() => {
        navigate('/exercise');
      });
  }, [_sessionId, navigate]);

  return (
    <main className='min-h-screen min-w-[375px] max-w-[480px] w-full mx-auto bg-gray-50 flex flex-col'>
      <div className='p-4 pb-20 w-full flex-1 flex flex-col justify-center items-center gap-4'>
        <PoseWebCam webcamRef={webcamRef} canvasRef={canvasRef} isLoading={isLoading} />

        {!isStart ? (
          <div className='w-full h-full flex flex-col items-center justify-center gap-6'>
            <div className='text-center mt-4'>
              <h2 className='text-xl font-semibold mb-2'>카메라 세팅 후 운동을 시작하세요</h2>
              <p className='text-gray-600'>카메라에 전신이 보이도록 해 주세요</p>
            </div>
            {!isLoading && !error && isConnected && (
              <Button onClick={handleStart} disabled={isLoading || !!error || !isConnected}>
                <PlayIcon />
                운동 시작
              </Button>
            )}
          </div>
        ) : (
          <>
            <ExerciseInfoCard exerciseInfo={session!} isPause={isPause} />

            {!isLoading && !error && (
              <div className='flex gap-2'>
                <Button onClick={handlePuase} disabled={isLoading || !!error}>
                  {isPause ? <PlayIcon /> : <PauseIcon />}
                  {isPause ? '운동 재시작' : '일시 정지'}
                </Button>
                <Button onClick={handleStop} disabled={isLoading || !!error}>
                  <StopCircleIcon />
                  운동 종료
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}

export default ExerciseCoachPage;
