/**
 * News Form — Create / Edit news article.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import toast from 'react-hot-toast';
import { FiArrowLeft } from 'react-icons/fi';

export default function NewsForm() {
    const { id } = useParams();
    const navigate = useNavigate();
    const isEdit = !!id;
    const [form, setForm] = useState({
        title: '', content: '', category: '', is_published: true,
    });
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (isEdit) {
            api.get(`/news/${id}`)
                .then((r) => setForm({
                    title: r.data.title || '',
                    content: r.data.content || '',
                    category: r.data.category || '',
                    is_published: r.data.is_published ?? true,
                }))
                .catch(() => toast.error('Failed to load article'));
        }
    }, [id]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            if (isEdit) {
                await api.put(`/news/${id}`, form);
                toast.success('Article updated');
            } else {
                await api.post('/news', form);
                toast.success('Article created');
            }
            navigate('/news');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to save');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <button onClick={() => navigate('/news')} className="btn-ghost text-sm">
                <FiArrowLeft className="w-4 h-4" /> Back to News
            </button>

            <h1 className="page-title">{isEdit ? 'Edit Article' : 'New Article'}</h1>

            <form onSubmit={handleSubmit} className="card p-6 space-y-5">
                <div>
                    <label className="label">Title</label>
                    <input className="input-field" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
                </div>

                <div>
                    <label className="label">Category</label>
                    <select className="input-field" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                        <option value="">Select category</option>
                        <option value="General">General</option>
                        <option value="Announcement">Announcement</option>
                        <option value="Policy">Policy</option>
                        <option value="Technical">Technical</option>
                        <option value="Event">Event</option>
                    </select>
                </div>

                <div>
                    <label className="label">Content</label>
                    <textarea
                        className="input-field min-h-[200px]"
                        value={form.content}
                        onChange={(e) => setForm({ ...form, content: e.target.value })}
                        required
                    />
                </div>

                <div className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        id="published"
                        checked={form.is_published}
                        onChange={(e) => setForm({ ...form, is_published: e.target.checked })}
                        className="w-4 h-4 text-nea-blue rounded"
                    />
                    <label htmlFor="published" className="text-sm text-gray-700">Publish immediately</label>
                </div>

                <div className="flex gap-3 pt-2">
                    <button type="submit" disabled={saving} className="btn-primary">
                        {saving ? 'Saving...' : (isEdit ? 'Update' : 'Create')} Article
                    </button>
                    <button type="button" onClick={() => navigate('/news')} className="btn-secondary">Cancel</button>
                </div>
            </form>
        </div>
    );
}
