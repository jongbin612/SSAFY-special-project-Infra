import { Skeleton } from '@/components/ui/skeleton';
import { AspectRatio } from '@radix-ui/react-aspect-ratio';
function SkeletonExerciseDetail() {
  return (
    <div className='flex flex-col space-y-4'>
      <AspectRatio ratio={16 / 9}>
        <Skeleton className='w-full h-full' />
      </AspectRatio>
      <div className='flex justify-between items-center space-x-2'>
        <Skeleton className='w-30 h-8' />
        <Skeleton className='w-10 h-6' />
      </div>
      <div className='flex flex-col space-y-2'>
        <Skeleton className='w-20 h-6' />
        <Skeleton className='w-10 h-5' />
      </div>
      <div className='flex flex-col space-y-2'>
        <Skeleton className='w-20 h-6' />
        <AspectRatio ratio={16 / 9}>
          <Skeleton className='w-full h-full' />
        </AspectRatio>
      </div>
      <div className='flex flex-col space-y-2'>
        <Skeleton className='w-20 h-6' />
        <AspectRatio ratio={16 / 9}>
          <Skeleton className='w-full h-full' />
        </AspectRatio>
      </div>
    </div>
  );
}

export default SkeletonExerciseDetail;
