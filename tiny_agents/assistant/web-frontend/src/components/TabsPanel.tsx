import { useState } from 'react';
import { InitTab } from './InitTab';
import { ChatTab } from './ChatTab';
import { NotesTab } from './NotesTab';
import { StatsTab } from './StatsTab';

type TabValue = 'init' | 'chat' | 'notes' | 'stats';

interface TabsPanelProps {
  onTabChange?: (tab: TabValue) => void;
}

export function TabsPanel({ onTabChange }: TabsPanelProps) {
  const [activeTab, setActiveTab] = useState<TabValue>('init');

  const handleTabChange = (tab: TabValue) => {
    setActiveTab(tab);
    onTabChange?.(tab);
  };

  const tabs = [
    { value: 'init' as const, label: '初始化', icon: '🚀', shortLabel: '初始化' },
    { value: 'chat' as const, label: '智能问答', icon: '💬', shortLabel: '问答' },
    { value: 'notes' as const, label: '学习笔记', icon: '📝', shortLabel: '笔记' },
    { value: 'stats' as const, label: '智能统计', icon: '📊', shortLabel: '统计' },
  ];

  return (
    <div className="w-full">
      {/* Tab 导航 */}
      <div className="mb-6">
        <div className="inline-flex bg-slate-900/80 backdrop-blur-sm rounded-2xl p-1.5 border border-slate-700/50 shadow-xl">
          {tabs.map((tab, idx) => {
            const isActive = activeTab === tab.value;
            return (
              <button
                key={tab.value}
                onClick={() => handleTabChange(tab.value)}
                className={`
                  relative px-6 py-3 rounded-xl font-medium text-sm transition-all duration-300
                  ${isActive
                    ? 'text-white'
                    : 'text-slate-400 hover:text-slate-200'
                  }
                `}
                style={{
                  animation: `fade-in 0.3s ease-out ${idx * 0.05}s both`,
                }}
              >
                {/* 激活状态背景 */}
                {isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-teal-600 rounded-xl shadow-lg shadow-cyan-500/30" />
                )}

                {/* 内容 */}
                <span className="relative flex items-center gap-2">
                  <span className="text-base">{tab.icon}</span>
                  <span className="hidden sm:inline">{tab.label}</span>
                  <span className="sm:hidden">{tab.shortLabel}</span>
                </span>

                {/* 底部指示器 */}
                {isActive && (
                  <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-gradient-to-r from-transparent via-white to-transparent rounded-full" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab 内容 */}
      <div className="relative">
        {/* 内容容器背景 */}
        <div className="absolute inset-0 bg-slate-900/50 backdrop-blur-xl rounded-3xl border border-slate-700/50" />
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-teal-500/5 rounded-3xl" />

        {/* 实际内容 */}
        <div className="relative p-6 sm:p-8 min-h-[500px]">
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            {activeTab === 'init' && <InitTab />}
            {activeTab === 'chat' && <ChatTab />}
            {activeTab === 'notes' && <NotesTab />}
            {activeTab === 'stats' && <StatsTab />}
          </div>
        </div>
      </div>
    </div>
  );
}
