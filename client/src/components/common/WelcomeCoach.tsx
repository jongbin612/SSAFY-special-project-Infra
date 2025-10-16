// client/src/components/common/WelcomeCoach.tsx
import * as React from 'react';

interface WelcomeCoachProps {
  imageSrc: string;
  title?: string;
  subtitle?: string;
  className?: string;
  align?: 'center' | 'left'; // 기본 center
  imgHeight?: string;
}

const WelcomeCoach: React.FC<WelcomeCoachProps> = ({
  imageSrc,
  title = '환영합니다!',
  subtitle = '오늘도 가볍게 몸을 풀어볼까요?',
  className = '',
  align = 'center',
  imgHeight, // 주면 이 값 우선 적용
}) => {
  const alignClasses = align === 'left' ? 'items-start text-left' : 'items-center text-center';

  const defaultImgClasses = 'h-32 md:h-40 lg:h-48';
  const imgClasses = imgHeight ? imgHeight : defaultImgClasses;

  return (
    <section className={`flex flex-col ${alignClasses} ${className}`}>
      {/* 이미지: 위 (좀 더 크게) */}
      <img
        src={imageSrc}
        alt=''
        aria-hidden='true'
        className={`${imgClasses} w-auto max-w-full select-none`}
        loading='eager'
        decoding='async'
      />

      {/* 텍스트: 아래 */}
      <h1 className='mt-3 text-2xl font-bold leading-tight tracking-tight md:text-3xl'>{title}</h1>

      {subtitle && <p className='mt-1 text-sm text-muted-foreground md:text-base'>{subtitle}</p>}
    </section>
  );
};

export default React.memo(WelcomeCoach);
