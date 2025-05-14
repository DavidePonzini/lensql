import { NavLink, useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

import '../styles/Navbar.css';

function Navbar() {
    const navigate = useNavigate();

    const { isLoggedIn, logout, userInfo, loadingUser } = useAuth();

    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-light sticky-top">
            <div className="container-fluid">
                <a className="navbar-brand" href="/">LensQL</a>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>

                <div className="collapse navbar-collapse" id="navbarSupportedContent">
                    <div className="navbar-nav me-auto mb-2 mb-lg-0">
                        <NavLink className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} to="/" end>Home</NavLink>
                        {isLoggedIn && (
                            <>
                                <NavLink className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} to="/profile">Profile</NavLink>
                                <NavLink className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} to="/assignments" end>Assignments</NavLink>
                            </>
                        )}

                        {userInfo?.isTeacher && (
                            <NavLink className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} to="/assignments/manage">Manage Assignments</NavLink>
                        )}
                    </div>

                    <div className="navbar-text">
                        {isLoggedIn ? (
                            <>
                                <span className="mx-2" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Your username">
                                    <i className="fa-solid fa-user"></i>
                                    <span>{loadingUser ? 'Loading...' : userInfo?.username || 'Unknown'}</span>
                                </span>
                                {userInfo?.isAdmin && (
                                    <i className="fa fa-shield-alt text-danger mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Admin"></i>
                                )}
                                {userInfo?.isTeacher && (
                                    <i className="fa fa-chalkboard-teacher text-success mx-1" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Teacher"></i>
                                )}
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
