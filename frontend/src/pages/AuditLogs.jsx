import React, { useEffect, useState } from 'react';
import { getAuditLogs } from '../services/api';

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await getAuditLogs();
      setLogs(data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to load audit logs.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = () => {
    if (logs.length === 0) {
      alert("No logs to export.");
      return;
    }
    const headers = ['Timestamp', 'Event Type', 'Description', 'User', 'ID', 'Station'];
    const csvContent = [
      headers.join(','),
      ...logs.map(log => `"${log.timestamp}","${log.event_type || ''}","${log.reject_reason || (log.status === 'APPROVED' ? 'Authentication successful.' : 'Log entry recorded.')}","${log.staff_name || 'Unknown'}","${log.staff_id || ''}","${log.camera_id || ''}"`)
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', `audit_logs.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getEventBadge = (status, eventType) => {
    if (status === 'REJECTED' || eventType?.toLowerCase().includes('spoof')) {
      return (
        <span className="inline-flex items-center px-sm py-xs rounded-full bg-error-container text-on-error-container text-label-sm font-bold border border-error/20">
          <span className="material-symbols-outlined text-[14px] mr-xs" style={{ fontVariationSettings: "'FILL' 1" }}>security</span>
          {eventType || 'Spoof Attempt'}
        </span>
      );
    }
    if (status === 'APPROVED' || eventType?.toLowerCase().includes('success')) {
      return (
        <span className="inline-flex items-center px-sm py-xs rounded-full bg-primary-container text-on-primary-container text-label-sm font-bold border border-primary/20">
          <span className="material-symbols-outlined text-[14px] mr-xs" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
          Success
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-sm py-xs rounded-full bg-surface-container-high text-on-surface-variant text-label-sm font-bold border border-outline-variant">
        <span className="material-symbols-outlined text-[14px] mr-xs">warning</span>
        System Error
      </span>
    );
  };

  return (
    <div className="p-xl max-w-container-max mx-auto w-full">
        {/* Filter Section */}
        <section className="bg-surface-container-lowest rounded-xl p-md mb-lg shadow-sm border border-outline-variant flex flex-wrap items-end gap-md">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-label-sm text-on-surface-variant mb-xs ml-1">Date Range</label>
            <div className="relative">
              <input className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all" type="date" />
            </div>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-label-sm text-on-surface-variant mb-xs ml-1">Event Type</label>
            <select className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm focus:ring-2 focus:ring-primary-container focus:border-primary outline-none appearance-none transition-all">
              <option value="all">All Events</option>
              <option value="success">Success</option>
              <option value="spoof">Spoof Attempt</option>
              <option value="error">System Error</option>
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-label-sm text-on-surface-variant mb-xs ml-1">Search User</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">search</span>
              <input className="w-full bg-surface border border-outline-variant rounded-lg pl-10 pr-md py-sm focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all" placeholder="Name or ID..." type="text" />
            </div>
          </div>
          <div className="flex gap-sm">
            <button onClick={fetchLogs} className="px-lg py-[10px] bg-surface-container-high text-on-surface font-semibold rounded-lg hover:bg-surface-variant transition-colors flex items-center gap-sm active:scale-95">
              <span className="material-symbols-outlined text-[18px]">refresh</span>
              <span>Refresh</span>
            </button>
            <button onClick={handleExportCSV} className="px-lg py-[10px] bg-primary-container text-on-primary-container font-semibold rounded-lg hover:opacity-90 transition-opacity flex items-center gap-sm active:scale-95">
              <span className="material-symbols-outlined text-[18px]">download</span>
              <span>Export CSV</span>
            </button>
          </div>
        </section>

        {error && (
          <div className="bg-error-container/20 border border-error/30 rounded-xl p-4 text-error mb-lg">
            {error}
          </div>
        )}

        {/* Logs Table Container */}
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-outline-variant bg-surface-container-low">
                  <th className="px-lg py-md font-label-md text-on-surface-variant uppercase tracking-wider">Timestamp</th>
                  <th className="px-lg py-md font-label-md text-on-surface-variant uppercase tracking-wider">Event Type</th>
                  <th className="px-lg py-md font-label-md text-on-surface-variant uppercase tracking-wider">Description</th>
                  <th className="px-lg py-md font-label-md text-on-surface-variant uppercase tracking-wider">User / ID</th>
                  <th className="px-lg py-md font-label-md text-on-surface-variant uppercase tracking-wider">Station</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="px-lg py-lg text-center text-on-surface-variant">Loading logs...</td>
                  </tr>
                ) : logs.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-lg py-lg text-center text-on-surface-variant">No audit logs for today.</td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.record_id} className="log-row hover:bg-surface-container-high transition-colors">
                      <td className="px-lg py-lg whitespace-nowrap">
                        <div className="font-body-md text-on-surface">{log.timestamp?.split(' ')[0] || log.timestamp}</div>
                        <div className="text-label-sm text-on-surface-variant">{log.timestamp?.split(' ')[1] || ''}</div>
                      </td>
                      <td className="px-lg py-lg">
                        {getEventBadge(log.status, log.event_type)}
                      </td>
                      <td className="px-lg py-lg max-w-xs">
                        <p className="font-body-md text-on-surface leading-tight">{log.reject_reason || (log.status === 'APPROVED' ? 'Authentication successful.' : 'Log entry recorded.')}</p>
                      </td>
                      <td className="px-lg py-lg">
                        <div className="font-body-md text-on-surface font-semibold">{log.staff_name || log.staff_id || 'Unknown'}</div>
                        <div className="text-label-sm text-on-surface-variant">ID: {log.staff_id || 'UNKN'}</div>
                      </td>
                      <td className="px-lg py-lg">
                        <div className="font-body-md text-on-surface">{log.camera_id}</div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {/* Pagination */}
          <div className="px-lg py-md bg-surface-container-low flex justify-between items-center border-t border-outline-variant">
            <p className="text-label-sm text-on-surface-variant">Showing {logs.length} events</p>
          </div>
        </div>
    </div>
  );
};

export default AuditLogs;
