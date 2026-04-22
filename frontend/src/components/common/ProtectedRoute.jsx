/**
 * ProtectedRoute
 * ==============
 * Wraps routes that require authentication and optionally a specific permission.
 * - If not authenticated → redirect to /login
 * - If authenticated but missing required permission → show Access Denied
 */

import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function ProtectedRoute({ children, permission }) {
    const { isAuthenticated, loading, hasPermission } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-nea-blue border-t-transparent" />
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (permission && !hasPermission(permission)) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <div className="text-6xl mb-4">🔒</div>
                    <h1 className="text-2xl font-bold text-gray-800 mb-2">Access Denied</h1>
                    <p className="text-gray-500">You do not have permission to access this page.</p>
                </div>
            </div>
        );
    }

    return children;
}
