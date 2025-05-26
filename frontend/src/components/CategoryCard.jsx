import React from 'react'
import { 
  User, Briefcase, CreditCard, Megaphone,
  Bell, Plane, ShoppingBag, Share2
} from 'lucide-react'

const CategoryCard = ({ category, count, onClick, isSelected = false }) => {
  const getCategoryIcon = (category) => {
    const iconMap = {
      'Personal': User,
      'Work': Briefcase,
      'Bank/Finance': CreditCard,
      'Promotions/Ads': Megaphone,
      'Notifications': Bell,
      'Travel': Plane,
      'Shopping': ShoppingBag,
      'Social Media': Share2
    }
    return iconMap[category] || Bell
  }

  const getCategoryColor = (category) => {
    const colorMap = {
      'Personal': 'text-green-600 bg-green-50 border-green-200',
      'Work': 'text-blue-600 bg-blue-50 border-blue-200',
      'Bank/Finance': 'text-yellow-600 bg-yellow-50 border-yellow-200',
      'Promotions/Ads': 'text-purple-600 bg-purple-50 border-purple-200',
      'Notifications': 'text-gray-600 bg-gray-50 border-gray-200',
      'Travel': 'text-indigo-600 bg-indigo-50 border-indigo-200',
      'Shopping': 'text-pink-600 bg-pink-50 border-pink-200',
      'Social Media': 'text-orange-600 bg-orange-50 border-orange-200'
    }
    return colorMap[category] || 'text-gray-600 bg-gray-50 border-gray-200'
  }
  const Icon = getCategoryIcon(category)
  const colorClass = getCategoryColor(category)
  
  return (
    <div 
      className={`
        card cursor-pointer transition-all duration-200 hover:shadow-md
        ${colorClass}
        ${isSelected ? 'ring-2 ring-primary-500' : ''}
      `}
      onClick={() => onClick && onClick(category)}
    >
      <div className="flex items-center space-x-3">
        <Icon className="h-6 w-6 flex-shrink-0" />
        <div className="min-w-0 flex-1">
          <div className="font-semibold text-sm truncate">{category}</div>
          <div className="text-2xl font-bold">{count}</div>
        </div>
      </div>
    </div>
  )
}

export default CategoryCard
