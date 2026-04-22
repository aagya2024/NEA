/**
 * Role Management — CRUD roles + permission assignment matrix.
 */

import { useState, useEffect } from 'react';
import api from '../../api/axios';
import toast from 'react-hot-toast';
import { FiPlus, FiEdit, FiTrash2, FiX, FiShield } from 'react-icons/fi';

export default function RoleManagement() {
    const [roles, setRoles] = useState([]);
    const [permissions, setPermissions] = useState([]);
    const [selectedRole, setSelectedRole] = useState(null);
    const [rolePerms, setRolePerms] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editId, setEditId] = useState(null);
    const [form, setForm] = useState({ name: '', description: '' });
    const [saving, setSaving] = useState(false);

    const fetchRoles = async () => {
        setLoading(true);
        try {
            const [rolesRes, permsRes] = await Promise.all([api.get('/roles'), api.get('/roles/permissions')]);
            setRoles(rolesRes.data.roles || rolesRes.data || []);
            setPermissions(permsRes.data.permissions || permsRes.data || []);
        } catch { }
        setLoading(false);
    };

    useEffect(() => { fetchRoles(); }, []);

    const selectRole = async (role) => {
        setSelectedRole(role);
        try {
            const { data } = await api.get(`/roles/${role.id}`);
            setRolePerms(data.permissions?.map((p) => p.id || p) || []);
        } catch { setRolePerms([]); }
    };

    const togglePermission = async (permId) => {
        const newPerms = rolePerms.includes(permId)
            ? rolePerms.filter((id) => id !== permId)
            : [...rolePerms, permId];
        setRolePerms(newPerms);
        try {
            await api.put(`/roles/${selectedRole.id}/permissions`, { permission_ids: newPerms });
            toast.success('Permissions updated');
        } catch { toast.error('Update failed'); }
    };

    const handleSave = async (e) => {
        e.preventDefault(); setSaving(true);
        try {
            if (editId) { await api.put(`/roles/${editId}`, form); toast.success('Role updated'); }
            else { await api.post('/roles', form); toast.success('Role created'); }
            setShowForm(false); fetchRoles();
        } catch (err) { toast.error(err.response?.data?.detail || 'Save failed'); }
        finally { setSaving(false); }
    };

    const handleDelete = async (id) => {
        if (!confirm('Delete this role?')) return;
        try { await api.delete(`/roles/${id}`); toast.success('Deleted'); fetchRoles(); if (selectedRole?.id === id) setSelectedRole(null); }
        catch { toast.error('Delete failed'); }
    };

    // Group permissions by module
    const permsByModule = permissions.reduce((acc, p) => {
        const mod = p.module || 'general';
        if (!acc[mod]) acc[mod] = [];
        acc[mod].push(p);
        return acc;
    }, {});

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="page-title">Role Management</h1>
                <button onClick={() => { setEditId(null); setForm({ name: '', description: '' }); setShowForm(true); }} className="btn-primary"><FiPlus className="w-4 h-4" /> New Role</button>
            </div>

            {showForm && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-md">
                        <div className="flex items-center justify-between px-6 py-4 border-b"><h3 className="text-lg font-semibold">{editId ? 'Edit Role' : 'New Role'}</h3><button onClick={() => setShowForm(false)}><FiX className="w-5 h-5" /></button></div>
                        <form onSubmit={handleSave} className="p-6 space-y-4">
                            <div><label className="label">Name</label><input className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
                            <div><label className="label">Description</label><textarea className="input-field" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
                            <div className="flex gap-3"><button type="submit" disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save'}</button><button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button></div>
                        </form>
                    </div>
                </div>
            )}

            <div className="grid lg:grid-cols-3 gap-6">
                {/* Roles List */}
                <div className="card divide-y divide-gray-100">
                    <div className="p-4"><h3 className="section-title">Roles</h3></div>
                    {loading ? (
                        <div className="p-4"><div className="animate-spin rounded-full h-6 w-6 border-2 border-nea-blue border-t-transparent mx-auto" /></div>
                    ) : roles.map((role) => (
                        <div
                            key={role.id}
                            className={`flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 ${selectedRole?.id === role.id ? 'bg-nea-blue/5 border-l-2 border-nea-blue' : ''
                                }`}
                            onClick={() => selectRole(role)}
                        >
                            <div>
                                <p className="text-sm font-medium">{role.name}</p>
                                <p className="text-xs text-gray-400">{role.description}</p>
                            </div>
                            <div className="flex gap-1">
                                <button onClick={(e) => { e.stopPropagation(); setEditId(role.id); setForm({ name: role.name, description: role.description || '' }); setShowForm(true); }} className="p-1 rounded hover:bg-gray-200"><FiEdit className="w-3.5 h-3.5 text-gray-400" /></button>
                                {!role.is_system_role && <button onClick={(e) => { e.stopPropagation(); handleDelete(role.id); }} className="p-1 rounded hover:bg-red-50"><FiTrash2 className="w-3.5 h-3.5 text-red-400" /></button>}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Permission Matrix */}
                <div className="lg:col-span-2 card">
                    <div className="p-4 border-b border-gray-100">
                        <h3 className="section-title">{selectedRole ? `Permissions: ${selectedRole.name}` : 'Select a Role'}</h3>
                    </div>
                    {selectedRole ? (
                        <div className="p-4 space-y-4">
                            {Object.entries(permsByModule).map(([module, perms]) => (
                                <div key={module}>
                                    <h4 className="text-xs text-gray-400 uppercase font-semibold mb-2">{module}</h4>
                                    <div className="grid grid-cols-2 gap-2">
                                        {perms.map((p) => (
                                            <label
                                                key={p.id}
                                                className={`flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition-colors ${rolePerms.includes(p.id) ? 'bg-nea-blue/5 border-nea-blue/30' : 'border-gray-200 hover:border-gray-300'
                                                    }`}
                                            >
                                                <input type="checkbox" checked={rolePerms.includes(p.id)} onChange={() => togglePermission(p.id)} className="w-4 h-4 rounded text-nea-blue" />
                                                <div>
                                                    <p className="text-sm font-medium">{p.name}</p>
                                                    <p className="text-[10px] text-gray-400">{p.key}</p>
                                                </div>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="p-12 text-center text-gray-400"><FiShield className="w-12 h-12 mx-auto mb-3 text-gray-300" /><p>Click a role to manage its permissions</p></div>
                    )}
                </div>
            </div>
        </div>
    );
}
