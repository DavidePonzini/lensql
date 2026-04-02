import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import useAuth from './useAuth';

function useNavigationTracking() {
    const { apiRequest, isLoggedIn } = useAuth();

    const location = useLocation();
    const lastPathRef = useRef(null);
    const visibleRef = useRef(document.visibilityState === 'visible');
    const wasLoggedInRef = useRef(isLoggedIn);

    function sendEvent(url, event, { force = false } = {}) {
        if (!isLoggedIn && !force) return;

        const body = JSON.stringify(
            {
                url,
                event
            }
        );

        // Best effort even during page close/hide
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/api/navigation/log', new Blob([body], { type: 'application/json' }));
            return;
        }

        apiRequest('/api/navigation/log', 'POST', { url, event });
    }

    // Route change tracking
    useEffect(() => {
        const url = location.pathname + location.search + location.hash;

        if (lastPathRef.current !== url) {
            lastPathRef.current = url;

            sendEvent(url, 'VISIT');
        }
    }, [location, isLoggedIn]);

    // Focus / unfocus / close tracking
    useEffect(() => {
        function handleVisibilityChange() {
            const url = window.location.pathname + window.location.search + window.location.hash;

            if (document.visibilityState === 'hidden' && visibleRef.current) {
                visibleRef.current = false;

                sendEvent(url, 'UNFOCUS');
            } else if (document.visibilityState === 'visible' && !visibleRef.current) {
                visibleRef.current = true;

                sendEvent(url, 'FOCUS');
            }
        }

        function handlePageHide() {
            const url = window.location.pathname + window.location.search + window.location.hash;

            sendEvent(url, 'CLOSE');
        }

        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('pagehide', handlePageHide);

        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('pagehide', handlePageHide);
        };
    }, [isLoggedIn]);

    // Login / logout tracking
    useEffect(() => {
        const url = window.location.pathname + window.location.search + window.location.hash;

        if (isLoggedIn && !wasLoggedInRef.current) {
            sendEvent(url, 'LOGIN', { force: true });
        } else if (!isLoggedIn && wasLoggedInRef.current) {
            sendEvent(url, 'LOGOUT', { force: true });
        }

        wasLoggedInRef.current = isLoggedIn;
    }, [isLoggedIn]);
}

export default useNavigationTracking;
