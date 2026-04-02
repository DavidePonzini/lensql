import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import useAuth from './useAuth';

export function useUserNavigationTracking() {
    const { apiRequest, isLoggedIn } = useAuth();

    const location = useLocation();
    const lastPathRef = useRef(null);
    const visibleRef = useRef(document.visibilityState === 'visible');

    // TODO: use cookie-based authetication for logging navigation events. Adapt the code and the api endpoint. Change the other endpoints to use cookie-based auth as well. Create a cookie notice/policy page.
    function sendEvent(url, event) {

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
        if (!isLoggedIn) {
            return;
        }

        const url = location.pathname + location.search + location.hash;

        if (lastPathRef.current !== url) {
            lastPathRef.current = url;

            sendEvent(url, 'PAGE_VISIT');
        }
    }, [location, isLoggedIn]);

    // Focus / unfocus / close tracking
    useEffect(() => {
        if (!isLoggedIn) {
            return;
        }

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
}