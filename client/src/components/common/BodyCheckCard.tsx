import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Props {
  imageSrc: string;
  title?: string;
  ctaLabel?: string;
  onCtaClick?: () => void;
  className?: string;
}

const BodyCheckCard: React.FC<Props> = ({
  imageSrc,
  title = '내 체형을 분석하여 맞춤형 운동을 추천받아보세요!',
  ctaLabel = '체형 분석하기',
  onCtaClick,
  className,
}) => {
  return (
    <Card className={'border-0 shadow-none bg-transparent text-center py-0' + (className ?? '')}>
      <img
        loading='lazy'
        src={imageSrc}
        alt='hero'
        className='mx-auto h-36 w-auto object-contain'
      />
      <p className='text-sm'>{title}</p>
      {ctaLabel && <Button onClick={onCtaClick}>{ctaLabel}</Button>}
    </Card>
  );
};

export default BodyCheckCard;
