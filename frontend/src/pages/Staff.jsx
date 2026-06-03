import { useEffect, useState } from 'react';
import { getStaff } from '../services/api';

const Staff = () => {
  const [staffList, setStaffList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStaff();
  }, []);

  const fetchStaff = async () => {
    try {
      setLoading(true);
      const data = await getStaff();
      setStaffList(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch staff:', err);
      setError('Failed to load staff members. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-margin-desktop flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="font-headline-md text-headline-md text-primary">Staff Management</h2>
          <p className="text-on-surface-variant text-body-sm mt-1">Manage and view all registered employees.</p>
        </div>
        <button className="bg-primary text-on-primary px-4 py-2 rounded-lg font-label-md hover:opacity-90 flex items-center gap-2">
          <span className="material-symbols-outlined text-[20px]">add</span>
          New Employee
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
              <th className="px-6 py-4">Employee ID</th>
              <th className="px-6 py-4">Name</th>
              <th className="px-6 py-4">Role</th>
              <th className="px-6 py-4">Department</th>
              <th className="px-6 py-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant font-body-sm text-body-sm text-on-surface">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-on-surface-variant">
                  Loading staff data...
                </td>
              </tr>
            ) : staffList.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-on-surface-variant">
                  No staff members found.
                </td>
              </tr>
            ) : (
              staffList.map((staff, index) => (
                <tr key={staff.employee_id} className={index % 2 === 0 ? 'bg-surface-container-low' : 'bg-surface-container'}>
                  <td className="px-6 py-4 font-label-sm text-primary">{staff.employee_id}</td>
                  <td className="px-6 py-4 font-medium">{staff.name}</td>
                  <td className="px-6 py-4 text-on-surface-variant">{staff.role || '-'}</td>
                  <td className="px-6 py-4 text-on-surface-variant">{staff.department || '-'}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-label-sm font-label-sm ${staff.is_active ? 'bg-secondary/10 text-secondary' : 'bg-outline-variant/30 text-outline'}`}>
                      {staff.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Staff;
