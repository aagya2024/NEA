/**
 * App.jsx — Root route configuration.
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Layouts
import DashboardLayout from './components/layout/DashboardLayout';
import ProtectedRoute from './components/common/ProtectedRoute';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';

// News
import NewsList from './pages/news/NewsList';
import NewsDetail from './pages/news/NewsDetail';
import NewsForm from './pages/news/NewsForm';

// Notices
import NoticeList from './pages/notices/NoticeList';
import NoticeDetail from './pages/notices/NoticeDetail';

// Documents
import DocumentList from './pages/documents/DocumentList';

// Forms
import FormList from './pages/forms/FormList';

// Acts
import ActList from './pages/acts/ActList';
import ActDetail from './pages/acts/ActDetail';

// Recruitment
import JobList from './pages/recruitment/JobList';
import JobDetail from './pages/recruitment/JobDetail';
import HRDashboard from './pages/recruitment/HRDashboard';

// Admin
import UserManagement from './pages/admin/UserManagement';
import RoleManagement from './pages/admin/RoleManagement';
import SystemConfig from './pages/admin/SystemConfig';

export default function App() {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-nea-blue border-t-transparent mx-auto" />
                    <p className="text-gray-400 mt-4 text-sm">Loading NEA Intranet…</p>
                </div>
            </div>
        );
    }

    return (
        <Routes>
            {/* Public */}
            <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <Login />} />

            {/* Protected — Dashboard Layout */}
            <Route
                element={
                    <ProtectedRoute>
                        <DashboardLayout />
                    </ProtectedRoute>
                }
            >
                <Route path="/" element={<Dashboard />} />
                <Route path="/profile" element={<Profile />} />

                {/* News */}
                <Route path="/news" element={<NewsList />} />
                <Route path="/news/new" element={<ProtectedRoute permission="create_news"><NewsForm /></ProtectedRoute>} />
                <Route path="/news/:id" element={<NewsDetail />} />
                <Route path="/news/:id/edit" element={<ProtectedRoute permission="edit_news"><NewsForm /></ProtectedRoute>} />

                {/* Notices */}
                <Route path="/notices" element={<NoticeList />} />
                <Route path="/notices/new" element={<ProtectedRoute permission="create_notice"><NoticeDetail /></ProtectedRoute>} />
                <Route path="/notices/:id" element={<NoticeDetail />} />

                {/* Documents */}
                <Route path="/documents" element={<DocumentList />} />

                {/* Forms */}
                <Route path="/forms" element={<FormList />} />

                {/* Acts */}
                <Route path="/acts" element={<ActList />} />
                <Route path="/acts/new" element={<ProtectedRoute permission="manage_acts"><ActDetail /></ProtectedRoute>} />
                <Route path="/acts/:id" element={<ActDetail />} />

                {/* Recruitment */}
                <Route path="/recruitment" element={<JobList />} />
                <Route path="/recruitment/new" element={<ProtectedRoute permission="manage_recruitment"><JobDetail /></ProtectedRoute>} />
                <Route path="/recruitment/hr" element={<ProtectedRoute permission="manage_recruitment"><HRDashboard /></ProtectedRoute>} />
                <Route path="/recruitment/:id" element={<JobDetail />} />

                {/* Admin */}
                <Route path="/admin/users" element={<ProtectedRoute permission="manage_users"><UserManagement /></ProtectedRoute>} />
                <Route path="/admin/roles" element={<ProtectedRoute permission="manage_roles"><RoleManagement /></ProtectedRoute>} />
                <Route path="/admin/system" element={<ProtectedRoute permission="manage_system"><SystemConfig /></ProtectedRoute>} />
            </Route>

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" />} />
        </Routes>
    );
}
