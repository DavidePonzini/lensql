import { useTranslation } from 'react-i18next';

function AchievementBadge({ name, description, icon = '🏅', rank, current, next, textNext }) {
    const { t } = useTranslation();

    const isLocked = rank === 0;
    const progress = Math.min(100, (current / next) * 100);

    function rankColor(r) {
        if (r <= 2) return '#cd7f32';       // bronze
        if (r <= 4) return '#b0b0b0';       // silver
        if (r <= 6) return '#d4af37';       // gold
        if (r <= 8) return '#2ecc71';       // green
        if (r === 9) return '#3498db';      // blue
        return '#9b59b6';                   // purple
    }

    return (
        <div style={{
            border: '1px solid #ddd',
            borderRadius: 16,
            padding: 20,
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            gap: 20,
            backgroundColor: isLocked ? '#f3f3f3' : '#fafafa',
            opacity: isLocked ? 0.65 : 1,
            height: 174
        }}>

            {/* Badge Icon */}
            <div style={{
                width: 72,
                height: 72,
                borderRadius: 12,
                backgroundColor: '#eee',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 36,
                userSelect: 'none',
                filter: isLocked ? 'grayscale(100%)' : 'none'
            }}>
                {isLocked ? '🔒' : icon}
            </div>

            {/* Badge Content */}
            <div style={{ flex: 1 }}>
                {/* Name */}
                <div style={{
                    fontSize: 20,
                    fontWeight: '600',
                    color: isLocked ? '#666' : rankColor(rank)
                }}>
                    {t(name)}
                </div>
                {/* Rank */}
                <div style={{
                    fontSize: 16,
                    color: '#888',
                    marginBottom: 10
                }}>
                    {isLocked ? t('gamification.badges.locked') : t('gamification.badges.rank', { rank })}
                </div>

                {/* Description */}
                <div style={{
                    fontSize: 14,
                    color: isLocked ? '#777' : '#555',
                    marginTop: 10
                }}>
                    {t(description)}
                </div>

                {/* Progress Bar */}
                <div style={{
                    width: '100%',
                    height: 12,
                    borderRadius: 6,
                    backgroundColor: '#e3e3e3',
                    overflow: 'hidden',
                    marginBottom: 6
                }}>
                    <div style={{
                        height: '100%',
                        width: `${progress}%`,
                        backgroundColor: rankColor(rank),
                        transition: 'width 0.3s'
                    }} />
                </div>

                <div style={{
                    fontSize: 13,
                    color: '#444'
                }}>
                    {current} / {next} {isLocked ? t(textNext + '_locked') : t(textNext)}
                </div>
            </div>
        </div >
    );
}

export default AchievementBadge;
