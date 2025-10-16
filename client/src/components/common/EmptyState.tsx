import * as React from 'react';
import { AlertTriangle, Dumbbell } from 'lucide-react';
import { cn } from '@/lib/utils'; // shadcn 프로젝트에 보통 있음 (없으면 optional)
import { Button } from '@/components/ui/button';

interface Props {
  title?: string;
  description?: string;
  icon?: 'alert' | 'dumbbell';
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

const EmptyState: React.FC<Props> = ({
  title = '준비중입니다.',
  description = '해당 부위의 운동은 아직 준비 중이에요. 다른 탭을 선택해보세요.',
  icon = 'alert',
  actionLabel,
  onAction,
  className,
}) => {
  const Icon = icon === 'dumbbell' ? Dumbbell : AlertTriangle;

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center',
        className,
      )}
    >
      <div className='flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-sm'>
        <Icon className='h-6 w-6 text-gray-700' />
      </div>
      <div>
        <h4 className='text-base font-semibold text-gray-900'>{title}</h4>
        <p className='mt-1 text-sm text-gray-600'>{description}</p>
      </div>

      {actionLabel && onAction && (
        <Button variant='secondary' size='sm' className='mt-2' onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
