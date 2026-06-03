import { useState, useEffect } from 'react';
import { getStaff, getAuditLogs } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({ totalStaff: 0, todayCheckins: 0, alerts: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [staffData, auditData] = await Promise.all([
        getStaff().catch(() => []),
        getAuditLogs().catch(() => [])
      ]);

      const checkins = auditData.filter(log => log.event_type === 'CHECK_IN' && log.status === 'APPROVED').length;
      const alerts = auditData.filter(log => log.status === 'REJECTED').length;

      setStats({
        totalStaff: staffData.length || 0,
        todayCheckins: checkins,
        alerts: alerts
      });
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-margin-desktop flex flex-col gap-6">
      <div>
        <h2 className="font-headline-md text-headline-md text-primary">Dashboard Overview</h2>
        <p className="text-on-surface-variant text-body-sm mt-1">High-level summary of your biometric system.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-surface-container rounded-xl border border-outline-variant p-6 flex flex-col gap-2">
          <div className="flex justify-between items-center text-on-surface-variant">
            <span className="font-label-md">Total Staff</span>
            <span className="material-symbols-outlined">groups</span>
          </div>
          <div className="text-[36px] font-headline-lg font-bold">
            {loading ? '-' : stats.totalStaff}
          </div>
        </div>

        <div className="bg-surface-container rounded-xl border border-outline-variant p-6 flex flex-col gap-2">
          <div className="flex justify-between items-center text-secondary">
            <span className="font-label-md">Today's Check-ins</span>
            <span className="material-symbols-outlined">how_to_reg</span>
          </div>
          <div className="text-[36px] font-headline-lg font-bold text-secondary">
            {loading ? '-' : stats.todayCheckins}
          </div>
        </div>

        <div className="bg-surface-container rounded-xl border border-outline-variant p-6 flex flex-col gap-2">
          <div className="flex justify-between items-center text-error">
            <span className="font-label-md">Security Alerts</span>
            <span className="material-symbols-outlined">warning</span>
          </div>
          <div className="text-[36px] font-headline-lg font-bold text-error">
            {loading ? '-' : stats.alerts}
          </div>
        </div>
      </div>
      
      <div className="bg-surface-container rounded-xl border border-outline-variant p-8 mt-4 flex items-center justify-center min-h-[300px]">
         <div className="text-center text-on-surface-variant max-w-md">
           <span className="material-symbols-outlined text-[64px] mb-4 text-primary opacity-50">insights</span>
           <h3 className="font-title-lg text-primary mb-2">System Healthy</h3>
           <p>All microservices (Face Recognition, Iris Verification, and Liveness Detection) are monitored centrally.</p>
         </div>
      </div>
    </div>
  );
};

export default Dashboard;
