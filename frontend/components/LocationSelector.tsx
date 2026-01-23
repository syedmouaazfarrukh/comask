'use client';

import { useState } from 'react';
import { ChevronDown, MapPin } from 'lucide-react';

interface LocationSelectorProps {
  onSelect: (location: string) => void;
}

const locations = [
  { value: 'colorado', label: 'Colorado', code: 'CO' },
  // Add more states later
];

export default function LocationSelector({ onSelect }: LocationSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);

  const handleSelect = (location: string) => {
    setSelected(location);
    setIsOpen(false);
    // Small delay for UI feedback
    setTimeout(() => {
      onSelect(location);
    }, 300);
  };

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <p className="text-lg text-gray-700 font-light">
          Where are you asking questions for?
        </p>
      </div>

      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full max-w-md mx-auto flex items-center justify-between px-6 py-4 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 text-left"
        >
          <div className="flex items-center gap-3">
            <MapPin className="w-5 h-5 text-gray-400" />
            <span className="text-gray-700 font-medium">
              {selected 
                ? locations.find(l => l.value === selected)?.label 
                : 'Select a location'}
            </span>
          </div>
          <ChevronDown 
            className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
              isOpen ? 'rotate-180' : ''
            }`} 
          />
        </button>

        {isOpen && (
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 w-full max-w-md bg-white/95 backdrop-blur-sm border border-gray-200 rounded-xl shadow-lg z-10 overflow-hidden">
            {locations.map((location) => (
              <button
                key={location.value}
                onClick={() => handleSelect(location.value)}
                className="w-full px-6 py-4 text-left hover:bg-gray-50 transition-colors duration-150 flex items-center gap-3"
              >
                <MapPin className="w-4 h-4 text-gray-400" />
                <span className="text-gray-700 font-medium">{location.label}</span>
                <span className="ml-auto text-sm text-gray-400">{location.code}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

