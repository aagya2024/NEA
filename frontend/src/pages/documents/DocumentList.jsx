/**
 * Document List Page — Upload, search, download documents.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import toast from 'react-hot-toast';
import { FiUploadCloud, FiDownload, FiTrash2, FiFile, FiPlus } from 'react-icons/fi';

export default function DocumentList() {
    const { hasPermission } = useAuth();
    const [docs, setDocs] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [showUpload, setShowUpload] = useState(false);
    const [uploadForm, setUploadForm] = useState({ title: '', category: '', description: '' });
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const perPage = 15;

    const fetchDocs = async () => {
        setLoading(true);
        try {
            const { data } = await api.get('/documents', {
                params: { page, per_page: perPage, search: search || undefined },
            });
            setDocs(data.documents || []);
            setTotal(data.total || 0);
        } catch { setDocs([]); }
        setLoading(false);
    };

    useEffect(() => { fetchDocs(); }, [page, search]);

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) { toast.error('Select a file'); return; }
        setUploading(true);
        try {
            const fd = new FormData();
            fd.append('file', file);
            fd.append('title', uploadForm.title);
            fd.append('category', uploadForm.category);
            fd.append('description', uploadForm.description);
            await api.post('/documents', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
            toast.success('Document uploaded');
            setShowUpload(false);
            setUploadForm({ title: '', category: '', description: '' });
            setFile(null);
            fetchDocs();
        } catch (err) { toast.error(err.response?.data?.detail || 'Upload failed'); }
        finally { setUploading(false); }
    };

    const handleDownload = async (id, title) => {
        try {
            const resp = await api.get(`/documents/${id}/download`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([resp.data]));
            const a = document.createElement('a'); a.href = url; a.download = title || 'document'; a.click();
            window.URL.revokeObjectURL(url);
        } catch { toast.error('Download failed'); }
    };

    const handleDelete = async (id) => {
        if (!confirm('Delete this document?')) return;
        try { await api.delete(`/documents/${id}`); toast.success('Deleted'); fetchDocs(); }
        catch { toast.error('Delete failed'); }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="page-title">Documents</h1>
                {hasPermission('upload_document') && (
                    <button onClick={() => setShowUpload(!showUpload)} className="btn-primary">
                        <FiPlus className="w-4 h-4" /> Upload Document
                    </button>
                )}
            </div>

            {/* Upload Panel */}
            {showUpload && (
                <form onSubmit={handleUpload} className="card p-6 space-y-4">
                    <h3 className="section-title">Upload New Document</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                        <div><label className="label">Title</label><input className="input-field" value={uploadForm.title} onChange={(e) => setUploadForm({ ...uploadForm, title: e.target.value })} required /></div>
                        <div><label className="label">Category</label><select className="input-field" value={uploadForm.category} onChange={(e) => setUploadForm({ ...uploadForm, category: e.target.value })}><option value="">Select</option><option value="Policy">Policy</option><option value="Technical">Technical</option><option value="Administrative">Administrative</option><option value="Financial">Financial</option></select></div>
                    </div>
                    <div><label className="label">Description</label><textarea className="input-field" rows={2} value={uploadForm.description} onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })} /></div>
                    <div><label className="label">File</label><input type="file" onChange={(e) => setFile(e.target.files?.[0])} className="input-field" accept=".pdf,.doc,.docx,.xls,.xlsx" required /></div>
                    <div className="flex gap-3"><button type="submit" disabled={uploading} className="btn-primary">{uploading ? 'Uploading...' : 'Upload'}</button><button type="button" onClick={() => setShowUpload(false)} className="btn-secondary">Cancel</button></div>
                </form>
            )}

            <div className="max-w-md"><SearchBar value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search documents..." /></div>

            {loading ? (
                <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>
            ) : docs.length === 0 ? (
                <div className="card p-12 text-center text-gray-400"><div className="text-5xl mb-3">📁</div><p>No documents found.</p></div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {docs.map((doc) => (
                        <div key={doc.id} className="card p-5 hover:shadow-md transition-shadow">
                            <div className="flex items-start gap-3">
                                <div className="w-10 h-10 bg-nea-blue/10 rounded-lg flex items-center justify-center shrink-0">
                                    <FiFile className="w-5 h-5 text-nea-blue" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h3 className="font-medium text-gray-800 text-sm line-clamp-2">{doc.title}</h3>
                                    {doc.category && <span className="badge-blue text-[10px] mt-1 inline-block">{doc.category}</span>}
                                    <p className="text-xs text-gray-400 mt-2">Downloads: {doc.download_count || 0}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 mt-4 pt-3 border-t border-gray-100">
                                <button onClick={() => handleDownload(doc.id, doc.title)} className="btn-ghost text-xs flex-1"><FiDownload className="w-3 h-3" /> Download</button>
                                {hasPermission('delete_document') && (
                                    <button onClick={() => handleDelete(doc.id)} className="p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50"><FiTrash2 className="w-3.5 h-3.5" /></button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <Pagination page={page} totalPages={Math.ceil(total / perPage)} onPageChange={setPage} />
        </div>
    );
}
