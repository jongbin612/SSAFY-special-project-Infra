import { AspectRatio } from '@radix-ui/react-aspect-ratio';
import { Badge } from '@/components/ui/badge';
import Image from '@/components/common/Image';

interface ExerciseDetailUiProps {
  thumbnail: string;
  title: string;
  category: string;
  target: string;
  howToWork: string;
  calory: string;
}

function ExerciseDetailUi({
  thumbnail,
  title,
  category,
  target,
  howToWork,
  calory,
}: ExerciseDetailUiProps) {
  return (
    <div className='flex flex-col gap-4'>
      <AspectRatio ratio={16 / 9}>
        <Image
          src={thumbnail}
          alt={title}
          className='w-full h-full object-contain'
          loading='lazy'
        />
      </AspectRatio>
      <div className='flex justify-between items-center gap-2'>
        <h2 className='text-2xl font-bold'>{title}</h2>
        <Badge variant='secondary' className='bg-chart-2/20'>
          {category} 운동
        </Badge>
      </div>
      <div className='flex flex-col gap-2'>
        <h3 className='text-lg font-bold'>소모 칼로리</h3>
        <p className='text-sm text-gray-500'>1회 {calory}kcal</p>
      </div>
      <div className='flex flex-col gap-2'>
        <h3 className='text-lg font-bold'>타겟 부위</h3>
        <AspectRatio ratio={16 / 9}>
          <Image
            src={target}
            alt={'운동 타겟 부위'}
            className='w-full h-full object-contain'
            loading='lazy'
          />
        </AspectRatio>
      </div>
      <div className='flex flex-col gap-2'>
        <h3 className='text-lg font-bold'>운동 방법</h3>
        <AspectRatio ratio={16 / 9}>
          <Image
            src={howToWork}
            alt={'운동 방법'}
            className='w-full h-full object-contain'
            loading='lazy'
          />
        </AspectRatio>
      </div>
    </div>
  );
}

export default ExerciseDetailUi;
