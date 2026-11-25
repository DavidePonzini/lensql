import { fireEvent, render, screen, within } from '@testing-library/react';
import { useEffect, useState } from 'react';

import { AuthProvider, useAuth } from './useAuth';

jest.mock('react-i18next', () => ({
    useTranslation: () => ({ i18n: { language: 'en' } }),
}));

function Account() {
    const { isLoggedIn, saveTokens, logout, apiRequest } = useAuth();
    const [username, setUsername] = useState('');

    useEffect(() => {
        if (isLoggedIn) apiRequest('/api/users/info').then(data => setUsername(data.username));
    }, [isLoggedIn, apiRequest]);

    return isLoggedIn ? (
        <section aria-label="Account">
            <span>{username}</span>
            <button onClick={logout}>Sign out</button>
        </section>
    ) : (
        <button onClick={saveTokens}>Sign in</button>
    );
}

test('restores a browser session and clears account state when switching users', async () => {
    let firstAccount = true;
    let finishSecondProfile;
    const previousFetch = global.fetch;
    global.fetch = jest.fn(endpoint => {
        switch (endpoint) {
            case '/api/auth/refresh':
            case '/api/navigation/log':
                return Promise.resolve({ ok: true, json: async () => ({ success: true }) });
            case '/api/auth/logout':
                firstAccount = false;
                return Promise.resolve({ ok: true });
            case '/api/users/info':
                if (firstAccount) {
                    return Promise.resolve({ ok: true, json: async () => ({ username: 'alice' }) });
                }
                return new Promise(resolve => {
                    finishSecondProfile = () => resolve({ ok: true, json: async () => ({ username: 'bob' }) });
                });
            default:
                throw new Error(`Unexpected request to ${endpoint}`);
        }
    });

    try {
        sessionStorage.clear();
        render(<AuthProvider><Account /></AuthProvider>);
        await screen.findByText('alice');

        fireEvent.click(screen.getByRole('button', { name: 'Sign out' }));
        fireEvent.click(await screen.findByRole('button', { name: 'Sign in' }));

        const secondAccount = within(await screen.findByRole('region', { name: 'Account' }));
        expect(secondAccount.queryByText('alice')).toBeNull();
        finishSecondProfile();
        await secondAccount.findByText('bob');
    } finally {
        global.fetch = previousFetch;
    }
});
