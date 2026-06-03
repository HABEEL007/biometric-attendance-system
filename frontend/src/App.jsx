import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './components/Layout/MainLayout';
import Dashboard from './pages/Dashboard';
import Staff from './pages/Staff';
import Enrollment from './pages/Enrollment';
import AuditLogs from './pages/AuditLogs';
import LiveMonitor from './pages/LiveMonitor';
import Records from './pages/Records';
import Settings from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="live-monitor" element={<LiveMonitor />} />
          <Route path="staff" element={<Staff />} />
          <Route path="enrollment" element={<Enrollment />} />
          <Route path="records" element={<Records />} />
          <Route path="audit-logs" element={<AuditLogs />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
