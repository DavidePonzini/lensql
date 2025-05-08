import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import useToken from './hooks/useToken';

import Login from './pages/Login';
import Query from './pages/Query';
import Profile from './pages/Profile';


function App() {
    const [ token, setToken ] = useToken();

    if (!token) {
        return (
            <Login setToken={setToken} />
        )
    }

    return (

        <React.StrictMode>
            <Router>
                <Routes>
                    <Route path="/" element={<Profile />} />
                    <Route path="/query" element={<Query />} />
                </Routes>
            </Router>
        </React.StrictMode>
    )
}

export default App;