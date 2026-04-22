/**
 * System Config + Scraper Control (combined admin page)
 */

import { useState, useEffect } from 'react';
import api from '../../api/axios';
import toast from 'react-hot-toast';
import { FiSave, FiRefreshCw, FiGlobe, FiSettings } from 'react-icons/fi';

export default function SystemConfig() {
    const [configs, setConfigs] = useState([]);
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [tab, setTab] = useState('config');
    const [scraping, setScraping] = useState(false);

    useEffect(() => {
        const fetch = async () => {
            try {
                const [configRes, logRes] = await Promise.all([
                    api.get('/system/config').catch(() => ({ data: [] })),
                    api.get('/system/logs', { params: { per_page: 50 } }).catch(() => ({ data: { logs: [] } })),
                ]);
                setConfigs(configRes.data.configs || configRes.data || []);
                setLogs(logRes.data.logs || logRes.data || []);
            } catch { }
            setLoading(false);
        };
        fetch();
    }, []);

    const handleConfigSave = async (key, value) => {
        try {
            await api.put('/system/config', { key, value });
            toast.success(`Updated: ${key}`);
        } catch { toast.error('Save failed'); }
    };

    const handleScrape = async () => {
        setScraping(true);
        try {
            await api.post('/scraper/sync');
            toast.success('Scraper sync triggered');
        } catch { toast.error('Scrape failed'); }
        finally { setScraping(false); }
    };

    return (
        <div className="space-y-6">
            <h1 className="page-title">System Administration</h1>

            <div className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit">
                {[{ key: 'config', label: 'Config', icon: FiSettings }, { key: 'scraper', label: 'Scraper', icon: FiGlobe }, { key: 'logs', label: 'Audit Logs', icon: FiRefreshCw }].map((t) => (
                    <button key={t.key} onClick={() => setTab(t.key)} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${tab === t.key ? 'bg-white text-nea-blue shadow-sm' : 'text-gray-500'}`}>
                        <t.icon className="w-4 h-4" />{t.label}
                    </button>
                ))}
            </div>

            {loading && <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" /></div>}

            {!loading && tab === 'config' && (
                <div className="card divide-y divide-gray-100">
                    {configs.length === 0 ? (
                        <div className="p-8 text-center text-gray-400">No configuration entries.</div>
                    ) : configs.map((c) => (
                        <div key={c.id || c.key} className="flex items-center gap-4 p-4">
                            <div className="flex-1"><p className="text-sm font-medium">{c.key}</p></div>
                            <input
                                className="input-field w-64"
                                defaultValue={c.value}
                                onBlur={(e) => { if (e.target.value !== c.value) handleConfigSave(c.key, e.target.value); }}
                            />
                        </div>
                    ))}
                </div>
            )}

            {!loading && tab === 'scraper' && (
                <div className="card p-8 text-center space-y-4">
                    <FiGlobe className="w-16 h-16 mx-auto text-gray-300" />
                    <h3 className="text-lg font-semibold">NEA Website Scraper</h3>
                    <p className="text-sm text-gray-500 max-w-md mx-auto">
                        Trigger a re-sync to fetch latest content from nea.org.np. This will update news, notices, and other public content.
                    </p>
                    <button onClick={handleScrape} disabled={scraping} className="btn-primary">
                        <FiRefreshCw className={`w-4 h-4 ${scraping ? 'animate-spin' : ''}`} />
                        {scraping ? 'Syncing...' : 'Trigger Sync'}
                    </button>
                </div>
            )}

            {!loading && tab === 'logs' && (
                <div className="card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead><tr className="bg-gray-50 border-b"><th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Time</th><th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">User</th><th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Action</th><th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Resource</th><th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Details</th></tr></thead>
                            <tbody className="divide-y divide-gray-50">
                                {logs.length === 0 ? (
                                    <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">No audit logs.</td></tr>
                                ) : logs.map((log, i) => (
                                    <tr key={log.id || i} className="hover:bg-gray-50">
                                        <td className="px-4 py-2.5 text-xs text-gray-400">{log.created_at ? new Date(log.created_at).toLocaleString() : '-'}</td>
                                        <td className="px-4 py-2.5">{log.user_id || '-'}</td>
                                        <td className="px-4 py-2.5"><span className="badge-blue">{log.action}</span></td>
                                        <td className="px-4 py-2.5">{log.resource || '-'}</td>
                                        <td className="px-4 py-2.5 text-xs text-gray-500">{log.details || '-'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
