/**
 * HR Dashboard — Review job applications.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import toast from 'react-hot-toast';
import DataTable from '../../components/common/DataTable';
import { FiArrowLeft, FiDownload } from 'react-icons/fi';

const statusStyles = { applied: 'badge-blue', shortlisted: 'badge-green', rejected: 'badge-red', under_review: 'badge-yellow' };

export default function HRDashboard() {
    const [jobs, setJobs] = useState([]);
    const [selectedJob, setSelectedJob] = useState(null);
    const [applications, setApplications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [appsLoading, setAppsLoading] = useState(false);

    useEffect(() => {
        api.get('/recruitment', { params: { per_page: 100 } })
            .then((r) => setJobs(r.data.jobs || []))
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    const loadApplications = async (jobId) => {
        setSelectedJob(jobId);
        setAppsLoading(true);
        try {
            const { data } = await api.get(`/recruitment/${jobId}/applications`);
            setApplications(data.applications || data || []);
        } catch { setApplications([]); }
        setAppsLoading(false);
    };

    const updateStatus = async (appId, status) => {
        try {
            await api.put(`/applications/${appId}/status`, { status });
            toast.success(`Application ${status}`);
            if (selectedJob) loadApplications(selectedJob);
        } catch { toast.error('Update failed'); }
    };

    const columns = [
        { key: 'applicant', label: 'Applicant', render: (row) => row.user?.full_name || row.applicant_name || `User #${row.user_id}` },
        { key: 'status', label: 'Status', render: (row) => <span className={statusStyles[row.status] || 'badge-gray'}>{row.status}</span> },
        { key: 'applied_at', label: 'Applied', render: (row) => row.applied_at ? new Date(row.applied_at).toLocaleDateString() : '-' },
        {
            key: 'actions', label: 'Actions', render: (row) => (
                <div className="flex gap-1">
                    <button onClick={() => updateStatus(row.id, 'shortlisted')} className="text-xs px-2 py-1 rounded bg-green-100 text-green-700 hover:bg-green-200">Shortlist</button>
                    <button onClick={() => updateStatus(row.id, 'rejected')} className="text-xs px-2 py-1 rounded bg-red-100 text-red-700 hover:bg-red-200">Reject</button>
                </div>
            )
        },
    ];

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-3">
                <Link to="/recruitment" className="btn-ghost text-sm"><FiArrowLeft className="w-4 h-4" /></Link>
                <h1 className="page-title">HR Dashboard</h1>
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
                {/* Job List Sidebar */}
                <div className="card divide-y divide-gray-100">
                    <div className="p-4"><h3 className="section-title">Job Postings</h3></div>
                    {loading ? (
                        <div className="p-4 text-center"><div className="animate-spin rounded-full h-6 w-6 border-2 border-nea-blue border-t-transparent mx-auto" /></div>
                    ) : jobs.length === 0 ? (
                        <div className="p-4 text-sm text-gray-400">No job postings</div>
                    ) : (
                        jobs.map((job) => (
                            <button
                                key={job.id}
                                onClick={() => loadApplications(job.id)}
                                className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors ${selectedJob === job.id ? 'bg-nea-blue/5 border-l-2 border-nea-blue' : ''
                                    }`}
                            >
                                <p className="text-sm font-medium text-gray-800">{job.title}</p>
                                <p className="text-xs text-gray-400">{job.department} • {job.status}</p>
                            </button>
                        ))
                    )}
                </div>

                {/* Applications */}
                <div className="lg:col-span-2">
                    {selectedJob ? (
                        <DataTable columns={columns} data={applications} loading={appsLoading} emptyMessage="No applications for this position." />
                    ) : (
                        <div className="card p-12 text-center text-gray-400">
                            <div className="text-5xl mb-3">📋</div>
                            <p>Select a job posting to view applications</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
