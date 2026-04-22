/**
 * User Management — CRUD users with role assignment.
 */

import { useState, useEffect } from 'react';
import api from '../../api/axios';
import DataTable from '../../components/common/DataTable';
import Pagination from '../../components/common/Pagination';
import SearchBar from '../../components/common/SearchBar';
import toast from 'react-hot-toast';
import { FiPlus, FiEdit, FiTrash2, FiX } from 'react-icons/fi';

export default function UserManagement() {
    const [users, setUsers] = useState([]);
    const [roles, setRoles] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editId, setEditId] = useState(null);
    const [form, setForm] = useState({ email: '', full_name: '', password: '', department: '', employee_id: '', phone: '', role_id: '' });
    const [saving, setSaving] = useState(false);
    const perPage = 15;

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const { data } = await api.get('/users', { params: { page, per_page: perPage, search: search || undefined } });
            setUsers(data.users || []);
            setTotal(data.total || 0);
        } catch { setUsers([]); }
        setLoading(false);
    };

    useEffect(() => { fetchUsers(); }, [page, search]);
    useEffect(() => { api.get('/roles').then((r) => setRoles(r.data.roles || r.data || [])).catch(() => { }); }, []);

    const openNew = () => {
        setEditId(null);
        setForm({ email: '', full_name: '', password: '', department: '', employee_id: '', phone: '', role_id: roles[0]?.id || '' });
        setShowForm(true);
    };

    const openEdit = (user) => {
        setEditId(user.id);
        setForm({ email: user.email, full_name: user.full_name, password: '', department: user.department || '', employee_id: user.employee_id || '', phone: user.phone || '', role_id: user.role_id });
        setShowForm(true);
    };

    const handleSave = async (e) => {
        e.preventDefault(); setSaving(true);
        try {
            if (editId) {
                const payload = { ...form };
                if (!payload.password) delete payload.password;
                await api.put(`/users/${editId}`, payload);
                toast.success('User updated');
            } else {
                await api.post('/users', form);
                toast.success('User created');
            }
            setShowForm(false);
            fetchUsers();
        } catch (err) { toast.error(err.response?.data?.detail || 'Save failed'); }
        finally { setSaving(false); }
    };

    const handleDelete = async (id) => {
        if (!confirm('Delete this user?')) return;
        try { await api.delete(`/users/${id}`); toast.success('Deleted'); fetchUsers(); }
        catch { toast.error('Delete failed'); }
    };

    const getRoleName = (roleId) => roles.find((r) => r.id === roleId)?.name || '-';

    const columns = [
        { key: 'full_name', label: 'Name' },
        { key: 'email', label: 'Email' },
        { key: 'department', label: 'Department', render: (r) => r.department || '-' },
        { key: 'role', label: 'Role', render: (r) => <span className="badge-blue">{getRoleName(r.role_id)}</span> },
        { key: 'status', label: 'Status', render: (r) => r.is_active ? <span className="badge-green">Active</span> : <span className="badge-red">Inactive</span> },
        {
            key: 'actions', label: '', width: '100px', render: (r) => (
                <div className="flex gap-1">
                    <button onClick={() => openEdit(r)} className="p-1.5 rounded hover:bg-gray-100"><FiEdit className="w-3.5 h-3.5 text-gray-500" /></button>
                    <button onClick={() => handleDelete(r.id)} className="p-1.5 rounded hover:bg-red-50"><FiTrash2 className="w-3.5 h-3.5 text-red-400" /></button>
                </div>
            )
        },
    ];

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="page-title">User Management</h1>
                <button onClick={openNew} className="btn-primary"><FiPlus className="w-4 h-4" /> Add User</button>
            </div>

            <div className="max-w-md"><SearchBar value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search users..." /></div>

            {/* Form Modal */}
            {showForm && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center justify-between px-6 py-4 border-b"><h3 className="text-lg font-semibold">{editId ? 'Edit User' : 'New User'}</h3><button onClick={() => setShowForm(false)}><FiX className="w-5 h-5 text-gray-400" /></button></div>
                        <form onSubmit={handleSave} className="p-6 space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div><label className="label">Full Name</label><input className="input-field" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required /></div>
                                <div><label className="label">Email</label><input type="email" className="input-field" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></div>
                            </div>
                            <div><label className="label">Password {editId && '(leave blank to keep)'}</label><input type="password" className="input-field" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} {...(!editId ? { required: true } : {})} /></div>
                            <div className="grid grid-cols-2 gap-4">
                                <div><label className="label">Department</label><input className="input-field" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} /></div>
                                <div><label className="label">Employee ID</label><input className="input-field" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })} /></div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div><label className="label">Phone</label><input className="input-field" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></div>
                                <div><label className="label">Role</label><select className="input-field" value={form.role_id} onChange={(e) => setForm({ ...form, role_id: parseInt(e.target.value) })} required>{roles.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}</select></div>
                            </div>
                            <div className="flex gap-3 pt-2"><button type="submit" disabled={saving} className="btn-primary">{saving ? 'Saving...' : (editId ? 'Update' : 'Create')}</button><button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button></div>
                        </form>
                    </div>
                </div>
            )}

            <DataTable columns={columns} data={users} loading={loading} emptyMessage="No users found." />
            <Pagination page={page} totalPages={Math.ceil(total / perPage)} onPageChange={setPage} />
        </div>
    );
}
