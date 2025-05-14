import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import { useAuth } from '../hooks/useAuth';

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Separator from "../components/Separator";

import Login from './Login';
import Profile from './Profile';
import Assignments from './Assignments';
import Home from './Home';
import ManageAssignments from './ManageAssignments';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import useTooltipObserver from '../hooks/useTooltipObserver';
import Assignment from './Assignment';



function App() {
    const { isLoggedIn, userInfo } = useAuth();

    useTooltipObserver();

    return (
        <>
            <Router>
                <Navbar />

                <div className="content">
                    <div className="container-md">
                        <Routes>
                            <Route path="/" element={<Home />} />

                            {isLoggedIn ? (
                                <>
                                    <Route path="/" element={<Home />} />
                                    <Route path="/profile" element={<Profile />} />
                                    <Route path="/assignments">
                                        <Route index element={<Assignments />} />
                                        <Route path=":assignmentId" element={<Assignment />} />
                                    </Route>

                                    {userInfo?.isTeacher && (
                                        <Route path="/manage" element={<ManageAssignments />} />
                                    )}

                                </>
                            ) : (
                                <Route path="*" element={<Login />} />
                            )}
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