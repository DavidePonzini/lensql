import { createContext, useContext, useState, useCallback, useEffect, useMemo, useRef } from 'react';

import useAuth from './useAuth';

import { getXpStats } from './useGamificationData';

const UserInfoContext = createContext();

function UserInfoProvider({ children }) {
    const { apiRequest, isLoggedIn, logout } = useAuth();
    const [userInfo, setUserInfo] = useState(null);
    const [loadingUserInfo, setLoadingUserInfo] = useState(false);
    const loading = useRef(false);

    const loadUserInfo = useCallback(async () => {
        if (!isLoggedIn || loading.current) return;

        loading.current = true;
        setLoadingUserInfo(true);
        try {
            const data = await apiRequest('/api/users/info');
            const xp = getXpStats(data.xp);

            setUserInfo({
                username: data.username,
                isTeacher: data.is_teacher,
                isAdmin: data.is_admin,
                coins: data.coins,
                aiGenerationCredits: data.ai_generation_credits,
                xpTotal: data.xp,
                xp: xp.current,
                xpToNextLevel: xp.next,
                level: xp.level,
            });
        } catch (err) {
            console.error('Failed to load user info.', err);
        } finally {
            loading.current = false;
            setLoadingUserInfo(false);
        }
    }, [isLoggedIn, apiRequest]);

    const incrementStats = useCallback((coins = 0, experience = 0) => {
        setUserInfo(prev => {
            if (!prev) return null;

            const xpTotal = prev.xpTotal + experience;
            const xp = getXpStats(xpTotal);

            return {
                ...prev,
                coins: prev.coins + coins,
                xpTotal,
                xp: xp.current,
                xpToNextLevel: xp.next,
                level: xp.level,
            };
        });
    }, []);

    const setTeacherStatus = useCallback((isTeacher) => {
        setUserInfo(prev => {
            if (!prev) return null;

            return {
                ...prev,
                isTeacher,
            };
        });
    }, []);

    useEffect(() => {
        loadUserInfo();
    }, [loadUserInfo]);

    const value = useMemo(() => ({
        userInfo,
        loadingUserInfo,
        loadUserInfo,
        incrementStats,
        logout,
        setTeacherStatus,
    }), [userInfo, loadingUserInfo, loadUserInfo, incrementStats, logout, setTeacherStatus]);

    return (
        <UserInfoContext.Provider value={value}>{children}</UserInfoContext.Provider>
    );
}

function useUserInfo() {
    return useContext(UserInfoContext);
}

export { UserInfoProvider, useUserInfo };
export default useUserInfo;
