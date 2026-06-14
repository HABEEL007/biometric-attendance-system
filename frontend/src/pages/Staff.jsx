import React, { useEffect, useState } from 'react';
import { getStaff, deleteStaff } from '../services/api';

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

  const handleDelete = async (employeeId) => {
    if (window.confirm(`Are you sure you want to delete employee ID ${employeeId}?`)) {
      try {
        await deleteStaff(employeeId);
        fetchStaff();
      } catch (err) {
        console.error('Failed to delete staff:', err);
        alert('Failed to delete staff member.');
      }
    }
  };

  return (
    <div className="p-xl max-w-container-max mx-auto w-full">
      <section className="space-y-lg">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-md">
          <div>
            <nav className="flex items-center gap-xs text-label-md text-on-surface-variant mb-xs">
              <span>Resources</span>
              <span className="material-symbols-outlined text-[14px]">chevron_right</span>
              <span className="text-primary font-bold">Staff Directory</span>
            </nav>
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Staff Directory</h2>
            <p className="font-body-md text-body-md text-on-surface-variant">Manage and monitor biometric enrollment for your enterprise workforce.</p>
          </div>
          <button className="bg-primary-container text-on-primary-container px-lg py-md rounded-lg font-body-md font-bold flex items-center gap-sm shadow-sm hover:opacity-90 active:scale-95 transition-all">
            <span className="material-symbols-outlined">person_add</span>
            Add New Staff
          </button>
        </div>

        {error && (
          <div className="bg-error-container/20 border border-error/30 rounded-xl p-4 text-error mb-lg">
            {error}
          </div>
        )}

        {/* Filters Bento Area */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-md">
          <div className="md:col-span-2 bg-surface border border-outline-variant rounded-xl p-md flex items-center gap-md shadow-sm">
            <div className="flex-1 relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">person_search</span>
              <input className="w-full bg-surface-container-lowest border-none focus:ring-0 text-body-md py-1 pl-10 outline-none" placeholder="Search by name, ID or department..." type="text" />
            </div>
          </div>
          <div className="bg-surface border border-outline-variant rounded-xl p-md flex items-center justify-between shadow-sm cursor-pointer hover:bg-surface-container-low transition-colors">
            <div className="flex items-center gap-sm">
              <span className="material-symbols-outlined text-on-surface-variant">category</span>
              <span className="text-body-md text-on-surface">Department</span>
            </div>
            <span className="material-symbols-outlined text-on-surface-variant">expand_more</span>
          </div>
          <div className="bg-surface border border-outline-variant rounded-xl p-md flex items-center justify-between shadow-sm cursor-pointer hover:bg-surface-container-low transition-colors">
            <div className="flex items-center gap-sm">
              <span className="material-symbols-outlined text-on-surface-variant">verified_user</span>
              <span className="text-body-md text-on-surface">Status</span>
            </div>
            <span className="material-symbols-outlined text-on-surface-variant">expand_more</span>
          </div>
        </div>

        {/* Staff Table Container */}
        <div className="bg-surface border border-outline-variant rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-surface-container text-on-surface-variant border-b border-outline-variant">
                  <th className="px-lg py-md font-label-md text-label-md uppercase tracking-wider">ID</th>
                  <th className="px-lg py-md font-label-md text-label-md uppercase tracking-wider">Staff Name</th>
                  <th className="px-lg py-md font-label-md text-label-md uppercase tracking-wider">Department</th>
                  <th className="px-lg py-md font-label-md text-label-md uppercase tracking-wider">Role</th>
                  <th className="px-lg py-md font-label-md text-label-md uppercase tracking-wider">Status</th>
                  <th className="px-lg py-md font-label-md text-label-md uppercase tracking-wider text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="px-lg py-md font-body-md text-on-surface text-center">Loading staff...</td>
                  </tr>
                ) : staffList.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-lg py-md font-body-md text-on-surface text-center">No staff members found.</td>
                  </tr>
                ) : (
                  staffList.map((staff, index) => (
                    <tr key={staff.employee_id} className="staff-table-row transition-colors group">
                      <td className="px-lg py-md font-body-md text-on-surface font-semibold">#{staff.employee_id}</td>
                      <td className="px-lg py-md">
                        <div className="flex items-center gap-md">
                          <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-[12px] font-bold text-primary">
                            {(staff.name || 'UN').substring(0, 2).toUpperCase()}
                          </div>
                          <span className="font-body-md text-on-surface">{staff.name}</span>
                        </div>
                      </td>
                      <td className="px-lg py-md font-body-md text-on-surface-variant">{staff.department || '-'}</td>
                      <td className="px-lg py-md font-body-md text-on-surface-variant">{staff.role || '-'}</td>
                      <td className="px-lg py-md">
                        {staff.is_active ? (
                          <span className="inline-flex items-center px-sm py-xs rounded-full bg-green-100 text-green-700 font-label-md text-[10px] uppercase">Active</span>
                        ) : (
                          <span className="inline-flex items-center px-sm py-xs rounded-full bg-red-100 text-red-700 font-label-md text-[10px] uppercase">Inactive</span>
                        )}
                      </td>
                      <td className="px-lg py-md text-right">
                        <div className="flex items-center justify-end gap-sm opacity-0 group-hover:opacity-100 transition-opacity">
                          <button className="p-xs hover:bg-surface-container-highest rounded-md text-on-surface-variant hover:text-primary" title="View"><span className="material-symbols-outlined text-[20px]">visibility</span></button>
                          <button className="p-xs hover:bg-surface-container-highest rounded-md text-on-surface-variant hover:text-primary" title="Edit"><span className="material-symbols-outlined text-[20px]">edit</span></button>
                          <button onClick={() => handleDelete(staff.employee_id)} className="p-xs hover:bg-surface-container-highest rounded-md text-on-surface-variant hover:text-error" title="Delete"><span className="material-symbols-outlined text-[20px]">delete</span></button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {/* Pagination */}
          <div className="bg-surface border-t border-outline-variant px-lg py-md flex items-center justify-between">
            <p className="font-label-md text-label-md text-on-surface-variant">Showing {staffList.length} results</p>
            <div className="flex items-center gap-xs">
              <button className="w-8 h-8 flex items-center justify-center rounded-lg border border-outline-variant text-on-surface-variant hover:bg-surface-container transition-colors disabled:opacity-40" disabled>
                <span className="material-symbols-outlined text-[18px]">chevron_left</span>
              </button>
              <button className="w-8 h-8 flex items-center justify-center rounded-lg bg-primary-container text-on-primary-container font-body-md font-bold">1</button>
              <button className="w-8 h-8 flex items-center justify-center rounded-lg border border-outline-variant text-on-surface-variant hover:bg-surface-container transition-colors disabled:opacity-40" disabled>
                <span className="material-symbols-outlined text-[18px]">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Staff;
