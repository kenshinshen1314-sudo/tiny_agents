/**
 * TravelWorkflow - 旅行工作流组件
 *
 * 功能：
 * - 搜索景点、搜索美食、查询天气、酒店推荐、生成行程、计算路线
 * - 组件水平排列在同一行
 * - 进度使用箭头表示，不改变节点样式
 */

import React, { useState } from 'react';

// 工作流节点类型
type WorkflowNode = {
  id: string;
  label: string;
  icon: string;
  status: 'pending' | 'processing' | 'completed';
};

// 初始工作流节点
const initialNodes: WorkflowNode[] = [
  { id: 'search_scenic', label: '搜索景点', icon: '✓', status: 'completed' },
  { id: 'search_food', label: '搜索美食', icon: '✓', status: 'completed' },
  { id: 'weather', label: '查询天气', icon: '✓', status: 'completed' },
  { id: 'hotel', label: '推荐酒店', icon: '🏨', status: 'processing' },
  { id: 'itinerary', label: '生成行程', icon: '📋', status: 'pending' },
  { id: 'route', label: '计算路线', icon: '🚗', status: 'pending' },
];

// 箭头组件
const Arrow: React.FC<{ status: WorkflowNode['status'] }> = ({ status }) => {
  const arrowColors = {
    pending: 'text-gray-300',
    processing: 'text-blue-500 animate-pulse',
    completed: 'text-green-500',
  };

  return (
    <span className={`mx-2 ${arrowColors[status]}`}>
      →
    </span>
  );
};

// 单个工作流节点
const WorkflowNode: React.FC<{
  node: WorkflowNode;
  onClick?: () => void;
}> = ({ node, onClick }) => {
  const statusStyles = {
    pending: {
      bg: 'bg-gray-100',
      text: 'text-gray-400',
      border: 'border-gray-200',
    },
    processing: {
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      border: 'border-blue-200',
    },
    completed: {
      bg: 'bg-green-50',
      text: 'text-green-600',
      border: 'border-green-200',
    },
  };

  const style = statusStyles[node.status];

  return (
    <button
      onClick={onClick}
      disabled={node.status === 'pending'}
      className={`
        flex items-center gap-2 px-4 py-2 rounded-lg
        ${style.bg} ${style.text} ${style.border}
        border transition-all duration-200
        hover:shadow-md cursor-pointer
        ${node.status === 'pending' ? 'cursor-not-allowed opacity-60' : ''}
      `}
    >
      <span className="text-base">{node.icon}</span>
      <span className="text-sm font-medium whitespace-nowrap">{node.label}</span>
    </button>
  );
};

// 主组件
const TravelWorkflow: React.FC = () => {
  const [nodes, setNodes] = useState<WorkflowNode[]>(initialNodes);
  const [currentStep, setCurrentStep] = useState(2); // 当前进行到的步骤

  const handleNodeClick = (nodeId: string) => {
    console.log(`点击了节点: ${nodeId}`);
    // 这里可以添加点击处理逻辑
  };

  // 模拟进度更新
  const updateProgress = () => {
    if (currentStep < nodes.length - 1) {
      const newNodes = [...nodes];
      newNodes[currentStep + 1] = {
        ...newNodes[currentStep + 1],
        status: 'processing',
      };
      setNodes(newNodes);
      setCurrentStep(currentStep + 1);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      <h2 className="text-xl font-bold mb-6 text-gray-800">旅行工作流</h2>

      {/* 工作流节点 - 水平排列 */}
      <div className="flex flex-wrap items-center gap-2 mb-8">
        {nodes.map((node, index) => (
          <React.Fragment key={node.id}>
            <WorkflowNode
              node={node}
              onClick={() => handleNodeClick(node.id)}
            />
            {index < nodes.length - 1 && (
              <Arrow status={node.status} />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* 测试按钮 */}
      <div className="flex gap-4">
        <button
          onClick={updateProgress}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          模拟进度更新
        </button>
        <button
          onClick={() => {
            setNodes(initialNodes);
            setCurrentStep(2);
          }}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
        >
          重置
        </button>
      </div>

      {/* 当前状态显示 */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold text-gray-700 mb-2">当前状态</h3>
        <div className="text-sm text-gray-600">
          <p>已完成: {nodes.filter(n => n.status === 'completed').length} 个任务</p>
          <p>进行中: {nodes.filter(n => n.status === 'processing').length} 个任务</p>
          <p>待处理: {nodes.filter(n => n.status === 'pending').length} 个任务</p>
        </div>
      </div>
    </div>
  );
};

export default TravelWorkflow;
