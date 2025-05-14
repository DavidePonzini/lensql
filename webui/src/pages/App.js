import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import { useAuth } from '../hooks/useAuth';

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Separator from "../components/Separator";

import Login from './Login';
import Profile from './Profile';
import Assignments from './Assignments';
import Home from './Home';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import useTooltipObserver from '../hooks/useTooltipObserver';
import Assignment from './Assignment';



function App() {
    const { isLoggedIn } = useAuth();

    useTooltipObserver();

    if (!isLoggedIn) {
        return (
            <Login />
        )
    }

    return (
        <>
            <Router>
                <Navbar />

                <div className="content">
                    <div className="container-md">
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/profile" element={<Profile />} />
                            <Route path="/assignments" element={<Assignments />} />
                            <Route path="/assignments/:assignmentId" element={<Assignment />} />
                        </Routes>
                    </div>
                </div>

                <Separator />
                <Footer />
            </Router>
        </>
    )
}

export default App;