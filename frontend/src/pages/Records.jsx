import React, { useState, useEffect } from 'react';
import { getAttendanceReport, deleteAttendanceRecord } from '../services/api';

const Records = () => {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Optionally fetch on mount
    handleSearch();
  }, []);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
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

  const handleDelete = async (recordId) => {
    if (!window.confirm("Are you sure you want to delete this attendance record?")) {
      return;
    }
    
    try {
      await deleteAttendanceRecord(recordId);
      // Refresh the records after deletion
      handleSearch();
    } catch (err) {
      console.error(err);
      alert('Failed to delete attendance record.');
    }
  };

  const handleExportCSV = () => {
    if (records.length === 0) {
      alert("No records to export for this date.");
      return;
    }
    const headers = ['Timestamp', 'Employee Name', 'ID', 'Type', 'Biometric Score', 'Status'];
    const csvContent = [
      headers.join(','),
      ...records.map(r => `"${r.timestamp}","${r.staff_name || 'Unknown'}","${r.staff_id || ''}","${r.event_type || 'Check-in'}","${(r.face_score * 100 || 0).toFixed(1)}%","${r.status || ''}"`)
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', `attendance_records_${date}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusColor = (status) => {
    if (status === 'APPROVED' || status?.toLowerCase() === 'present') {
      return (
        <span className="bg-green-100 text-green-800 px-sm py-[2px] rounded-full text-[12px] font-semibold">
          Present
        </span>
      );
    } else if (status === 'REJECTED' || status?.toLowerCase() === 'absent') {
      return (
        <span className="bg-red-100 text-red-800 px-sm py-[2px] rounded-full text-[12px] font-semibold">
          Absent
        </span>
      );
    } else if (status?.toLowerCase() === 'late') {
      return (
        <span className="bg-yellow-100 text-yellow-800 px-sm py-[2px] rounded-full text-[12px] font-semibold">
          Late
        </span>
      );
    }
    return (
      <span className="bg-gray-100 text-gray-800 px-sm py-[2px] rounded-full text-[12px] font-semibold">
        {status}
      </span>
    );
  };

  // Calculate some simple stats for the UI
  const totalPresent = records.filter(r => r.status === 'APPROVED' || r.status?.toLowerCase() === 'present').length;
  const totalAbsent = records.filter(r => r.status === 'REJECTED' || r.status?.toLowerCase() === 'absent').length;
  const totalLate = records.filter(r => r.status?.toLowerCase() === 'late').length;

  return (
    <div className="p-xl max-w-container-max mx-auto w-full">
      {/* Filter Bar */}
      <section className="bg-surface-container-lowest rounded-xl p-md mb-lg custom-shadow flex flex-wrap items-center justify-between gap-md border border-outline-variant">
        <form onSubmit={handleSearch} className="flex flex-wrap items-center gap-md">
          <div className="flex flex-col gap-xs">
            <label className="font-label-sm text-label-sm text-on-surface-variant px-xs">Date</label>
            <div className="relative">
              <input 
                className="bg-white border border-outline-variant rounded-lg px-md py-sm text-body-md font-body-md focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 outline-none w-48" 
                type="date" 
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>
          </div>
          <div className="flex flex-col gap-xs">
            <label className="font-label-sm text-label-sm text-on-surface-variant px-xs">Department</label>
            <select className="bg-white border border-outline-variant rounded-lg px-md py-sm text-body-md font-body-md focus:border-primary-container outline-none min-w-[200px]">
              <option>All Departments</option>
              <option>Engineering</option>
              <option>Operations</option>
              <option>Human Resources</option>
            </select>
          </div>
          <div className="flex items-end self-end h-full pt-6">
            <button 
              type="submit" 
              disabled={loading}
              className="bg-primary text-on-primary font-label-md text-label-md px-xl py-sm rounded-lg flex items-center gap-sm hover:opacity-90 disabled:opacity-50 active:scale-95 transition-all shadow-sm h-full"
            >
              <span className="material-symbols-outlined text-[18px]">search</span>
              {loading ? 'SEARCHING...' : 'SEARCH'}
            </button>
          </div>
        </form>
        <div className="flex items-end self-end h-full pt-6">
          <button onClick={handleExportCSV} className="bg-primary-container text-on-primary-container font-label-md text-label-md px-xl py-sm rounded-lg flex items-center gap-sm hover:opacity-90 active:scale-95 transition-all shadow-sm">
            <span className="material-symbols-outlined text-[18px]">download</span>
            EXPORT RECORDS
          </button>
        </div>
      </section>

      {error && (
        <div className="bg-error-container/20 border border-error/30 rounded-xl p-4 text-error mb-lg">
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-lg mb-lg">
        <div className="bg-white rounded-xl p-lg custom-shadow border-t-2 border-[#4CAF50]">
          <div className="flex justify-between items-start">
            <div>
              <p className="font-label-md text-label-md text-on-surface-variant mb-xs">Total Present</p>
              <h3 className="font-headline-lg text-headline-lg text-on-surface">{totalPresent}</h3>
            </div>
            <div className="p-sm bg-green-50 rounded-lg">
              <span className="material-symbols-outlined text-[#4CAF50]" style={{ fontVariationSettings: "'FILL' 1" }}>how_to_reg</span>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-lg custom-shadow border-t-2 border-[#F44336]">
          <div className="flex justify-between items-start">
            <div>
              <p className="font-label-md text-label-md text-on-surface-variant mb-xs">Total Absent</p>
              <h3 className="font-headline-lg text-headline-lg text-on-surface">{totalAbsent}</h3>
            </div>
            <div className="p-sm bg-red-50 rounded-lg">
              <span className="material-symbols-outlined text-[#F44336]" style={{ fontVariationSettings: "'FILL' 1" }}>person_off</span>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-lg custom-shadow border-t-2 border-[#FFD700]">
          <div className="flex justify-between items-start">
            <div>
              <p className="font-label-md text-label-md text-on-surface-variant mb-xs">Late Arrivals</p>
              <h3 className="font-headline-lg text-headline-lg text-on-surface">{totalLate}</h3>
            </div>
            <div className="p-sm bg-yellow-50 rounded-lg">
              <span className="material-symbols-outlined text-[#FFC107]" style={{ fontVariationSettings: "'FILL' 1" }}>alarm_on</span>
            </div>
          </div>
        </div>
      </section>

      {/* Attendance Table */}
      <section className="bg-white rounded-xl custom-shadow overflow-hidden border border-outline-variant">
        <div className="px-lg py-md border-b border-outline-variant flex justify-between items-center">
          <h4 className="font-headline-sm text-headline-sm text-on-surface">Daily Log: {new Date(date).toLocaleDateString()}</h4>
          <div className="flex items-center gap-md">
            <div className="relative">
              <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]">search</span>
              <input className="bg-surface-container-low border-none rounded-full pl-xl pr-md py-xs text-body-md outline-none w-64 focus:ring-2 focus:ring-primary-container" placeholder="Search employee..." type="text" />
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse striped-table">
            <thead>
              <tr className="bg-surface-container-low text-on-surface-variant font-label-md text-label-md border-b border-outline-variant">
                <th className="px-lg py-md font-bold uppercase tracking-wider">Timestamp</th>
                <th className="px-lg py-md font-bold uppercase tracking-wider">Employee Name</th>
                <th className="px-lg py-md font-bold uppercase tracking-wider">Type</th>
                <th className="px-lg py-md font-bold uppercase tracking-wider text-center">Biometric Score</th>
                <th className="px-lg py-md font-bold uppercase tracking-wider">Method</th>
                <th className="px-lg py-md font-bold uppercase tracking-wider">Status</th>
                <th className="px-lg py-md font-bold uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="text-body-md font-body-md text-on-surface">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-lg py-md text-center text-on-surface-variant">Loading records...</td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-lg py-md text-center text-on-surface-variant">No records found for {date}.</td>
                </tr>
              ) : (
                records.map((record, index) => (
                  <tr key={record.record_id || index} className="transition-colors hover:bg-surface-container-low border-b border-outline-variant">
                    <td className="px-lg py-md">
                      <span className="font-semibold block">{record.timestamp?.split(' ')[1] || record.timestamp}</span>
                      <span className="text-[11px] text-on-surface-variant">{record.timestamp?.split(' ')[0] || date}</span>
                    </td>
                    <td className="px-lg py-md flex items-center gap-md">
                      <div className="w-8 h-8 rounded-full bg-tertiary-container text-on-tertiary-container flex items-center justify-center text-[12px] font-bold">
                        {(record.staff_name || 'UN').substring(0,2).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-semibold">{record.staff_name || record.staff_id || 'Unknown'}</p>
                        <p className="text-[11px] text-on-surface-variant">ID: {record.staff_id}</p>
                      </div>
                    </td>
                    <td className="px-lg py-md">
                      <span className="bg-[#E8F5E9] text-[#2E7D32] px-sm py-xs rounded-full text-label-sm font-label-md flex items-center gap-xs w-fit">
                        <span className="material-symbols-outlined text-[14px]">login</span>
                        {record.event_type || 'Check-in'}
                      </span>
                    </td>
                    <td className="px-lg py-md text-center">
                      <div className="inline-flex items-center gap-xs bg-surface-container px-sm py-xs rounded-lg">
                        <span className="font-bold text-primary">{(record.face_score * 100 || 99).toFixed(1)}%</span>
                        <span className="material-symbols-outlined text-[16px] text-[#4CAF50]">verified</span>
                      </div>
                    </td>
                    <td className="px-lg py-md">
                      <div className="flex gap-xs">
                        <span className="material-symbols-outlined text-on-surface-variant" title="Face Recognition">face</span>
                        <span className="material-symbols-outlined text-on-surface-variant" title="Iris Scan">visibility</span>
                      </div>
                    </td>
                    <td className="px-lg py-md">
                      {getStatusColor(record.status)}
                    </td>
                    <td className="px-lg py-md text-right">
                      <button 
                        onClick={() => handleDelete(record.record_id)}
                        className="text-error hover:bg-error-container/20 p-xs rounded-full transition-colors"
                        title="Delete Record"
                      >
                        <span className="material-symbols-outlined text-[20px]">delete</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default Records;
