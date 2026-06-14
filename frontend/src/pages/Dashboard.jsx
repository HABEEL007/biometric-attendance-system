import React, { useState, useEffect } from 'react';
import { getStaff, getAuditLogs } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({ totalStaff: 0, todayCheckins: 0, alerts: 0 });
  const [logs, setLogs] = useState([]);
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
      setLogs(auditData.slice(0, 5)); // Keep only recent 5 logs
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-xl max-w-container-max mx-auto w-full">
        {/* Page Header & Quick Actions */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-xl gap-gutter">
          <div>
            <h2 className="font-display text-display text-on-surface">Welcome back, Admin</h2>
            <p className="text-on-surface-variant text-body-lg">Here's what's happening in your enterprise biometric network today.</p>
          </div>
          <div className="flex gap-sm mt-4 md:mt-0">
            <button onClick={() => window.location.href = '/live'} className="bg-primary-container text-on-primary-container font-semibold py-3 px-6 rounded-lg flex items-center gap-2 hover:opacity-90 active:scale-95 transition-all shadow-sm">
              <span className="material-symbols-outlined" data-icon="videocam">videocam</span>
              Start Live Monitor
            </button>
            <button onClick={() => window.location.href = '/enrollment'} className="bg-surface border border-outline text-on-surface font-semibold py-3 px-6 rounded-lg flex items-center gap-2 hover:bg-surface-container-high active:scale-95 transition-all">
              <span className="material-symbols-outlined" data-icon="person_add">person_add</span>
              Enroll New Staff
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter mb-xl">
          {/* Stat Card 1 */}
          <div className="bg-surface p-lg rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 rounded-lg bg-primary/10 text-primary">
                <span className="material-symbols-outlined" data-icon="check_circle">check_circle</span>
              </div>
              <span className="text-on-surface-variant text-label-md">Today</span>
            </div>
            <p className="text-on-surface-variant text-label-md font-semibold uppercase tracking-tight">Today's Attendance</p>
            <div className="flex items-baseline gap-2 mt-1">
              <h3 className="text-headline-lg font-bold">{loading ? '-' : stats.todayCheckins}</h3>
              <span className="text-body-md text-on-surface-variant">Check-ins</span>
            </div>
          </div>
          {/* Stat Card 2 */}
          <div className="bg-surface p-lg rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 rounded-lg bg-tertiary/10 text-tertiary">
                <span className="material-symbols-outlined" data-icon="badge">badge</span>
              </div>
              <span class="text-on-surface-variant text-label-md">Global Pool</span>
            </div>
            <p className="text-on-surface-variant text-label-md font-semibold uppercase tracking-tight">Total Staff</p>
            <div className="flex items-baseline gap-2 mt-1">
              <h3 className="text-headline-lg font-bold">{loading ? '-' : stats.totalStaff}</h3>
              <span className="text-body-md text-on-surface-variant">Active profiles</span>
            </div>
          </div>
          {/* Stat Card 3 */}
          <div className="bg-surface p-lg rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 rounded-lg bg-secondary/10 text-secondary">
                <span className="material-symbols-outlined" data-icon="bolt">bolt</span>
              </div>
              <span className="text-on-surface-variant text-label-md">Optimized</span>
            </div>
            <p className="text-on-surface-variant text-label-md font-semibold uppercase tracking-tight">Avg Verification</p>
            <div className="flex items-baseline gap-2 mt-1">
              <h3 className="text-headline-lg font-bold">1.2s</h3>
              <span className="text-body-md text-on-surface-variant">Response time</span>
            </div>
          </div>
          {/* Stat Card 4 */}
          <div className="bg-surface p-lg rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 rounded-lg bg-error/10 text-error">
                <span className="material-symbols-outlined" data-icon="security">security</span>
              </div>
              <span className="text-error font-bold text-label-md">Requires Action</span>
            </div>
            <p className="text-on-surface-variant text-label-md font-semibold uppercase tracking-tight">Failed Attempts</p>
            <div className="flex items-baseline gap-2 mt-1">
              <h3 className="text-headline-lg font-bold">{loading ? '-' : stats.alerts}</h3>
              <span className="text-body-md text-on-surface-variant">Blocked</span>
            </div>
          </div>
        </div>

        {/* Dashboard Charts and Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
          {/* Attendance Trend Chart */}
          <div className="col-span-12 lg:col-span-8 bg-surface p-lg rounded-xl border border-outline-variant shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-headline-md font-bold text-on-surface">Weekly Attendance Trend</h3>
              <div className="flex gap-2">
                <button className="text-label-md px-3 py-1 bg-surface-container-high rounded-full">Last 7 Days</button>
                <button className="text-label-md px-3 py-1 text-on-surface-variant hover:bg-surface-container-high rounded-full">Month</button>
              </div>
            </div>
            <div className="relative h-64 flex items-end justify-between gap-4 pt-4">
              {/* Y-Axis Labels */}
              <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-[10px] text-on-surface-variant opacity-50 pr-4 pointer-events-none">
                <span>150</span>
                <span>100</span>
                <span>50</span>
                <span>0</span>
              </div>
              {/* Mock Bars */}
              <div className="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
                <div className="w-full bg-surface-container rounded-t-lg relative group-hover:bg-primary-container transition-colors" style={{ height: '70%' }}>
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-on-surface text-surface text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">112</div>
                </div>
                <span className="text-label-md text-on-surface-variant">Mon</span>
              </div>
              <div className="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
                <div className="w-full bg-surface-container rounded-t-lg relative group-hover:bg-primary-container transition-colors" style={{ height: '85%' }}>
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-on-surface text-surface text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">125</div>
                </div>
                <span className="text-label-md text-on-surface-variant">Tue</span>
              </div>
              <div className="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
                <div className="w-full bg-primary-container rounded-t-lg relative" style={{ height: '90%' }}>
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-on-surface text-surface text-[10px] px-2 py-1 rounded">134</div>
                </div>
                <span className="text-label-md font-bold text-primary">Wed</span>
              </div>
              <div className="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
                <div className="w-full bg-surface-container rounded-t-lg relative group-hover:bg-primary-container transition-colors" style={{ height: '78%' }}>
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-on-surface text-surface text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">118</div>
                </div>
                <span className="text-label-md text-on-surface-variant">Thu</span>
              </div>
              <div className="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
                <div className="w-full bg-surface-container rounded-t-lg relative group-hover:bg-primary-container transition-colors" style={{ height: '92%' }}>
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-on-surface text-surface text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">142</div>
                </div>
                <span className="text-label-md text-on-surface-variant">Fri</span>
              </div>
            </div>
          </div>

          {/* Verification Modes Glass Card */}
          <div className="col-span-12 lg:col-span-4 bg-white/80 backdrop-blur-md p-lg rounded-xl border border-outline-variant shadow-sm flex flex-col justify-between">
            <div>
              <h3 className="text-headline-md font-bold text-on-surface mb-6">Verification Method</h3>
              <div className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-label-md font-semibold">
                    <span>Face Recognition</span>
                    <span>72%</span>
                  </div>
                  <div className="w-full h-2 bg-surface-container-high rounded-full overflow-hidden">
                    <div className="h-full bg-primary" style={{ width: '72%' }}></div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-label-md font-semibold">
                    <span>Iris Scan</span>
                    <span>24%</span>
                  </div>
                  <div className="w-full h-2 bg-surface-container-high rounded-full overflow-hidden">
                    <div className="h-full bg-tertiary" style={{ width: '24%' }}></div>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-8 pt-6 border-t border-outline-variant flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-primary"></span>
                <span className="text-label-md text-on-surface-variant">Primary System Active</span>
              </div>
              <span className="material-symbols-outlined text-on-surface-variant cursor-help" title="Based on last 24h data">info</span>
            </div>
          </div>

          {/* Recent Activity Table */}
          <div className="col-span-12 bg-surface rounded-xl border border-outline-variant shadow-sm overflow-hidden mt-6">
            <div className="px-lg py-6 border-b border-outline-variant flex justify-between items-center">
              <h3 className="text-headline-md font-bold text-on-surface">Recent Activity</h3>
              <button onClick={() => window.location.href = '/logs'} className="text-primary font-semibold text-body-md hover:underline">View All Records</button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-surface-container-low text-on-surface-variant font-label-md uppercase tracking-wider">
                    <th className="px-lg py-4 font-semibold">Name</th>
                    <th className="px-lg py-4 font-semibold">Time</th>
                    <th className="px-lg py-4 font-semibold">Event Type</th>
                    <th className="px-lg py-4 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant">
                  {loading ? (
                    <tr>
                      <td colSpan="4" className="px-lg py-4 text-center">Loading logs...</td>
                    </tr>
                  ) : logs.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="px-lg py-4 text-center">No recent activity.</td>
                    </tr>
                  ) : (
                    logs.map((log) => (
                      <tr key={log.log_id} className="hover:bg-surface-container-low transition-colors">
                        <td className="px-lg py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-[10px]">
                              {log.employee_id.substring(0, 2).toUpperCase()}
                            </div>
                            <span className="font-body-md font-semibold">{log.employee_id}</span>
                          </div>
                        </td>
                        <td className="px-lg py-4 text-body-md text-on-surface-variant">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="px-lg py-4">
                          <div className="flex items-center gap-2 text-on-surface-variant">
                            <span className="material-symbols-outlined text-[18px]" data-icon="event">{log.event_type === 'CHECK_IN' ? 'login' : 'face'}</span>
                            <span className="text-body-md">{log.event_type}</span>
                          </div>
                        </td>
                        <td className="px-lg py-4">
                          <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase ${log.status === 'APPROVED' ? 'bg-green-100 text-green-700' : 'bg-error-container text-error'}`}>
                            {log.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
      </div>
    </div>
  );
};

export default Dashboard;
