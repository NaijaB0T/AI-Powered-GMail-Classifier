import React from 'react'

const ProgressBar = ({ progress, total, label, showPercentage = true }) => {
  const percentage = total > 0 ? Math.round((progress / total) * 100) : 0

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          {showPercentage && (
            <span className="text-sm text-gray-500">{percentage}%</span>
          )}
        </div>
      )}
      
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-primary-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      
      {total > 0 && (
        <div className="flex justify-between items-center mt-1">
          <span className="text-xs text-gray-500">{progress} of {total}</span>
        </div>
      )}
    </div>
  )
}

export default ProgressBar
