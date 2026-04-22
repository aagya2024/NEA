/**
 * Notice Detail + Create/Edit (combined for simplicity)
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import toast from 'react-hot-toast';
import { FiArrowLeft, FiEdit, FiTrash2 } from 'react-icons/fi';

export default function NoticeDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { hasPermission } = useAuth();
    const isNew = id === 'new';
    const [isEditing, setIsEditing] = useState(isNew);
    const [notice, setNotice] = useState(null);
    const [form, setForm] = useState({ title: '', content: '', notice_type: 'internal', priority: 'normal', expires_at: '' });
    const [loading, setLoading] = useState(!isNew);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (!isNew) {
            api.get(`/notices/${id}`)
                .then((r) => { setNotice(r.data); setForm({ title: r.data.title, content: r.data.content, notice_type: r.data.notice_type || 'internal', priority: r.data.priority || 'normal', expires_at: r.data.expires_at ? r.data.expires_at.split('T')[0] : '' }); })
                .catch(() => toast.error('Notice not found'))
                .finally(() => setLoading(false));
        }
    }, [id]);

    const handleSave = async (e) => {
        e.preventDefault();
        setSaving(true);
        const payload = { ...form, expires_at: form.expires_at || null };
        try {
            if (isNew) { await api.post('/notices', payload); toast.success('Notice created'); }
            else { await api.put(`/notices/${id}`, payload); toast.success('Notice updated'); setIsEditing(false); }
            navigate('/notices');
        } catch (err) { toast.error(err.response?.data?.detail || 'Save failed'); }
        finally { setSaving(false); }
    };

    const handleDelete = async () => {
        if (!confirm('Delete this notice?')) return;
        try { await api.delete(`/notices/${id}`); toast.success('Deleted'); navigate('/notices'); }
        catch { toast.error('Delete failed'); }
    };

    if (loading) return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>;

    if (isEditing || isNew) {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <button onClick={() => navigate('/notices')} className="btn-ghost text-sm"><FiArrowLeft className="w-4 h-4" /> Back</button>
                <h1 className="page-title">{isNew ? 'Create Notice' : 'Edit Notice'}</h1>
                <form onSubmit={handleSave} className="card p-6 space-y-4">
                    <div><label className="label">Title</label><input className="input-field" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></div>
                    <div className="grid grid-cols-2 gap-4">
                        <div><label className="label">Type</label><select className="input-field" value={form.notice_type} onChange={(e) => setForm({ ...form, notice_type: e.target.value })}><option value="internal">Internal</option><option value="public">Public</option></select></div>
                        <div><label className="label">Priority</label><select className="input-field" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}><option value="low">Low</option><option value="normal">Normal</option><option value="medium">Medium</option><option value="high">High</option></select></div>
                    </div>
                    <div><label className="label">Expires At</label><input type="date" className="input-field" value={form.expires_at} onChange={(e) => setForm({ ...form, expires_at: e.target.value })} /></div>
                    <div><label className="label">Content</label><textarea className="input-field min-h-[150px]" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} required /></div>
                    <div className="flex gap-3"><button type="submit" disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save'}</button><button type="button" onClick={() => isNew ? navigate('/notices') : setIsEditing(false)} className="btn-secondary">Cancel</button></div>
                </form>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <Link to="/notices" className="btn-ghost text-sm"><FiArrowLeft className="w-4 h-4" /> Back to Notices</Link>
            <article className="card p-8">
                <div className="flex items-start justify-between mb-4">
                    <div>
                        {notice?.priority && <span className={`badge mb-2 inline-block ${notice.priority === 'high' ? 'badge-red' : notice.priority === 'medium' ? 'badge-yellow' : 'badge-gray'}`}>{notice.priority}</span>}
                        <h1 className="text-2xl font-bold text-gray-800">{notice?.title}</h1>
                    </div>
                    <div className="flex gap-2">
                        {hasPermission('edit_notice') && <button onClick={() => setIsEditing(true)} className="btn-ghost text-sm"><FiEdit className="w-4 h-4" /></button>}
                        {hasPermission('delete_notice') && <button onClick={handleDelete} className="btn-ghost text-sm text-red-500"><FiTrash2 className="w-4 h-4" /></button>}
                    </div>
                </div>
                <div className="text-xs text-gray-400 mb-6 flex gap-4">
                    <span>Type: {notice?.notice_type}</span>
                    {notice?.created_at && <span>Posted: {new Date(notice.created_at).toLocaleDateString()}</span>}
                    {notice?.expires_at && <span className="text-amber-500">Expires: {new Date(notice.expires_at).toLocaleDateString()}</span>}
                </div>
                <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">{notice?.content}</div>
            </article>
        </div>
    );
}
