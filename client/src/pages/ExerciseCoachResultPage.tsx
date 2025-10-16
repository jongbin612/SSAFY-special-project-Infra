import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { type SessionDetail } from '@/types/exercise';
import { getSessionDetail } from '@apis/exercises';
import { AspectRatio } from '@radix-ui/react-aspect-ratio';
import Image from '@/components/common/Image';
import LoadingPage from '@pages/LoadingPage';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

function ExerciseCoachResultPage() {
  const { sessionId } = useParams();
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!sessionId) return;

    setIsLoading(true);
    getSessionDetail(sessionId)
      .then((data) => {
        setSession(data.session);
      })
      .catch(() => {
        navigate('/exercise');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [sessionId, navigate]);

  return (
    <main className='min-h-screen min-w-[375px] max-w-[480px] w-full mx-auto bg-gray-50 flex flex-col'>
      <div className='p-4 pb-20 w-full flex-1 flex flex-col justify-center items-center gap-6'>
        {isLoading && <LoadingPage />}
        {session && (
          <>
            <AspectRatio ratio={16 / 9}>
              <Image
                className='w-full h-full object-contain'
                src={session?.exercise.thumbnail_url}
                alt={session?.exercise.name}
              />
            </AspectRatio>
            <h2 className='text-2xl font-bold'>{session?.exercise.name} 완료 결과</h2>
            <Card className='w-full'>
              <CardContent>
                <div className='w-full flex flex-col gap-4'>
                  <div className='flex w-full items-center justify-between text-lg'>
                    <p>운동 레벨</p>
                    <Badge className='bg-chart-2'>{session?.level.level} 레벨</Badge>
                  </div>
                  <div className='flex w-full items-center justify-between text-lg'>
                    <p>소모 칼로리</p>
                    <p className='text-chart-2'>{session?.total_calories_burned} kcal</p>
                  </div>
                  <div className='flex w-full items-center justify-between text-lg'>
                    <p>진행한 운동 세트</p>
                    <p className='text-chart-2'>
                      {session?.current_set - 1} / {session?.level.target_sets}
                    </p>
                  </div>
                  <div className='flex w-full items-center justify-between text-lg'>
                    <p>총 운동 횟수</p>
                    <p className='text-chart-2'>
                      {session.total_reps_completed + session.total_reps_failed} 회
                    </p>
                  </div>
                  <div className='flex w-full items-center justify-between text-lg'>
                    <p>성공한 운동 횟수</p>
                    <p className='text-chart-2'>{session.total_reps_completed} 회</p>
                  </div>
                  <div className='flex w-full items-center justify-between text-lg'>
                    <p>실패한 운동 횟수</p>
                    <p className='text-chart-2'>{session.total_reps_failed} 회</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Button className='w-full' onClick={() => navigate('/exercise')}>
              다른 운동 하러가기
            </Button>
          </>
        )}
      </div>
    </main>
  );
}

export default ExerciseCoachResultPage;
