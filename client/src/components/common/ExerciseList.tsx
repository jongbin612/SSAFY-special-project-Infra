// client/src/components/common/ExerciseList.tsx
import * as React from 'react';
import ExerciseCard from './ExerciseCard';
import type { Exercise } from '@/types/exercise';

interface Props {
  items: Exercise[];
  onItemClick?: (item: Exercise) => void;
  className?: string;
}

const ExerciseListBase: React.FC<Props> = ({ items, onItemClick, className }) => {
  const handleClick = React.useCallback((it: Exercise) => () => onItemClick?.(it), [onItemClick]);

  return (
    <div className={className}>
      <ul className='space-y-4 [content-visibility:auto]'>
        {items.map((it) => (
          <li key={it.exercise_id}>
            <ExerciseCard
              image={it.thumbnail_url}
              name={it.name}
              kcalPerHour={it.calorie}
              onClick={onItemClick ? handleClick(it) : undefined}
            />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default React.memo(ExerciseListBase);
