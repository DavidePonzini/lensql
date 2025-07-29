import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import useAuth from '../hooks/useAuth';
import useUserInfo from '../hooks/useUserInfo';
import useTooltipObserver from '../hooks/useTooltipObserver';

import Navbar from "../components/navbar/Navbar";
import Separator from "../components/Separator";
import Footer from "../components/footer/Footer";
import BadgeNotifier from '../components/notifications/BadgeNotifier';

import Home from './Home';
import About from './About';
import Login from './Login';
import Register from './Register';
import Profile from './profile/Profile';
import Learning from './profile/Learning';
import ExerciseList from './classes/ExerciseList';
import ClassList from './classes/ClassList';
import Exercise from './exercises/Exercise';
import Admin from './admin/Admin';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

function App() {
    const { isLoggedIn } = useAuth();
    const { userInfo } = useUserInfo();

    useTooltipObserver();

    return (
        <>
            <Router>
                <Navbar />

                <div className="content">
                    <Routes>
                        <Route path="/">
                            <Route index element={<Home />} />
                            <Route path="about" element={<About />} />

                            {isLoggedIn ? (
                                <>
                                    <Route path="profile" element={<Profile />} />
                                    <Route path="learning" element={<Learning />} />

                                    <Route path="classes">
                                        <Route index element={<ClassList />} />
                                        <Route path=":classId" element={<ExerciseList />} />
                                    </Route>

                                    <Route path="exercises/:exerciseId" element={<Exercise />} />

                                    {userInfo?.isAdmin && (
                                        <Route path="admin" element={<Admin />} />
                                    )}
                                </>
                            ) : (
                                <>
                                    <Route path="login" element={<Login />} />
                                    <Route path="register" element={<Register />} />
                                </>
                            )}

                            <Route path="*" element={<Home />} />
                        </Route>
                    </Routes>
                </div>

                <Separator />
                <Footer />
            </Router>

            <BadgeNotifier />
        </>
    )
}

export default App;