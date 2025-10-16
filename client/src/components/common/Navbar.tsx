import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeftIcon } from 'lucide-react';
import { Button } from '@components/ui/button';
import useUserStore from '@/stores/userStore';
import { toast } from 'sonner';
import logo from '@assets/logo.png';
function Navbar() {
  const navigate = useNavigate();
  const isLogin = useUserStore.getState().isLogin;
  const handleGoBack = () => {
    void navigate(-1);
  };

  const handleBackKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleGoBack();
    }
  };

  const isMain = useLocation().pathname === '/';

  return (
    <div className='flex items-center justify-between py-3 px-2 border-gray-200'>
      {!isMain && (
        <Button
          variant='ghost'
          onClick={handleGoBack}
          onKeyDown={handleBackKeyDown}
          tabIndex={0}
          aria-label='이전 페이지로 돌아가기'
          className='flex items-center justify-center w-10 h-10 rounded-full'
        >
          <ArrowLeftIcon />
        </Button>
      )}
      <Button
        onClick={() => {
          navigate('/');
        }}
        variant='link'
        className='mr-auto flex items-center justify-center gap-2 text-primary-60'
      >
        <img src={logo} alt='logo' className='text-chart-2 w-8 h-8' />
        <h1 className='text-lg font-bold'>HPT</h1>
      </Button>
      {isLogin ? (
        <Button
          variant='link'
          onClick={() => {
            useUserStore.getState().logout();
            toast.success('로그아웃 성공');
            navigate('/login');
          }}
        >
          로그아웃
        </Button>
      ) : (
        <Button
          variant='link'
          onClick={() => {
            navigate('/login');
          }}
        >
          로그인
        </Button>
      )}
    </div>
  );
}

export default Navbar;
