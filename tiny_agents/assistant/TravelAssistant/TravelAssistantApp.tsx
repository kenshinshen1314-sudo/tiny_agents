/**
 * TravelAssistant App - 旅行助手主应用
 */
import React from 'react';
import TravelWorkflow from './TravelWorkflow';

const TravelAssistantApp: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-800">✈️ 旅行助手</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        <TravelWorkflow />
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t py-3">
        <div className="max-w-6xl mx-auto px-6 flex justify-center gap-8 text-sm text-gray-500">
          <span>© 2026 旅行助手</span>
          <span>Powered by Tiny Agents</span>
        </div>
      </footer>
    </div>
  );
};

export default TravelAssistantApp;
