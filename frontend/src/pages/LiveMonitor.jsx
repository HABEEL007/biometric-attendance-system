import { useState, useEffect } from 'react';
import { startCamera, stopCamera, getCameraStatus, processSnapshot } from '../services/api';

const LiveMonitor = () => {
  const [status, setStatus] = useState('INACTIVE');
  const [loading, setLoading] = useState(false);
  const [snapshotResult, setSnapshotResult] = useState(null);

  useEffect(() => {
    checkStatus();
    // Poll status occasionally
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      const data = await getCameraStatus();
      setStatus(data.is_running ? 'ACTIVE' : 'INACTIVE');
    } catch (err) {
      setStatus('OFFLINE');
    }
  };

  const handleStart = async () => {
    setLoading(true);
    try {
      await startCamera({ source: "0", camera_id: "main_gate" });
      await checkStatus();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await stopCamera();
      await checkStatus();
      setSnapshotResult(null);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSnapshot = async () => {
    setLoading(true);
    try {
      const result = await processSnapshot();
      setSnapshotResult(result);
    } catch (err) {
      console.error(err);
      alert('Failed to process snapshot');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-margin-desktop flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="font-headline-md text-headline-md text-primary">Live Monitor</h2>
          <p className="text-on-surface-variant text-body-sm mt-1">Real-time camera feed and biometric analysis.</p>
        </div>
        
        <div className="flex gap-4">
          <span className={`px-4 py-2 rounded-lg font-label-md flex items-center gap-2 border ${status === 'ACTIVE' ? 'bg-secondary/10 border-secondary text-secondary' : 'bg-outline-variant/30 border-outline-variant text-outline'}`}>
            <span className="w-2 h-2 rounded-full bg-current" />
            {status}
          </span>
          
          {status !== 'ACTIVE' ? (
            <button onClick={handleStart} disabled={loading} className="bg-primary text-on-primary px-6 py-2 rounded-lg font-label-md hover:opacity-90 disabled:opacity-50">
              Start Camera
            </button>
          ) : (
            <button onClick={handleStop} disabled={loading} className="bg-error text-on-error px-6 py-2 rounded-lg font-label-md hover:opacity-90 disabled:opacity-50">
              Stop Camera
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Camera View */}
        <div className="lg:col-span-2 bg-black rounded-xl border border-outline-variant overflow-hidden flex flex-col relative min-h-[400px]">
          {status === 'ACTIVE' ? (
             <div className="flex-1 flex items-center justify-center relative">
               <span className="text-outline">Camera is active in backend process.</span>
               <div className="absolute top-4 left-4 bg-error/20 text-error px-3 py-1 rounded text-label-sm font-label-sm flex items-center gap-2 border border-error/50">
                 <span className="w-2 h-2 rounded-full bg-error animate-pulse" />
                 REC
               </div>
               
               <button onClick={handleSnapshot} disabled={loading} className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-surface/80 backdrop-blur-md text-primary border border-primary/50 px-6 py-3 rounded-full hover:bg-primary hover:text-on-primary transition-all flex items-center gap-2 shadow-glow">
                 <span className="material-symbols-outlined">center_focus_strong</span>
                 Process Frame
               </button>
             </div>
          ) : (
             <div className="flex-1 flex flex-col items-center justify-center text-outline-variant">
               <span className="material-symbols-outlined text-[64px] mb-4 opacity-50">videocam_off</span>
               <p>Camera is currently inactive</p>
             </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="bg-surface-container rounded-xl border border-outline-variant p-6 overflow-y-auto">
          <h3 className="font-title-lg text-primary mb-4 border-b border-outline-variant pb-4">Verification Results</h3>
          
          {!snapshotResult ? (
            <p className="text-on-surface-variant text-center mt-10">No snapshot processed yet.</p>
          ) : (
            <div className="space-y-6">
               <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-full ${snapshotResult.success ? 'bg-secondary/20 text-secondary' : 'bg-error/20 text-error'}`}>
                    <span className="material-symbols-outlined text-[32px]">{snapshotResult.success ? 'check_circle' : 'cancel'}</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-[18px]">{snapshotResult.success ? 'Access Granted' : 'Access Denied'}</h4>
                    <p className="text-on-surface-variant text-sm">{snapshotResult.message}</p>
                  </div>
               </div>

               {snapshotResult.face_verification && snapshotResult.face_verification.staff && (
                 <div className="bg-surface-container-low p-4 rounded-lg border border-outline-variant mt-4">
                   <p className="font-label-sm text-primary mb-1">Identified Employee</p>
                   <p className="font-bold text-lg">{snapshotResult.face_verification.staff.name}</p>
                   <p className="text-on-surface-variant text-sm">{snapshotResult.face_verification.staff.role}</p>
                 </div>
               )}
               
               <div className="space-y-4 pt-4 border-t border-outline-variant">
                 <div>
                   <div className="flex justify-between text-sm mb-1">
                     <span className="text-on-surface-variant">Face Confidence</span>
                     <span className={snapshotResult.face_verification?.success ? 'text-secondary' : 'text-error'}>
                       {snapshotResult.face_verification?.confidence ? (snapshotResult.face_verification.confidence * 100).toFixed(1) + '%' : 'N/A'}
                     </span>
                   </div>
                   <div className="w-full bg-surface-variant h-2 rounded-full overflow-hidden">
                     <div className={`h-full ${snapshotResult.face_verification?.success ? 'bg-secondary' : 'bg-error'}`} style={{ width: snapshotResult.face_verification?.confidence ? `${snapshotResult.face_verification.confidence * 100}%` : '0%' }} />
                   </div>
                 </div>
                 
                 <div>
                   <div className="flex justify-between text-sm mb-1">
                     <span className="text-on-surface-variant">Iris Verification</span>
                     <span className={snapshotResult.iris_verification?.success ? 'text-secondary' : 'text-error'}>
                       {snapshotResult.iris_verification?.confidence ? (snapshotResult.iris_verification.confidence * 100).toFixed(1) + '%' : 'N/A'}
                     </span>
                   </div>
                   <div className="w-full bg-surface-variant h-2 rounded-full overflow-hidden">
                     <div className={`h-full ${snapshotResult.iris_verification?.success ? 'bg-secondary' : 'bg-error'}`} style={{ width: snapshotResult.iris_verification?.confidence ? `${snapshotResult.iris_verification.confidence * 100}%` : '0%' }} />
                   </div>
                 </div>

                 <div>
                   <div className="flex justify-between text-sm mb-1">
                     <span className="text-on-surface-variant">Liveness Check</span>
                     <span className={snapshotResult.liveness_verification?.is_live ? 'text-secondary' : 'text-error'}>
                       {snapshotResult.liveness_verification?.liveness_score ? (snapshotResult.liveness_verification.liveness_score * 100).toFixed(1) + '%' : 'N/A'}
                     </span>
                   </div>
                   <div className="w-full bg-surface-variant h-2 rounded-full overflow-hidden">
                     <div className={`h-full ${snapshotResult.liveness_verification?.is_live ? 'bg-secondary' : 'bg-error'}`} style={{ width: snapshotResult.liveness_verification?.liveness_score ? `${snapshotResult.liveness_verification.liveness_score * 100}%` : '0%' }} />
                   </div>
                 </div>
               </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveMonitor;
