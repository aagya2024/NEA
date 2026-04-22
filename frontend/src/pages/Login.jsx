/**
 * Login Page
 * ==========
 * Full-screen NEA-branded login with email/password.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Login() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await login(email, password);
            toast.success('Welcome to NEA Intranet');
            navigate('/');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Login failed. Check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex">
            {/* Left side — branding */}
            <div className="hidden lg:flex lg:w-1/2 bg-nea-blue flex-col justify-center items-center p-12 relative overflow-hidden">
                {/* Decorative circles */}
                <div className="absolute -top-20 -left-20 w-80 h-80 bg-white/5 rounded-full" />
                <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-white/5 rounded-full" />
                <div className="absolute top-1/3 right-10 w-40 h-40 bg-white/5 rounded-full" />

                <div className="relative z-10 text-center">
                    <div className="w-24 h-24 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-6 p-3">
                        <img src="/nea-logo.png" alt="NEA Logo" className="w-full h-full object-contain" />
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2">Nepal Electricity Authority</h1>
                    <p className="text-white/60 text-sm mb-1">नेपाल विद्युत् प्राधिकरण</p>
                    <p className="text-white/40 text-sm mt-6 max-w-sm">
                        Internal Intranet Portal for staff communication, document management, and AI-powered knowledge assistance.
                    </p>
                </div>
            </div>

            {/* Right side — login form */}
            <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
                <div className="w-full max-w-md">
                    {/* Mobile logo */}
                    <div className="lg:hidden text-center mb-8">
                        <div className="w-16 h-16 bg-nea-blue rounded-xl flex items-center justify-center mx-auto mb-4 p-2">
                            <img src="/nea-logo.png" alt="NEA Logo" className="w-full h-full object-contain" />
                        </div>
                        <h1 className="text-xl font-bold text-gray-800">NEA Intranet</h1>
                    </div>

                    <div className="card p-8">
                        <h2 className="text-2xl font-bold text-gray-800 mb-1">Sign In</h2>
                        <p className="text-sm text-gray-400 mb-6">Enter your credentials to access the portal</p>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="label">Email Address</label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="input-field"
                                    placeholder="you@nea.org.np"
                                    required
                                    autoFocus
                                />
                            </div>

                            <div>
                                <label className="label">Password</label>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input-field"
                                    placeholder="Enter your password"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="btn-primary w-full py-3"
                            >
                                {loading ? (
                                    <span className="flex items-center gap-2">
                                        <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                                        Signing in...
                                    </span>
                                ) : (
                                    'Sign In'
                                )}
                            </button>
                        </form>

                        <p className="text-xs text-gray-400 mt-6 text-center">
                            Contact IT department if you need access credentials.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
