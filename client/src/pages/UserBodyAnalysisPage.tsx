import { useState, useCallback } from 'react';
import ImageInput from '@components/exercise/ImageInput';
import { Button } from '@components/ui/button';
import { PlusIcon } from 'lucide-react';
import { toast } from 'sonner';
import { postBodyAnalysis } from '@apis/analyze';
import type { BodyAnalysisResponse } from '@/types/analyze';
import LoadingPage from '@pages/LoadingPage';
import Image from '@/components/common/Image';
import ExerciseList from '@components/common/ExerciseList';
import type { Exercise } from '@/types/exercise';
import { useNavigate } from 'react-router-dom';
import { AspectRatio } from '@radix-ui/react-aspect-ratio';

const BODY_TYPE_DESCRIPTIONS = {
  skinny: {
    title: '슬림한 체형',
    description: '당신은 체지방이 적고 근육이 적은 슬림한 체형입니다.',
  },
  ordinary: {
    title: '보통의 체형',
    description: '당신은 체지방이 적고 근육이 적은 보통의 체형입니다.',
  },
  overweight: { title: '과체중', description: '당신은 체지방이 많고 근육이 적은 과체중입니다.' },
  hulk: { title: '헐크체형', description: '당신은 체지방이 많고 근육이 많은 헐크체형입니다.' },
};

function UserBodyAnalysisPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<BodyAnalysisResponse | null>(null);

  const navigate = useNavigate();
  const handleItemClick = useCallback(
    (item: Exercise) => {
      navigate(`/exercise/${item.exercise_id}`);
    },
    [navigate],
  );
  const handleAnalyze = useCallback(() => {
    if (files.length === 0) {
      toast.error('이미지를 추가해주세요.');
      return;
    }
    setIsLoading(true);
    postBodyAnalysis(files[0])
      .then((res) => {
        toast.success(res.message);
        setResult(res);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [files]);
  return (
    <>
      {isLoading && <LoadingPage />}
      {!result && (
        <div className='flex flex-col gap-6 h-full my-auto'>
          <ImageInput setFiles={setFiles} files={files} className='w-full h-full' />
          <Button onClick={handleAnalyze} disabled={isLoading}>
            <PlusIcon />
            분석하기
          </Button>
        </div>
      )}
      {!isLoading && result && (
        <div className='flex flex-col gap-6 items-center'>
          <h1 className='text-2xl font-bold'>체형 분석 결과</h1>
          <AspectRatio ratio={16 / 9}>
            <Image
              src={result.body_type_image_url}
              alt='체형 이미지'
              className='w-full h-full object-contain'
            />
          </AspectRatio>
          <h2 className='text-2xl font-bold'>
            {BODY_TYPE_DESCRIPTIONS[result.predicted_body_type].title}
          </h2>
          <p className='text-sm text-gray-500'>
            {BODY_TYPE_DESCRIPTIONS[result.predicted_body_type].description}
          </p>
          <h3 className='text-2xl font-bold'>추천 운동</h3>
          <ExerciseList items={result.recommendations} onItemClick={handleItemClick} />
        </div>
      )}
    </>
  );
}

export default UserBodyAnalysisPage;
