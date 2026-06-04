import { NavLink } from 'react-router-dom';
import logo from '../assets/logo.png';

const Sidebar = () => {
  return (
    <aside className="flex flex-col h-full py-6 gap-2 sticky left-0 top-0 overflow-y-auto bg-surface/40 backdrop-blur-xl border-r border-outline-variant w-64 shrink-0 shadow-[0_0_40px_rgba(139,92,246,0.1)]">
      <div className="px-6 mb-8 flex flex-col items-center justify-center text-center">
        <div className="w-20 h-20 mb-3 rounded-2xl overflow-hidden shadow-[0_0_20px_rgba(139,92,246,0.3)] border border-primary/30">
            <img src={logo} alt="BioAttend Logo" className="w-full h-full object-cover" />
        </div>
        <div className="font-headline-md text-headline-md font-bold text-primary bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">BioAttend</div>
        <div className="font-label-md text-label-md text-on-surface-variant">Enterprise Biometrics</div>
      </div>
      <nav className="flex-1 space-y-1">
        <NavLink to="/" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 mx-2 rounded-xl transition-all duration-200 ${isActive ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:bg-surface-variant'}`}>
          <span className="material-symbols-outlined">dashboard</span>
          <span className="font-label-md text-label-md">Dashboard</span>
        </NavLink>
        <NavLink to="/live-monitor" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 mx-2 rounded-xl transition-all duration-200 ${isActive ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:bg-surface-variant'}`}>
          <span className="material-symbols-outlined">videocam</span>
          <span className="font-label-md text-label-md">Live Monitor</span>
        </NavLink>
        <NavLink to="/staff" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 mx-2 rounded-xl transition-all duration-200 ${isActive ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:bg-surface-variant'}`}>
          <span className="material-symbols-outlined">groups</span>
          <span className="font-label-md text-label-md">Staff</span>
        </NavLink>
        <NavLink to="/enrollment" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 mx-2 rounded-xl transition-all duration-200 ${isActive ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:bg-surface-variant'}`}>
          <span className="material-symbols-outlined">person_add_alt</span>
          <span className="font-label-md text-label-md">Enrollment</span>
        </NavLink>
        <NavLink to="/records" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 mx-2 rounded-xl transition-all duration-200 ${isActive ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:bg-surface-variant'}`}>
          <span className="material-symbols-outlined">receipt_long</span>
          <span className="font-label-md text-label-md">Records</span>
        </NavLink>
        <NavLink to="/audit-logs" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 mx-2 rounded-xl transition-all duration-200 ${isActive ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:bg-surface-variant'}`}>
          <span className="material-symbols-outlined">fact_check</span>
          <span className="font-label-md text-label-md">Audit Logs</span>
        </NavLink>
        <NavLink to="/settings" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 mx-2 rounded-xl transition-all duration-200 ${isActive ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:bg-surface-variant'}`}>
          <span className="material-symbols-outlined">settings</span>
          <span className="font-label-md text-label-md">Settings</span>
        </NavLink>
      </nav>
    </aside>
  );
};

export default Sidebar;
