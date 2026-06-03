import { useEffect, useState } from 'react';
import { getAuditLogs } from '../services/api';

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLog, setSelectedLog] = useState(null); // For modal

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

  const getStatusColor = (status) => {
    switch (status) {
      case 'APPROVED': return 'text-secondary';
      case 'REJECTED': return 'text-error';
      default: return 'text-on-surface-variant';
    }
  };

  return (
    <div className="p-margin-desktop flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="font-headline-md text-headline-md text-primary">Audit Logs</h2>
          <p className="text-on-surface-variant text-body-sm mt-1">Real-time biometric access events.</p>
        </div>
        <button onClick={fetchLogs} className="bg-surface-variant text-on-surface p-2 rounded-lg hover:bg-outline-variant transition-colors flex items-center justify-center">
          <span className="material-symbols-outlined">refresh</span>
        </button>
      </div>

      {error && (
        <div className="bg-error-container/20 border border-error/30 rounded-xl p-4 text-error">
          {error}
        </div>
      )}

      <div className="bg-surface-container rounded-xl border border-outline-variant overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead className="bg-surface-container-high font-label-md text-label-md text-on-surface-variant">
            <tr>
              <th className="px-6 py-4">Timestamp</th>
              <th className="px-6 py-4">Employee</th>
              <th className="px-6 py-4">Event Type</th>
              <th className="px-6 py-4">Station</th>
              <th className="px-6 py-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant font-body-sm text-body-sm text-on-surface">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-on-surface-variant">
                  Loading logs...
                </td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-on-surface-variant">
                  No audit logs for today.
                </td>
              </tr>
            ) : (
              logs.map((log, index) => (
                <tr 
                  key={log.record_id} 
                  className={`cursor-pointer hover:bg-surface-variant transition-colors ${index % 2 === 0 ? 'bg-surface-container-low' : 'bg-surface-container'}`}
                  onClick={() => setSelectedLog(log)}
                >
                  <td className="px-6 py-4">{log.timestamp}</td>
                  <td className="px-6 py-4 font-medium">{log.staff_name || log.staff_id}</td>
                  <td className="px-6 py-4">{log.event_type}</td>
                  <td className="px-6 py-4 text-on-surface-variant">{log.camera_id}</td>
                  <td className={`px-6 py-4 font-bold ${getStatusColor(log.status)}`}>{log.status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Basic Modal for Details */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-margin-mobile">
          <div className="bg-surface-container-low w-full max-w-2xl rounded-xl border border-outline-variant shadow-2xl flex flex-col">
            <div className="px-8 py-6 border-b border-outline-variant flex justify-between items-center">
              <div>
                <h2 className="font-headline-md text-headline-md text-primary">Log Detail</h2>
                <p className="font-label-sm text-label-sm text-on-surface-variant">Event ID: {selectedLog.record_id} • {selectedLog.camera_id}</p>
              </div>
              <button onClick={() => setSelectedLog(null)} className="material-symbols-outlined text-on-surface-variant hover:text-on-surface transition-colors p-2">close</button>
            </div>
            
            <div className="p-8 flex flex-col gap-4">
              <div className="bg-surface-variant p-4 rounded-lg flex flex-col gap-2">
                 <p><strong className="text-on-surface-variant">Employee:</strong> {selectedLog.staff_name || selectedLog.staff_id}</p>
                 <p><strong className="text-on-surface-variant">Type:</strong> {selectedLog.event_type}</p>
                 <p><strong className="text-on-surface-variant">Status:</strong> <span className={getStatusColor(selectedLog.status)}>{selectedLog.status}</span></p>
                 <p><strong className="text-on-surface-variant">Face Confidence:</strong> {selectedLog.face_score}</p>
                 <p><strong className="text-on-surface-variant">Reason:</strong> {selectedLog.reject_reason || 'N/A'}</p>
              </div>
            </div>

            <div className="px-8 py-6 border-t border-outline-variant bg-surface-container flex justify-end items-center gap-4">
              <button onClick={() => setSelectedLog(null)} className="px-6 py-2.5 rounded-lg border border-outline-variant text-on-surface font-label-md text-label-md hover:bg-surface-variant transition-colors">
                Close Detail
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditLogs;
