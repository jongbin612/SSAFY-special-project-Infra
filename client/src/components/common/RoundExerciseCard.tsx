// client/src/components/common/RoundExerciseCard.tsx
import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Avatar } from '@/components/ui/avatar';
import notFound from '@assets/notFound.png';
import Image from '@components/common/Image';
interface RoundExerciseCardProps {
  image?: string | null;
  name: string;
  onClick?: () => void;
  className?: string;
  /** px 단위 지름 */
  size?: number;
}

const RoundExerciseCard: React.FC<RoundExerciseCardProps> = ({
  image,
  name,
  onClick,
  className = '',
}) => {
  const src = image && image.trim() ? image : notFound;

  return (
    <div className={`flex flex-col items-center gap-2 ${className}`}>
      <Button
        type='button'
        variant='ghost'
        className='rounded-full w-full h-full p-0 shadow-sm hover:shadow transition'
        onClick={onClick}
        aria-label={name}
      >
        <Avatar className='h-full w-full bg-background'>
          <Image className='aspect-square size-full p-4' src={src} alt={name} />
        </Avatar>
      </Button>
    </div>
  );
};

export default React.memo(RoundExerciseCard);
