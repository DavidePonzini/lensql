import '../styles/Navbar.css';

function Navbar() {
    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-light sticky-top">
            <div className="container-fluid">
                <a className="navbar-brand" href="/">LensQL</a>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarSupportedContent">
                    <div className="navbar-nav me-auto mb-2 mb-lg-0">
                    </div>
                    <div className="navbar-text">
                        <span className="mx-2" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Your username">
                            <i className="fa-solid fa-user"></i>
                            <span id="username">Not logged in</span>
                        </span>
                    </div>
                    {/* <button class="btn btn-outline-primary mx-1" type="button" onclick="show_leaderboard()">Leaderboard</button> */}
                </div>
            </div>
        </nav>
    );
}

export default Navbar;