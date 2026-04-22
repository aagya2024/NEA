/**
 * Sidebar
 * =======
 * NEA-blue vertical sidebar with navigation links grouped by module.
 * Links are filtered by user permissions.
 */

import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
    FiHome, FiFileText, FiBell, FiFolder, FiClipboard,
    FiBook, FiBriefcase, FiUsers, FiShield, FiSettings,
    FiMessageSquare, FiGlobe,
} from 'react-icons/fi';

const navItems = [
    { to: '/', icon: FiHome, label: 'Dashboard' },
    { to: '/news', icon: FiFileText, label: 'News' },
    { to: '/notices', icon: FiBell, label: 'Notices' },
    { to: '/documents', icon: FiFolder, label: 'Documents' },
    { to: '/forms', icon: FiClipboard, label: 'Forms' },
    { to: '/acts', icon: FiBook, label: 'Acts & Bylaws' },
    { to: '/recruitment', icon: FiBriefcase, label: 'Recruitment' },
    { divider: true, label: 'Administration' },
    { to: '/admin/users', icon: FiUsers, label: 'User Management', permission: 'manage_users' },
    { to: '/admin/roles', icon: FiShield, label: 'Role Management', permission: 'manage_roles' },
    { to: '/admin/system', icon: FiSettings, label: 'System Config', permission: 'manage_system' },
    { to: '/admin/scraper', icon: FiGlobe, label: 'Scraper Control', permission: 'manage_system' },
];

export default function Sidebar({ collapsed, onToggle }) {
    const { hasPermission, user } = useAuth();

    return (
        <aside
            className={`fixed top-0 left-0 h-screen bg-nea-blue text-white flex flex-col z-30 transition-all duration-300 ${collapsed ? 'w-[68px]' : 'w-64'
                }`}
        >
            {/* Logo Area */}
            <div className="h-16 flex items-center gap-3 px-4 border-b border-white/10 shrink-0">
                <div className="w-9 h-9 rounded-lg bg-white/20 flex items-center justify-center shrink-0 p-1">
                    <img src="/nea-logo.png" alt="NEA" className="w-full h-full object-contain" />
                </div>
                {!collapsed && (
                    <div className="overflow-hidden">
                        <div className="text-sm font-bold leading-tight">NEA Intranet</div>
                        <div className="text-[10px] text-white/60">नेपाल विद्युत् प्राधिकरण</div>
                    </div>
                )}
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
                {navItems.map((item, i) => {
                    if (item.divider) {
                        if (collapsed) return null;
                        // Check if any items after this divider are visible
                        const hasVisibleItems = navItems.slice(i + 1).some(
                            (ni) => !ni.divider && (!ni.permission || hasPermission(ni.permission))
                        );
                        if (!hasVisibleItems) return null;
                        return (
                            <div key={item.label} className="pt-4 pb-1 px-3">
                                <span className="text-[10px] uppercase tracking-widest text-white/40 font-semibold">
                                    {item.label}
                                </span>
                            </div>
                        );
                    }

                    // Permission check
                    if (item.permission && !hasPermission(item.permission)) return null;

                    const Icon = item.icon;
                    return (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            end={item.to === '/'}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group ${isActive
                                    ? 'bg-white/20 text-white'
                                    : 'text-white/70 hover:bg-white/10 hover:text-white'
                                }`
                            }
                            title={collapsed ? item.label : undefined}
                        >
                            <Icon className="w-5 h-5 shrink-0" />
                            {!collapsed && <span>{item.label}</span>}
                        </NavLink>
                    );
                })}
            </nav>

            {/* User Role Badge */}
            {!collapsed && user && (
                <div className="p-4 border-t border-white/10">
                    <div className="text-xs text-white/50">Logged in as</div>
                    <div className="text-sm font-medium truncate">{user.full_name}</div>
                    <div className="text-[10px] text-nea-gold font-medium">{user.role_name}</div>
                </div>
            )}

            {/* Toggle Button */}
            <button
                onClick={onToggle}
                className="h-12 flex items-center justify-center border-t border-white/10 hover:bg-white/10 transition-colors"
                title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
                <svg className={`w-5 h-5 transition-transform ${collapsed ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
            </button>
        </aside>
    );
}
