import React from 'react';
import { Check, Users } from 'lucide-react';
import { DEMOGRAPHIC_OPTIONS, DemographicOption } from '@/types';
import { clsx } from 'clsx';

interface DemographicsSelectorProps {
  selected: string[];
  onChange: (selected: string[]) => void;
}

const demographicDescriptions: Record<DemographicOption, string> = {
  'Age': 'Age range or specific age',
  'Gender': 'Gender identity',
  'Location': 'Geographic location', 
  'Education': 'Educational background',
  'Income': 'Income range',
  'Occupation': 'Job title or industry',
  'Ethnicity': 'Ethnic background'
};

export const DemographicsSelector: React.FC<DemographicsSelectorProps> = ({
  selected,
  onChange
}) => {
  const toggleDemographic = (demographic: string) => {
    if (selected.includes(demographic)) {
      onChange(selected.filter(d => d !== demographic));
    } else {
      onChange([...selected, demographic]);
    }
  };

  const selectAll = () => {
    onChange([...DEMOGRAPHIC_OPTIONS]);
  };

  const clearAll = () => {
    onChange([]);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <Users className="w-4 h-4" />
          <span>Select demographic information to collect</span>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={selectAll}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Select All
          </button>
          <span className="text-gray-300">|</span>
          <button
            onClick={clearAll}
            className="text-sm text-gray-600 hover:text-gray-700 font-medium"  
          >
            Clear All
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {DEMOGRAPHIC_OPTIONS.map((demographic) => {
          const isSelected = selected.includes(demographic);
          
          return (
            <button
              key={demographic}
              onClick={() => toggleDemographic(demographic)}
              className={clsx(
                'p-4 rounded-lg border-2 text-left transition-all duration-200',
                isSelected
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <div className={clsx(
                      'w-5 h-5 rounded border-2 flex items-center justify-center transition-colors',
                      isSelected
                        ? 'border-primary-500 bg-primary-500'
                        : 'border-gray-300'
                    )}>
                      {isSelected && (
                        <Check className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{demographic}</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        {demographicDescriptions[demographic]}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {selected.length > 0 && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            <strong>{selected.length}</strong> demographic{selected.length !== 1 ? 's' : ''} selected: {selected.join(', ')}
          </p>
        </div>
      )}
    </div>
  );
};