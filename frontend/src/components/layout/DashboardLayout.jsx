/**
 * DashboardLayout
 * ================
 * Main layout wrapper: Sidebar + Header + scrollable content area.
 */

import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import Footer from './Footer';
import ChatWidget from '../chat/ChatWidget';

export default function DashboardLayout() {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    return (
        <div className="min-h-screen flex">
            {/* Sidebar */}
            <Sidebar
                collapsed={sidebarCollapsed}
                onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
            />

            {/* Main content area */}
            <div
                className={`flex flex-col flex-1 transition-all duration-300 ${sidebarCollapsed ? 'ml-[68px]' : 'ml-64'
                    }`}
            >
                <Header onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)} />

                {/* Page Content */}
                <main className="flex-1 p-6 overflow-auto bg-nea-gray">
                    <Outlet />
                </main>

                <Footer />
            </div>

            {/* Floating Chat Widget */}
            <ChatWidget />
        </div>
    );
}
