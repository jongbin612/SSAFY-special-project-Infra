import { Tabs, TabsList, TabsTrigger } from '@components/ui/tabs';
import { useLocation, Link } from 'react-router-dom';
import { HomeIcon, DumbbellIcon, UserIcon } from 'lucide-react';
import { useMemo } from 'react';

const TAB_LIST = [
  {
    value: 'home',
    label: '홈',
    path: '/',
    icon: <HomeIcon />,
  },
  {
    value: 'exercise',
    label: '운동',
    path: '/exercise',
    icon: <DumbbellIcon />,
  },
  {
    value: 'mky_page',
    label: '마이페이지',
    path: '/my_page',
    icon: <UserIcon />,
  },
];

function Tabbar() {
  const location = useLocation();
  const pathname = location.pathname;

  // 현재 경로에 따라 활성 탭을 결정하는 로직
  const activeTab = useMemo(() => {
    // 정확한 경로 매칭을 위한 함수
    const getTabFromPath = (path: string): string => {
      // 루트 경로
      if (path === '/') {
        return 'home';
      }

      // TAB_LIST에서 매칭되는 탭 찾기 (가장 긴 경로부터 매칭)
      const sortedTabs = [...TAB_LIST].sort((a, b) => b.path.length - a.path.length);

      for (const tab of sortedTabs) {
        if (tab.path !== '/' && path.startsWith(tab.path)) {
          return tab.value;
        }
      }

      // 매칭되는 탭이 없으면 첫 번째 세그먼트로 판단
      const firstSegment = path.split('/')[1];
      return firstSegment || 'home';
    };

    return getTabFromPath(pathname);
  }, [pathname]);

  return (
    <Tabs value={activeTab} className='fixed bottom-0 w-full max-w-[480px] min-w-[375px]'>
      <TabsList className='w-full rounded-none p-2  bg-white shadow h-fit'>
        {TAB_LIST.map((item) => (
          <TabsTrigger
            key={item.value}
            value={item.value}
            className='h-fit p-0 data-[state=active]:border-chart-2 data-[state=active]:text-chart-2'
          >
            <Link
              to={item.path}
              className='flex flex-col items-center justify-center p-2  gap-1 w-full h-full'
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
}

export default Tabbar;
