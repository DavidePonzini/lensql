import { useEffect } from 'react';
import { Tooltip } from 'bootstrap/dist/js/bootstrap.bundle.min';

function useTooltipObserver() {
    useEffect(() => {
        const observer = new MutationObserver(() => {
            document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
                if (!el.getAttribute('data-bs-initialized')) {
                    new Tooltip(el);
                    el.setAttribute('data-bs-initialized', 'true');
                }
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });

        return () => observer.disconnect();
    }, []);
}


export default useTooltipObserver;