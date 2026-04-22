/**
 * News List Page — Paginated, searchable news articles.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import { FiPlus, FiEye, FiCalendar } from 'react-icons/fi';

export default function NewsList() {
    const { hasPermission } = useAuth();
    const [news, setNews] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const perPage = 12;

    useEffect(() => {
        const fetch = async () => {
            setLoading(true);
            try {
                const { data } = await api.get('/news', {
                    params: { page, per_page: perPage, search: search || undefined },
                });
                setNews(data.news || []);
                setTotal(data.total || 0);
            } catch { setNews([]); }
            setLoading(false);
        };
        fetch();
    }, [page, search]);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="page-title">News</h1>
                {hasPermission('create_news') && (
                    <Link to="/news/new" className="btn-primary"><FiPlus className="w-4 h-4" /> New Article</Link>
                )}
            </div>

            <div className="max-w-md">
                <SearchBar value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search news..." />
            </div>

            {loading ? (
                <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>
            ) : news.length === 0 ? (
                <div className="card p-12 text-center text-gray-400">
                    <div className="text-5xl mb-3">📰</div>
                    <p>No news articles found.</p>
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {news.map((item) => (
                        <Link key={item.id} to={`/news/${item.id}`} className="card overflow-hidden group hover:shadow-md transition-shadow">
                            <div className="h-2 bg-nea-blue" />
                            <div className="p-5">
                                {item.category && <span className="badge-blue text-[10px] mb-2 inline-block">{item.category}</span>}
                                <h3 className="font-semibold text-gray-800 line-clamp-2 group-hover:text-nea-blue transition-colors">
                                    {item.title}
                                </h3>
                                <p className="text-xs text-gray-400 mt-3 flex items-center gap-3">
                                    <span className="flex items-center gap-1"><FiCalendar className="w-3 h-3" /> {item.published_at ? new Date(item.published_at).toLocaleDateString() : 'Draft'}</span>
                                    <span className="flex items-center gap-1"><FiEye className="w-3 h-3" /> {item.view_count || 0}</span>
                                </p>
                                {item.author_name && <p className="text-xs text-gray-400 mt-1">By {item.author_name}</p>}
                            </div>
                        </Link>
                    ))}
                </div>
            )}

            <Pagination page={page} totalPages={Math.ceil(total / perPage)} onPageChange={setPage} />
        </div>
    );
}
