/**
 * Act Detail + Create/Edit
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import toast from 'react-hot-toast';
import { FiArrowLeft, FiEdit, FiTrash2, FiDownload } from 'react-icons/fi';

export default function ActDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { hasPermission } = useAuth();
    const isNew = id === 'new';
    const [isEditing, setIsEditing] = useState(isNew);
    const [act, setAct] = useState(null);
    const [form, setForm] = useState({ title: '', content: '', act_type: '', year: new Date().getFullYear(), tags: '' });
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(!isNew);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (!isNew) {
            api.get(`/acts/${id}`)
                .then((r) => { setAct(r.data); setForm({ title: r.data.title, content: r.data.content || '', act_type: r.data.act_type || '', year: r.data.year || '', tags: r.data.tags || '' }); })
                .catch(() => toast.error('Act not found'))
                .finally(() => setLoading(false));
        }
    }, [id]);

    const handleSave = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            if (isNew) {
                const fd = new FormData();
                fd.append('title', form.title); fd.append('content', form.content);
                fd.append('act_type', form.act_type); fd.append('year', form.year);
                fd.append('tags', form.tags);
                if (file) fd.append('file', file);
                await api.post('/acts', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
                toast.success('Act created');
            } else {
                await api.put(`/acts/${id}`, form);
                toast.success('Act updated');
            }
            navigate('/acts');
        } catch (err) { toast.error(err.response?.data?.detail || 'Save failed'); }
        finally { setSaving(false); }
    };

    const handleDelete = async () => {
        if (!confirm('Delete this act?')) return;
        try { await api.delete(`/acts/${id}`); toast.success('Deleted'); navigate('/acts'); }
        catch { toast.error('Delete failed'); }
    };

    if (loading) return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>;

    if (isEditing || isNew) {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <button onClick={() => navigate('/acts')} className="btn-ghost text-sm"><FiArrowLeft className="w-4 h-4" /> Back</button>
                <h1 className="page-title">{isNew ? 'Add Act' : 'Edit Act'}</h1>
                <form onSubmit={handleSave} className="card p-6 space-y-4">
                    <div><label className="label">Title</label><input className="input-field" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></div>
                    <div className="grid grid-cols-2 gap-4">
                        <div><label className="label">Type</label><select className="input-field" value={form.act_type} onChange={(e) => setForm({ ...form, act_type: e.target.value })}><option value="">Select</option><option value="Act">Act</option><option value="Bylaw">Bylaw</option><option value="Regulation">Regulation</option><option value="Policy">Policy</option></select></div>
                        <div><label className="label">Year</label><input type="number" className="input-field" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} /></div>
                    </div>
                    <div><label className="label">Tags (comma-separated)</label><input className="input-field" value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} placeholder="electricity, tariff, safety" /></div>
                    <div><label className="label">Content</label><textarea className="input-field min-h-[150px]" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} /></div>
                    {isNew && <div><label className="label">Upload File (PDF)</label><input type="file" className="input-field" accept=".pdf" onChange={(e) => setFile(e.target.files?.[0])} /></div>}
                    <div className="flex gap-3"><button type="submit" disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save'}</button><button type="button" onClick={() => navigate('/acts')} className="btn-secondary">Cancel</button></div>
                </form>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <Link to="/acts" className="btn-ghost text-sm"><FiArrowLeft className="w-4 h-4" /> Back to Acts</Link>
            <article className="card p-8">
                <div className="flex items-start justify-between mb-4">
                    <div>
                        {act?.act_type && <span className="badge-gray mb-2 inline-block">{act.act_type}</span>}
                        <h1 className="text-2xl font-bold text-gray-800">{act?.title}</h1>
                    </div>
                    <div className="flex gap-2">
                        {hasPermission('manage_acts') && <button onClick={() => setIsEditing(true)} className="btn-ghost text-sm"><FiEdit className="w-4 h-4" /></button>}
                        {hasPermission('manage_acts') && <button onClick={handleDelete} className="btn-ghost text-sm text-red-500"><FiTrash2 className="w-4 h-4" /></button>}
                    </div>
                </div>
                <div className="text-xs text-gray-400 mb-6 flex gap-4">
                    {act?.year && <span>Year: {act.year}</span>}
                    {act?.tags && <span>Tags: {act.tags}</span>}
                </div>
                <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">{act?.content}</div>
                {act?.file_path && (
                    <div className="mt-6 pt-4 border-t border-gray-100">
                        <button onClick={() => window.open(`/api/acts/${act.id}/download`, '_blank')} className="btn-secondary text-sm">
                            <FiDownload className="w-4 h-4" /> Download PDF
                        </button>
                    </div>
                )}
            </article>
        </div>
    );
}
