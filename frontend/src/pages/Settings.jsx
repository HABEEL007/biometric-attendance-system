import React, { useState } from 'react';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general');

  return (
    <div className="p-xl max-w-container-max mx-auto w-full">
        {/* Bento-style Tab Navigation */}
        <div className="mb-lg bg-surface-container-lowest rounded-xl p-sm shadow-sm flex items-center gap-sm">
          <button
            className={`tab-btn flex-1 flex items-center justify-center gap-sm py-md rounded-lg transition-all ${activeTab === 'general' ? 'text-primary border-b-[3px] border-primary-container' : 'text-on-surface-variant hover:bg-surface-container-low'}`}
            onClick={() => setActiveTab('general')}
          >
            <span className="material-symbols-outlined">tune</span>
            <span className="font-label-md text-label-md">General</span>
          </button>
          <button
            className={`tab-btn flex-1 flex items-center justify-center gap-sm py-md rounded-lg transition-all ${activeTab === 'thresholds' ? 'text-primary border-b-[3px] border-primary-container' : 'text-on-surface-variant hover:bg-surface-container-low'}`}
            onClick={() => setActiveTab('thresholds')}
          >
            <span className="material-symbols-outlined">speed</span>
            <span className="font-label-md text-label-md">Thresholds</span>
          </button>
          <button
            className={`tab-btn flex-1 flex items-center justify-center gap-sm py-md rounded-lg transition-all ${activeTab === 'camera' ? 'text-primary border-b-[3px] border-primary-container' : 'text-on-surface-variant hover:bg-surface-container-low'}`}
            onClick={() => setActiveTab('camera')}
          >
            <span className="material-symbols-outlined">videocam_auto</span>
            <span className="font-label-md text-label-md">Camera</span>
          </button>
          <button
            className={`tab-btn flex-1 flex items-center justify-center gap-sm py-md rounded-lg transition-all ${activeTab === 'security' ? 'text-primary border-b-[3px] border-primary-container' : 'text-on-surface-variant hover:bg-surface-container-low'}`}
            onClick={() => setActiveTab('security')}
          >
            <span className="material-symbols-outlined">security</span>
            <span className="font-label-md text-label-md">Security</span>
          </button>
        </div>

        {/* Settings Content */}
        <div id="content-area">
          {/* General Section */}
          <section className={`space-y-lg animate-fade-in ${activeTab !== 'general' ? 'hidden' : ''}`} id="tab-general">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
              <div className="bg-surface-container-lowest p-lg rounded-xl shadow-sm border-t-2 border-[#FFD700]">
                <h3 className="font-headline-sm text-headline-sm mb-md flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary">info</span> Identity
                </h3>
                <div className="space-y-md">
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">System Name</label>
                    <input className="w-full bg-white border border-outline-variant rounded-lg px-md py-sm focus:outline-none focus:ring-2 focus:ring-primary-container focus:border-primary transition-all" type="text" defaultValue="Bio Attendance Pro v4.2" />
                  </div>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">Organization ID</label>
                    <input className="w-full bg-surface-container-low border border-outline-variant rounded-lg px-md py-sm text-on-surface-variant" disabled type="text" defaultValue="ORG-2024-ATTEND" />
                  </div>
                </div>
              </div>
              <div className="bg-surface-container-lowest p-lg rounded-xl shadow-sm border-t-2 border-[#FFD700]">
                <h3 className="font-headline-sm text-headline-sm mb-md flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary">schedule</span> Timing
                </h3>
                <div className="space-y-md">
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">Recognition Cooldown (Seconds)</label>
                    <input className="w-full bg-white border border-outline-variant rounded-lg px-md py-sm focus:outline-none focus:ring-2 focus:ring-primary-container" type="number" defaultValue="10" />
                  </div>
                  <div className="grid grid-cols-2 gap-md">
                    <div>
                      <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">Work Start</label>
                      <input className="w-full bg-white border border-outline-variant rounded-lg px-md py-sm" type="time" defaultValue="08:00" />
                    </div>
                    <div>
                      <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">Work End</label>
                      <input className="w-full bg-white border border-outline-variant rounded-lg px-md py-sm" type="time" defaultValue="17:00" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <button className="bg-primary-container text-on-primary-container font-semibold px-xl py-md rounded-lg shadow-sm hover:brightness-95 transition-all flex items-center gap-md active:scale-98">
                <span className="material-symbols-outlined">save</span> Save General Settings
              </button>
            </div>
          </section>

          {/* Thresholds Section */}
          <section className={`space-y-lg animate-fade-in ${activeTab !== 'thresholds' ? 'hidden' : ''}`} id="tab-thresholds">
            <div className="bg-surface-container-lowest p-lg rounded-xl shadow-sm border-t-2 border-[#FFD700]">
              <h3 className="font-headline-sm text-headline-sm mb-lg flex items-center gap-sm">
                <span className="material-symbols-outlined text-primary">analytics</span> Accuracy &amp; Confidence
              </h3>
              <div className="space-y-xl">
                <div>
                  <div className="flex justify-between mb-md">
                    <label className="font-body-lg text-body-lg">Face Match Threshold</label>
                    <span className="text-primary font-bold">0.85</span>
                  </div>
                  <input className="w-full h-2 bg-surface-container rounded-lg appearance-none cursor-pointer" max="0.9" min="0.1" step="0.01" type="range" defaultValue="0.85" />
                  <p className="text-xs text-on-surface-variant mt-sm">Higher values reduce false positives but may increase rejection rates.</p>
                </div>
                <div className="border-t border-outline-variant pt-lg">
                  <div className="flex justify-between mb-md">
                    <label className="font-body-lg text-body-lg">Iris Scan Threshold</label>
                    <span className="text-primary font-bold">0.92</span>
                  </div>
                  <input className="w-full h-2 bg-surface-container rounded-lg appearance-none cursor-pointer" max="0.9" min="0.1" step="0.01" type="range" defaultValue="0.92" />
                </div>
                <div className="border-t border-outline-variant pt-lg">
                  <div className="flex justify-between mb-md">
                    <label className="font-body-lg text-body-lg">Liveness Detection (PAD)</label>
                    <span className="text-primary font-bold">0.75</span>
                  </div>
                  <input className="w-full h-2 bg-surface-container rounded-lg appearance-none cursor-pointer" max="0.9" min="0.1" step="0.01" type="range" defaultValue="0.75" />
                  <p className="text-xs text-on-surface-variant mt-sm">Presentation Attack Detection sensitivity. Critical for anti-spoofing.</p>
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <button className="bg-primary-container text-on-primary-container font-semibold px-xl py-md rounded-lg shadow-sm hover:brightness-95 transition-all flex items-center gap-md active:scale-98">
                <span className="material-symbols-outlined">save</span> Save Thresholds
              </button>
            </div>
          </section>

          {/* Camera Section */}
          <section className={`space-y-lg animate-fade-in ${activeTab !== 'camera' ? 'hidden' : ''}`} id="tab-camera">
            <div className="bg-surface-container-lowest p-lg rounded-xl shadow-sm border-t-2 border-[#FFD700]">
              <h3 className="font-headline-sm text-headline-sm mb-lg flex items-center gap-sm">
                <span className="material-symbols-outlined text-primary">photo_camera</span> Visual Capture Configuration
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-xl">
                <div className="space-y-lg">
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">Default Camera Device</label>
                    <select className="w-full bg-white border border-outline-variant rounded-lg px-md py-sm">
                      <option>Integrated AI Cam (Primary)</option>
                      <option>USB-3 Biometric Sensor</option>
                      <option>Wide-Angle Entrance Cam</option>
                    </select>
                  </div>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">Frame Resolution</label>
                    <select className="w-full bg-white border border-outline-variant rounded-lg px-md py-sm" defaultValue="2K Quad HD (2560x1440)">
                      <option>4K Ultra HD (3840x2160)</option>
                      <option value="2K Quad HD (2560x1440)">2K Quad HD (2560x1440)</option>
                      <option>1080p Full HD (1920x1080)</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-lg">
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">FPS Limit</label>
                    <input className="w-full bg-white border border-outline-variant rounded-lg px-md py-sm" type="number" defaultValue="30" />
                  </div>
                  <div className="p-md bg-surface-container-low rounded-lg flex items-center gap-md">
                    <span className="material-symbols-outlined text-tertiary">wb_sunny</span>
                    <div>
                      <p className="font-label-md text-label-md">Auto-Exposure</p>
                      <p className="text-xs text-on-surface-variant">Recommended for variable lighting</p>
                    </div>
                    <label className="ml-auto relative inline-flex items-center cursor-pointer">
                      <input defaultChecked className="sr-only peer" type="checkbox" />
                      <div className="w-11 h-6 bg-surface-container-highest rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <button className="bg-primary-container text-on-primary-container font-semibold px-xl py-md rounded-lg shadow-sm hover:brightness-95 transition-all flex items-center gap-md active:scale-98">
                <span className="material-symbols-outlined">save</span> Save Camera Settings
              </button>
            </div>
          </section>

          {/* Security Section */}
          <section className={`space-y-lg animate-fade-in ${activeTab !== 'security' ? 'hidden' : ''}`} id="tab-security">
            <div className="bg-surface-container-lowest p-lg rounded-xl shadow-sm border-t-2 border-[#FFD700]">
              <h3 className="font-headline-sm text-headline-sm mb-lg flex items-center gap-sm">
                <span className="material-symbols-outlined text-primary">admin_panel_settings</span> Administrator Controls
              </h3>
              <div className="max-w-[448px] space-y-lg">
                <div>
                  <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">Current Admin Password</label>
                  <div className="relative">
                    <input className="w-full bg-white border border-outline-variant rounded-lg px-md py-sm" type="password" defaultValue="••••••••••••" />
                    <span className="material-symbols-outlined absolute right-md top-1/2 -translate-y-1/2 text-on-surface-variant cursor-pointer">visibility</span>
                  </div>
                </div>
                <div>
                  <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">Session Timeout (Minutes)</label>
                  <input className="w-full bg-white border border-outline-variant rounded-lg px-md py-sm" type="number" defaultValue="15" />
                </div>
                <div className="flex items-center gap-md p-md bg-error-container/20 rounded-lg border border-error/10">
                  <span className="material-symbols-outlined text-error">shield_lock</span>
                  <div className="flex-1">
                    <p className="font-label-md text-label-md text-on-error-container">Two-Factor Authentication</p>
                    <p className="text-xs text-on-surface-variant">Currently disabled. Enable for higher security.</p>
                  </div>
                  <button className="text-primary font-bold text-xs uppercase tracking-widest hover:underline">Setup</button>
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <button className="bg-primary-container text-on-primary-container font-semibold px-xl py-md rounded-lg shadow-sm hover:brightness-95 transition-all flex items-center gap-md active:scale-98">
                <span className="material-symbols-outlined">save</span> Update Security
              </button>
            </div>
          </section>
        </div>
    </div>
  );
};

export default Settings;
