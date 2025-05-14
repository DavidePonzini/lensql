import { useState } from 'react';

function useAuth() {
    const [accessToken, setAccessToken] = useState(sessionStorage.getItem('access_token'));
    const [refreshToken, setRefreshToken] = useState(sessionStorage.getItem('refresh_token'));

    // Save tokens in sessionStorage and state
    function saveTokens(access, refresh) {
        sessionStorage.setItem('access_token', access);
        sessionStorage.setItem('refresh_token', refresh);
        setAccessToken(access);
        setRefreshToken(refresh);
    };

    // Logout function
    function logout () {
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('refresh_token');
        setAccessToken(null);
        setRefreshToken(null);
    };

    // Refresh token when needed
    async function refreshAccessToken() {
        if (!refreshToken) {
            logout();
            throw new Error('No refresh token available.');
        }

        const response = await fetch('/api/refresh', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + refreshToken,
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (data.success) {
            sessionStorage.setItem('access_token', data.access_token);
            setAccessToken(data.access_token);
            return data.access_token;
        } else {
            logout();
            throw new Error('Refresh token expired or invalid.');
        }
    };

    // API request wrapper with auto-refresh
    async function apiRequest(endpoint, method = 'GET', body = null) {
        let token = accessToken;

        let response = await fetch(endpoint, {
            method,
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json',
            },
            body: body ? JSON.stringify(body) : null,
        });

        if (response.status === 401) {
            try {
                token = await refreshAccessToken();
                response = await fetch(endpoint, {
                    method,
                    headers: {
                        'Authorization': 'Bearer ' + token,
                        'Content-Type': 'application/json',
                    },
                    body: body ? JSON.stringify(body) : null,
                });
            } catch (err) {
                console.error('Session expired, logging out.');
                logout();
                throw err;
            }
        }

        return response.json();
    };

    return {
        isLoggedIn: !!accessToken,
        saveTokens,
        logout,
        apiRequest,
    };
}

export default useAuth;