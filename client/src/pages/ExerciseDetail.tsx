import { useParams } from 'react-router-dom';
import ExerciseDetailUi from '@components/exercise/ExerciseDetailUi';
import SkeletonExerciseDetail from '@/components/exercise/SkeletonExerciseDetail';
import { useState, useEffect, useMemo } from 'react';
import { getExerciseDetail } from '@apis/exercises';
import type { Exercise } from '@/types/exercise';
import { useNavigate } from 'react-router-dom';
import MakeSessionBtn from '@/components/exercise/MakeSessionBtn';

const ACCESS_EXERCISE_LIST = [1, 2];

function ExerciseDetail() {
  const { exerciseId } = useParams();
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState(true);
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const level = useMemo(() => {
    if (!exercise) return 1;
    return exercise.levels.find((lv) => !lv.is_locked && !lv.is_completed)?.level || 1;
  }, [exercise]);
  useEffect(() => {
    if (!exerciseId) return;
    scrollTo(0, 0);
    setIsLoading(true);
    getExerciseDetail(exerciseId)
      .then((data) => {
        setExercise(data);
      })
      .catch(() => {
        navigate('/exercise');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [exerciseId, navigate]);
  return (
    <>
      {isLoading ? (
        <SkeletonExerciseDetail />
      ) : (
        exercise && (
          <div className='flex flex-col gap-6'>
            <ExerciseDetailUi
              thumbnail={exercise.thumbnail_url}
              title={exercise.name}
              category={exercise.category.name}
              target={exercise.target_image_url}
              howToWork={exercise.howto_image_url}
              calory={exercise.calorie.toString()}
            />
            {exercise.exercise_id && ACCESS_EXERCISE_LIST.includes(exercise.exercise_id) && (
              <MakeSessionBtn exerciseId={exercise.exercise_id} level={level} />
            )}
          </div>
        )
      )}
    </>
  );
}

export default ExerciseDetail;
