import { useState, useEffect, useCallback } from 'react';
import { getXpStats } from '../constants/Gamification';
import { useAuth } from './useAuth';

function useUserInfo() {
    const { apiRequest, logout, accessToken } = useAuth();
    const [userInfo, setUserInfo] = useState(null);

    const loadUserInfo = useCallback(async () => {
        if (!accessToken) return;

        try {
            const data = await apiRequest('/api/users/info');

            const xp = getXpStats(data.xp);
            setUserInfo({
                username: data.username,
                isAdmin: data.is_admin,
                coins: data.coins,
                xpTotal: data.xp,
                xp: xp.current,
                xpToNextLevel: xp.next,
                level: xp.level,
            });
        } catch (err) {
            console.error('Failed to load user info.', err);
            logout();
        }
    }, [accessToken, apiRequest, logout]);

    useEffect(() => {
        if (accessToken && !userInfo) {
            loadUserInfo();
        }
    }, [accessToken, userInfo, loadUserInfo]);

    const incrementStats = useCallback((coins = 0, experience = 0) => {
        setUserInfo(prev => {
            if (!prev) return null;

            const xpTotal = prev.xpTotal + experience;
            const xp = getXpStats(xpTotal);

            const newStats = {
                ...prev,
                coins: prev.coins + coins,
                xpTotal,
                xp: xp.current,
                xpToNextLevel: xp.next,
                level: xp.level,
            };

            console.log('Incremented stats:', newStats);

            return newStats;
        });
    }, []);

    return { userInfo, loadUserInfo, incrementStats };
}

export default useUserInfo;
