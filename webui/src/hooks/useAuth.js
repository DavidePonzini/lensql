import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext();

function AuthProvider({ children }) {
    const [accessToken, setAccessToken] = useState(sessionStorage.getItem('access_token'));
    const [refreshToken, setRefreshToken] = useState(sessionStorage.getItem('refresh_token'));
    const [userInfo, setUserInfo] = useState(null);
    const [loadingUser, setLoadingUser] = useState(false);

    // Tokens management
    function saveTokens(access, refresh) {
        sessionStorage.setItem('access_token', access);
        sessionStorage.setItem('refresh_token', refresh);
        setAccessToken(access);
        setRefreshToken(refresh);
        setUserInfo(null); // Reset user info on new token
    }

    function logout() {
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('refresh_token');
        setAccessToken(null);
        setRefreshToken(null);
        setUserInfo(null);
    }

    async function refreshAccessToken() {
        if (!refreshToken) {
            logout();
            throw new Error('No refresh token.');
        }

        const response = await fetch('/api/refresh', {
            method: 'POST',
            headers: { 'Authorization': 'Bearer ' + refreshToken, 'Content-Type': 'application/json' },
        });

        const data = await response.json();
        if (data.success) {
            sessionStorage.setItem('access_token', data.access_token);
            setAccessToken(data.access_token);
            return data.access_token;
        } else {
            logout();
            throw new Error('Refresh token invalid.');
        }
    }

    async function apiRequest(endpoint, method = 'GET', body = null) {
        let token = accessToken;
        let response = await fetch(endpoint, {
            method,
            headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
            body: body ? JSON.stringify(body) : null,
        });

        if (response.status === 401) {
            token = await refreshAccessToken();
            response = await fetch(endpoint, {
                method,
                headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
                body: body ? JSON.stringify(body) : null,
            });
        }

        return response.json();
    }

    // Load user info safely and only once if needed
    const loadUserInfo = useCallback(async () => {
        if (!accessToken) return;
        setLoadingUser(true);
        try {
            const response = await apiRequest('/api/me');
            setUserInfo({
                username: response.username,
                isTeacher: response.is_teacher,
                isAdmin: response.is_admin,
            });
        } catch (err) {
            console.error('Failed to load user info.', err);
            logout();
        } finally {
            setLoadingUser(false);
        }
    }, [accessToken]);      // eslint-disable-line react-hooks/exhaustive-deps

    // Auto-load user info on login
    useEffect(() => {
        if (accessToken && !userInfo) {
            loadUserInfo();
        }
    }, [accessToken, userInfo, loadUserInfo]);

    return (
        <AuthContext.Provider value={{
            isLoggedIn: !!accessToken,
            userInfo,
            loadingUser,
            saveTokens,
            logout,
            apiRequest,
            loadUserInfo,
        }}>
            {children}
        </AuthContext.Provider>
    );
}

function useAuth() {
    return useContext(AuthContext);
}

export { AuthProvider, useAuth };
export default useAuth;