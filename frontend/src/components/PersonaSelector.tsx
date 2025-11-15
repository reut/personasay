import React from 'react';
import { Persona } from '../config/personas.config';

interface PersonaSelectorProps {
  personas: Persona[];
  selected: string[];
  setSelected: (selected: string[]) => void;
  disabled?: boolean;
}

export const PersonaSelector = ({ personas, selected, setSelected, disabled = false }: PersonaSelectorProps) => {
  const togglePersona = (personaId: string) => {
    if (disabled) return; // Don't allow changes when disabled
    if (selected.includes(personaId)) {
      setSelected(selected.filter(id => id !== personaId));
    } else {
      setSelected([...selected, personaId]);
    }
  };

  return (
    <div className="space-y-2 overflow-y-auto stable-layout">
      {personas.map((persona) => (
        <div 
          key={persona.id}
          onClick={() => togglePersona(persona.id)}
          className={`
            group transition-all duration-200 p-4 rounded-xl min-h-[70px] flex items-center will-change-auto backdrop-blur-sm
            ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}
            ${selected.includes(persona.id) 
              ? 'shadow-lg' 
              : !disabled ? 'hover:shadow-md' : ''
            }
          `}
          style={{
            backgroundColor: selected.includes(persona.id) 
              ? 'rgba(34, 211, 238, 0.15)' 
              : 'rgba(1, 35, 43, 0.4)',
            border: selected.includes(persona.id) 
              ? '1px solid rgba(34, 211, 238, 0.3)' 
              : '1px solid rgba(34, 211, 238, 0.12)'
          }}
          onMouseEnter={(e) => {
            if (!selected.includes(persona.id)) {
              e.currentTarget.style.backgroundColor = 'rgba(1, 35, 43, 0.6)';
              e.currentTarget.style.borderColor = 'rgba(34, 211, 238, 0.2)';
            }
          }}
          onMouseLeave={(e) => {
            if (!selected.includes(persona.id)) {
              e.currentTarget.style.backgroundColor = 'rgba(1, 35, 43, 0.4)';
              e.currentTarget.style.borderColor = 'rgba(34, 211, 238, 0.12)';
            }
          }}
        >
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center space-x-3">
              {/* Avatar */}
              <div 
                className="w-10 h-10 rounded-xl overflow-hidden flex items-center justify-center transition-all duration-200 backdrop-blur-sm"
                style={{
                  background: selected.includes(persona.id) 
                    ? 'linear-gradient(45deg, #22d3ee, #2dd4bf)' 
                    : 'rgba(4, 47, 56, 0.8)',
                  border: '1px solid rgba(34, 211, 238, 0.18)'
                }}
                onMouseEnter={(e) => {
                  if (!selected.includes(persona.id)) {
                    e.currentTarget.style.background = 'rgba(6, 78, 94, 0.8)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!selected.includes(persona.id)) {
                    e.currentTarget.style.background = 'rgba(4, 47, 56, 0.8)';
                  }
                }}
              >
                {persona.avatar.startsWith('/') ? (
                  <img 
                    src={persona.avatar} 
                    alt={persona.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      target.parentElement!.innerHTML = `<span class=\"text-white font-medium text-xs\">${persona.name.charAt(0)}</span>`;
                    }}
                  />
                ) : (
                  <span className="text-white font-medium text-xs">{persona.avatar}</span>
                )}
              </div>
              
              {/* Persona Info */}
              <div>
                <div 
                  className="font-semibold text-base transition-colors duration-200"
                  style={{
                    color: selected.includes(persona.id) 
                      ? '#ffffff' 
                      : '#ccfbf1'
                  }}
                >
                  {persona.name}
                </div>
                <div 
                  className="text-sm transition-colors duration-200"
                  style={{
                    color: selected.includes(persona.id) 
                      ? '#67e8f9' 
                      : '#94a3b8'
                  }}
                >
                  {persona.title}
                </div>
                <div 
                  className="text-xs transition-colors duration-200 mt-0.5"
                  style={{
                    color: selected.includes(persona.id) 
                      ? '#a7f3d0' 
                      : '#6b7280'
                  }}
                >
                  {persona.company}
                </div>
              </div>
            </div>
            
            {/* Selection indicator */}
            <div 
              className="w-2 h-2 rounded-full transition-all duration-200"
              style={{
                background: selected.includes(persona.id) 
                  ? 'linear-gradient(45deg, #22d3ee, #2dd4bf)' 
                  : 'transparent',
                opacity: selected.includes(persona.id) 
                  ? 1 
                  : 0,
                boxShadow: selected.includes(persona.id) 
                  ? '0 0 8px rgba(34, 211, 238, 0.5)' 
                  : 'none'
              }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
};
