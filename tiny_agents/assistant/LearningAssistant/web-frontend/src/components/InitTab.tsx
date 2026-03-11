import { useState } from 'react';
import { useAssistant } from '../hooks/useAssistant';
import {
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
  Rocket,
  X,
  UploadCloud,
  File,
} from 'lucide-react';

export function InitTab() {
  const {
    userId,
    setUserId,
    isInitialized,
    initialize,
    uploadPDF,
    loadDocument,
    getSuggestions,
    uploadedFileName,
    loadedDocument,
    isLoadingDocument,
    error,
    clearError,
  } = useAssistant();

  const [isInitializing, setIsInitializing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleInitialize = async () => {
    setIsInitializing(true);
    await initialize();
    setIsInitializing(false);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('请选择 PDF 文件');
      return;
    }

    setIsUploading(true);
    clearError();
    await uploadPDF(file);
    setIsUploading(false);
  };

  const handleLoadDocument = async () => {
    await loadDocument();
    // 文档加载完成后，获取建议问题
    getSuggestions();
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* 错误提示 */}
      {error && (
        <div className="bg-red-950/50 backdrop-blur-sm border border-red-500/30 rounded-xl p-4 flex items-start gap-3 animate-in fade-in slide-in-from-top-4 duration-300">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-red-300 font-medium text-sm">错误</p>
            <p className="text-red-400/80 text-sm mt-1">{error}</p>
          </div>
          <button
            onClick={clearError}
            className="text-red-400/60 hover:text-red-400 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* 助手初始化 */}
      <div className="relative overflow-hidden rounded-2xl bg-slate-800/50 backdrop-blur-sm border border-slate-700/50">
        {/* 顶部装饰 */}
        <div className="h-1 bg-gradient-to-r from-cyan-500 via-teal-500 to-cyan-500" />

        <div className="p-6">
          <h2 className="text-lg font-semibold text-white flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-teal-500/20 flex items-center justify-center">
              <Rocket className="w-5 h-5 text-cyan-400" />
            </div>
            助手初始化
          </h2>

          <div className="space-y-4">
            <div>
              <label htmlFor="user-id" className="block text-sm font-medium text-slate-300 mb-2">
                用户 ID
              </label>
              <input
                id="user-id"
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                disabled={isInitialized}
                placeholder="输入您的用户 ID"
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-transparent disabled:bg-slate-900/30 disabled:cursor-not-allowed text-white placeholder:text-slate-500 transition-all duration-200"
              />
            </div>

            <button
              onClick={handleInitialize}
              disabled={!userId || isInitialized || isInitializing}
              className={`
                w-full py-3.5 px-4 rounded-xl font-medium transition-all duration-300 flex items-center justify-center gap-2 relative overflow-hidden group
                ${!userId || isInitialized || isInitializing
                  ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-cyan-600 to-teal-600 text-white hover:shadow-lg hover:shadow-cyan-500/30 hover:scale-[1.02] active:scale-[0.98]'
                }
              `}
            >
              {/* 光泽效果 */}
              {!isInitialized && !isInitializing && userId && (
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
              )}

              {isInitializing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  初始化中...
                </>
              ) : isInitialized ? (
                <>
                  <CheckCircle className="w-5 h-5" />
                  已初始化
                </>
              ) : (
                <>
                  <Rocket className="w-5 h-5" />
                  初始化助手
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* PDF 上传 */}
      <div className="relative overflow-hidden rounded-2xl bg-slate-800/50 backdrop-blur-sm border border-slate-700/50">
        <div className="h-1 bg-gradient-to-r from-cyan-500 via-blue-500 to-cyan-500" />

        <div className="p-6">
          <h2 className="text-lg font-semibold text-white flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center">
              <Upload className="w-5 h-5 text-cyan-400" />
            </div>
            上传 PDF 文档
          </h2>

          <div className="space-y-4">
            {/* 上传区域 */}
            <div className={`
              relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300
              ${!isInitialized
                ? 'border-slate-700/50 opacity-50 cursor-not-allowed bg-slate-900/30'
                : 'border-slate-600/50 hover:border-cyan-500/50 hover:bg-slate-900/30 group'
              }
            `}>
              <input
                id="pdf-upload"
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                disabled={isUploading || !isInitialized}
                className="hidden"
              />
              <label
                htmlFor="pdf-upload"
                className={`
                  cursor-pointer inline-flex flex-col items-center transition-all duration-300
                  ${!isInitialized ? 'pointer-events-none' : 'group'}
                `}
              >
                <div className={`
                  w-16 h-16 rounded-2xl flex items-center justify-center mb-4 transition-all duration-300
                  ${!isInitialized
                    ? 'bg-slate-800'
                    : 'bg-slate-800 group-hover:bg-cyan-600 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-cyan-500/30'
                  }
                `}>
                  <UploadCloud className={`w-8 h-8 transition-colors duration-300 ${!isInitialized ? 'text-slate-600' : 'text-slate-400 group-hover:text-white'}`} />
                </div>
                <span className={`text-sm font-medium mb-1 transition-colors duration-300 ${!isInitialized ? 'text-slate-500' : 'text-slate-300 group-hover:text-white'}`}>
                  {isUploading ? '上传中...' : '点击选择 PDF 文件'}
                </span>
                <span className="text-xs text-slate-500">支持 .pdf 格式</span>
              </label>
            </div>

            {/* 已上传文件 */}
            {uploadedFileName && (
              <div className="bg-emerald-950/50 backdrop-blur-sm border border-emerald-500/30 rounded-xl p-4 flex items-center gap-3 animate-in fade-in slide-in-from-left-4 duration-300">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                  <File className="w-5 h-5 text-emerald-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-emerald-300 truncate">{uploadedFileName}</p>
                  <p className="text-xs text-emerald-400/60">文件已准备好加载</p>
                </div>
                <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
              </div>
            )}

            {/* 加载文档按钮 */}
            <button
              onClick={handleLoadDocument}
              disabled={!uploadedFileName || isLoadingDocument}
              className={`
                w-full py-3.5 px-4 rounded-xl font-medium transition-all duration-300 flex items-center justify-center gap-2 relative overflow-hidden group
                ${!uploadedFileName || isLoadingDocument
                  ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white hover:shadow-lg hover:shadow-cyan-500/30 hover:scale-[1.02] active:scale-[0.98]'
                }
              `}
            >
              {/* 光泽效果 */}
              {!isLoadingDocument && uploadedFileName && (
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
              )}

              {isLoadingDocument ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  加载中...
                </>
              ) : (
                <>
                  <FileText className="w-5 h-5" />
                  加载文档到知识库
                </>
              )}
            </button>

            {/* 已加载文档 */}
            {loadedDocument && (
              <div className="bg-blue-950/50 backdrop-blur-sm border border-blue-500/30 rounded-xl p-4 flex items-center gap-3 animate-in fade-in slide-in-from-left-4 duration-300">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-blue-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-blue-300">
                    文档已加载: {loadedDocument}
                  </p>
                  <p className="text-xs text-blue-400/60">可以开始智能问答了</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-blue-400" />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
