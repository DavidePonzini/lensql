import { createContext, useContext, useState, useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

const AuthContext = createContext();

class RequestSizeError extends Error {
    constructor(size, maxSize) {
        super('Request size exceeds the maximum limit.');
        this.size = size;
        this.maxSize = maxSize;
    }
}

function AuthProvider({ children }) {
    const { i18n } = useTranslation();

    const MAX_REQUEST_SIZE = 1024 * 1024 * 20;

    const hasAccessCookie = typeof document !== 'undefined' && document.cookie.includes('access_token_cookie=');
    const [isAuthenticated, setIsAuthenticated] = useState(
        sessionStorage.getItem('is_authenticated') === 'true' || hasAccessCookie
    );

    const logout = useCallback(() => {
        const url = window.location?.pathname + window.location?.search + window.location?.hash;

        // log the logout event while the cookie is still present
        fetch('/api/navigation/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ url, event: 'LOGOUT' }),
            keepalive: true,
        }).catch(() => {});

        fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include',
        }).catch(() => {
            // ignore network errors on logout
        }).finally(() => {
            sessionStorage.removeItem('is_authenticated');
            setIsAuthenticated(false);
        });
    }, []);

    const refreshAccessToken = useCallback(async () => {
        const response = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        const data = await response.json();
        if (data.success) {
            setIsAuthenticated(true);
            sessionStorage.setItem('is_authenticated', 'true');
            return true;
        } else {
            logout();
            throw new Error('Refresh token invalid.');
        }
    }, [logout]);

    const apiRequest = useCallback(async (endpoint, method = 'GET', body = null, { stream = false } = {}) => {
        async function doRequest() {
            let content = body ? JSON.stringify(body) : null;
            if (content && content.length > MAX_REQUEST_SIZE) {
                throw new RequestSizeError(content.length, MAX_REQUEST_SIZE);
            }

            return fetch(endpoint, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-Language': i18n.language,
                },
                credentials: 'include',
                body: content,
            });
        }

        let response = await doRequest();

        if (response.status === 401) {
            await refreshAccessToken();
            response = await doRequest();
        }

        if (!response.ok) {
            const error = new Error(`HTTP error ${response.status}`);
            error.status = response.status;
            throw error;
        }

        return stream ? response.body : response.json();
    }, [refreshAccessToken, MAX_REQUEST_SIZE, i18n.language]);

    const saveTokens = useCallback(() => {
        sessionStorage.setItem('is_authenticated', 'true');
        setIsAuthenticated(true);
    }, []);

    const value = useMemo(() => ({
        isLoggedIn: isAuthenticated,
        saveTokens,
        logout,
        apiRequest,
    }), [isAuthenticated, apiRequest, logout, saveTokens]);

    return (
        <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );
}

function useAuth() {
    return useContext(AuthContext);
}

export { AuthProvider, useAuth, RequestSizeError };
export default useAuth;
