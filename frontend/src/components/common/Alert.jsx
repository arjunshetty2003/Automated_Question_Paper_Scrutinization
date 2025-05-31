import React from 'react';

const Alert = ({ type = 'info', message, onClose, className = '' }) => {
  const alertClasses = {
    success: 'alert-success',
    error: 'alert-error',
    warning: 'alert-warning',
    info: 'alert-info'
  };

  const iconClasses = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };

  return (
    <div className={`${alertClasses[type]} flex items-center justify-between ${className}`}>
      <div className="flex items-center">
        <span className="mr-2 font-bold">{iconClasses[type]}</span>
        <span>{message}</span>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="ml-4 text-lg hover:opacity-70 transition-opacity"
          aria-label="Close alert"
        >
          ×
        </button>
      )}
    </div>
  );
};

export default Alert;
