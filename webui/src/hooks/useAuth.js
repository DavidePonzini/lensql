import { createContext, useContext, useState, useCallback, useMemo } from 'react';

const AuthContext = createContext();

class RequestSizeError extends Error {
    constructor(size, maxSize) {
        super('Request size exceeds the maximum limit.');
        this.size = size;
        this.maxSize = maxSize;
    }
}

function AuthProvider({ children }) {
    const MAX_REQUEST_SIZE = 1024 * 1024 * 20;

    const [accessToken, setAccessToken] = useState(sessionStorage.getItem('access_token'));
    const [refreshToken, setRefreshToken] = useState(sessionStorage.getItem('refresh_token'));

    const logout = useCallback(() => {
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('refresh_token');
        setAccessToken(null);
        setRefreshToken(null);
    }, []);

    const refreshAccessToken = useCallback(async () => {
        if (!refreshToken) {
            logout();
            throw new Error('No refresh token.');
        }

        const response = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + refreshToken,
                'Content-Type': 'application/json'
            }
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
    }, [refreshToken, logout]);

    const apiRequest = useCallback(async (endpoint, method = 'GET', body = null, { stream = false } = {}) => {
        let token = accessToken;

        async function doRequest(currentToken) {
            let content = body ? JSON.stringify(body) : null;
            if (content && content.length > MAX_REQUEST_SIZE) {
                throw new RequestSizeError(content.length, MAX_REQUEST_SIZE);
            }

            return fetch(endpoint, {
                method,
                headers: {
                    'Authorization': 'Bearer ' + currentToken,
                    'Content-Type': 'application/json'
                },
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

        return stream ? response.body : response.json();
    }, [accessToken, refreshAccessToken, MAX_REQUEST_SIZE]);

    const saveTokens = useCallback((access, refresh) => {
        sessionStorage.setItem('access_token', access);
        sessionStorage.setItem('refresh_token', refresh);
        setAccessToken(access);
        setRefreshToken(refresh);
    }, []);

    const value = useMemo(() => ({
        isLoggedIn: !!accessToken,
        saveTokens,
        logout,
        apiRequest,
        accessToken,
    }), [accessToken, apiRequest, logout, saveTokens]);

    return (
        <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );
}

function useAuth() {
    return useContext(AuthContext);
}

export { AuthProvider, useAuth, RequestSizeError };
export default useAuth;
