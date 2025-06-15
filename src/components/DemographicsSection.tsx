import React from 'react'
import { User, Calendar, MapPin, GraduationCap, Briefcase, DollarSign, Users, Heart, Home, Car, Baby, Globe, Languages, Zap } from 'lucide-react'

interface DemographicItem {
  id: string
  label: string
  icon: React.ReactNode
  enabled: boolean
}

interface DemographicsSectionProps {
  demographics: DemographicItem[]
  onToggle: (id: string) => void
}

export default function DemographicsSection({ demographics, onToggle }: DemographicsSectionProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
        Select Demographics
      </h3>
      <p className="text-gray-600 mb-6">Choose which demographic information to collect from respondents</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {demographics.map((item) => (
          <div
            key={item.id}
            className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="text-gray-600">
                  {item.icon}
                </div>
                <span className="font-medium text-gray-900">{item.label}</span>
              </div>
              
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={item.enabled}
                  onChange={() => onToggle(item.id)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-600"></div>
              </label>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export const defaultDemographics: DemographicItem[] = [
  { id: 'age', label: 'Age', icon: <Calendar className="w-5 h-5" />, enabled: false },
  { id: 'gender', label: 'Gender', icon: <User className="w-5 h-5" />, enabled: false },
  { id: 'location', label: 'Location', icon: <MapPin className="w-5 h-5" />, enabled: false },
  { id: 'education', label: 'Education Level', icon: <GraduationCap className="w-5 h-5" />, enabled: false },
  { id: 'occupation', label: 'Occupation', icon: <Briefcase className="w-5 h-5" />, enabled: false },
  { id: 'income', label: 'Income Range', icon: <DollarSign className="w-5 h-5" />, enabled: false },
  { id: 'household', label: 'Household Size', icon: <Users className="w-5 h-5" />, enabled: false },
  { id: 'marital', label: 'Marital Status', icon: <Heart className="w-5 h-5" />, enabled: false },
  { id: 'housing', label: 'Housing Type', icon: <Home className="w-5 h-5" />, enabled: false },
  { id: 'transport', label: 'Transportation', icon: <Car className="w-5 h-5" />, enabled: false },
  { id: 'children', label: 'Number of Children', icon: <Baby className="w-5 h-5" />, enabled: false },
  { id: 'nationality', label: 'Nationality', icon: <Globe className="w-5 h-5" />, enabled: false },
  { id: 'languages', label: 'Languages Spoken', icon: <Languages className="w-5 h-5" />, enabled: false },
  { id: 'employment', label: 'Employment Status', icon: <Zap className="w-5 h-5" />, enabled: false },
]