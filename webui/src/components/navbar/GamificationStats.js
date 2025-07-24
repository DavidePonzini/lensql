function GamificationStats({ userInfo }) {
    return (
        <>
            <span className="mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Level">
                <i className="fa fa-star text-primary me-1" />
                {userInfo?.level || 0}
            </span>
            <span className="mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Experience points">
                <i className="fa fa-diamond text-info me-1" />
                {userInfo?.xp || 0}/{userInfo?.xpToNextLevel || 0}
            </span>
            <span className="mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="LensCoins">
                <i className="fa fa-coins text-warning me-1" />
                {userInfo?.coins || 0}
            </span>
        </>
    );
}

export default GamificationStats;