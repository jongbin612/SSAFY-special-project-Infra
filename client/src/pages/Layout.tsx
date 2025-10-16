import { Outlet } from 'react-router-dom';
import Navbar from '@components/common/Navbar';
import Tabbar from '@components/common/Tabbar';
import { useEffect } from 'react';
import useUserStore from '@/stores/userStore';
import { useNavigate } from 'react-router-dom';

function Layout() {
  const navigate = useNavigate();

  useEffect(() => {
    useUserStore
      .getState()
      .checkLogin()
      .catch(() => {
        useUserStore.getState().logout();
        navigate('/login');
      });
  }, [navigate]);

  return (
    <main className='min-h-screen max-w-[480px] min-w-[375px] w-full mx-auto bg-gray-50 flex flex-col'>
      <Navbar />
      <div className='p-4 pb-20 w-full flex-1 flex flex-col'>
        <Outlet />
      </div>
      <Tabbar />
    </main>
  );
}

export default Layout;
