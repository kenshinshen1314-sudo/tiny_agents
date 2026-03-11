import { BookOpen, MessageSquare, FileText, BarChart3, Sparkles } from 'lucide-react';

export function Header() {
  return (
    <header className="relative">
      {/* 装饰线条 */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* 主标题区域 */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-3 mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full animate-pulse" />
              <div className="relative bg-gradient-to-br from-cyan-500 to-teal-600 rounded-2xl p-3 shadow-2xl shadow-cyan-500/30">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
            </div>
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight">
              <span className="bg-gradient-to-r from-cyan-200 via-white to-teal-200 bg-clip-text text-transparent">
                PDFParserAssistant
              </span>
            </h1>
          </div>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            智能文档解析助手 — 结合 RAG 检索增强生成与记忆系统，<br className="hidden sm:block" />
            为您提供深度文档理解与智能问答体验
          </p>
        </div>

        {/* 功能卡片网格 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
          {[
            { icon: FileText, label: '文档加载', color: 'from-cyan-500/20 to-blue-500/20', iconColor: 'text-cyan-400' },
            { icon: MessageSquare, label: '智能问答', color: 'from-teal-500/20 to-cyan-500/20', iconColor: 'text-teal-400' },
            { icon: BookOpen, label: '学习笔记', color: 'from-emerald-500/20 to-teal-500/20', iconColor: 'text-emerald-400' },
            { icon: BarChart3, label: '智能统计', color: 'from-amber-500/20 to-orange-500/20', iconColor: 'text-amber-400' },
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="group relative overflow-hidden rounded-xl p-4"
                style={{
                  animation: `fade-in-up 0.5s ease-out ${idx * 0.1}s both`,
                }}
              >
                {/* 背景渐变 */}
                <div className={`absolute inset-0 bg-gradient-to-br ${item.color} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
                {/* 边框光泽 */}
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                <div className="relative flex flex-col items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-slate-800/80 backdrop-blur-sm flex items-center justify-center border border-slate-700/50 group-hover:border-cyan-500/50 transition-colors duration-300">
                    <Icon className={`w-6 h-6 ${item.iconColor}`} />
                  </div>
                  <span className="text-sm font-medium text-slate-300">{item.label}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* 底部装饰线 */}
        <div className="mt-10 flex items-center justify-center gap-4">
          <div className="flex-1 h-px bg-gradient-to-r from-transparent to-slate-700/50 max-w-32" />
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            <div className="w-1 h-1 rounded-full bg-cyan-400/50" />
            <div className="w-1 h-1 rounded-full bg-cyan-400/30" />
          </div>
          <div className="flex-1 h-px bg-gradient-to-l from-transparent to-slate-700/50 max-w-32" />
        </div>
      </div>
    </header>
  );
}
