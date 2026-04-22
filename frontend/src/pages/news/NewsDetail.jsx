/**
 * News Detail Page
 */

import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import toast from 'react-hot-toast';
import { FiArrowLeft, FiEdit, FiTrash2, FiEye, FiCalendar, FiUser } from 'react-icons/fi';

export default function NewsDetail() {
    const { id } = useParams();
    const { hasPermission } = useAuth();
    const navigate = useNavigate();
    const [news, setNews] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get(`/news/${id}`)
            .then((r) => setNews(r.data))
            .catch(() => toast.error('News article not found'))
            .finally(() => setLoading(false));
    }, [id]);

    const handleDelete = async () => {
        if (!confirm('Delete this article?')) return;
        try {
            await api.delete(`/news/${id}`);
            toast.success('Deleted');
            navigate('/news');
        } catch { toast.error('Delete failed'); }
    };

    if (loading) return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>;
    if (!news) return <div className="card p-12 text-center text-gray-400">Article not found.</div>;

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <Link to="/news" className="btn-ghost text-sm"><FiArrowLeft className="w-4 h-4" /> Back to News</Link>

            <article className="card p-8">
                <div className="flex items-start justify-between mb-4">
                    <div>
                        {news.category && <span className="badge-blue mb-2 inline-block">{news.category}</span>}
                        <h1 className="text-2xl font-bold text-gray-800">{news.title}</h1>
                    </div>
                    <div className="flex gap-2 shrink-0">
                        {hasPermission('edit_news') && (
                            <Link to={`/news/${id}/edit`} className="btn-ghost text-sm"><FiEdit className="w-4 h-4" /></Link>
                        )}
                        {hasPermission('delete_news') && (
                            <button onClick={handleDelete} className="btn-ghost text-sm text-red-500 hover:text-red-700"><FiTrash2 className="w-4 h-4" /></button>
                        )}
                    </div>
                </div>

                <div className="flex items-center gap-4 text-xs text-gray-400 mb-6 pb-4 border-b border-gray-100">
                    {news.author_name && <span className="flex items-center gap-1"><FiUser className="w-3 h-3" /> {news.author_name}</span>}
                    <span className="flex items-center gap-1"><FiCalendar className="w-3 h-3" /> {news.published_at ? new Date(news.published_at).toLocaleDateString() : 'Draft'}</span>
                    <span className="flex items-center gap-1"><FiEye className="w-3 h-3" /> {news.view_count || 0} views</span>
                </div>

                <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {news.content}
                </div>
            </article>
        </div>
    );
}
