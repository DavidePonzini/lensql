import { useEffect, useRef, useState } from 'react';

function ObservedOnce({ onFirstVisible, threshold = 0.1, children}) {
    const ref = useRef(null);
    const [hasBeenInView, setHasBeenInView] = useState(false);

    useEffect(() => {
        if (hasBeenInView)
            return;

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setHasBeenInView(true);
                    onFirstVisible?.();
                    observer.disconnect();
                }
            },
            { threshold }
        );

        if (ref.current) {
            observer.observe(ref.current);
        }

        return () => observer.disconnect();
    }, [hasBeenInView, onFirstVisible, threshold]);

    return (
        <div ref={ref}>
            {children}
        </div>
    );
}

export default ObservedOnce;