/**
 * Notice List Page
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import { FiPlus, FiCalendar, FiAlertCircle } from 'react-icons/fi';

const priorityStyles = { high: 'badge-red', medium: 'badge-yellow', low: 'badge-green', normal: 'badge-gray' };

export default function NoticeList() {
    const { hasPermission } = useAuth();
    const [notices, setNotices] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const perPage = 12;

    useEffect(() => {
        const fetch = async () => {
            setLoading(true);
            try {
                const { data } = await api.get('/notices', {
                    params: { page, per_page: perPage, search: search || undefined },
                });
                setNotices(data.notices || []);
                setTotal(data.total || 0);
            } catch { setNotices([]); }
            setLoading(false);
        };
        fetch();
    }, [page, search]);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="page-title">Notices</h1>
                {hasPermission('create_notice') && (
                    <Link to="/notices/new" className="btn-primary"><FiPlus className="w-4 h-4" /> New Notice</Link>
                )}
            </div>

            <div className="max-w-md">
                <SearchBar value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search notices..." />
            </div>

            {loading ? (
                <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>
            ) : notices.length === 0 ? (
                <div className="card p-12 text-center text-gray-400"><div className="text-5xl mb-3">📋</div><p>No notices found.</p></div>
            ) : (
                <div className="space-y-3">
                    {notices.map((item) => (
                        <Link key={item.id} to={`/notices/${item.id}`} className="card p-5 block hover:shadow-md transition-shadow">
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        {item.priority && <span className={priorityStyles[item.priority] || 'badge-gray'}>{item.priority}</span>}
                                        {item.notice_type && <span className="badge-blue">{item.notice_type}</span>}
                                    </div>
                                    <h3 className="font-semibold text-gray-800 line-clamp-1">{item.title}</h3>
                                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">{item.content?.substring(0, 150)}</p>
                                </div>
                                <div className="flex flex-col items-end text-xs text-gray-400 shrink-0">
                                    <span className="flex items-center gap-1"><FiCalendar className="w-3 h-3" />{item.created_at && new Date(item.created_at).toLocaleDateString()}</span>
                                    {item.expires_at && (
                                        <span className="flex items-center gap-1 mt-1 text-amber-500">
                                            <FiAlertCircle className="w-3 h-3" />Expires {new Date(item.expires_at).toLocaleDateString()}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}

            <Pagination page={page} totalPages={Math.ceil(total / perPage)} onPageChange={setPage} />
        </div>
    );
}
