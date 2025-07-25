import { NavLink } from 'react-router-dom';
import { useState } from 'react';
import AppName from '../AppName';
import useAuth from '../../hooks/useAuth';

import './Navbar.css';

import GamificationStats from './GamificationStats';


function Navbar() {
    const { isLoggedIn, logout, userInfo, loadingUser } = useAuth();
    const [isDropdownOpen, setDropdownOpen] = useState(false);

    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-light sticky-top">
            <div className="container-fluid">
                <a className="navbar-brand" href="/"><AppName /></a>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>

                <div className="collapse navbar-collapse" id="navbarSupportedContent">
                    <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                        <li className="nav-item">
                            <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/" end>
                                Home
                            </NavLink>
                        </li>

                        {isLoggedIn && (
                            <>
                                <li
                                    className={`nav-item dropdown ${isDropdownOpen ? 'show' : ''}`}
                                    onMouseEnter={() => setDropdownOpen(true)}
                                    onMouseLeave={() => setDropdownOpen(false)}
                                >
                                    <NavLink
                                        className={`nav-link dropdown-toggle ${isDropdownOpen ? 'active' : ''}`}
                                        to="/profile"
                                        onClick={() => setDropdownOpen(false)}
                                        aria-expanded={isDropdownOpen ? 'true' : 'false'}
                                    >
                                        <i className="fa-solid fa-user-circle"></i> Profile
                                    </NavLink>
                                    <ul className={`dropdown-menu ${isDropdownOpen ? 'show' : ''}`}>
                                        <li onClick={() => setDropdownOpen(false)}>
                                            <NavLink className="dropdown-item" to="/profile">
                                                <i className="fa-solid fa-user"></i> View Profile
                                            </NavLink>
                                        </li>
                                        <li onClick={() => setDropdownOpen(false)}>
                                            <NavLink className="dropdown-item" to="/learning">
                                                <i className="fa-solid fa-chart-line"></i> Learning Insights
                                            </NavLink>
                                        </li>
                                    </ul>
                                </li>

                                <li className="nav-item">
                                    <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/classes" end>
                                        <i className="fa-solid fa-tasks"></i> Courses
                                    </NavLink>
                                </li>
                            </>
                        )}

                        {userInfo?.isAdmin && (
                            <li className="nav-item">
                                <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/admin">
                                    <i className="fa-solid fa-shield-alt"></i> Admin
                                </NavLink>
                            </li>
                        )}
                    </ul>

                    <div className="navbar-text">
                        {isLoggedIn ? (
                            <>
                                <span className="mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Your username">
                                    <i className="fa-solid fa-user" />
                                    <span>{loadingUser ? 'Loading...' : userInfo?.username || 'Unknown'}</span>
                                </span>

                                {userInfo?.isAdmin && (
                                    <i className="fa fa-shield-alt text-danger mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Admin"></i>
                                )}

                                <div className="vr mx-1" />

                                <GamificationStats userInfo={userInfo} />

                                <button className="btn btn-outline-danger mx-1" type="button" onClick={logout}>
                                    Logout
                                </button>
                            </>
                        ) : (
                            <>
                                <NavLink to="/login" className="btn btn-primary mx-1 text-light">
                                    <i className="fa fa-sign-in-alt"></i> Login
                                </NavLink>

                                <NavLink to="/register" className="btn btn-secondary mx-1 text-light">
                                    <i className="fa fa-user-plus"></i> Register
                                </NavLink>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
