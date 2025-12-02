import { Link, NavLink } from 'react-router-dom';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';
import useUserInfo from '../../hooks/useUserInfo';

import AppName from '../AppName';
import LanguageSelectionButton from './LanguageSelectionButton';
import GamificationStats from './GamificationStats';

import './Navbar.css';

function Navbar() {
    const { t } = useTranslation();

    const { isLoggedIn } = useAuth();
    const { userInfo, loadingUserInfo, logout } = useUserInfo();
    const [isDropdownOpen, setDropdownOpen] = useState(false);

    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-light sticky-top">
            <div className="container-fluid d-flex justify-content-between align-items-center">
                {/* Brand on the left */}
                <Link className="navbar-brand me-3" to="/"><AppName /></Link>

                {/* Toggler button on the far right */}
                <button
                    className="navbar-toggler ms-3 order-3"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarSupportedContent"
                    aria-controls="navbarSupportedContent"
                    aria-expanded="false"
                    aria-label="Toggle navigation"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>

                {/* Right-side content, always visible */}
                <div className='d-lg-flex align-items-center order-2'>
                    <div className="navbar-text d-flex align-items-center">
                        {isLoggedIn ? (
                            <>
                                <span className="mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title={t('components.navbar.nav.username_tooltip')}>
                                    <i className="fa-solid fa-user" />
                                    <span>{loadingUserInfo ? t('components.navbar.nav.loading') : userInfo?.username || t('components.navbar.nav.unknown')}</span>
                                </span>

                                {userInfo?.isTeacher && (
                                    <i className="fa fa-chalkboard-teacher text-primary mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title={t('components.navbar.nav.teacher_tooltip')}></i>
                                )}

                                {userInfo?.isAdmin && (
                                    <i className="fa fa-shield-alt text-danger mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title={t('components.navbar.nav.admin_tooltip')}></i>
                                )}

                                <div className="vr mx-1" />

                                <GamificationStats userInfo={userInfo} />

                                <LanguageSelectionButton className="mx-1" />

                                <button className="btn btn-outline-danger mx-1" type="button" onClick={logout}>
                                    {t('components.navbar.nav.logout')}
                                </button>
                            </>
                        ) : (
                            <>
                                <LanguageSelectionButton />

                                <NavLink to="/login" className="btn btn-primary mx-1 text-light">
                                    <i className="fa fa-sign-in-alt"></i> {t('components.navbar.nav.login')}
                                </NavLink>

                                <NavLink to="/register" className="btn btn-secondary mx-1 text-light">
                                    <i className="fa fa-user-plus"></i> {t('components.navbar.nav.register')}
                                </NavLink>
                            </>
                        )}
                    </div>
                </div>

                {/* Collapsible content in the middle */}
                <div className="collapse navbar-collapse" id="navbarSupportedContent">
                    <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                        <li className="nav-item">
                            <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/" end>
                                {t('components.navbar.nav.home')}
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
                                        <i className="fa-solid fa-user-circle"></i> {t('components.navbar.nav.profile')}
                                    </NavLink>
                                    <ul className={`dropdown-menu ${isDropdownOpen ? 'show' : ''}`}>
                                        <li onClick={() => setDropdownOpen(false)}>
                                            <NavLink className="dropdown-item" to="/profile">
                                                <i className="fa-solid fa-user"></i> {t('components.navbar.nav.view_profile')}
                                            </NavLink>
                                        </li>
                                        <li onClick={() => setDropdownOpen(false)}>
                                            <NavLink className="dropdown-item" to="/learning">
                                                <i className="fa-solid fa-chart-line"></i> {t('components.navbar.nav.learning')}
                                            </NavLink>
                                        </li>
                                    </ul>
                                </li>

                                <li className="nav-item">
                                    <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/datasets" end>
                                        <i className="fa-solid fa-database"></i> {t('components.navbar.nav.datasets')}
                                    </NavLink>
                                </li>

                                <li className="nav-item">
                                    <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/datasets/_EXPLORE" end>
                                        <i className="fa-solid fa-magnifying-glass-arrow-right"></i> {t('components.navbar.nav.explore_sql')}
                                    </NavLink>
                                </li>
                            </>
                        )}

                        {userInfo?.isAdmin && (
                            <li className="nav-item">
                                <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/admin">
                                    <i className="fa-solid fa-shield-alt"></i> {t('components.navbar.nav.admin')}
                                </NavLink>
                            </li>
                        )}
                    </ul>
                </div>
            </div>
        </nav>
    );
}

export default Navbar; 
