// client/src/components/common/UnderlineTabs.tsx
import { cn } from '@/lib/utils';

interface Tab {
  label: string;
  value: string;
}

interface UnderlineTabsProps {
  tabs: Tab[];
  value: string;
  onChange: (v: string) => void;
  className?: string;
}

export function UnderlineTabs({ tabs, value, onChange, className }: UnderlineTabsProps) {
  return (
    <div className={cn('flex gap-6 px-4 pt-3', className)}>
      {tabs.map((t) => {
        const active = value === t.value;
        return (
          <button
            key={t.value}
            onClick={() => onChange(t.value)}
            className={cn(
              'relative pb-2 text-lg font-medium transition',
              active ? 'text-foreground' : 'text-muted-foreground',
            )}
          >
            {t.label}
            <span
              className={cn(
                'absolute left-0 -bottom-[2px] h-[2px] w-full rounded-full transition',
                active ? 'bg-foreground' : 'bg-transparent',
              )}
            />
          </button>
        );
      })}
    </div>
  );
}
