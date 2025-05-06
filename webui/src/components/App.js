import '../styles/App.css';
import Footer from './Footer';
import Separator from './Separator';
import Navbar from './Navbar';
import Query from './Query';

function App() {
  return (
    <>
        <Navbar>
            <div className="navbar-nav me-auto mb-2 mb-lg-0">
            </div>
            <div className="navbar-text">
                <span className="mx-2" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Your username">
                    <i className="fa-solid fa-user"></i>
                    <span id="username">Not logged in</span>
                </span>
            </div>
            {/* <button class="btn btn-outline-primary mx-1" type="button" onclick="show_leaderboard()">Leaderboard</button> */}
        </Navbar>

        <div className="content">
            <div className="container-md">
                <Query />
            </div>
        </div>

        <Separator />
        <Footer />
    </>
  );
}

export default App;
