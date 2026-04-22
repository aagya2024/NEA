/**
 * Auth Context
 * =============
 * Provides authentication state and methods to the entire app:
 * - login / logout
 * - current user object (with permissions)
 * - loading state while checking auth
 * - permission helper: hasPermission(key)
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Fetch current user profile from /auth/me
    const fetchUser = useCallback(async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                setUser(null);
                setLoading(false);
                return;
            }
            const { data } = await api.get('/auth/me');
            setUser(data);
        } catch {
            setUser(null);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUser();
    }, [fetchUser]);

    const login = async (email, password) => {
        const { data } = await api.post('/auth/login', { email, password });
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        await fetchUser();
        return data;
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    };

    const hasPermission = (permKey) => {
        if (!user) return false;
        // Super Admin bypass
        if (user.role_name === 'Super Admin') return true;
        return user.permissions?.includes(permKey);
    };

    const value = {
        user,
        loading,
        login,
        logout,
        hasPermission,
        isAuthenticated: !!user,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
}
