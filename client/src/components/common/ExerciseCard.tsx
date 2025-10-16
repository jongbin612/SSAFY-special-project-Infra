// client/src/components/common/ExerciseCard.tsx
import * as React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import notFound from '@/assets/notFound.png';

interface Props {
  image?: string | null;
  name: string;
  kcalPerHour: number;
  onClick?: () => void;
  className?: string;
  aspectClass?: string;
}

const ExerciseCardBase: React.FC<Props> = ({
  image,
  name,
  kcalPerHour,
  onClick,
  className = '',
  aspectClass = 'aspect-[16/9]',
}) => {
  const [imgSrc, setImgSrc] = React.useState<string>(image && image.trim() ? image : notFound);

  // prop이 바뀌면 다시 반영
  React.useEffect(() => {
    setImgSrc(image && image.trim() ? image : notFound);
  }, [image]);

  const handleImgError = React.useCallback((e: React.SyntheticEvent<HTMLImageElement>) => {
    if (e.currentTarget.src !== notFound) {
      setImgSrc(notFound); // 무한루프 방지
    }
  }, []);

  return (
    <Card
      role='button'
      tabIndex={0}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onClick?.()}
      onClick={onClick}
      className={`overflow-hidden cursor-pointer  py-0 gap-0 ${className}`}
    >
      <div className={`w-full ${aspectClass} overflow-hidden bg-accent border-b p-2`}>
        <img
          src={imgSrc}
          alt={name || 'thumbnail'}
          className='h-full w-full object-contain object-center'
          loading='lazy'
          decoding='async'
          onError={handleImgError}
        />
      </div>

      <CardContent className='px-4 py-3'>
        <div className='flex items-center justify-between'>
          <h3 className='text-xl font-semibold tracking-tight'>{name}</h3>
          <span className='text-sm text-gray-500'>{kcalPerHour}Kcal/hr</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default React.memo(ExerciseCardBase);
