import React from 'react';
import { Toaster } from 'react-hot-toast';

export const CustomToaster = () => {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: '#FFFFFF',
          color: '#231F20',
          border: '1px solid #E8E2D5',
          borderRadius: '1rem',
          padding: '12px 16px',
          boxShadow: '0 10px 30px -10px rgba(88, 17, 26, 0.12)',
          fontSize: '0.875rem',
          fontFamily: "'Plus Jakarta Sans', sans-serif",
          fontWeight: 500,
        },
        success: {
          iconTheme: {
            primary: '#2D6A4F',
            secondary: '#FFFFFF',
          },
        },
        error: {
          iconTheme: {
            primary: '#58111A',
            secondary: '#FFFFFF',
          },
        },
      }}
    />
  );
};

export default CustomToaster;
