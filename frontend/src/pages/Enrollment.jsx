import { useState } from 'react';
import { enrollStaff } from '../services/api';

const Enrollment = () => {
  const [formData, setFormData] = useState({
    employee_id: '',
    name: '',
    role: '',
    department: '',
    shift_start_time: '09:00'
  });
  const [faceImages, setFaceImages] = useState([]);
  const [eyeImages, setEyeImages] = useState([]);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleImageUpload = (e, type) => {
    const files = Array.from(e.target.files);
    
    files.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        // Remove the data URL prefix (e.g., "data:image/jpeg;base64,") to send raw base64
        const base64String = reader.result.split(',')[1];
        if (type === 'face') {
          setFaceImages(prev => [...prev, base64String]);
        } else {
          setEyeImages(prev => [...prev, base64String]);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: '', message: '' });

    if (faceImages.length === 0 || eyeImages.length === 0) {
      setStatus({ type: 'error', message: 'You must provide at least one face image and one eye image.' });
      setLoading(false);
      return;
    }
    
    try {
      const payload = { ...formData, face_images: faceImages, eye_images: eyeImages };
      await enrollStaff(payload);
      setStatus({ type: 'success', message: 'Staff member enrolled successfully!' });
      
      // Reset form
      setFormData({ employee_id: '', name: '', role: '', department: '', shift_start_time: '09:00' });
      setFaceImages([]);
      setEyeImages([]);
    } catch (err) {
      console.error(err);
      setStatus({ type: 'error', message: err.response?.data?.detail || 'Failed to enroll staff member.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-margin-desktop flex flex-col gap-6 max-w-4xl">
      <div>
        <h2 className="font-headline-md text-headline-md text-primary">New Enrollment</h2>
        <p className="text-on-surface-variant text-body-sm mt-1">Register a new employee and their biometric data.</p>
      </div>

      {status.message && (
        <div className={`p-4 rounded-xl border ${status.type === 'success' ? 'bg-secondary-container/20 border-secondary-container text-secondary' : 'bg-error-container/20 border-error/30 text-error'}`}>
          {status.message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-surface-container rounded-xl border border-outline-variant p-8 flex flex-col gap-8">
        
        {/* Personal Details Section */}
        <section>
          <h3 className="font-title-lg text-primary mb-4 border-b border-outline-variant pb-2">Employee Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex flex-col gap-2">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Employee ID</label>
              <input 
                type="text" name="employee_id" value={formData.employee_id} onChange={handleChange} required
                className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2.5 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all"
                placeholder="e.g. EMP-101"
              />
            </div>
            
            <div className="flex flex-col gap-2">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Full Name</label>
              <input 
                type="text" name="name" value={formData.name} onChange={handleChange} required
                className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2.5 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all"
                placeholder="e.g. Jane Doe"
              />
            </div>
            
            <div className="flex flex-col gap-2">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Role</label>
              <input 
                type="text" name="role" value={formData.role} onChange={handleChange}
                className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2.5 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all"
                placeholder="e.g. Security Engineer"
              />
            </div>
            
            <div className="flex flex-col gap-2">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Department</label>
              <input 
                type="text" name="department" value={formData.department} onChange={handleChange}
                className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2.5 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all"
                placeholder="e.g. IT"
              />
            </div>
            
            <div className="flex flex-col gap-2">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Shift Start Time</label>
              <input 
                type="time" name="shift_start_time" value={formData.shift_start_time} onChange={handleChange}
                className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2.5 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all"
              />
            </div>
          </div>
        </section>

        {/* Biometrics Section */}
        <section>
          <h3 className="font-title-lg text-primary mb-4 border-b border-outline-variant pb-2">Biometric Capture</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            
            {/* Face Capture */}
            <div className="flex flex-col gap-4 p-6 bg-surface-container-low border border-outline-variant rounded-xl">
              <div className="flex justify-between items-center">
                <span className="font-bold text-on-surface">Face Images</span>
                <span className={`text-sm ${faceImages.length > 0 ? 'text-secondary' : 'text-error'}`}>
                  {faceImages.length} Captured
                </span>
              </div>
              <p className="text-sm text-on-surface-variant">Upload at least 1 clear photo of the employee's face.</p>
              
              <div className="flex items-center justify-center w-full">
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-outline-variant border-dashed rounded-lg cursor-pointer bg-surface hover:bg-surface-variant transition-colors">
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                          <span className="material-symbols-outlined text-outline-variant mb-2 text-3xl">add_a_photo</span>
                          <p className="mb-2 text-sm text-on-surface-variant"><span className="font-bold">Click to upload</span> or drag and drop</p>
                      </div>
                      <input type="file" accept="image/*" multiple onChange={(e) => handleImageUpload(e, 'face')} className="hidden" />
                  </label>
              </div>
              
              {faceImages.length > 0 && (
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {faceImages.map((b64, idx) => (
                    <img key={idx} src={`data:image/jpeg;base64,${b64}`} alt={`Face ${idx}`} className="w-16 h-16 object-cover rounded-md border border-primary" />
                  ))}
                </div>
              )}
            </div>

            {/* Eye Capture */}
            <div className="flex flex-col gap-4 p-6 bg-surface-container-low border border-outline-variant rounded-xl">
              <div className="flex justify-between items-center">
                <span className="font-bold text-on-surface">Iris/Eye Images</span>
                <span className={`text-sm ${eyeImages.length > 0 ? 'text-secondary' : 'text-error'}`}>
                  {eyeImages.length} Captured
                </span>
              </div>
              <p className="text-sm text-on-surface-variant">Upload clear close-up photos of the employee's eyes.</p>
              
              <div className="flex items-center justify-center w-full">
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-outline-variant border-dashed rounded-lg cursor-pointer bg-surface hover:bg-surface-variant transition-colors">
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                          <span className="material-symbols-outlined text-outline-variant mb-2 text-3xl">visibility</span>
                          <p className="mb-2 text-sm text-on-surface-variant"><span className="font-bold">Click to upload</span> or drag and drop</p>
                      </div>
                      <input type="file" accept="image/*" multiple onChange={(e) => handleImageUpload(e, 'eye')} className="hidden" />
                  </label>
              </div>

              {eyeImages.length > 0 && (
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {eyeImages.map((b64, idx) => (
                    <img key={idx} src={`data:image/jpeg;base64,${b64}`} alt={`Eye ${idx}`} className="w-16 h-16 object-cover rounded-md border border-primary" />
                  ))}
                </div>
              )}
            </div>

          </div>
        </section>

        <div className="border-t border-outline-variant pt-6 mt-2 flex justify-end">
          <button 
            type="submit" disabled={loading}
            className="bg-primary text-on-primary px-8 py-2.5 rounded-lg font-label-md hover:opacity-90 disabled:opacity-50 transition-all Active:scale-95 flex items-center gap-2"
          >
            {loading ? 'Processing...' : 'Complete Enrollment'}
            {!loading && <span className="material-symbols-outlined text-[18px]">how_to_reg</span>}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Enrollment;
