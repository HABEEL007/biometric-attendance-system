import { useState } from 'react';
import { getAttendanceReport } from '../services/api';

const Records = () => {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await getAttendanceReport(date);
      setRecords(data);
      setSearched(true);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch attendance report for this date.');
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
      <div>
        <h2 className="font-headline-md text-headline-md text-primary">Attendance Records</h2>
        <p className="text-on-surface-variant text-body-sm mt-1">View historical attendance and access records by date.</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-4 items-end bg-surface-container p-6 rounded-xl border border-outline-variant">
        <div className="flex flex-col gap-2 flex-1 max-w-xs">
          <label className="font-label-sm text-label-sm text-on-surface-variant">Select Date</label>
          <input 
            type="date" 
            value={date} 
            onChange={(e) => setDate(e.target.value)}
            className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2.5 text-on-surface focus:outline-none focus:border-primary"
            required
          />
        </div>
        <button 
          type="submit" 
          disabled={loading}
          className="bg-primary text-on-primary px-6 py-2.5 rounded-lg font-label-md hover:opacity-90 disabled:opacity-50 transition-all flex items-center gap-2"
        >
          {loading ? 'Searching...' : 'Search Records'}
        </button>
      </form>

      {error && (
        <div className="bg-error-container/20 border border-error/30 rounded-xl p-4 text-error">
          {error}
        </div>
      )}

      {searched && !error && (
        <div className="bg-surface-container rounded-xl border border-outline-variant overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead className="bg-surface-container-high font-label-md text-label-md text-on-surface-variant">
              <tr>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4">Employee</th>
                <th className="px-6 py-4">Event Type</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant font-body-sm text-body-sm text-on-surface">
              {records.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-on-surface-variant">
                    No records found for {date}.
                  </td>
                </tr>
              ) : (
                records.map((record, index) => (
                  <tr key={record.record_id} className={index % 2 === 0 ? 'bg-surface-container-low' : 'bg-surface-container'}>
                    <td className="px-6 py-4">{record.timestamp}</td>
                    <td className="px-6 py-4 font-medium">{record.staff_name || record.staff_id}</td>
                    <td className="px-6 py-4">{record.event_type}</td>
                    <td className={`px-6 py-4 font-bold ${getStatusColor(record.status)}`}>{record.status}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Records;
