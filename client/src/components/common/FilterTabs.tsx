// client/src/components/common/FilterTabs.tsx
import * as React from 'react';
type Tab = '전체' | '가슴' | '등' | '어깨' | '하체' | '복근';

interface Props {
  tabs: Tab[];
  value: Tab;
  onChange: (val: Tab) => void;
  className?: string;
}

const FilterTabsBase: React.FC<Props> = ({ tabs, value, onChange, className }) => {
  const onChangeStable = React.useCallback(onChange, [onChange]);

  return (
    <nav className={`text-sm ${className ?? ''}`} role='tablist' aria-label='운동 부위'>
      <ul className='flex gap-2 flex-wrap'>
        {tabs.map((t) => {
          const active = t === value;
          return (
            <li key={t}>
              <button
                type='button'
                role='tab'
                aria-selected={active}
                onClick={() => onChangeStable(t)}
                className={
                  'px-3 py-1.5 rounded-full transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-border ' +
                  (active
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200')
                }
              >
                {t}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export default React.memo(FilterTabsBase);
