import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@components/ui/card';
import type { SessionDetail } from '@/types/exercise';

function ExerciseInfoCard({
  exerciseInfo,
  isPause,
}: {
  exerciseInfo: SessionDetail;
  isPause: boolean;
}) {
  return (
    <Card className='w-full'>
      <CardHeader>
        <CardTitle>{isPause ? '운동 멈춤' : '운동 진행중...'}</CardTitle>
        <CardDescription>
          <div className='flex justify-between items-center'>
            <span>{exerciseInfo.exercise.name}</span>
            <span>{exerciseInfo.level.level}레벨</span>
          </div>
        </CardDescription>
      </CardHeader>
      <CardContent className='flex justify-between items-center gap-2'>
        <div className='flex flex-col gap-2 justify-between items-center w-full border rounded-md p-2'>
          <span className='text-2xl font-semibold text-chart-2'>
            {exerciseInfo.current_set} / {exerciseInfo.level.target_sets}
          </span>
          <span>세트</span>
        </div>
        <div className='flex flex-col gap-2 justify-between items-center w-full border rounded-md p-2'>
          <span className='text-2xl font-semibold text-chart-1'>
            {exerciseInfo.current_set_reps} / {exerciseInfo.level.target_reps}
          </span>
          <span>횟수</span>
        </div>
      </CardContent>
    </Card>
  );
}

export default ExerciseInfoCard;
