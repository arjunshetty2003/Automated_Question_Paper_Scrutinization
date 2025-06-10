import React from 'react';

const Alert = ({ type, message, onClose, className = '' }) => {
  const alertClasses = {
    error: 'alert-error',
    success: 'alert-success',
    warning: 'alert-warning',
  };

  return (
    <div className={`${alertClasses[type]} ${className}`}>
      <div className="flex justify-between items-center">
        <span>{message}</span>
        {onClose && (
          <button onClick={onClose} className="ml-4 text-lg font-semibold">
            ×
          </button>
        )}
      </div>
    </div>
  );
};

export default Alert;
