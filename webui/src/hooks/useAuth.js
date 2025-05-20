import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext();

class RequestSizeError extends Error {
    constructor(size, maxSize) {
        super('Request size exceeds the maximum limit.');
        this.size = size;
        this.maxSize = maxSize;
    }
}


function AuthProvider({ children }) {
    const MAX_REQUEST_SIZE = 1024 * 1000; // a bit less than 1MB

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

    async function apiRequest(endpoint, method = 'GET', body = null, { stream = false } = {}) {
        let token = accessToken;

        async function doRequest(currentToken) {
            let content = body ? JSON.stringify(body) : null;
            if (content && content.length > MAX_REQUEST_SIZE) {
                throw new RequestSizeError(content.length, MAX_REQUEST_SIZE);
            }

            return fetch(endpoint, {
                method,
                headers: { 'Authorization': 'Bearer ' + currentToken, 'Content-Type': 'application/json' },
                body: content,
            });
        }

        let response = await doRequest(token);

        if (response.status === 401) {
            token = await refreshAccessToken();
            response = await doRequest(token);
        }

        if (!response.ok) {
            const error = new Error(`HTTP error ${response.status}`);
            error.status = response.status;
            throw error;
        }

        if (stream) {
            if (!response.body) {
                throw new Error('No response body (streaming not supported)');
            }
            return response.body; // Return ReadableStream for caller to handle
        } else {
            return response.json(); // Standard JSON handling
        }
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

export { AuthProvider, useAuth, RequestSizeError };
export default useAuth;