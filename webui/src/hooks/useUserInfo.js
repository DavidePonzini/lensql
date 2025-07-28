import { createContext, useContext, useState, useCallback, useEffect, useMemo } from 'react';
import { getXpStats } from '../constants/Gamification';
import useAuth from './useAuth';

const UserInfoContext = createContext();

function UserInfoProvider({ children }) {
    const { apiRequest, accessToken, logout } = useAuth();

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

    const logoutUser = useCallback(() => {
        setUserInfo(null);
        logout();
    }, [logout]);

    useEffect(() => {
        if (accessToken && !userInfo) {
            loadUserInfo();
        }
    }, [accessToken, userInfo, loadUserInfo]);

    const value = useMemo(() => ({
        userInfo,
        loadUserInfo,
        incrementStats,
        logout: logoutUser,
    }), [userInfo, loadUserInfo, incrementStats, logoutUser]);

    return (
        <UserInfoContext.Provider value={value}>{children}</UserInfoContext.Provider>
    );
}

function useUserInfo() {
    return useContext(UserInfoContext);
}

export { UserInfoProvider, useUserInfo };
export default useUserInfo;
