import { Link, NavLink } from 'react-router-dom';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import NavDropdown from 'react-bootstrap/NavDropdown';

import useAuth from '../../hooks/useAuth';
import useUserInfo from '../../hooks/useUserInfo';

import AppName from '../AppName';
import LanguageSelectionButton from './LanguageSelectionButton';
import GamificationStats from './GamificationStats';

import './Navbar.css';

function NavbarDropdown({ id, icon, title, children }) {
    const [isOpen, setOpen] = useState(false);

    return (
        <NavDropdown
            as="li"
            id={id}
            title={<><i className={icon} aria-hidden="true" /> {title}</>}
            show={isOpen}
            onToggle={setOpen}
            onMouseEnter={() => setOpen(true)}
            onMouseLeave={() => setOpen(false)}
        >
            {children}
        </NavDropdown>
    );
}

function Navbar() {
    const { t } = useTranslation();

    const { isLoggedIn } = useAuth();
    const { userInfo, loadingUserInfo, logout } = useUserInfo();
    const [logoutError, setLogoutError] = useState(false);

    async function handleLogout() {
        setLogoutError(false);
        try {
            await logout();
        } catch {
            setLogoutError(true);
        }
    }

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
                <div className='d-lg-flex align-items-center ms-auto order-2'>
                    <div className="navbar-text d-flex align-items-center">
                        {isLoggedIn ? (
                            <>
                                <LanguageSelectionButton className="mx-1" />

                                <button className="btn btn-outline-danger mx-1" type="button" onClick={handleLogout}>
                                    {t('components.navbar.nav.logout')}
                                </button>
                                {logoutError && (
                                    <span className="text-danger" role="alert">
                                        {t('components.navbar.nav.logoutError')}
                                    </span>
                                )}
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
                    <ul className="navbar-nav me-auto mb-2 mb-lg-0 w-100">
                        <li className="nav-item">
                            <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/" end>
                                {t('components.navbar.nav.home')}
                            </NavLink>
                        </li>

                        {isLoggedIn && (
                            <>
                                <NavbarDropdown
                                    id="navbar-profile"
                                    icon="fa-solid fa-user-circle"
                                    title={t('components.navbar.nav.profile')}
                                >
                                    <NavDropdown.Item as={NavLink} to="/profile">
                                        <i className="fa-solid fa-user" aria-hidden="true" /> {t('components.navbar.nav.view_profile')}
                                    </NavDropdown.Item>
                                    <NavDropdown.Item as={NavLink} to="/learning">
                                        <i className="fa-solid fa-chart-line" aria-hidden="true" /> {t('components.navbar.nav.learning')}
                                    </NavDropdown.Item>
                                </NavbarDropdown>

                                <li className="nav-item">
                                    <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/activities" end>
                                        <i className="fa-solid fa-chalkboard-user"></i> {t('components.navbar.nav.activities')}
                                    </NavLink>
                                </li>

                                {/* <li className="nav-item">
                                    <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/activities/_EXPLORE" end>
                                        <i className="fa-solid fa-magnifying-glass-arrow-right"></i> {t('components.navbar.nav.explore_sql')}
                                    </NavLink>
                                </li> */}
                            </>
                        )}

                        <NavbarDropdown
                            id="navbar-help"
                            icon="fa-solid fa-circle-question"
                            title={t('components.navbar.nav.help')}
                        >
                            <NavDropdown.Item as={NavLink} to="/howto" end>
                                <i className="fa-brands fa-readme" aria-hidden="true" /> {t('components.navbar.nav.howto')}
                            </NavDropdown.Item>
                            <NavDropdown.Item as={NavLink} to="/error-taxonomy">
                                <i className="fa-solid fa-book" aria-hidden="true" /> {t('pages.errorTaxonomy.title')}
                            </NavDropdown.Item>
                        </NavbarDropdown>

                        {userInfo?.isAdmin && (
                            <li className="nav-item">
                                <NavLink className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} to="/admin">
                                    <i className="fa-solid fa-shield-alt"></i> {t('components.navbar.nav.admin')}
                                </NavLink>
                            </li>
                        )}

                        {isLoggedIn && (
                            <div className="navbar-text d-flex align-items-center ms-auto">
                                {isLoggedIn && (
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
                                    </>
                                )}
                            </div>
                        )}
                    </ul>
                </div>
            </div>
        </nav>
    );
}

export default Navbar; 
