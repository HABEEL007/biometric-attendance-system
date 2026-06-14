import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // State for interactions
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  
  // Refs for closing dropdowns when clicking outside
  const notifRef = useRef(null);
  const profileRef = useRef(null);

  // Initialize dark mode from localStorage or OS preference
  useEffect(() => {
    const savedMode = localStorage.getItem('theme');
    if (savedMode === 'dark' || (!savedMode && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  // Handle clicking outside to close dropdowns
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setShowProfileMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleDarkMode = () => {
    if (isDarkMode) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      setIsDarkMode(false);
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      setIsDarkMode(true);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const getPageTitle = (pathname) => {
    switch (pathname) {
      case '/': return 'Dashboard';
      case '/live-monitor': return 'Live Monitor';
      case '/staff': return 'Staff Management';
      case '/enrollment': return 'Enrollment';
      case '/records': return 'Records';
      case '/audit-logs': return 'Audit Logs';
      case '/settings': return 'Settings';
      default: return 'BioAttend';
    }
  };

  // Get user details if available
  const user = JSON.parse(localStorage.getItem('user')) || { name: 'Admin User', role: 'Administrator' };

  return (
    <header className="w-full sticky top-0 z-10 bg-surface-container border-b border-outline-variant">
      <div className="flex justify-between items-center h-16 px-xl max-w-container-max mx-auto w-full relative">
        <div className="font-headline-md text-headline-md font-bold text-primary">
          {getPageTitle(location.pathname)}
        </div>
        
        <div className="flex items-center gap-4">
          {/* Dark Mode Button */}
          <button 
            onClick={toggleDarkMode}
            className="material-symbols-outlined p-2 rounded-full hover:bg-surface-variant transition-colors text-on-surface-variant"
            title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {isDarkMode ? 'light_mode' : 'dark_mode'}
          </button>
          
          {/* Notifications Dropdown */}
          <div className="relative" ref={notifRef}>
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="material-symbols-outlined p-2 rounded-full hover:bg-surface-variant transition-colors text-on-surface-variant relative"
            >
              notifications
              {/* Notification Badge Example */}
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full"></span>
            </button>
            
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white border border-outline-variant shadow-lg rounded-xl z-50 overflow-hidden animate-fade-in">
                <div className="p-3 border-b border-outline-variant bg-surface-container-low flex justify-between items-center">
                  <h3 className="font-bold text-label-md">Notifications</h3>
                  <button className="text-primary text-xs hover:underline">Mark all as read</button>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  <div className="p-3 hover:bg-surface-variant transition-colors cursor-pointer border-b border-outline-variant/50">
                    <p className="text-sm font-semibold text-on-surface">System Update Available</p>
                    <p className="text-xs text-on-surface-variant">Version 2.1 is ready to be installed.</p>
                    <p className="text-[10px] text-primary mt-1">2 hours ago</p>
                  </div>
                  <div className="p-3 hover:bg-surface-variant transition-colors cursor-pointer border-b border-outline-variant/50">
                    <p className="text-sm font-semibold text-on-surface">Failed Login Attempt</p>
                    <p className="text-xs text-on-surface-variant">Unauthorized access blocked on front gate.</p>
                    <p className="text-[10px] text-primary mt-1">5 hours ago</p>
                  </div>
                </div>
                <div className="p-2 text-center bg-surface-container-low border-t border-outline-variant">
                  <button className="text-primary text-sm font-semibold w-full">View All Activity</button>
                </div>
              </div>
            )}
          </div>
          
          {/* Profile Dropdown */}
          <div className="relative" ref={profileRef}>
            <button 
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="w-8 h-8 rounded-full bg-surface-variant overflow-hidden border border-outline-variant hover:border-primary transition-colors focus:ring-2 focus:ring-primary-container"
            >
              <img alt="Administrator Profile" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDDSu9lBiMY1yQ_fSSa_S3NgBxxpaADo4pCQcxfP-wBf9w0SUXoqy18nPrjZuytfq3X5DghpgarCgc5gnthb-dAgOOurO0IX3extYlrpUhW1D_yDtElKov7R2wGKN_La8ZpifLUeXNE6n4IHDCUnGM4dkce3A34v8Fr_YWYsErFt0d9plQ62Js96i6LUw_3ytOzFiqdJ_q908pgqQaB9qL9tgPW3nbus4CXy467s_knQaQyJPCILQNpKvE95eFLA_vYe8IEKt2pPbHf" className="w-full h-full object-cover" />
            </button>
            
            {showProfileMenu && (
              <div className="absolute right-0 mt-2 w-56 bg-white border border-outline-variant shadow-lg rounded-xl z-50 overflow-hidden animate-fade-in">
                <div className="p-4 border-b border-outline-variant bg-surface-container-lowest">
                  <p className="font-bold text-on-surface truncate">{user.name}</p>
                  <p className="text-xs text-on-surface-variant truncate">{user.email || user.role}</p>
                </div>
                <div className="p-2">
                  <button 
                    onClick={() => { setShowProfileMenu(false); navigate('/settings'); }}
                    className="w-full text-left px-3 py-2 text-sm text-on-surface-variant hover:bg-surface-variant rounded-md flex items-center gap-2 transition-colors"
                  >
                    <span className="material-symbols-outlined text-[18px]">settings</span>
                    Account Settings
                  </button>
                  <button 
                    onClick={handleLogout}
                    className="w-full text-left px-3 py-2 text-sm text-error hover:bg-error-container hover:text-error rounded-md flex items-center gap-2 transition-colors mt-1"
                  >
                    <span className="material-symbols-outlined text-[18px]">logout</span>
                    Sign out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
