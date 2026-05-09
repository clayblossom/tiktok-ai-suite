import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helpText?: string;
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helpText?: string;
}

interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  label?: string;
  error?: string;
  helpText?: string;
  options: { value: string; label: string }[];
  placeholder?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helpText, className = '', ...props }, ref) => {
    return (
      <div className="space-y-1">
        {label && <label className="block text-sm font-medium text-slate-700">{label}</label>}
        <input
          ref={ref}
          className={`w-full px-3 py-2 bg-white border rounded-lg text-sm text-slate-800 placeholder-slate-400 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
            error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-slate-300'
          } ${className}`}
          {...props}
        />
        {error && <p className="text-xs text-red-600">{error}</p>}
        {helpText && !error && <p className="text-xs text-slate-500">{helpText}</p>}
      </div>
    );
  }
);
Input.displayName = 'Input';

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, helpText, className = '', ...props }, ref) => {
    return (
      <div className="space-y-1">
        {label && <label className="block text-sm font-medium text-slate-700">{label}</label>}
        <textarea
          ref={ref}
          className={`w-full px-3 py-2 bg-white border rounded-lg text-sm text-slate-800 placeholder-slate-400 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none ${
            error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-slate-300'
          } ${className}`}
          {...props}
        />
        {error && <p className="text-xs text-red-600">{error}</p>}
        {helpText && !error && <p className="text-xs text-slate-500">{helpText}</p>}
      </div>
    );
  }
);
Textarea.displayName = 'Textarea';

export function Select({ label, error, helpText, options, placeholder, className = '', ...props }: SelectProps) {
  return (
    <div className="space-y-1">
      {label && <label className="block text-sm font-medium text-slate-700">{label}</label>}
      <select
        className={`w-full px-3 py-2 bg-white border rounded-lg text-sm text-slate-800 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 appearance-none cursor-pointer ${
          error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-slate-300'
        } ${className}`}
        {...props}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>{option.label}</option>
        ))}
      </select>
      {error && <p className="text-xs text-red-600">{error}</p>}
      {helpText && !error && <p className="text-xs text-slate-500">{helpText}</p>}
    </div>
  );
}
