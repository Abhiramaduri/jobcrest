import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import CustomToaster from '../components/common/Toast';

export const MainLayout = () => {
  return (
    <div className="min-h-screen flex flex-col bg-sand-canvas text-ink-charcoal selection:bg-wine-deep selection:text-white">
      <CustomToaster />
      <Navbar />
      <main className="flex-grow">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default MainLayout;
