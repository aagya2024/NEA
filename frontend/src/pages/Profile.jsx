/**
 * Profile Page — View/edit own profile and change password.
 */

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import toast from 'react-hot-toast';

export default function Profile() {
    const { user } = useAuth();
    const [tab, setTab] = useState('profile');
    const [form, setForm] = useState({
        full_name: user?.full_name || '',
        phone: user?.phone || '',
        department: user?.department || '',
    });
    const [pwForm, setPwForm] = useState({ current_password: '', new_password: '', confirm: '' });
    const [saving, setSaving] = useState(false);

    const handleProfileSave = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            await api.put('/users/me/profile', form);
            toast.success('Profile updated');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to update profile');
        } finally {
            setSaving(false);
        }
    };

    const handlePasswordChange = async (e) => {
        e.preventDefault();
        if (pwForm.new_password !== pwForm.confirm) {
            toast.error('Passwords do not match');
            return;
        }
        setSaving(true);
        try {
            await api.put('/users/me/password', {
                current_password: pwForm.current_password,
                new_password: pwForm.new_password,
            });
            toast.success('Password changed');
            setPwForm({ current_password: '', new_password: '', confirm: '' });
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to change password');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <h1 className="page-title">My Profile</h1>

            {/* User Info Card */}
            <div className="card p-6 flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-nea-blue text-white flex items-center justify-center text-2xl font-semibold">
                    {user?.full_name?.charAt(0) || 'U'}
                </div>
                <div>
                    <h2 className="text-lg font-semibold">{user?.full_name}</h2>
                    <p className="text-sm text-gray-500">{user?.email}</p>
                    <span className="badge-blue mt-1 inline-block">{user?.role_name}</span>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit">
                {['profile', 'password'].map((t) => (
                    <button
                        key={t}
                        onClick={() => setTab(t)}
                        className={`px-4 py-2 rounded-md text-sm font-medium capitalize transition-colors ${tab === t ? 'bg-white text-nea-blue shadow-sm' : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        {t === 'password' ? 'Change Password' : 'Edit Profile'}
                    </button>
                ))}
            </div>

            {tab === 'profile' ? (
                <form onSubmit={handleProfileSave} className="card p-6 space-y-4">
                    <div>
                        <label className="label">Full Name</label>
                        <input className="input-field" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
                    </div>
                    <div>
                        <label className="label">Phone</label>
                        <input className="input-field" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                    </div>
                    <div>
                        <label className="label">Department</label>
                        <input className="input-field" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
                    </div>
                    <button type="submit" disabled={saving} className="btn-primary">
                        {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                </form>
            ) : (
                <form onSubmit={handlePasswordChange} className="card p-6 space-y-4">
                    <div>
                        <label className="label">Current Password</label>
                        <input type="password" className="input-field" value={pwForm.current_password} onChange={(e) => setPwForm({ ...pwForm, current_password: e.target.value })} required />
                    </div>
                    <div>
                        <label className="label">New Password</label>
                        <input type="password" className="input-field" value={pwForm.new_password} onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })} required />
                    </div>
                    <div>
                        <label className="label">Confirm New Password</label>
                        <input type="password" className="input-field" value={pwForm.confirm} onChange={(e) => setPwForm({ ...pwForm, confirm: e.target.value })} required />
                    </div>
                    <button type="submit" disabled={saving} className="btn-primary">
                        {saving ? 'Changing...' : 'Change Password'}
                    </button>
                </form>
            )}
        </div>
    );
}
