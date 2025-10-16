// client/src/components/common/RecentExercisesRow.tsx
import * as React from 'react';
import type { Exercise } from '@/types/exercise';
import RoundExerciseCard from './RoundExerciseCard';

export interface RecentExercisesRowProps {
  items: Exercise[];
  title?: string;
  onItemClick?: (it: Exercise) => void;
  className?: string;
  limit?: number; // 기본 3
  order?: 'asc' | 'desc'; // 기본 'desc' (최신이 왼쪽)
}

const RecentExercisesRow: React.FC<RecentExercisesRowProps> = ({
  items,
  title = '최근 진행한 운동 바로가기',
  onItemClick,
  className = '',
  limit = 3,
  order = 'desc',
}) => {
  const display = React.useMemo(() => {
    const arr = order === 'asc' ? [...items].reverse() : items;
    return arr.slice(0, limit);
  }, [items, limit, order]);

  const few = display.length <= 3; // 3개 이하면 균등 배치

  return (
    <section className={className}>
      <h2 className='mb-6 text-xl font-semibold'>{title}</h2>

      {few ? (
        // ✅ 3개 이하: 가운데 정렬 + 균등 분배
        <div className='grid grid-cols-3 gap-4 justify-items-center w-full'>
          {display.map((it) => (
            <RoundExerciseCard
              key={it.exercise_id}
              image={it.thumbnail_url}
              name={it.name}
              onClick={() => onItemClick?.(it)}
              className='w-full' // 카드 지름과 맞춰 폭 고정 -> 균일
            />
          ))}
        </div>
      ) : (
        // 4개 이상: 가로 스크롤 + 스냅 + 좌우 패딩
        <div className='flex gap-4 overflow-x-auto pb-2 px-2 no-scrollbar snap-x snap-mandatory'>
          {display.map((it) => (
            <div key={it.exercise_id} className='snap-start'>
              <RoundExerciseCard
                image={it.thumbnail_url}
                name={it.name}
                onClick={() => onItemClick?.(it)}
                className='w-full shrink-0'
              />
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export default React.memo(RecentExercisesRow);
