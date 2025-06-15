import React from 'react'
import { Mail, Phone, Globe, Linkedin, Twitter, Instagram, Shield, MapPin, Building, Calendar, FileText, Camera, Music, Gamepad2, Book, Dumbbell, Plane, ShoppingBag, CreditCard, Smartphone } from 'lucide-react'

interface ProfileItem {
  id: string
  label: string
  icon: React.ReactNode
  enabled: boolean
  validated?: boolean
}

interface ProfileSectionProps {
  profileInfo: ProfileItem[]
  onToggle: (id: string) => void
}

export default function ProfileSection({ profileInfo, onToggle }: ProfileSectionProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
        Select Profile Information
      </h3>
      <p className="text-gray-600 mb-6">Choose which contact and profile information to collect</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {profileInfo.map((item) => (
          <div
            key={item.id}
            className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="text-gray-600">
                  {item.icon}
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-900">{item.label}</span>
                  {item.validated && (
                    <Shield className="w-4 h-4 text-green-600" title="Validated field" />
                  )}
                </div>
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

export const defaultProfileInfo: ProfileItem[] = [
  // Contact Information
  { id: 'email', label: 'Email Address', icon: <Mail className="w-5 h-5" />, enabled: false, validated: true },
  { id: 'phone', label: 'Phone Number', icon: <Phone className="w-5 h-5" />, enabled: false, validated: true },
  { id: 'address', label: 'Home Address', icon: <MapPin className="w-5 h-5" />, enabled: false },
  { id: 'website', label: 'Personal Website', icon: <Globe className="w-5 h-5" />, enabled: false, validated: true },
  
  // Social Media
  { id: 'linkedin', label: 'LinkedIn Profile', icon: <Linkedin className="w-5 h-5" />, enabled: false },
  { id: 'twitter', label: 'Twitter Handle', icon: <Twitter className="w-5 h-5" />, enabled: false },
  { id: 'instagram', label: 'Instagram Handle', icon: <Instagram className="w-5 h-5" />, enabled: false },
  
  // Professional Information
  { id: 'company', label: 'Company Name', icon: <Building className="w-5 h-5" />, enabled: false },
  { id: 'jobtitle', label: 'Job Title', icon: <FileText className="w-5 h-5" />, enabled: false },
  { id: 'experience', label: 'Years of Experience', icon: <Calendar className="w-5 h-5" />, enabled: false },
  
  // Personal Interests
  { id: 'hobbies', label: 'Hobbies & Interests', icon: <Camera className="w-5 h-5" />, enabled: false },
  { id: 'music', label: 'Music Preferences', icon: <Music className="w-5 h-5" />, enabled: false },
  { id: 'gaming', label: 'Gaming Preferences', icon: <Gamepad2 className="w-5 h-5" />, enabled: false },
  { id: 'reading', label: 'Reading Habits', icon: <Book className="w-5 h-5" />, enabled: false },
  { id: 'fitness', label: 'Fitness Activities', icon: <Dumbbell className="w-5 h-5" />, enabled: false },
  { id: 'travel', label: 'Travel Frequency', icon: <Plane className="w-5 h-5" />, enabled: false },
  
  // Consumer Behavior
  { id: 'shopping', label: 'Shopping Habits', icon: <ShoppingBag className="w-5 h-5" />, enabled: false },
  { id: 'budget', label: 'Monthly Budget', icon: <CreditCard className="w-5 h-5" />, enabled: false },
  { id: 'devices', label: 'Devices Used', icon: <Smartphone className="w-5 h-5" />, enabled: false },
]