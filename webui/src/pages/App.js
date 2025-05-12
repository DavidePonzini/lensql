import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import useToken from '../hooks/useToken';

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Separator from "../components/Separator";

import Login from './Login';
import Query from './Query';
import Profile from './Profile';
import Assignments from './Assignments';


function App() {
    const [token, setToken] = useToken();

    if (!token) {
        return (
            <Login setToken={setToken} />
        )
    }

    return (
        <>
            <React.StrictMode>
                <Router>
                    <Navbar />

                    <div className="content">
                        <div className="container-md">
                            <Routes>
                                <Route path="/profile" element={<Profile />} />
                                <Route path="/assignments" element={<Assignments />} />
                                <Route path="/assignments/q" element={<Query exerciseId={0} exerciseText="Find the users who are called Davide"/>} />
                            </Routes>
                        </div>
                    </div>

                    <Separator />
                    <Footer />
                </Router>
            </React.StrictMode>
        </>
    )
}

export default App;