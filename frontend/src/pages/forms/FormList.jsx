/**
 * Form List Page — Downloadable internal forms with upload capability.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import toast from 'react-hot-toast';
import { FiDownload, FiPlus, FiTrash2, FiClipboard } from 'react-icons/fi';

export default function FormList() {
    const { hasPermission } = useAuth();
    const [forms, setForms] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [showUpload, setShowUpload] = useState(false);
    const [uploadForm, setUploadForm] = useState({ title: '', category: '' });
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const perPage = 15;

    const fetchForms = async () => {
        setLoading(true);
        try {
            const { data } = await api.get('/forms', { params: { page, per_page: perPage, search: search || undefined } });
            setForms(data.forms || []);
            setTotal(data.total || 0);
        } catch { setForms([]); }
        setLoading(false);
    };

    useEffect(() => { fetchForms(); }, [page, search]);

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) { toast.error('Select a file'); return; }
        setUploading(true);
        try {
            const fd = new FormData();
            fd.append('file', file);
            fd.append('title', uploadForm.title);
            fd.append('category', uploadForm.category);
            await api.post('/forms', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
            toast.success('Form uploaded');
            setShowUpload(false);
            fetchForms();
        } catch (err) { toast.error(err.response?.data?.detail || 'Upload failed'); }
        finally { setUploading(false); }
    };

    const handleDownload = async (id, title) => {
        try {
            const resp = await api.get(`/forms/${id}/download`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([resp.data]));
            const a = document.createElement('a'); a.href = url; a.download = title || 'form'; a.click();
            window.URL.revokeObjectURL(url);
        } catch { toast.error('Download failed'); }
    };

    const handleDelete = async (id) => {
        if (!confirm('Delete this form?')) return;
        try { await api.delete(`/forms/${id}`); toast.success('Deleted'); fetchForms(); }
        catch { toast.error('Delete failed'); }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="page-title">Forms</h1>
                {hasPermission('upload_form') && (
                    <button onClick={() => setShowUpload(!showUpload)} className="btn-primary"><FiPlus className="w-4 h-4" /> Upload Form</button>
                )}
            </div>

            {showUpload && (
                <form onSubmit={handleUpload} className="card p-6 space-y-4">
                    <h3 className="section-title">Upload Form Template</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                        <div><label className="label">Title</label><input className="input-field" value={uploadForm.title} onChange={(e) => setUploadForm({ ...uploadForm, title: e.target.value })} required /></div>
                        <div><label className="label">Category</label><select className="input-field" value={uploadForm.category} onChange={(e) => setUploadForm({ ...uploadForm, category: e.target.value })}><option value="">Select</option><option value="HR">HR</option><option value="Finance">Finance</option><option value="Technical">Technical</option><option value="Administrative">Administrative</option></select></div>
                    </div>
                    <div><label className="label">File</label><input type="file" onChange={(e) => setFile(e.target.files?.[0])} className="input-field" required /></div>
                    <div className="flex gap-3"><button type="submit" disabled={uploading} className="btn-primary">{uploading ? 'Uploading...' : 'Upload'}</button><button type="button" onClick={() => setShowUpload(false)} className="btn-secondary">Cancel</button></div>
                </form>
            )}

            <div className="max-w-md"><SearchBar value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search forms..." /></div>

            {loading ? (
                <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>
            ) : forms.length === 0 ? (
                <div className="card p-12 text-center text-gray-400"><div className="text-5xl mb-3">📄</div><p>No forms found.</p></div>
            ) : (
                <div className="space-y-3">
                    {forms.map((item) => (
                        <div key={item.id} className="card p-4 flex items-center gap-4 hover:shadow-md transition-shadow">
                            <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center shrink-0"><FiClipboard className="w-5 h-5 text-emerald-600" /></div>
                            <div className="flex-1 min-w-0">
                                <h3 className="font-medium text-gray-800 text-sm">{item.title}</h3>
                                <p className="text-xs text-gray-400">{item.category && <span className="badge-green mr-2">{item.category}</span>}Downloads: {item.download_count || 0}</p>
                            </div>
                            <div className="flex items-center gap-2 shrink-0">
                                <button onClick={() => handleDownload(item.id, item.title)} className="btn-ghost text-xs"><FiDownload className="w-4 h-4" /></button>
                                {hasPermission('delete_form') && <button onClick={() => handleDelete(item.id)} className="p-2 text-gray-400 hover:text-red-500"><FiTrash2 className="w-4 h-4" /></button>}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <Pagination page={page} totalPages={Math.ceil(total / perPage)} onPageChange={setPage} />
        </div>
    );
}
