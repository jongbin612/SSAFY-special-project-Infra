// client/src/pages/Home.tsx
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Exercise } from '@/types/exercise';
import ExerciseList from '@/components/common/ExerciseList';
import EmptyState from '@/components/common/EmptyState';
import RecentExercisesRow from '@/components/common/RecentExercisesRow';
import WelcomeCoach from '@/components/common/WelcomeCoach';
import welcomeCoachImg from '@/assets/welcome-coach.png';
import { getHomeFeed } from '@/apis/home';

export default function Home() {
  const navigate = useNavigate();
  const [recent, setRecent] = React.useState<Exercise[]>([]);
  const [hot, setHot] = React.useState<Exercise[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let alive = true;
    setLoading(true);
    setError(null);

    getHomeFeed()
      .then(({ recent, hot }) => {
        if (!alive) return;
        setRecent(Array.isArray(recent) ? recent : []);
        setHot(Array.isArray(hot) ? hot : []);
      })
      .catch((e) => {
        if (!alive) return;
        setError(e?.response?.data?.detail || '홈 데이터를 불러오지 못했습니다.');
      })
      .finally(() => {
        if (alive) setLoading(false);
      });

    return () => {
      alive = false;
    };
  }, []);

  const goDetail = (it: Exercise) => navigate(`/exercise/${it.exercise_id}`);

  return (
    <div>
      {/* 최상단 환영 배너 */}
      <WelcomeCoach
        imageSrc={welcomeCoachImg}
        title='환영합니다!'
        subtitle='내 손안의 AI 트레이너, 홈PT와 함께 운동해봐요!'
        className='mb-10 text-chart-2'
      />

      {/* 최근 진행한 운동: 3개만, 최신이 왼쪽 */}
      {loading ? (
        <div className='h-[120px] animate-pulse rounded-xl bg-gray-100' />
      ) : recent.length > 0 ? (
        <RecentExercisesRow
          items={recent}
          onItemClick={goDetail}
          className='mb-6'
          limit={3}
          order='desc'
        />
      ) : (
        <div>
          <h2 className='mb-2 text-xl font-semibold'>최근 진행한 운동 바로가기</h2>
          <EmptyState title='최근 기록 없음' description='운동을 시작해보세요!' />
        </div>
      )}

      {/* 인기 운동 */}
      <h2 className='text-xl font-semibold mb-6'>인기 운동</h2>

      {loading ? (
        <div className='space-y-4'>
          <div className='h-[140px] animate-pulse rounded-2xl bg-gray-100' />
          <div className='h-[140px] animate-pulse rounded-2xl bg-gray-100' />
          <div className='h-[140px] animate-pulse rounded-2xl bg-gray-100' />
        </div>
      ) : error ? (
        <EmptyState title='오류' description={error} />
      ) : hot.length > 0 ? (
        <ExerciseList items={hot} onItemClick={goDetail} />
      ) : (
        <EmptyState title='인기 운동 준비 중' description='첫 운동을 기록해보세요!' />
      )}
    </div>
  );
}
