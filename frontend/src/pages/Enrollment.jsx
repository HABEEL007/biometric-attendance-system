import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { enrollStaff } from '../services/api';

const Enrollment = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    employee_id: '',
    name: '',
    role: '',
    department: 'Engineering',
    shift_start_time: '09:00',
    email: ''
  });
  const [faceImages, setFaceImages] = useState([]);
  const [eyeImages, setEyeImages] = useState([]);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleImageUpload = (e, type) => {
    const files = Array.from(e.target.files);
    files.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
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

  const handleSubmit = async () => {
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
      setShowSuccessModal(true);
    } catch (err) {
      console.error(err);
      setStatus({ type: 'error', message: err.response?.data?.detail || 'Failed to enroll staff member.' });
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({ employee_id: '', name: '', role: '', department: 'Engineering', shift_start_time: '09:00', email: '' });
    setFaceImages([]);
    setEyeImages([]);
    setStep(1);
    setStatus({ type: '', message: '' });
    setShowSuccessModal(false);
  };

  const progressMap = { 1: '0%', 2: '50%', 3: '100%' };

  return (
    <div className="p-xl max-w-container-max mx-auto w-full">
        {/* Progress Indicator */}
        <div className="mb-xl bg-white p-lg rounded-xl shadow-sm border border-[#E5E7EB]">
          <div className="flex justify-between items-center max-w-2xl mx-auto relative">
            {/* Connector Lines */}
            <div className="absolute top-5 left-0 w-full h-0.5 bg-[#E5E7EB] -z-0"></div>
            <div className="absolute top-5 left-0 h-0.5 bg-primary-container transition-all duration-500 -z-0" style={{ width: progressMap[step] }}></div>
            
            {/* Step 1 */}
            <div className="relative z-10 flex flex-col items-center gap-2">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${step >= 1 ? 'bg-primary-container text-on-primary-container' : 'bg-white border-2 border-[#E5E7EB] text-on-surface-variant'}`}>
                {step > 1 ? <span className="material-symbols-outlined text-[20px]">check</span> : '1'}
              </div>
              <span className={`font-label-md text-label-md ${step >= 1 ? 'text-on-surface font-bold' : 'text-on-surface-variant'}`}>Details</span>
            </div>
            
            {/* Step 2 */}
            <div className="relative z-10 flex flex-col items-center gap-2">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${step >= 2 ? 'bg-primary-container text-on-primary-container' : 'bg-white border-2 border-[#E5E7EB] text-on-surface-variant'}`}>
                {step > 2 ? <span className="material-symbols-outlined text-[20px]">check</span> : '2'}
              </div>
              <span className={`font-label-md text-label-md ${step >= 2 ? 'text-on-surface font-bold' : 'text-on-surface-variant'}`}>Face Capture</span>
            </div>
            
            {/* Step 3 */}
            <div className="relative z-10 flex flex-col items-center gap-2">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${step >= 3 ? 'bg-primary-container text-on-primary-container' : 'bg-white border-2 border-[#E5E7EB] text-on-surface-variant'}`}>
                {step > 3 ? <span className="material-symbols-outlined text-[20px]">check</span> : '3'}
              </div>
              <span className={`font-label-md text-label-md ${step >= 3 ? 'text-on-surface font-bold' : 'text-on-surface-variant'}`}>Iris Capture</span>
            </div>
          </div>
        </div>

        {status.message && (
          <div className={`mb-lg p-4 rounded-xl border ${status.type === 'success' ? 'bg-secondary-container/20 border-secondary-container text-secondary' : 'bg-error-container/20 border-error/30 text-error'}`}>
            {status.message}
          </div>
        )}

        {/* Enrollment Card */}
        <div className="bg-white rounded-xl shadow-sm border border-[#E5E7EB] min-h-[500px] flex flex-col overflow-hidden">
          
          {/* Step 1 Content: Employee Details */}
          {step === 1 && (
            <div className="p-xl flex-1 flex flex-col">
              <div className="mb-lg">
                <h2 className="font-headline-lg text-headline-lg mb-2">Employee Information</h2>
                <p className="text-on-surface-variant">Enter the base credentials to begin the biometric enrollment process.</p>
              </div>
              <div className="grid grid-cols-2 gap-lg">
                <div className="flex flex-col gap-2">
                  <label className="text-label-md text-on-surface-variant">Full Name</label>
                  <input name="name" value={formData.name} onChange={handleChange} className="w-full px-md py-3 rounded-lg border border-[#E5E7EB] focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all" placeholder="e.g. Jonathan Doe" type="text" />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-label-md text-on-surface-variant">Employee ID</label>
                  <input name="employee_id" value={formData.employee_id} onChange={handleChange} className="w-full px-md py-3 rounded-lg border border-[#E5E7EB] focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all" placeholder="EMP-00123" type="text" />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-label-md text-on-surface-variant">Email Address</label>
                  <input name="email" value={formData.email} onChange={handleChange} className="w-full px-md py-3 rounded-lg border border-[#E5E7EB] focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all" placeholder="j.doe@enterprise.com" type="email" />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-label-md text-on-surface-variant">Department</label>
                  <select name="department" value={formData.department} onChange={handleChange} className="w-full px-md py-3 rounded-lg border border-[#E5E7EB] focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all bg-white">
                    <option value="Engineering">Engineering</option>
                    <option value="Operations">Operations</option>
                    <option value="Human Resources">Human Resources</option>
                    <option value="Security">Security</option>
                  </select>
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-label-md text-on-surface-variant">Role</label>
                  <input name="role" value={formData.role} onChange={handleChange} className="w-full px-md py-3 rounded-lg border border-[#E5E7EB] focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all" placeholder="e.g. Security Engineer" type="text" />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-label-md text-on-surface-variant">Shift Start Time</label>
                  <input name="shift_start_time" value={formData.shift_start_time} onChange={handleChange} className="w-full px-md py-3 rounded-lg border border-[#E5E7EB] focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all" type="time" />
                </div>
              </div>
              <div className="mt-auto pt-xl flex justify-end">
                <button onClick={() => setStep(2)} className="bg-primary-container text-on-primary-container px-xl py-3 rounded-lg font-semibold hover:opacity-90 transition-all flex items-center gap-2">
                  Next Step
                  <span className="material-symbols-outlined">arrow_forward</span>
                </button>
              </div>
            </div>
          )}

          {/* Step 2 Content: Face Capture */}
          {step === 2 && (
            <div className="p-xl flex-1 flex flex-col">
              <div className="mb-lg">
                <h2 className="font-headline-lg text-headline-lg mb-2">Face Recognition Setup</h2>
                <p className="text-on-surface-variant">Ensure the subject is in a well-lit area and looking directly at the camera.</p>
              </div>
              <div className="flex flex-col md:flex-row gap-xl h-full flex-1">
                <div className="flex-1 bg-surface-container rounded-xl overflow-hidden relative group border border-outline-variant flex items-center justify-center min-h-[300px]">
                  <span className="material-symbols-outlined text-[64px] text-outline-variant opacity-50">face</span>
                  <div className="absolute bottom-6 left-1/2 -translate-x-1/2">
                    <label className="bg-white border-2 border-primary-container text-primary-container px-lg py-2 rounded-full font-bold hover:bg-primary-container hover:text-on-primary-container transition-all flex items-center gap-2 cursor-pointer shadow-md">
                      <span className="material-symbols-outlined">camera</span>
                      Upload Face Photo
                      <input type="file" accept="image/*" multiple onChange={(e) => handleImageUpload(e, 'face')} className="hidden" />
                    </label>
                  </div>
                </div>
                <div className="w-full md:w-48 flex flex-col gap-md">
                  <p className="text-label-md font-bold uppercase tracking-wider text-on-surface-variant">Captured Samples ({faceImages.length})</p>
                  <div className="flex md:flex-col gap-md overflow-x-auto md:overflow-visible">
                    {faceImages.map((b64, idx) => (
                      <div key={idx} className="w-24 h-24 md:w-full md:aspect-square shrink-0 bg-surface-container-high rounded-lg border-2 border-primary overflow-hidden">
                        <img src={`data:image/jpeg;base64,${b64}`} alt={`Face ${idx}`} className="w-full h-full object-cover" />
                      </div>
                    ))}
                    {faceImages.length < 3 && (
                      <label className="w-24 h-24 md:w-full md:aspect-square shrink-0 bg-surface-container-high rounded-lg border-2 border-dashed border-outline-variant flex items-center justify-center hover:border-primary transition-colors cursor-pointer">
                        <span className="material-symbols-outlined text-outline">add_a_photo</span>
                        <input type="file" accept="image/*" onChange={(e) => handleImageUpload(e, 'face')} className="hidden" />
                      </label>
                    )}
                  </div>
                </div>
              </div>
              <div className="mt-xl pt-lg border-t border-[#E5E7EB] flex justify-between">
                <button onClick={() => setStep(1)} className="px-xl py-3 text-on-surface hover:bg-surface-container transition-all flex items-center gap-2">
                  <span className="material-symbols-outlined">arrow_back</span> Previous
                </button>
                <button onClick={() => setStep(3)} className="bg-primary-container text-on-primary-container px-xl py-3 rounded-lg font-semibold hover:opacity-90 transition-all flex items-center gap-2">
                  Next Step <span className="material-symbols-outlined">arrow_forward</span>
                </button>
              </div>
            </div>
          )}

          {/* Step 3 Content: Iris Capture */}
          {step === 3 && (
            <div className="p-xl flex-1 flex flex-col">
              <div className="mb-lg">
                <h2 className="font-headline-lg text-headline-lg mb-2">Iris Biometrics</h2>
                <p className="text-on-surface-variant">Please align the subject's eyes within the designated scanning zones.</p>
              </div>
              <div className="flex-1 flex flex-col md:flex-row gap-lg items-center justify-center py-lg">
                <div className="flex flex-col items-center gap-md">
                  <div className="w-56 h-56 rounded-full border-4 border-outline-variant relative overflow-hidden bg-surface-container-highest group flex items-center justify-center">
                    <span className="material-symbols-outlined text-[64px] text-outline-variant">visibility</span>
                    {eyeImages[0] && (
                      <img src={`data:image/jpeg;base64,${eyeImages[0]}`} className="absolute inset-0 w-full h-full object-cover z-10" alt="Left Eye" />
                    )}
                  </div>
                  <label className="border-2 border-primary-container text-on-surface px-lg py-2 rounded-lg font-semibold hover:bg-primary-container transition-all cursor-pointer">
                    Upload Eye Photo
                    <input type="file" accept="image/*" onChange={(e) => handleImageUpload(e, 'eye')} className="hidden" />
                  </label>
                </div>
                <div className="flex flex-col items-center gap-md">
                   <p className="text-label-md font-bold uppercase text-on-surface-variant">Uploaded Eyes: {eyeImages.length}</p>
                   <div className="flex gap-2 flex-wrap max-w-[200px] justify-center">
                     {eyeImages.map((b64, idx) => (
                       <img key={idx} src={`data:image/jpeg;base64,${b64}`} className="w-12 h-12 rounded object-cover border border-primary" alt={`Eye ${idx}`} />
                     ))}
                   </div>
                </div>
              </div>
              <div className="mt-xl pt-lg border-t border-[#E5E7EB] flex justify-between">
                <button onClick={() => setStep(2)} className="px-xl py-3 text-on-surface hover:bg-surface-container transition-all flex items-center gap-2">
                  <span className="material-symbols-outlined">arrow_back</span> Previous
                </button>
                <button onClick={handleSubmit} disabled={loading} className="bg-primary-container text-on-primary-container px-xl py-3 rounded-lg font-bold hover:opacity-90 transition-all shadow-md active:scale-95 disabled:opacity-50">
                  {loading ? 'Processing...' : 'Complete Enrollment'}
                </button>
              </div>
            </div>
          )}
        </div>

      {/* Success Notification Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-lg">
          <div className="bg-white rounded-xl max-w-[448px] w-full p-xl text-center shadow-2xl scale-100 transition-all border border-outline-variant">
            <div className="w-20 h-20 bg-primary-container text-on-primary-container rounded-full flex items-center justify-center mx-auto mb-lg">
              <span className="material-symbols-outlined text-[40px]" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
            </div>
            <h3 className="font-headline-lg text-headline-lg mb-2">Enrollment Successful</h3>
            <p className="text-on-surface-variant mb-xl">The biometric profile for {formData.name || 'the employee'} has been successfully added to the enterprise secure database.</p>
            <div className="flex flex-col gap-3">
              <button onClick={resetForm} className="bg-primary-container text-on-primary-container py-3 rounded-lg font-bold hover:opacity-90">New Enrollment</button>
              <button onClick={() => navigate('/')} className="text-primary font-semibold py-3 hover:bg-surface-container rounded-lg">Return to Dashboard</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Enrollment;
