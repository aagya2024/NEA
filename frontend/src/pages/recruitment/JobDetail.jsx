/**
 * Job Detail + Create/Edit + Apply
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import toast from 'react-hot-toast';
import { FiArrowLeft, FiEdit, FiTrash2, FiSend, FiClock, FiMapPin } from 'react-icons/fi';

export default function JobDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { hasPermission, user } = useAuth();
    const isNew = id === 'new';
    const [isEditing, setIsEditing] = useState(isNew);
    const [job, setJob] = useState(null);
    const [form, setForm] = useState({ title: '', description: '', department: '', requirements: '', deadline: '', status: 'open' });
    const [applying, setApplying] = useState(false);
    const [appForm, setAppForm] = useState({ cover_letter: '' });
    const [cvFile, setCvFile] = useState(null);
    const [loading, setLoading] = useState(!isNew);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (!isNew) {
            api.get(`/recruitment/${id}`)
                .then((r) => { setJob(r.data); setForm({ title: r.data.title, description: r.data.description || '', department: r.data.department || '', requirements: r.data.requirements || '', deadline: r.data.deadline ? r.data.deadline.split('T')[0] : '', status: r.data.status || 'open' }); })
                .catch(() => toast.error('Job not found'))
                .finally(() => setLoading(false));
        }
    }, [id]);

    const handleSave = async (e) => {
        e.preventDefault(); setSaving(true);
        try {
            const payload = { ...form, deadline: form.deadline || null };
            if (isNew) { await api.post('/recruitment', payload); toast.success('Job created'); }
            else { await api.put(`/recruitment/${id}`, payload); toast.success('Job updated'); }
            navigate('/recruitment');
        } catch (err) { toast.error(err.response?.data?.detail || 'Save failed'); }
        finally { setSaving(false); }
    };

    const handleApply = async (e) => {
        e.preventDefault(); setSaving(true);
        try {
            const fd = new FormData();
            fd.append('cover_letter', appForm.cover_letter);
            if (cvFile) fd.append('cv', cvFile);
            await api.post(`/recruitment/${id}/apply`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
            toast.success('Application submitted!');
            setApplying(false);
        } catch (err) { toast.error(err.response?.data?.detail || 'Application failed'); }
        finally { setSaving(false); }
    };

    const handleDelete = async () => {
        if (!confirm('Delete this posting?')) return;
        try { await api.delete(`/recruitment/${id}`); toast.success('Deleted'); navigate('/recruitment'); }
        catch { toast.error('Delete failed'); }
    };

    if (loading) return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>;

    if (isEditing || isNew) {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <button onClick={() => navigate('/recruitment')} className="btn-ghost text-sm"><FiArrowLeft className="w-4 h-4" /> Back</button>
                <h1 className="page-title">{isNew ? 'Post New Job' : 'Edit Job'}</h1>
                <form onSubmit={handleSave} className="card p-6 space-y-4">
                    <div><label className="label">Title</label><input className="input-field" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></div>
                    <div className="grid grid-cols-2 gap-4">
                        <div><label className="label">Department</label><input className="input-field" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} /></div>
                        <div><label className="label">Deadline</label><input type="date" className="input-field" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} /></div>
                    </div>
                    <div><label className="label">Status</label><select className="input-field" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}><option value="open">Open</option><option value="closed">Closed</option><option value="draft">Draft</option></select></div>
                    <div><label className="label">Description</label><textarea className="input-field min-h-[120px]" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required /></div>
                    <div><label className="label">Requirements</label><textarea className="input-field min-h-[100px]" value={form.requirements} onChange={(e) => setForm({ ...form, requirements: e.target.value })} /></div>
                    <div className="flex gap-3"><button type="submit" disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save'}</button><button type="button" onClick={() => navigate('/recruitment')} className="btn-secondary">Cancel</button></div>
                </form>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <Link to="/recruitment" className="btn-ghost text-sm"><FiArrowLeft className="w-4 h-4" /> Back</Link>
            <div className="card p-8">
                <div className="flex items-start justify-between mb-4">
                    <div>
                        <span className={`badge mb-2 inline-block ${job?.status === 'open' ? 'badge-green' : 'badge-red'}`}>{job?.status}</span>
                        <h1 className="text-2xl font-bold text-gray-800">{job?.title}</h1>
                    </div>
                    <div className="flex gap-2">
                        {hasPermission('manage_recruitment') && <button onClick={() => setIsEditing(true)} className="btn-ghost"><FiEdit className="w-4 h-4" /></button>}
                        {hasPermission('manage_recruitment') && <button onClick={handleDelete} className="btn-ghost text-red-500"><FiTrash2 className="w-4 h-4" /></button>}
                    </div>
                </div>
                <div className="flex gap-4 text-xs text-gray-400 mb-6">
                    {job?.department && <span className="flex items-center gap-1"><FiMapPin className="w-3 h-3" />{job.department}</span>}
                    {job?.deadline && <span className="flex items-center gap-1"><FiClock className="w-3 h-3" />Deadline: {new Date(job.deadline).toLocaleDateString()}</span>}
                </div>
                <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap mb-6">{job?.description}</div>
                {job?.requirements && (<div><h3 className="font-semibold text-gray-800 mb-2">Requirements</h3><div className="text-sm text-gray-600 whitespace-pre-wrap">{job.requirements}</div></div>)}
            </div>

            {/* Apply Section */}
            {job?.status === 'open' && !applying && (
                <button onClick={() => setApplying(true)} className="btn-primary w-full py-3"><FiSend className="w-4 h-4" /> Apply for this Position</button>
            )}

            {applying && (
                <form onSubmit={handleApply} className="card p-6 space-y-4">
                    <h3 className="section-title">Submit Application</h3>
                    <div><label className="label">Cover Letter</label><textarea className="input-field min-h-[120px]" value={appForm.cover_letter} onChange={(e) => setAppForm({ ...appForm, cover_letter: e.target.value })} placeholder="Why are you interested in this position?" required /></div>
                    <div><label className="label">Upload CV</label><input type="file" className="input-field" accept=".pdf,.doc,.docx" onChange={(e) => setCvFile(e.target.files?.[0])} /></div>
                    <div className="flex gap-3"><button type="submit" disabled={saving} className="btn-primary">{saving ? 'Submitting...' : 'Submit Application'}</button><button type="button" onClick={() => setApplying(false)} className="btn-secondary">Cancel</button></div>
                </form>
            )}
        </div>
    );
}
