const Settings = () => {
  return (
    <div className="p-margin-desktop flex flex-col gap-6 max-w-4xl">
      <div>
        <h2 className="font-headline-md text-headline-md text-primary">System Settings</h2>
        <p className="text-on-surface-variant text-body-sm mt-1">Configure global parameters for the BioAttend Enterprise system.</p>
      </div>

      <div className="bg-surface-container rounded-xl border border-outline-variant p-8 flex flex-col gap-8">
        <section>
          <h3 className="font-title-lg text-primary mb-4 border-b border-outline-variant pb-2">Biometric Thresholds</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex flex-col gap-2">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Face Similarity Threshold</label>
              <input type="number" step="0.01" defaultValue="0.50" className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2 text-on-surface focus:outline-none" />
              <p className="text-[12px] text-on-surface-variant">Minimum score required for a successful face match (0.0 - 1.0).</p>
            </div>
            <div className="flex flex-col gap-2">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Iris Similarity Threshold</label>
              <input type="number" step="0.01" defaultValue="0.75" className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2 text-on-surface focus:outline-none" />
              <p className="text-[12px] text-on-surface-variant">Minimum score required for a successful iris match (0.0 - 1.0).</p>
            </div>
            <div className="flex flex-col gap-2">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Liveness Strictness</label>
              <select defaultValue="HIGH" className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2 text-on-surface focus:outline-none">
                <option value="LOW">Low (Faster)</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High (Most Secure)</option>
              </select>
            </div>
          </div>
        </section>

        <section>
          <h3 className="font-title-lg text-primary mb-4 border-b border-outline-variant pb-2">System Integrations</h3>
          <div className="flex flex-col gap-4">
             <div className="flex items-center justify-between p-4 bg-surface-container-low border border-outline-variant rounded-lg">
               <div>
                 <p className="font-bold text-on-surface">Active Directory Sync</p>
                 <p className="text-sm text-on-surface-variant">Automatically import staff members from your AD server.</p>
               </div>
               <button className="bg-surface-variant text-on-surface px-4 py-2 rounded font-label-sm hover:bg-outline-variant transition-colors">Configure</button>
             </div>
             <div className="flex items-center justify-between p-4 bg-surface-container-low border border-outline-variant rounded-lg">
               <div>
                 <p className="font-bold text-on-surface">Email Notifications</p>
                 <p className="text-sm text-on-surface-variant">Send alerts to administrators on failed attendance attempts.</p>
               </div>
               <button className="bg-surface-variant text-on-surface px-4 py-2 rounded font-label-sm hover:bg-outline-variant transition-colors">Configure</button>
             </div>
          </div>
        </section>
        
        <div className="border-t border-outline-variant pt-6 mt-4 flex justify-end gap-4">
          <button className="px-6 py-2.5 rounded-lg border border-outline-variant text-on-surface font-label-md hover:bg-surface-variant transition-colors">
            Reset Defaults
          </button>
          <button className="bg-primary text-on-primary px-8 py-2.5 rounded-lg font-label-md hover:opacity-90 transition-all flex items-center gap-2">
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
