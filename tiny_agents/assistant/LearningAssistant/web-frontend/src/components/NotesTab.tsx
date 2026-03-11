import { useState } from 'react';
import { useAssistant } from '../hooks/useAssistant';
import { Save, Loader2, Plus, FileText, Clock, Lightbulb } from 'lucide-react';

export function NotesTab() {
  const { notes, addNote, isSavingNote } = useAssistant();

  const [content, setContent] = useState('');
  const [concept, setConcept] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    await addNote(content.trim(), concept.trim() || undefined);
    setContent('');
    setConcept('');
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="grid lg:grid-cols-2 gap-6">
        {/* 添加笔记表单 */}
        <div className="relative overflow-hidden rounded-2xl bg-slate-800/50 backdrop-blur-sm border border-slate-700/50">
          <div className="h-1 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500" />

          <div className="p-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center">
                <Plus className="w-5 h-5 text-emerald-400" />
              </div>
              添加笔记
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="note-content" className="block text-sm font-medium text-slate-300 mb-2">
                  笔记内容
                </label>
                <textarea
                  id="note-content"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="记录您的学习心得..."
                  rows={6}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-cyan-600/50 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-none text-white placeholder:text-slate-500 transition-all duration-200"
                />
              </div>

              <div>
                <label htmlFor="note-concept" className="block text-sm font-medium text-slate-300 mb-2">
                  相关概念（可选）
                </label>
                <input
                  id="note-concept"
                  type="text"
                  value={concept}
                  onChange={(e) => setConcept(e.target.value)}
                  placeholder="例如：机器学习、深度学习..."
                  className="w-full px-4 py-3 bg-slate-900/50 border border-cyan-600/50 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white placeholder:text-slate-500 transition-all duration-200"
                />
              </div>

              <button
                type="submit"
                disabled={!content.trim() || isSavingNote}
                className={`
                  w-full py-3.5 px-4 rounded-xl font-medium transition-all duration-300 flex items-center justify-center gap-2 relative overflow-hidden group
                  ${!content.trim() || isSavingNote
                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white hover:shadow-lg hover:shadow-emerald-500/30 hover:scale-[1.02] active:scale-[0.98]'
                  }
                `}
              >
                {isSavingNote ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5" />
                    保存笔记
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* 笔记列表 */}
        <div className="relative overflow-hidden rounded-2xl bg-slate-800/50 backdrop-blur-sm border border-slate-700/50">
          <div className="h-1 bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500" />

          <div className="p-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 flex items-center justify-center">
                <FileText className="w-5 h-5 text-amber-400" />
              </div>
              笔记列表 ({notes.length})
            </h2>

            <div className="space-y-3 max-h-[420px] overflow-y-auto scrollbar-thin pr-2">
              {notes.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 rounded-2xl bg-slate-800/50 flex items-center justify-center mx-auto mb-4">
                    <Lightbulb className="w-8 h-8 text-slate-600" />
                  </div>
                  <p className="text-slate-500 mb-1">还没有笔记</p>
                  <p className="text-sm text-slate-600">开始记录您的学习吧！</p>
                </div>
              ) : (
                [...notes].reverse().map((note, idx) => (
                  <div
                    key={note.id}
                    className="bg-slate-900/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50 hover:border-cyan-500/50 transition-all duration-200 group animate-fade-in-up"
                    style={{ animationDelay: `${idx * 0.05}s` }}
                  >
                    {/* 概念标签 */}
                    {note.concept && (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-medium rounded-full mb-3">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                        {note.concept}
                      </span>
                    )}

                    {/* 笔记内容 */}
                    <p className="text-sm text-slate-200 mb-3 leading-relaxed">{note.content}</p>

                    {/* 时间戳 */}
                    <div className="flex items-center gap-1.5 text-xs text-slate-500">
                      <Clock className="w-3 h-3" />
                      <span>{formatDate(note.timestamp)}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
