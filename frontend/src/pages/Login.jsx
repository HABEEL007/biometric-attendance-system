import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const togglePassword = () => {
    setShowPassword(!showPassword);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = await login({ email, password });
      // Success
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials. Please use the demo login provided below.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-surface text-on-surface font-body-md overflow-hidden">
      <main className="flex h-screen w-full">
        {/* Left Side: Branding/Info (50%) */}
        <section className="hidden lg:flex w-1/2 bg-primary-container relative flex-col justify-center px-xl overflow-hidden">
          {/* Decorative Patterns */}
          <div className="absolute top-0 left-0 w-full h-full pattern-bg opacity-30 pointer-events-none"></div>
          <div className="absolute -top-24 -left-24 w-96 h-96 rounded-full border-[32px] border-primary-fixed opacity-20 pointer-events-none"></div>
          <div className="absolute bottom-12 right-12 w-64 h-64 rounded-full bg-primary-fixed opacity-10 pointer-events-none"></div>
          
          <div className="relative z-10 max-w-[512px] mx-auto">
            <header className="mb-lg">
              <h1 className="font-display text-display text-inverse-surface mb-xs tracking-tighter">Bio Attendance</h1>
              <h2 className="font-headline-md text-headline-md text-on-primary-container uppercase tracking-widest opacity-80">
                AI Biometric Attendance System
              </h2>
            </header>
            <p className="font-body-lg text-body-lg text-on-primary-container mb-xl font-semibold opacity-90">
              Face Recognition + Iris Verification + Liveness Detection
            </p>
            <ul className="space-y-md">
              <li className="flex items-center gap-md group">
                <div className="w-8 h-8 rounded-full bg-inverse-surface flex items-center justify-center text-primary-container group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-[18px]">check</span>
                </div>
                <span className="font-headline-md text-headline-md text-inverse-surface">Real-time Face Recognition</span>
              </li>
              <li className="flex items-center gap-md group">
                <div className="w-8 h-8 rounded-full bg-inverse-surface flex items-center justify-center text-primary-container group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-[18px]">check</span>
                </div>
                <span className="font-headline-md text-headline-md text-inverse-surface">Iris/Eye Verification</span>
              </li>
              <li className="flex items-center gap-md group">
                <div className="w-8 h-8 rounded-full bg-inverse-surface flex items-center justify-center text-primary-container group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-[18px]">check</span>
                </div>
                <span className="font-headline-md text-headline-md text-inverse-surface">Anti-Spoofing Protection</span>
              </li>
              <li className="flex items-center gap-md group">
                <div className="w-8 h-8 rounded-full bg-inverse-surface flex items-center justify-center text-primary-container group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-[18px]">check</span>
                </div>
                <span className="font-headline-md text-headline-md text-inverse-surface">Automated Attendance Tracking</span>
              </li>
            </ul>
          </div>
        </section>

        {/* Right Side: Login Form (50%) */}
        <section className="w-full lg:w-1/2 bg-surface-container-lowest flex flex-col justify-between items-center py-xl px-lg">
          {/* Mobile Branding (Logo only) */}
          <div className="lg:hidden w-full text-center mb-xl">
            <h1 className="font-display text-display text-primary tracking-tighter">Bio Attendance</h1>
          </div>
          
          <div className="w-full max-w-[448px] flex-grow flex flex-col justify-center">
            <div className="mb-xl">
              <h2 className="font-headline-lg text-headline-lg text-on-surface mb-xs">Welcome Back</h2>
              <p className="font-body-md text-body-md text-on-surface-variant">Sign in to continue to your dashboard</p>
            </div>

            {error && (
              <div className="mb-md p-3 bg-error-container/20 border border-error/50 rounded-lg text-error text-sm">
                {error}
              </div>
            )}

            <form className="space-y-lg" onSubmit={handleLogin}>
              {/* Email Field */}
              <div className="space-y-xs">
                <label className="font-label-md text-label-md text-on-surface-variant block" htmlFor="email">Email Address</label>
                <input 
                  id="email" 
                  name="email" 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@bioattendance.com" 
                  required 
                  className="w-full px-md py-3 rounded-lg border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary-container focus:border-primary-container transition-all text-on-surface outline-none" 
                />
              </div>

              {/* Password Field */}
              <div className="space-y-xs">
                <div className="flex justify-between items-center">
                  <label className="font-label-md text-label-md text-on-surface-variant" htmlFor="password">Password</label>
                  <button 
                    type="button" 
                    onClick={togglePassword} 
                    className="font-label-md text-label-md text-primary hover:underline focus:outline-none"
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
                <div className="relative">
                  <input 
                    id="password" 
                    name="password" 
                    type={showPassword ? "text" : "password"} 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••" 
                    required 
                    className="w-full px-md py-3 rounded-lg border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary-container focus:border-primary-container transition-all text-on-surface outline-none" 
                  />
                </div>
              </div>

              {/* Remember & Forgot Row */}
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-sm cursor-pointer select-none">
                  <input type="checkbox" className="w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary-container" />
                  <span className="font-body-md text-body-md text-on-surface-variant">Remember me</span>
                </label>
                <a href="#" className="font-body-md text-body-md font-semibold text-primary hover:text-primary-container transition-colors">
                  Forgot Password?
                </a>
              </div>

              {/* Login Button */}
              <button 
                type="submit" 
                disabled={loading}
                className={`w-full py-4 font-headline-md text-headline-md rounded-lg shadow-sm transition-all flex items-center justify-center gap-sm ${loading ? 'bg-primary-container opacity-80 cursor-not-allowed text-inverse-surface' : 'bg-primary-container text-inverse-surface hover:shadow-md active:scale-[0.98]'}`}
              >
                {loading ? <span className="loading-dots">Authenticating</span> : <span>Login to System</span>}
              </button>
            </form>

            <div className="text-center mt-md">
              <p className="text-body-md text-on-surface-variant">
                Don't have an account? <button type="button" onClick={() => navigate('/signup')} className="text-primary font-semibold hover:underline">Sign up</button>
              </p>
            </div>

            {/* Demo Box */}
            <div className="mt-xl p-md bg-surface-container rounded-xl border border-outline-variant/30 text-center">
              <p className="font-label-md text-label-md text-on-surface-variant mb-unit uppercase tracking-widest">Demo Credentials</p>
              <p className="font-body-md text-body-md font-semibold text-on-surface">
                Admin: <span className="text-primary select-all">admin@bioattendance.com</span> / <span className="text-primary select-all">admin123</span>
              </p>
            </div>
          </div>

          {/* Footer */}
          <footer className="mt-xl">
            <p className="font-body-md text-body-md text-on-surface-variant opacity-60">
              © 2024 Bio Attendance. All rights reserved.
            </p>
          </footer>
        </section>
      </main>
    </div>
  );
};

export default Login;
