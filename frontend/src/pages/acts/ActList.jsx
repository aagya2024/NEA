/**
 * Acts & Bylaws List Page
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import { FiPlus, FiBook } from 'react-icons/fi';

export default function ActList() {
    const { hasPermission } = useAuth();
    const [acts, setActs] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const perPage = 12;

    useEffect(() => {
        const fetch = async () => {
            setLoading(true);
            try {
                const { data } = await api.get('/acts', { params: { page, per_page: perPage, search: search || undefined } });
                setActs(data.acts || []);
                setTotal(data.total || 0);
            } catch { setActs([]); }
            setLoading(false);
        };
        fetch();
    }, [page, search]);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="page-title">Acts & Bylaws</h1>
                {hasPermission('manage_acts') && (
                    <Link to="/acts/new" className="btn-primary"><FiPlus className="w-4 h-4" /> Add Act</Link>
                )}
            </div>

            <div className="max-w-md"><SearchBar value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search acts..." /></div>

            {loading ? (
                <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>
            ) : acts.length === 0 ? (
                <div className="card p-12 text-center text-gray-400"><div className="text-5xl mb-3">⚖️</div><p>No acts found.</p></div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {acts.map((act) => (
                        <Link key={act.id} to={`/acts/${act.id}`} className="card p-5 hover:shadow-md transition-shadow group">
                            <div className="flex items-start gap-3">
                                <div className="w-10 h-10 bg-rose-100 rounded-lg flex items-center justify-center shrink-0"><FiBook className="w-5 h-5 text-rose-600" /></div>
                                <div className="flex-1 min-w-0">
                                    <h3 className="font-medium text-gray-800 text-sm group-hover:text-nea-blue transition-colors line-clamp-2">{act.title}</h3>
                                    <div className="flex items-center gap-2 mt-2">
                                        {act.act_type && <span className="badge-gray text-[10px]">{act.act_type}</span>}
                                        {act.year && <span className="text-xs text-gray-400">{act.year}</span>}
                                    </div>
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
