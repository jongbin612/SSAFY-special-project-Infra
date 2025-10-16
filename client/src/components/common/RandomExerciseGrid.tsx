import * as React from 'react';
import type { Exercise } from '@/types/exercise';
import ExerciseCard from './ExerciseCard';

interface RandomExerciseGridProps {
  items: Exercise[];
  count?: number; // 기본 3
  title?: string; // 섹션 제목
  onItemClick?: (it: Exercise) => void;
  className?: string;
  /** 같은 날짜에 같은 시드를 쓰고 싶을 때 구분용 키 (페이지/섹션별로 다르게) */
  seedKey?: string;
}

/* -------------------- 시드 유틸 -------------------- */
// 로컬 날짜 YYYY-MM-DD
function todayKey(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}
// 간단한 해시(xmur3)
function xmur3(str: string) {
  let h = 1779033703 ^ str.length;
  for (let i = 0; i < str.length; i++) {
    h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  return function () {
    h = Math.imul(h ^ (h >>> 16), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    return (h ^= h >>> 16) >>> 0;
  };
}
// 시드 난수기(mulberry32)
function mulberry32(a: number) {
  return function () {
    let t = (a += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function sampleUniqueDeterministic<T>(arr: T[], k: number, rnd: () => number): T[] {
  if (arr.length <= k) return [...arr];
  const a = [...arr];
  // 부분 Fisher–Yates (앞 k개만 섞기)
  for (let i = 0; i < k; i++) {
    const j = i + Math.floor(rnd() * (a.length - i));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a.slice(0, k);
}

/* -------------------- 컴포넌트 -------------------- */
const RandomExerciseGrid: React.FC<RandomExerciseGridProps> = ({
  items,
  count = 3,
  title = '추천 운동',
  onItemClick,
  className = '',
  seedKey = 'default',
}) => {
  // 날짜 + 구분키로 시드 고정 → 하루 동안 결과 동일
  const picked = React.useMemo(() => {
    const seedStr = `${todayKey()}|${seedKey}`;
    const seed = xmur3(seedStr)();
    const rnd = mulberry32(seed);
    return sampleUniqueDeterministic(items, count, rnd);
  }, [items, count, seedKey]);

  return (
    <section className={className}>
      <h2 className='mb-3 text-xl font-semibold'>{title}</h2>

      {picked.length === 0 ? (
        <p className='text-sm text-muted-foreground'>표시할 운동이 없어요.</p>
      ) : (
        <ul className='grid grid-cols-1 gap-4 md:grid-cols-2'>
          {picked.map((it) => (
            <li key={it.exercise_id}>
              <ExerciseCard
                image={it.thumbnail_url}
                name={it.name}
                kcalPerHour={it.calorie}
                onClick={() => onItemClick?.(it)}
              />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
};

export default React.memo(RandomExerciseGrid);
