import { useEffect, useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { Home, Zap, BarChart2, CheckCircle, Info, BatteryCharging } from 'lucide-react';

export default function Layout() {
  const navItems = [
    { to: "/", icon: <Home size={20} />, label: "Dashboard" },
    { to: "/predict", icon: <Zap size={20} />, label: "Predict Demand" },
    { to: "/analytics", icon: <BarChart2 size={20} />, label: "Peak Analytics" },
    { to: "/performance", icon: <CheckCircle size={20} />, label: "Model Performance" },
    { to: "/about", icon: <Info size={20} />, label: "About / Methodology" },
  ];

  return (
    <div className="flex h-screen bg-gray-50 text-gray-800 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col hidden md:flex">
        <div className="p-6 flex items-center gap-3 text-blue-600 border-b border-gray-100">
          <BatteryCharging size={28} />
          <span className="font-bold text-xl tracking-tight text-gray-900">EV Analytics</span>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-gray-600 hover:bg-gray-50'
                }`
              }
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Mobile Header (simplified) */}
        <div className="md:hidden bg-white p-4 border-b flex items-center gap-3 text-blue-600">
          <BatteryCharging size={24} />
          <span className="font-bold text-lg text-gray-900">EV Analytics</span>
        </div>
        
        <div className="p-6 md:p-8 max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
