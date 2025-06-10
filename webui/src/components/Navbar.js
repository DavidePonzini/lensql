import { NavLink, useNavigate } from 'react-router-dom';
import AppName from './AppName';
import useAuth from '../hooks/useAuth';

import './Navbar.css';

function GamificationStats({ userInfo }) {
    return (
        <>
            {userInfo?.level && (
                <span className="mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Level">
                    <i className="fa fa-trophy text-primary" />
                    {userInfo.level}
                </span>
            )}

            {userInfo?.xp && userInfo?.xpToNextLevel && (
                <span className="mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Experience points">
                    <i className="fa fa-star text-info" />
                    {userInfo.xp}/{userInfo.xpToNextLevel}
                </span>
            )}

            {userInfo?.coins && (
                <span className="mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="LensCoins">
                    <i className="fa fa-coins text-warning" />
                    {userInfo.coins}
                </span>
            )}
        </>
    );
}


function Navbar() {
    const navigate = useNavigate();

    const { isLoggedIn, logout, userInfo, loadingUser } = useAuth();

    // TODO placeholder data for testing
    if (userInfo) {
        userInfo.coins = 75;
        userInfo.xp = 1500;
        userInfo.xpToNextLevel = 2000;
        userInfo.level = 5;
    }

    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-light sticky-top">
            <div className="container-fluid">
                <a className="navbar-brand" href="/"><AppName /></a>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>

                <div className="collapse navbar-collapse" id="navbarSupportedContent">
                    <div className="navbar-nav me-auto mb-2 mb-lg-0">
                        <NavLink className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} to="/" end>Home</NavLink>
                        {isLoggedIn && (
                            <>
                                <NavLink className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} to="/profile">
                                    <i className="fa-solid fa-user-circle"></i> Profile
                                </NavLink>

                                <NavLink className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} to="/learning">
                                    <i className="fa-solid fa-chart-line"></i> Learning Insights
                                </NavLink>
                                <NavLink className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} to="/assignments" end>
                                    <i className="fa-solid fa-tasks"></i> Assignments
                                </NavLink>
                            </>
                        )}

                        {userInfo?.isTeacher && (
                            <NavLink className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} to="/assignments/manage">
                                <i className="fa-solid fa-cogs"></i> Manage Assignments
                            </NavLink>
                        )}

                        {userInfo?.isAdmin && (
                            <NavLink className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} to="/admin">
                                <i className="fa-solid fa-shield-alt"></i> Admin
                            </NavLink>
                        )}
                    </div>

                    <div className="navbar-text">
                        {isLoggedIn ? (
                            <>
                                {/* User info */}
                                <span className="mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Your username">
                                    <i className="fa-solid fa-user" />
                                    <span>{loadingUser ? 'Loading...' : userInfo?.username || 'Unknown'}</span>
                                </span>
                                {userInfo?.isAdmin && (
                                    <i className="fa fa-shield-alt text-danger mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Admin"></i>
                                )}
                                {userInfo?.isTeacher && (
                                    <i className="fa fa-chalkboard-teacher text-success mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Teacher"></i>
                                )}

                                <div className='vr mx-1' />

                                <GamificationStats userInfo={userInfo} />

                                <button className="btn btn-outline-danger mx-1" type="button" onClick={logout}>
                                    Logout
                                </button>
                            </>
                        ) : (
                            <button className="btn btn-primary mx-1" type="button" onClick={() => navigate('/login')}>
                                Login
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
