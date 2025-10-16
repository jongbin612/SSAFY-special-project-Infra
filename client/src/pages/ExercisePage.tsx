// client/src/pages/ExercisePage.tsx
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import BodyCheckCard from '@/components/common/BodyCheckCard';
import FilterTabs from '@/components/common/FilterTabs';
import ExerciseList from '@/components/common/ExerciseList';
import EmptyState from '@/components/common/EmptyState';
import type { Exercise } from '@/types/exercise';
import { getExercises } from '@/apis/exercises';
import bodycheckImage from '@/assets/bodytype-check.png';

const TABS = ['전체', '가슴', '등', '어깨', '하체', '복근'] as const;
type Tab = (typeof TABS)[number];

const ExercisePage: React.FC = () => {
  const navigate = useNavigate();

  const [items, setItems] = React.useState<Exercise[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [tab, setTab] = React.useState<Tab>('전체');

  React.useEffect(() => {
    let alive = true;
    setLoading(true);
    getExercises()
      .then((data) => {
        if (!alive) return;
        setItems(Array.isArray(data) ? data : []);
      })
      .catch(() => {
        setItems([]);
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  const filtered = React.useMemo(() => {
    if (tab === '전체') return items;
    return items.filter((it) => it.category?.name === tab);
  }, [items, tab]);

  const handleItemClick = React.useCallback(
    (it: Exercise) => {
      navigate(`/exercise/${it.exercise_id}`);
    },
    [navigate],
  );

  return (
    <div>
      {/* 상단 체형 분석 카드 */}
      <section className='mb-4'>
        <BodyCheckCard
          imageSrc={bodycheckImage}
          onCtaClick={() => navigate('/user/body_analysis')}
          className='mb-2'
        />
      </section>

      {/* 카테고리 탭 */}
      <section className='mb-4'>
        <FilterTabs tabs={[...TABS]} value={tab} onChange={setTab as (t: Tab) => void} />
      </section>

      {/* 운동 리스트 */}
      <section aria-busy={loading ? 'true' : 'false'}>
        {loading ? (
          <EmptyState
            title='불러오는 중...'
            description='운동 목록을 가져오고 있어요.'
            icon='dumbbell'
            className='h-40'
          />
        ) : filtered.length > 0 ? (
          <ExerciseList items={filtered} onItemClick={handleItemClick} />
        ) : (
          <EmptyState
            title='운동이 없어요'
            description={
              tab === '전체' ? '등록된 운동이 없습니다.' : `${tab} 카테고리에 운동이 없습니다.`
            }
            icon='alert'
          />
        )}
      </section>
    </div>
  );
};

export default ExercisePage;
