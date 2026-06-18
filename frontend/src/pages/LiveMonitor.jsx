import React, { useState, useEffect, useRef } from 'react';
import { startCamera, stopCamera, getCameraStatus, processSnapshot, verifyFrame, API_URL } from '../services/api';

const LiveMonitor = () => {
  const [status, setStatus] = useState('INACTIVE');
  const [loading, setLoading] = useState(false);
  const [snapshotResult, setSnapshotResult] = useState(null);
  const [rtspUrl, setRtspUrl] = useState('');
  
  // Local Webcam State
  const [useLocalWebcam, setUseLocalWebcam] = useState(true);
  const [autoDetect, setAutoDetect] = useState(false);
  const [videoDevices, setVideoDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState('');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const autoDetectInterval = useRef(null);
  const [recentEvents, setRecentEvents] = useState([]);

  useEffect(() => {
    const getDevices = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoInputDevices = devices.filter(device => device.kind === 'videoinput');
        setVideoDevices(videoInputDevices);
        if (videoInputDevices.length > 0 && !selectedDeviceId) {
          setSelectedDeviceId(videoInputDevices[0].deviceId);
        }
      } catch (err) {
        console.error("Error fetching devices:", err);
      }
    };
    if (useLocalWebcam) {
      getDevices();
      navigator.mediaDevices.addEventListener('devicechange', getDevices);
      return () => navigator.mediaDevices.removeEventListener('devicechange', getDevices);
    }
  }, [useLocalWebcam]);

  useEffect(() => {
    if (!useLocalWebcam) {
      checkStatus();
      const interval = setInterval(checkStatus, 5000);
      return () => clearInterval(interval);
    } else {
      // Do not auto-start local camera. User must click Start.
      return () => stopLocalCamera();
    }
  }, [useLocalWebcam]);

  useEffect(() => {
    if (useLocalWebcam && status === 'ACTIVE') {
      startLocalCamera();
    }
  }, [selectedDeviceId]);

  useEffect(() => {
    if (status === 'ACTIVE' && useLocalWebcam && videoRef.current && streamRef.current) {
      if (videoRef.current.srcObject !== streamRef.current) {
        videoRef.current.srcObject = streamRef.current;
      }
    }
  }, [status, useLocalWebcam]);

  useEffect(() => {
    if (autoDetect && status === 'ACTIVE') {
      autoDetectInterval.current = setInterval(() => {
        if (!loading) {
          if (useLocalWebcam) {
            handleLocalSnapshot();
          } else {
            handleSnapshot();
          }
        }
      }, 3000);
    } else {
      if (autoDetectInterval.current) {
        clearInterval(autoDetectInterval.current);
      }
    }
    return () => clearInterval(autoDetectInterval.current);
  }, [useLocalWebcam, autoDetect, status, loading]);

  const startLocalCamera = async () => {
    try {
      // Stop old stream before starting a new one
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const constraints = {
          video: selectedDeviceId ? 
            { deviceId: { exact: selectedDeviceId }, width: { ideal: 1280 }, height: { ideal: 720 } } : 
            { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" }
        };
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        streamRef.current = stream;
        setStatus('ACTIVE');
      }
    } catch (err) {
      console.error("Error accessing local webcam:", err);
      alert("Camera access error: " + err.message + "\nMake sure the camera is not being used by another application.");
      setStatus('OFFLINE');
    }
  };

  const stopLocalCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setStatus('INACTIVE');
    setAutoDetect(false);
  };

  const checkStatus = async () => {
    try {
      const data = await getCameraStatus();
      setStatus(data.is_running ? (data.status === 'CONNECTED' ? 'ACTIVE' : data.status) : 'INACTIVE');
    } catch (err) {
      setStatus('OFFLINE');
    }
  };

  const handleStart = async () => {
    if (useLocalWebcam) {
      await startLocalCamera();
    } else {
      setLoading(true);
      try {
        const source = rtspUrl.trim() !== '' ? rtspUrl : "0";
        await startCamera({ source: source, camera_id: "main_gate" });
        await checkStatus();
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleStop = async () => {
    if (useLocalWebcam) {
      stopLocalCamera();
      setSnapshotResult(null);
    } else {
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
    }
  };

  const handleLocalSnapshot = async () => {
    if (!videoRef.current || !canvasRef.current || !streamRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const base64Full = canvas.toDataURL('image/jpeg', 0.8);
    const base64Data = base64Full.split(',')[1];
    
    setLoading(true);
    try {
      const result = await verifyFrame({
        image: base64Data,
        camera_id: "browser_webcam"
      });
      if (result && result.status !== "SKIPPED") {
        setSnapshotResult(result);
        if (result.name) {
          setRecentEvents(prev => [{...result, timestamp: new Date()}, ...prev].slice(0, 5));
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSnapshot = async () => {
    if (useLocalWebcam) {
      await handleLocalSnapshot();
    } else {
      setLoading(true);
      try {
        const result = await processSnapshot();
        setSnapshotResult(result);
        if (result.name) {
          setRecentEvents(prev => [{...result, timestamp: new Date()}, ...prev].slice(0, 5));
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="p-xl max-w-container-max mx-auto w-full">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-lg">
        
        {/* Video Feed Section */}
        <div className="col-span-12 lg:col-span-8 flex flex-col gap-md">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-xs gap-4">
            <div>
              <h2 className="font-headline-lg text-headline-lg text-on-surface">Live Monitoring</h2>
              <p className="text-body-md text-on-surface-variant">Real-time biometric authentication stream</p>
            </div>
            <div className="flex flex-wrap gap-sm items-center">
              {useLocalWebcam && videoDevices.length > 0 && (
                <select 
                  value={selectedDeviceId}
                  onChange={(e) => setSelectedDeviceId(e.target.value)}
                  className="bg-surface border border-outline-variant rounded-lg px-md py-2 text-body-md focus:border-primary-container focus:ring-1 focus:ring-primary-container outline-none"
                >
                  {videoDevices.map((device, index) => (
                    <option key={device.deviceId} value={device.deviceId}>{device.label || `Camera ${index + 1}`}</option>
                  ))}
                </select>
              )}
              {!useLocalWebcam && (
                <input 
                  type="text" 
                  value={rtspUrl}
                  onChange={(e) => setRtspUrl(e.target.value)}
                  placeholder="RTSP Stream URL (default: 0)"
                  className="bg-surface border border-outline-variant rounded-lg px-md py-2 text-body-md focus:border-primary-container focus:ring-1 focus:ring-primary-container outline-none min-w-[250px]"
                />
              )}
              
              <div className="flex bg-surface-variant rounded-lg p-1 border border-outline-variant">
                <button 
                  className={`px-4 py-1.5 text-sm rounded-md transition-all ${useLocalWebcam ? 'bg-primary text-on-primary shadow' : 'text-on-surface-variant hover:text-white'}`}
                  onClick={() => { setUseLocalWebcam(true); setSnapshotResult(null); }}
                >
                  Webcam
                </button>
                <button 
                  className={`px-4 py-1.5 text-sm rounded-md transition-all ${!useLocalWebcam ? 'bg-primary text-on-primary shadow' : 'text-on-surface-variant hover:text-white'}`}
                  onClick={() => { setUseLocalWebcam(false); stopLocalCamera(); setSnapshotResult(null); }}
                >
                  Backend
                </button>
              </div>

              {status === 'INACTIVE' || status === 'OFFLINE' ? (
                <button onClick={handleStart} disabled={loading} className="bg-primary-container text-on-primary-container px-lg py-2 rounded-lg font-bold shadow-sm hover:opacity-90 transition-opacity flex items-center gap-xs">
                  <span className="material-symbols-outlined">play_arrow</span> Start
                </button>
              ) : (
                <button onClick={handleStop} disabled={loading} className="bg-error text-white px-lg py-2 rounded-lg font-bold shadow-sm hover:opacity-90 transition-opacity flex items-center gap-xs">
                  <span className="material-symbols-outlined">stop</span> Stop
                </button>
              )}
            </div>
          </div>

          {/* Main Video Frame */}
          <div className="relative bg-black border-4 border-primary-container rounded-xl overflow-hidden aspect-video shadow-lg group">
            {status === 'ACTIVE' ? (
              <>
                {useLocalWebcam ? (
                  <>
                    <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
                    <canvas ref={canvasRef} className="hidden" />
                  </>
                ) : (
                  <img src={`${API_URL}/camera/stream?t=${Date.now()}`} alt="Live Stream" className="w-full h-full object-cover" />
                )}
                {/* Scanning HUD */}
                <div className="absolute inset-0 pointer-events-none">
                  <div className="absolute top-md left-md bg-black/60 text-white px-md py-xs rounded flex items-center gap-xs">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                    <span className="text-label-md">LIVE RECAP</span>
                  </div>
                </div>

                <div className="absolute top-4 right-4 flex items-center gap-2 bg-surface/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-outline-variant z-10">
                  <label className="text-sm font-medium text-on-surface cursor-pointer select-none">Auto Detect</label>
                  <div 
                    className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${autoDetect ? 'bg-primary' : 'bg-surface-variant'}`}
                    onClick={() => setAutoDetect(!autoDetect)}
                  >
                    <div className={`w-4 h-4 bg-white rounded-full absolute top-0.5 transition-all ${autoDetect ? 'left-[22px]' : 'left-0.5'}`} />
                  </div>
                </div>

                {!autoDetect && (
                  <button onClick={handleSnapshot} disabled={loading} className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-surface/80 backdrop-blur-md text-primary border border-primary/50 px-6 py-3 rounded-full hover:bg-primary hover:text-on-primary transition-all flex items-center gap-2 shadow-glow z-10">
                    <span className="material-symbols-outlined">center_focus_strong</span>
                    {loading ? 'Processing...' : 'Process Frame'}
                  </button>
                )}
              </>
            ) : status === 'CONNECTING' ? (
              <div className="flex flex-col items-center justify-center h-full bg-surface-container text-outline-variant">
                <span className="material-symbols-outlined text-[64px] mb-4 opacity-50 animate-spin">sync</span>
                <p>Connecting to Camera Stream...</p>
              </div>
            ) : status === 'ERROR' ? (
              <div className="flex flex-col items-center justify-center h-full bg-surface-container text-error">
                <span className="material-symbols-outlined text-[64px] mb-4 opacity-80">error</span>
                <p>Failed to connect to camera source</p>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full bg-surface-container text-outline-variant">
                <span className="material-symbols-outlined text-[64px] mb-4 opacity-50">videocam_off</span>
                <p>Camera is currently inactive</p>
              </div>
            )}
          </div>

          {/* Last 5 Detections */}
          {recentEvents.length > 0 && (
            <div className="bg-surface border border-outline-variant rounded-xl p-md shadow-sm">
              <h3 className="text-label-md text-on-surface-variant uppercase tracking-wider mb-md">Recent Events</h3>
              <div className="flex gap-md overflow-x-auto pb-xs">
                {recentEvents.map((ev, i) => (
                  <div key={i} className="flex-shrink-0 w-48 bg-surface-container-low rounded-lg p-xs border border-outline-variant hover:border-primary-container transition-colors cursor-pointer">
                    <div className="relative h-24 rounded overflow-hidden mb-xs bg-surface-variant flex items-center justify-center">
                      <span className="material-symbols-outlined text-4xl text-outline-variant">person</span>
                      <div className={`absolute bottom-0 right-0 px-xs rounded-tl text-[10px] font-bold ${ev.success ? 'bg-green-100 text-green-800' : 'bg-error-container text-error'}`}>
                        {ev.success ? 'PASS' : 'FAIL'}
                      </div>
                    </div>
                    <p className="text-label-md font-bold truncate">{ev.name || 'Unknown'}</p>
                    <p className="text-[10px] text-on-surface-variant">{ev.timestamp.toLocaleTimeString()}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Analysis & Info Sidebar */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-lg">
          {/* Real-time Results Panel */}
          <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
            <h3 className="text-headline-md font-bold mb-lg flex items-center gap-xs">
              <span className="material-symbols-outlined text-primary">analytics</span>
              Analysis Status
            </h3>
            
            {!snapshotResult ? (
              <div className="text-center text-on-surface-variant py-8">
                <span className="material-symbols-outlined text-4xl mb-2 opacity-50">hourglass_empty</span>
                <p>Waiting for scan...</p>
              </div>
            ) : (
              <div className="space-y-lg">
                <div className="flex items-center justify-between">
                  <span className="text-body-md font-semibold text-on-surface-variant">Face Match Status</span>
                  <span className={`px-md py-xs rounded-full text-label-md font-bold flex items-center gap-xs ${snapshotResult.face_score >= 0.40 ? 'bg-green-100 text-green-800' : 'bg-error-container text-error'}`}>
                    <span className="material-symbols-outlined text-[16px]">{snapshotResult.face_score >= 0.40 ? 'check_circle' : 'cancel'}</span> 
                    {snapshotResult.face_score !== undefined ? (snapshotResult.face_score * 100).toFixed(1) + '%' : 'N/A'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-body-md font-semibold text-on-surface-variant">Iris Verification</span>
                  <span className={`px-md py-xs rounded-full text-label-md font-bold flex items-center gap-xs ${snapshotResult.iris_passed ? 'bg-green-100 text-green-800' : 'bg-error-container text-error'}`}>
                    <span className="material-symbols-outlined text-[16px]">{snapshotResult.iris_passed ? 'check_circle' : 'cancel'}</span> 
                    {snapshotResult.iris_score !== undefined ? (snapshotResult.iris_score * 100).toFixed(1) + '%' : '0.0%'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-body-md font-semibold text-on-surface-variant">Liveness Check</span>
                  <span className={`px-md py-xs rounded-full text-label-md font-bold flex items-center gap-xs ${snapshotResult.liveness_passed ? 'bg-green-100 text-green-800' : 'bg-error-container text-error'}`}>
                    <span className="material-symbols-outlined text-[16px]">{snapshotResult.liveness_passed ? 'check_circle' : 'cancel'}</span> 
                    {snapshotResult.liveness_score !== undefined ? (snapshotResult.liveness_score * 100).toFixed(1) + '%' : 'N/A'}
                  </span>
                </div>
                <hr className="border-outline-variant" />
                <div className={`p-md rounded-lg flex items-center justify-between border ${snapshotResult.success ? 'bg-secondary-container/10 border-secondary-container' : 'bg-error-container/10 border-error'}`}>
                  <div>
                    <p className={`text-label-md font-bold uppercase ${snapshotResult.success ? 'text-on-secondary-container' : 'text-error'}`}>Final Decision</p>
                    <p className={`text-headline-md font-bold ${snapshotResult.success ? 'text-primary' : 'text-error'}`}>
                      {snapshotResult.success ? 'ACCESS GRANTED' : 'ACCESS DENIED'}
                    </p>
                  </div>
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center ${snapshotResult.success ? 'bg-primary-container text-on-primary-container' : 'bg-error text-white'}`}>
                    <span className="material-symbols-outlined text-[32px]">{snapshotResult.success ? 'verified' : 'gpp_bad'}</span>
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* Current Employee Card */}
          {snapshotResult && snapshotResult.success && snapshotResult.name && (
            <section className="bg-surface border border-outline-variant rounded-xl overflow-hidden shadow-sm">
              <div className="bg-primary-container p-md flex items-center gap-md">
                <div className="w-16 h-16 rounded-lg bg-surface flex items-center justify-center border-2 border-white shadow-sm text-primary">
                  <span className="material-symbols-outlined text-4xl">person</span>
                </div>
                <div className="text-on-primary-container">
                  <h4 className="font-bold text-headline-md leading-tight">{snapshotResult.name}</h4>
                  <p className="text-label-md opacity-90">ID: {snapshotResult.employee_id}</p>
                </div>
              </div>
              <div className="p-lg space-y-md">
                <div className="grid grid-cols-2 gap-md">
                  <div>
                    <p className="text-label-md text-on-surface-variant">Department</p>
                    <p className="text-body-md font-bold">{snapshotResult.department || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-label-md text-on-surface-variant">Role</p>
                    <p className="text-body-md font-bold">{snapshotResult.role || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-label-md text-on-surface-variant">Status</p>
                    <p className="text-body-md font-bold text-primary">Verified</p>
                  </div>
                  <div>
                    <p className="text-label-md text-on-surface-variant">Time</p>
                    <p className="text-body-md font-bold">{new Date().toLocaleTimeString()}</p>
                  </div>
                </div>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveMonitor;
