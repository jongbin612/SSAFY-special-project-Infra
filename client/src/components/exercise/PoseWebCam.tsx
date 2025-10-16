import Webcam from 'react-webcam';
import { toast } from 'sonner';
import LoadingPage from '@pages/LoadingPage';

interface PoseWebCamProps {
  webcamRef: React.RefObject<Webcam | null>;
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  isLoading: boolean;
}

function PoseWebCam({ webcamRef, canvasRef, isLoading }: PoseWebCamProps) {
  return (
    <div className='w-full max-w-md mx-auto relative'>
      {/* 1:1 비율 컨테이너 */}
      <div className='aspect-square w-full relative overflow-hidden rounded-lg bg-gray-900'>
        <Webcam
          className='absolute inset-0 w-full h-full object-cover scale-x-[-1]'
          ref={webcamRef}
          audio={false}
          height={640}
          width={640}
          videoConstraints={{
            facingMode: 'user',
            frameRate: 5,
            width: 640,
            height: 640, // 1:1 비율로 변경
          }}
          onUserMediaError={() => {
            toast.error('웹캠에 접근할 수 없습니다. 권한을 확인해 주세요.');
          }}
        />
        <canvas
          ref={canvasRef}
          className='absolute inset-0 w-full h-full z-20 scale-x-[-1]'
          width={640}
          height={640}
        />
      </div>
      {isLoading && <LoadingPage message='카메라 키는 중...' />}
    </div>
  );
}

export default PoseWebCam;
