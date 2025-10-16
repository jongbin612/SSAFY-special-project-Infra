// client/src/pages/MyPage.tsx
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import useUserStore from '@/stores/userStore';
import { me } from '@apis/account';
import { Card, CardContent } from '@/components/ui/card';
import Image from '@/components/common/Image';
import welcome from '@/assets/welcome-coach.png';

const Row: React.FC<{ label: string; value?: React.ReactNode }> = ({ label, value }) => (
  <div className='flex items-center justify-between py-3'>
    <span className='text-sm text-muted-foreground'>{label}</span>
    <span className='text-base font-medium'>{value ?? '-'}</span>
  </div>
);

const formatDate = (iso?: string) => {
  if (!iso) return '-';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}.${m}.${day}`;
};

const MyPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, setUser, isLogin, logout, checkLogin } = useUserStore();
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const token = await checkLogin();
        if (!token) {
          navigate('/login');
          return;
        }
        const u = await me();
        setUser(u);
      } catch {
        logout();
        navigate('/login');
      } finally {
        setLoading(false);
      }
    })();
  }, [checkLogin, navigate, setUser, logout]);

  if (loading) {
    return (
      <div className='flex flex-col gap-6'>
        <div className='animate-pulse h-[160px] rounded-2xl bg-gray-100' />
        <div className='animate-pulse h-[280px] rounded-2xl bg-gray-100' />
      </div>
    );
  }

  if (!isLogin || !user) return null;

  return (
    <div className='flex flex-col gap-4'>
      <section className='flex flex-col items-center text-center'>
        <Image src={welcome} alt='welcome' className='w-full max-h-64 object-contain' />
        <h1 className='mt-4 text-2xl font-bold'>안녕하세요, {user.name}님!</h1>
        <p className='text-sm text-muted-foreground mt-1'>오늘도 가볍게 몸을 풀어볼까요?</p>
      </section>

      {/* 프로필 카드 */}
      <Card className='py-4'>
        <CardContent>
          <div className='flex items-center gap-4 mb-2'>
            <div className='size-16 overflow-hidden rounded-full border bg-muted'>
              <Image
                src={user.profile_image_url || welcome}
                alt='profile'
                className='size-full object-cover'
              />
            </div>
            <div className='flex-1'>
              <div className='text-lg font-semibold'>{user.name}</div>
              <div className='text-xs text-muted-foreground'>{user.email}</div>
            </div>
          </div>

          <hr className='my-2' />

          <Row label='생년월일' value={formatDate(user.birth_date)} />
          <Row label='성별' value={user.gender || '-'} />
          <Row label='키' value={user.height ? `${user.height} cm` : '-'} />
          <Row label='몸무게' value={user.weight ? `${user.weight} kg` : '-'} />
          <Row label='가입일' value={formatDate(user.created_at)} />
        </CardContent>
      </Card>
    </div>
  );
};

export default MyPage;
