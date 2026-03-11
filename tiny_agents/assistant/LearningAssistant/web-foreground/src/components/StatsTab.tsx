import { useAssistant } from '../hooks/useAssistant';
import {
  RefreshCw,
  FileText,
  Download,
  Loader2,
  Clock,
  MessageSquare,
  BookOpen,
  BarChart,
  TrendingUp,
} from 'lucide-react';

export function StatsTab() {
  const { stats, isLoadingStats, getStats, generateReport, loadedDocument } = useAssistant();

  const statsItems = stats
    ? [
        {
          key: '会话时长',
          value: stats['会话时长'],
          icon: Clock,
          color: 'from-blue-500/20 to-sky-500/20',
          iconColor: 'text-sky-400',
          borderColor: 'border-sky-500/30',
        },
        {
          key: '加载文档',
          value: stats['加载文档'],
          icon: FileText,
          color: 'from-emerald-500/20 to-teal-500/20',
          iconColor: 'text-emerald-400',
          borderColor: 'border-emerald-500/30',
        },
        {
          key: '提问次数',
          value: stats['提问次数'],
          icon: MessageSquare,
          color: 'from-teal-500/20 to-cyan-500/20',
          iconColor: 'text-teal-400',
          borderColor: 'border-teal-500/30',
        },
        {
          key: '学习笔记',
          value: stats['学习笔记'],
          icon: BookOpen,
          color: 'from-amber-500/20 to-orange-500/20',
          iconColor: 'text-amber-400',
          borderColor: 'border-amber-500/30',
        },
      ]
    : [];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 操作按钮 */}
      <div className="flex flex-col sm:flex-row gap-4">
        <button
          onClick={getStats}
          disabled={isLoadingStats}
          className={`
            flex-1 py-4 px-6 rounded-xl font-medium transition-all duration-300 flex items-center justify-center gap-2 relative overflow-hidden group
            ${isLoadingStats
              ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-cyan-600 to-teal-600 text-white hover:shadow-lg hover:shadow-cyan-500/30 hover:scale-[1.02] active:scale-[0.98]'
            }
          `}
        >
          {isLoadingStats ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              刷新中...
            </>
          ) : (
            <>
              <RefreshCw className="w-5 h-5" />
              实时刷新
            </>
          )}
        </button>

        <button
          onClick={generateReport}
          disabled={!stats}
          className={`
            flex-1 py-4 px-6 rounded-xl font-medium transition-all duration-300 flex items-center justify-center gap-2 relative overflow-hidden group
            ${!stats
              ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white hover:shadow-lg hover:shadow-emerald-500/30 hover:scale-[1.02] active:scale-[0.98]'
            }
          `}
        >
          <Download className="w-5 h-5" />
          生成报告
        </button>
      </div>

      {/* 统计卡片网格 */}
      {statsItems.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {statsItems.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={item.key}
                className="relative overflow-hidden rounded-2xl bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 p-5 group hover:scale-105 transition-transform duration-300"
                style={{ animation: `fade-in-up 0.4s ease-out ${idx * 0.1}s both` }}
              >
                {/* 背景渐变 */}
                <div className={`absolute inset-0 bg-gradient-to-br ${item.color} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />

                {/* 内容 */}
                <div className="relative">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center mb-4 border ${item.borderColor}`}>
                    <Icon className={`w-6 h-6 ${item.iconColor}`} />
                  </div>
                  <p className="text-3xl font-bold text-white mb-1">{item.value}</p>
                  <p className="text-sm text-slate-400">{item.key}</p>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700/50 p-12 text-center animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-slate-900/50 flex items-center justify-center mx-auto mb-4">
            <BarChart className="w-8 h-8 text-slate-600" />
          </div>
          <p className="text-slate-500 mb-2">暂无统计数据</p>
          <p className="text-sm text-slate-600">点击"实时刷新"按钮获取统计信息</p>
        </div>
      )}

      {/* 当前文档状态 */}
      {loadedDocument && (
        <div className="bg-gradient-to-r from-cyan-950/50 to-teal-950/50 backdrop-blur-sm rounded-2xl border border-cyan-500/30 p-5 flex items-center gap-4 animate-fade-in-up">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center border border-cyan-500/30">
            <FileText className="w-6 h-6 text-cyan-400" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-cyan-200">当前文档</p>
            <p className="text-xs text-cyan-400/80 mt-0.5">{loadedDocument}</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center border border-cyan-500/30">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
          </div>
        </div>
      )}

      {/* 说明卡片 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm border border-slate-700/50 p-6">
        {/* 装饰图标 */}
        <div className="absolute top-4 right-4 opacity-10">
          <BarChart className="w-24 h-24 text-slate-400" />
        </div>

        <div className="relative">
          <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            统计说明
          </h3>
          <div className="grid sm:grid-cols-2 gap-4 text-sm text-slate-400">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-sky-500/20 flex items-center justify-center flex-shrink-0">
                <Clock className="w-4 h-4 text-sky-400" />
              </div>
              <div>
                <p className="text-slate-300 font-medium">会话时长</p>
                <p className="text-xs text-slate-500 mt-1">自初始化以来的时间</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                <FileText className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <p className="text-slate-300 font-medium">加载文档</p>
                <p className="text-xs text-slate-500 mt-1">已加载到知识库的文档数</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-teal-500/20 flex items-center justify-center flex-shrink-0">
                <MessageSquare className="w-4 h-4 text-teal-400" />
              </div>
              <div>
                <p className="text-slate-300 font-medium">提问次数</p>
                <p className="text-xs text-slate-500 mt-1">进行的问答次数</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                <BookOpen className="w-4 h-4 text-amber-400" />
              </div>
              <div>
                <p className="text-slate-300 font-medium">学习笔记</p>
                <p className="text-xs text-slate-500 mt-1">保存的笔记数量</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
