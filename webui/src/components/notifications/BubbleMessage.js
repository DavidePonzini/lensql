import { useEffect, useState } from 'react';

function BubbleMessage({ children, className = '', style = {}, duration = 3000, visible, onHide }) {
    const [fading, setFading] = useState(false);

    useEffect(() => {
        if (!visible) return;

        setFading(false);
        const fadeTimeout = setTimeout(() => setFading(true), duration - 500);
        const hideTimeout = setTimeout(() => {
            setFading(false);
            onHide?.();
        }, duration);

        return () => {
            clearTimeout(fadeTimeout);
            clearTimeout(hideTimeout);
        };
    }, [visible, duration, onHide]);

    if (!visible) return null;

    const baseStyle = {
        fontWeight: 500,
        fontSize: '0.95rem',
        transition: 'opacity 0.5s ease, transform 0.5s ease',
        opacity: fading ? 0 : 1,
        transform: fading ? 'translateY(-10px)' : 'translateY(0)',
        display: 'inline-block',
    };

    return (
        <div style={{ ...baseStyle, ...style }} className={className}>
            {children}
        </div>
    );
}

export default BubbleMessage;
