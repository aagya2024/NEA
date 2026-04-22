/**
 * Dashboard
 * =========
 * Overview page with stats cards, recent news, and active notices.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import {
    FiFileText, FiBell, FiFolder, FiBriefcase, FiUsers, FiBook,
} from 'react-icons/fi';

export default function Dashboard() {
    const { user } = useAuth();
    const [news, setNews] = useState([]);
    const [notices, setNotices] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetch = async () => {
            try {
                const [newsRes, noticesRes] = await Promise.all([
                    api.get('/news', { params: { per_page: 5 } }),
                    api.get('/notices', { params: { per_page: 5 } }),
                ]);
                setNews(newsRes.data.news || []);
                setNotices(noticesRes.data.notices || []);
            } catch { /* silent */ }
            setLoading(false);
        };
        fetch();
    }, []);

    const stats = [
        { label: 'News Articles', icon: FiFileText, color: 'bg-blue-500', link: '/news' },
        { label: 'Active Notices', icon: FiBell, color: 'bg-amber-500', link: '/notices' },
        { label: 'Documents', icon: FiFolder, color: 'bg-emerald-500', link: '/documents' },
        { label: 'Open Positions', icon: FiBriefcase, color: 'bg-purple-500', link: '/recruitment' },
        { label: 'Acts & Bylaws', icon: FiBook, color: 'bg-rose-500', link: '/acts' },
        { label: 'Employees', icon: FiUsers, color: 'bg-indigo-500', link: '/admin/users' },
    ];

    return (
        <div className="space-y-6">
            {/* Welcome Banner */}
            <div className="card bg-gradient-to-r from-nea-blue to-nea-blue-light p-6 text-white">
                <h1 className="text-2xl font-bold text-white">Welcome back, {user?.full_name}!</h1>
                <p className="text-white/70 mt-1 text-sm">
                    NEA Intranet Portal — {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {stats.map(({ label, icon: Icon, color, link }) => (
                    <Link key={label} to={link} className="card p-4 hover:shadow-md transition-shadow group">
                        <div className={`w-10 h-10 ${color} rounded-lg flex items-center justify-center mb-3`}>
                            <Icon className="w-5 h-5 text-white" />
                        </div>
                        <p className="text-xs text-gray-500 group-hover:text-nea-blue transition-colors">{label}</p>
                    </Link>
                ))}
            </div>

            {/* Content Grid */}
            <div className="grid lg:grid-cols-2 gap-6">
                {/* Recent News */}
                <div className="card">
                    <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
                        <h2 className="section-title">Recent News</h2>
                        <Link to="/news" className="text-xs text-nea-blue hover:underline">View all →</Link>
                    </div>
                    <div className="divide-y divide-gray-50">
                        {loading ? (
                            <div className="p-8 text-center"><div className="animate-spin rounded-full h-6 w-6 border-2 border-nea-blue border-t-transparent mx-auto" /></div>
                        ) : news.length === 0 ? (
                            <div className="p-6 text-center text-sm text-gray-400">No news articles yet.</div>
                        ) : (
                            news.map((item) => (
                                <Link
                                    key={item.id}
                                    to={`/news/${item.id}`}
                                    className="block px-5 py-3 hover:bg-gray-50 transition-colors"
                                >
                                    <p className="text-sm font-medium text-gray-800 line-clamp-1">{item.title}</p>
                                    <p className="text-xs text-gray-400 mt-0.5">
                                        {item.category && <span className="badge-blue mr-2">{item.category}</span>}
                                        {item.published_at && new Date(item.published_at).toLocaleDateString()}
                                    </p>
                                </Link>
                            ))
                        )}
                    </div>
                </div>

                {/* Active Notices */}
                <div className="card">
                    <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
                        <h2 className="section-title">Active Notices</h2>
                        <Link to="/notices" className="text-xs text-nea-blue hover:underline">View all →</Link>
                    </div>
                    <div className="divide-y divide-gray-50">
                        {loading ? (
                            <div className="p-8 text-center"><div className="animate-spin rounded-full h-6 w-6 border-2 border-nea-blue border-t-transparent mx-auto" /></div>
                        ) : notices.length === 0 ? (
                            <div className="p-6 text-center text-sm text-gray-400">No active notices.</div>
                        ) : (
                            notices.map((item) => (
                                <Link
                                    key={item.id}
                                    to={`/notices/${item.id}`}
                                    className="block px-5 py-3 hover:bg-gray-50 transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        {item.priority === 'high' && <span className="w-2 h-2 bg-red-500 rounded-full" />}
                                        {item.priority === 'medium' && <span className="w-2 h-2 bg-amber-500 rounded-full" />}
                                        <p className="text-sm font-medium text-gray-800 line-clamp-1">{item.title}</p>
                                    </div>
                                    <p className="text-xs text-gray-400 mt-0.5">
                                        {item.notice_type && <span className="badge-gray mr-2">{item.notice_type}</span>}
                                        {item.expires_at && `Expires: ${new Date(item.expires_at).toLocaleDateString()}`}
                                    </p>
                                </Link>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
