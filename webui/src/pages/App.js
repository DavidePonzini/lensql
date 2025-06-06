import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import { useAuth } from '../hooks/useAuth';

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Separator from "../components/Separator";

import Login from './Login';
import Home from './Home';
import Profile from './profile/Profile';
import Learning from './learning/Learning';
import AssignmentList from './assignmentList/AssignmentList';
import ManageAssignments from './manageAssignments/ManageAssignments';
import Assignment from './assignment/Assignment';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import useTooltipObserver from '../hooks/useTooltipObserver';



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
                            <Route path="/">
                                <Route index element={<Home />} />
                                {isLoggedIn ? (
                                    <>
                                        <Route path="profile" element={<Profile />} />
                                        <Route path="learning" element={<Learning />} />
                                        <Route path="assignments">
                                            <Route index element={<AssignmentList />} />
                                            {userInfo?.isTeacher && (
                                                <Route path="manage" element={<ManageAssignments />} />
                                            )}
                                            <Route path="q/:assignmentId" element={<Assignment />} />
                                        </Route>
                                    </>
                                ) : (
                                    <Route path="*" element={<Login />} />
                                )}
                            </Route>
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