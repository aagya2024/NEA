/**
 * Recruitment — Job List Page
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import Pagination from '../../components/common/Pagination';
import { FiPlus, FiBriefcase, FiClock, FiMapPin } from 'react-icons/fi';

const statusStyles = { open: 'badge-green', closed: 'badge-red', draft: 'badge-gray' };

export default function JobList() {
    const { hasPermission } = useAuth();
    const [jobs, setJobs] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const perPage = 12;

    useEffect(() => {
        const fetch = async () => {
            setLoading(true);
            try {
                const { data } = await api.get('/recruitment', { params: { page, per_page: perPage } });
                setJobs(data.jobs || []);
                setTotal(data.total || 0);
            } catch { setJobs([]); }
            setLoading(false);
        };
        fetch();
    }, [page]);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="page-title">Recruitment</h1>
                <div className="flex gap-3">
                    {hasPermission('manage_recruitment') && (
                        <Link to="/recruitment/hr" className="btn-secondary text-sm">HR Dashboard</Link>
                    )}
                    {hasPermission('manage_recruitment') && (
                        <Link to="/recruitment/new" className="btn-primary"><FiPlus className="w-4 h-4" /> Post Job</Link>
                    )}
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>
            ) : jobs.length === 0 ? (
                <div className="card p-12 text-center text-gray-400"><div className="text-5xl mb-3">💼</div><p>No open positions.</p></div>
            ) : (
                <div className="grid md:grid-cols-2 gap-5">
                    {jobs.map((job) => (
                        <Link key={job.id} to={`/recruitment/${job.id}`} className="card p-5 hover:shadow-md transition-shadow group">
                            <div className="flex items-start justify-between mb-2">
                                <h3 className="font-semibold text-gray-800 group-hover:text-nea-blue transition-colors">{job.title}</h3>
                                <span className={statusStyles[job.status] || 'badge-gray'}>{job.status}</span>
                            </div>
                            <p className="text-sm text-gray-500 line-clamp-2 mb-3">{job.description?.substring(0, 120)}</p>
                            <div className="flex items-center gap-4 text-xs text-gray-400">
                                {job.department && <span className="flex items-center gap-1"><FiMapPin className="w-3 h-3" />{job.department}</span>}
                                {job.deadline && <span className="flex items-center gap-1"><FiClock className="w-3 h-3" />Deadline: {new Date(job.deadline).toLocaleDateString()}</span>}
                            </div>
                        </Link>
                    ))}
                </div>
            )}

            <Pagination page={page} totalPages={Math.ceil(total / perPage)} onPageChange={setPage} />
        </div>
    );
}
