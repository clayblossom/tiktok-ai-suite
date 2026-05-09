import React, { useState, useRef, useEffect } from 'react';

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

const positionStyles = {
  top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
  bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
  left: 'right-full top-1/2 -translate-y-1/2 mr-2',
  right: 'left-full top-1/2 -translate-y-1/2 ml-2',
};

export function Tooltip({ content, children, position = 'top', className = '' }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    return () => { if (timeoutRef.current) clearTimeout(timeoutRef.current); };
  }, []);

  return (
    <div
      className={`relative inline-flex ${className}`}
      onMouseEnter={() => { timeoutRef.current = setTimeout(() => setIsVisible(true), 200); }}
      onMouseLeave={() => { if (timeoutRef.current) clearTimeout(timeoutRef.current); setIsVisible(false); }}
    >
      {children}
      {isVisible && (
        <div className={`absolute z-50 px-2.5 py-1.5 text-xs font-medium text-white bg-slate-800 rounded-lg shadow-lg whitespace-nowrap animate-fade-in ${positionStyles[position]}`}>
          {content}
          <div className={`absolute w-2 h-2 bg-slate-800 rotate-45 ${
            position === 'top' ? 'top-full left-1/2 -translate-x-1/2 -mt-1' :
            position === 'bottom' ? 'bottom-full left-1/2 -translate-x-1/2 -mb-1' :
            position === 'left' ? 'left-full top-1/2 -translate-y-1/2 -ml-1' :
            'right-full top-1/2 -translate-y-1/2 -mr-1'
          }`} />
        </div>
      )}
    </div>
  );
}
