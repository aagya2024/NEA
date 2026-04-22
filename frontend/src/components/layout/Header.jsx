/**
 * Header
 * ======
 * Top bar with search, notification dropdown, user dropdown, and sidebar toggle.
 */

import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { FiMenu, FiSearch, FiBell, FiUser, FiLogOut, FiSettings } from 'react-icons/fi';
import api from '../../api/axios';

// Helper: format relative time
function timeAgo(dateStr) {
    if (!dateStr) return '';
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
}

// Priority badge colors
const priorityColors = {
    urgent: 'bg-red-100 text-red-700',
    high: 'bg-orange-100 text-orange-700',
    normal: 'bg-blue-100 text-blue-700',
    low: 'bg-gray-100 text-gray-600',
};

export default function Header({ onToggleSidebar }) {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    // Dropdown states
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [notifOpen, setNotifOpen] = useState(false);
    const dropdownRef = useRef(null);
    const notifRef = useRef(null);

    // Notification data
    const [notices, setNotices] = useState([]);
    const [hasUnread, setHasUnread] = useState(false);
    const [loadingNotifs, setLoadingNotifs] = useState(false);

    // Close dropdowns on outside click
    useEffect(() => {
        const handler = (e) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setDropdownOpen(false);
            }
            if (notifRef.current && !notifRef.current.contains(e.target)) {
                setNotifOpen(false);
            }
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, []);

    // Fetch recent notices for notifications
    const fetchNotices = async () => {
        setLoadingNotifs(true);
        try {
            const { data } = await api.get('/notices', {
                params: { per_page: 5, active_only: true },
            });
            setNotices(data.notices || []);
            setHasUnread(false); // Mark as read when opened
        } catch (err) {
            console.error('Failed to fetch notices:', err);
            setNotices([]);
        } finally {
            setLoadingNotifs(false);
        }
    };

    // Check for notices on mount to show unread dot
    useEffect(() => {
        const checkNotices = async () => {
            try {
                const { data } = await api.get('/notices', {
                    params: { per_page: 1, active_only: true },
                });
                if (data.total > 0) setHasUnread(true);
            } catch {
                // silently ignore
            }
        };
        checkNotices();
    }, []);

    const handleBellClick = () => {
        const opening = !notifOpen;
        setNotifOpen(opening);
        setDropdownOpen(false);
        if (opening) fetchNotices();
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shrink-0">
            {/* Left: hamburger + search */}
            <div className="flex items-center gap-4">
                <button
                    onClick={onToggleSidebar}
                    className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 transition-colors lg:hidden"
                >
                    <FiMenu className="w-5 h-5" />
                </button>

                <div className="relative hidden sm:block">
                    <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                        type="text"
                        placeholder="Search..."
                        className="pl-10 pr-4 py-2 w-64 bg-gray-50 border border-gray-200 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-nea-blue/30 focus:border-nea-blue transition-all"
                    />
                </div>
            </div>

            {/* Right: notifications + user */}
            <div className="flex items-center gap-3">
                {/* Notification Bell */}
                <div ref={notifRef} className="relative">
                    <button
                        onClick={handleBellClick}
                        className="relative p-2 rounded-lg hover:bg-gray-100 text-gray-600 transition-colors"
                    >
                        <FiBell className="w-5 h-5" />
                        {hasUnread && (
                            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                        )}
                    </button>

                    {notifOpen && (
                        <div className="absolute right-0 top-full mt-2 w-80 bg-white border border-gray-200 rounded-xl shadow-lg z-50 overflow-hidden">
                            {/* Header */}
                            <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                                <h3 className="text-sm font-semibold text-gray-800">Notifications</h3>
                                <span className="text-xs text-gray-400">
                                    {notices.length} recent
                                </span>
                            </div>

                            {/* List */}
                            <div className="max-h-72 overflow-y-auto">
                                {loadingNotifs ? (
                                    <div className="py-8 text-center text-sm text-gray-400">
                                        Loading...
                                    </div>
                                ) : notices.length === 0 ? (
                                    <div className="py-8 text-center">
                                        <FiBell className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                                        <p className="text-sm text-gray-400">No notifications</p>
                                    </div>
                                ) : (
                                    notices.map((notice) => (
                                        <button
                                            key={notice.id}
                                            onClick={() => {
                                                setNotifOpen(false);
                                                navigate('/notices');
                                            }}
                                            className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-50 transition-colors"
                                        >
                                            <div className="flex items-start justify-between gap-2">
                                                <p className="text-sm font-medium text-gray-800 line-clamp-1">
                                                    {notice.title}
                                                </p>
                                                {notice.priority && (
                                                    <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full whitespace-nowrap ${priorityColors[notice.priority] || priorityColors.normal}`}>
                                                        {notice.priority}
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-xs text-gray-400 mt-1">
                                                {timeAgo(notice.created_at)}
                                                {notice.author_name && ` · ${notice.author_name}`}
                                            </p>
                                        </button>
                                    ))
                                )}
                            </div>

                            {/* Footer */}
                            <button
                                onClick={() => {
                                    setNotifOpen(false);
                                    navigate('/notices');
                                }}
                                className="w-full px-4 py-2.5 text-center text-xs font-medium text-nea-blue hover:bg-blue-50 border-t border-gray-100 transition-colors"
                            >
                                View All Notices
                            </button>
                        </div>
                    )}
                </div>

                {/* User Dropdown */}
                <div ref={dropdownRef} className="relative">
                    <button
                        onClick={() => { setDropdownOpen(!dropdownOpen); setNotifOpen(false); }}
                        className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        <div className="w-8 h-8 rounded-full bg-nea-blue text-white flex items-center justify-center text-sm font-semibold">
                            {user?.full_name?.charAt(0) || 'U'}
                        </div>
                        <div className="hidden md:block text-left">
                            <div className="text-sm font-medium text-gray-800">{user?.full_name}</div>
                            <div className="text-[10px] text-gray-400">{user?.role_name}</div>
                        </div>
                    </button>

                    {dropdownOpen && (
                        <div className="absolute right-0 top-full mt-2 w-56 bg-white border border-gray-200 rounded-xl shadow-lg py-2 z-50">
                            <div className="px-4 py-2 border-b border-gray-100">
                                <div className="text-sm font-medium text-gray-800">{user?.full_name}</div>
                                <div className="text-xs text-gray-400">{user?.email}</div>
                            </div>
                            <button
                                onClick={() => { setDropdownOpen(false); navigate('/profile'); }}
                                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                            >
                                <FiUser className="w-4 h-4" /> Profile
                            </button>
                            <button
                                onClick={() => { setDropdownOpen(false); navigate('/admin/system'); }}
                                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                            >
                                <FiSettings className="w-4 h-4" /> Settings
                            </button>
                            <div className="border-t border-gray-100 mt-1 pt-1">
                                <button
                                    onClick={handleLogout}
                                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                                >
                                    <FiLogOut className="w-4 h-4" /> Logout
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}

