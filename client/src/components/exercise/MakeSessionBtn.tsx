import { Button } from '@components/ui/button';
import { useCallback, useState } from 'react';
import { PlayIcon } from 'lucide-react';
import { postSession } from '@apis/exercises';
import { useNavigate } from 'react-router-dom';

function MakeSessionBtn({ exerciseId, level }: { exerciseId: number; level: number }) {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const handleStartExercise = useCallback(() => {
    // 운동 시작 로직
    if (!exerciseId) return;
    setIsLoading(true);
    postSession(exerciseId, level)
      .then((data) => {
        setIsLoading(false);
        navigate(`/exercise/coach/${data.session_id}`);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [exerciseId, navigate, level]);
  return (
    <Button onClick={handleStartExercise} className='w-full' disabled={isLoading}>
      <PlayIcon />
      운동하러 가기
    </Button>
  );
}

export default MakeSessionBtn;
