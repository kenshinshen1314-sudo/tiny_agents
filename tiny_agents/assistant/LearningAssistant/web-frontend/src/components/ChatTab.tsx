import { useState, useRef, useEffect } from 'react';
import { useAssistant } from '../hooks/useAssistant';
import { Send, Loader2, User, Bot, FileText, Sparkle, Lightbulb } from 'lucide-react';

const EXAMPLES = [
  '文档的主要内容是什么？',
  '总结一下这个文档的核心观点',
  '文档中提到了哪些关键技术？',
  '解释一下文档中的这个概念...',
];

export function ChatTab() {
  const {
    messages,
    isAsking,
    loadedDocument,
    askQuestion,
    suggestions,
    getSuggestions,
    isLoadingSuggestions,
  } = useAssistant();

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 加载建议问题
  useEffect(() => {
    if (loadedDocument && !isLoadingSuggestions && suggestions.length === 0) {
      getSuggestions();
    }
  }, [loadedDocument, isLoadingSuggestions, suggestions.length, getSuggestions]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isAsking) return;

    const question = input.trim();
    setInput('');
    await askQuestion(question);
  };

  const handleExampleClick = (example: string) => {
    setInput(example);
  };

  if (!loadedDocument) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center text-slate-500">
          <div className="w-16 h-16 rounded-2xl bg-slate-800/50 flex items-center justify-center mx-auto mb-4">
            <FileText className="w-8 h-8 text-slate-600" />
          </div>
          <p className="text-lg mb-2">请先加载文档</p>
          <p className="text-sm text-slate-600">切换到"初始化"标签页上传并加载 PDF 文档</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto h-[500px] flex flex-col">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto bg-slate-900/50 backdrop-blur-sm rounded-t-2xl border border-slate-700/50 p-4 space-y-4 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            {/* 空状态图标 */}
            <div className="relative w-20 h-20 mx-auto mb-6">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-teal-500/20 rounded-full blur-xl animate-pulse" />
              <div className="relative w-20 h-20 rounded-full bg-slate-800/80 backdrop-blur-sm flex items-center justify-center border border-slate-700/50">
                <Sparkle className="w-10 h-10 text-cyan-400" />
              </div>
            </div>
            <p className="text-lg font-medium text-slate-300 mb-2">开始与文档对话</p>
            <p className="text-sm text-slate-500 mb-6">选择一个问题开始，或输入您自己的问题</p>

            {/* 示例问题 */}
            <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
              {EXAMPLES.map((example, idx) => (
                <button
                  key={example}
                  onClick={() => handleExampleClick(example)}
                  className="px-4 py-2 text-sm bg-cyan-600/10 hover:bg-cyan-600/30 border border-cyan-500/30 hover:border-cyan-400/50 rounded-full text-cyan-200 hover:text-white transition-all duration-200 hover:scale-105 active:scale-95 shadow-lg shadow-cyan-500/10"
                  style={{ animation: `fade-in-up 0.3s ease-out ${idx * 0.1}s both` }}
                >
                  {example}
                </button>
              ))}
            </div>

            {/* 智能建议问题 */}
            {suggestions.length > 0 && (
              <div className="mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center justify-center gap-2 mb-4">
                  <Lightbulb className="w-5 h-5 text-amber-400" />
                  <span className="text-sm font-medium text-amber-200">你可能想问</span>
                </div>
                <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
                  {suggestions.map((suggestion, idx) => (
                    <button
                      key={suggestion}
                      onClick={() => handleExampleClick(suggestion)}
                      className="px-3 py-2 text-xs bg-amber-600/10 hover:bg-amber-600/25 border border-amber-500/30 hover:border-amber-400/50 rounded-lg text-amber-100 hover:text-white transition-all duration-200 hover:scale-105 active:scale-95 shadow-md"
                      style={{ animation: `fade-in-up 0.3s ease-out ${0.4 + idx * 0.08}s both` }}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`
                flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}
                animate-in fade-in slide-in-from-bottom-2 duration-300
              `}
            >
              <div
                className={`
                  flex gap-3 max-w-[85%]
                  ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}
                `}
              >
                {/* 头像 */}
                <div
                  className={`
                    w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 border
                    ${message.role === 'user'
                      ? 'bg-gradient-to-br from-cyan-600 to-teal-600 border-cyan-500/30 shadow-lg shadow-cyan-500/20'
                      : 'bg-slate-800/80 backdrop-blur-sm border-slate-700/50'
                    }
                  `}
                >
                  {message.role === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-cyan-400" />
                  )}
                </div>

                {/* 消息内容 */}
                <div
                  className={`
                    px-4 py-3 rounded-2xl text-sm leading-relaxed
                    ${message.role === 'user'
                      ? 'bg-gradient-to-br from-cyan-600 to-teal-600 text-white shadow-lg shadow-cyan-500/20 rounded-tr-sm'
                      : 'bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 text-slate-200 rounded-tl-sm'
                    }
                  `}
                >
                  <p className="whitespace-pre-wrap break-words">{message.content}</p>
                </div>
              </div>
            </div>
          ))
        )}

        {/* 正在输入指示器 */}
        {isAsking && (
          <div className="flex justify-start animate-in fade-in slide-in-from-left-2 duration-300">
            <div className="flex gap-3">
              <div className="w-9 h-9 rounded-xl bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 flex items-center justify-center">
                <Bot className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                  <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse delay-100" />
                  <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse delay-200" />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />

        {/* 消息后的建议问题 */}
        {messages.length > 0 && suggestions.length > 0 && !isAsking && (
          <div className="mt-4 pt-4 border-t border-slate-700/50 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-medium text-slate-400">你可能想问</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((suggestion, idx) => (
                <button
                  key={suggestion}
                  onClick={() => handleExampleClick(suggestion)}
                  className="px-3 py-1.5 text-xs bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 hover:border-slate-600/50 rounded-md text-slate-300 hover:text-white transition-all duration-200 hover:scale-105 active:scale-95"
                  style={{ animation: `fade-in-up 0.2s ease-out ${idx * 0.05}s both` }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 输入框 */}
      <form onSubmit={handleSubmit} className="bg-slate-900/50 backdrop-blur-sm rounded-b-2xl border border-t-0 border-slate-700/50 p-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入您的问题..."
            disabled={isAsking}
            className="flex-1 px-4 py-3 bg-slate-900/80 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-transparent disabled:bg-slate-900/30 text-white placeholder:text-slate-500 transition-all duration-200"
          />
          <button
            type="submit"
            disabled={!input.trim() || isAsking}
            className={`
              px-5 py-3 rounded-xl font-medium transition-all duration-300 flex items-center gap-2 relative overflow-hidden group
              ${!input.trim() || isAsking
                ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-cyan-600 to-teal-600 text-white hover:shadow-lg hover:shadow-cyan-500/30 hover:scale-105 active:scale-95'
              }
            `}
          >
            {/* 光泽效果 */}
            {!isAsking && input.trim() && (
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
            )}
            {isAsking ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            <span className="hidden sm:inline">发送</span>
          </button>
        </div>
      </form>
    </div>
  );
}
