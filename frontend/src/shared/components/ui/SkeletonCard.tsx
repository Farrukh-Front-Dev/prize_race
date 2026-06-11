import React from 'react'

export const SkeletonCard: React.FC = () => (
  <div className="bg-white border border-gray-200 rounded-2xl p-5 mb-4 animate-pulse">
    <div className="flex justify-between items-start mb-4">
      <div className="flex-1">
        <div className="h-5 bg-gray-200 rounded w-3/5 mb-2" />
        <div className="h-3 bg-gray-100 rounded w-4/5" />
      </div>
      <div className="h-5 w-16 bg-gray-200 rounded-full ml-2" />
    </div>
    <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-gray-100">
      <div className="h-10 bg-gray-100 rounded" />
      <div className="h-10 bg-gray-100 rounded" />
    </div>
    <div className="h-10 bg-gray-200 rounded-lg" />
  </div>
)
