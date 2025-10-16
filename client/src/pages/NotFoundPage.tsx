import { Link } from 'react-router-dom';
import { Button } from '@components/ui/button';
import Image from '@components/common/Image';
function NotFoundPage() {
  return (
    <div className='flex flex-col items-center justify-center h-screen gap-4 '>
      <Image src='/src/assets/notFound.png' alt='404' className='w-1/2 h-1/2' />
      <h1>404 페이지를 찾을 수 없습니다...</h1>
      <Link to='/'>
        <Button>홈으로 돌아가기</Button>
      </Link>
    </div>
  );
}

export default NotFoundPage;
