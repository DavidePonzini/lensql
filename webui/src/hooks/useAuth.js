import { createContext, Fragment, useContext, useState, useCallback, useEffect, useMemo, useRef } from 'react';
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

    const [isAuthenticated, setIsAuthenticated] = useState(null);
    const sessionVersion = useRef(0);
    const version = sessionVersion.current;
    const pendingRefresh = useRef(null);
    const pendingLogout = useRef(null);

    const endSession = useCallback(() => {
        sessionVersion.current += 1;
        sessionStorage.removeItem('hasProvidedFeedback');
        setIsAuthenticated(false);
    }, []);

    const logout = useCallback(() => {
        if (pendingLogout.current) return pendingLogout.current;

        const url = window.location?.pathname + window.location?.search + window.location?.hash;

        // log the logout event while the cookie is still present
        fetch('/api/navigation/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ url, event: 'LOGOUT' }),
            keepalive: true,
        }).catch(() => {});

        const operation = (async () => {
            // Apply the logout cookie headers after any refresh already in flight.
            await pendingRefresh.current?.catch(() => {});
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include',
            });
            if (!response.ok) throw new Error('Logout failed.');
            endSession();
        })().finally(() => {
            pendingLogout.current = null;
        });
        pendingLogout.current = operation;
        return operation;
    }, [endSession]);

    const refreshAccessToken = useCallback(() => {
        if (pendingRefresh.current) return pendingRefresh.current;

        const operation = fetch('/api/auth/refresh', {
            method: 'POST',
            credentials: 'include',
        }).then(async response => {
            if (response.status === 401 || response.status === 422) return false;
            if (!response.ok) throw new Error('Session refresh failed.');
            return (await response.json()).success === true;
        }).finally(() => {
            pendingRefresh.current = null;
        });
        pendingRefresh.current = operation;
        return operation;
    }, []);

    useEffect(() => {
        let active = true;
        sessionStorage.removeItem('is_authenticated');
        refreshAccessToken().catch(() => false).then(authenticated => {
            if (active) setIsAuthenticated(authenticated);
        });
        return () => { active = false; };
    }, [refreshAccessToken]);

    const apiRequest = useCallback(async (endpoint, method = 'GET', body = null, { stream = false } = {}) => {
        function checkSession() {
            if (version !== sessionVersion.current || pendingLogout.current) {
                throw new Error('Session changed.');
            }
        }

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

        checkSession();
        let response = await doRequest();
        checkSession();

        if (response.status === 401) {
            const refreshed = await refreshAccessToken();
            checkSession();
            if (!refreshed) {
                endSession();
                throw new Error('Session expired.');
            }
            response = await doRequest();
            checkSession();
        }

        if (!response.ok) {
            const error = new Error(`HTTP error ${response.status}`);
            error.status = response.status;
            throw error;
        }

        const result = stream ? response.body : await response.json();
        checkSession();
        return result;
    }, [refreshAccessToken, endSession, version, MAX_REQUEST_SIZE, i18n.language]);

    const saveTokens = useCallback(() => {
        sessionVersion.current += 1;
        sessionStorage.removeItem('hasProvidedFeedback');
        setIsAuthenticated(true);
    }, []);

    const value = useMemo(() => ({
        isLoggedIn: isAuthenticated,
        saveTokens,
        logout,
        apiRequest,
    }), [isAuthenticated, apiRequest, logout, saveTokens]);

    return (
        <AuthContext.Provider value={value}>
            {isAuthenticated !== null && (
                <Fragment key={String(isAuthenticated)}>{children}</Fragment>
            )}
        </AuthContext.Provider>
    );
}

function useAuth() {
    return useContext(AuthContext);
}

export { AuthProvider, useAuth, RequestSizeError };
export default useAuth;
