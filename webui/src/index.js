import ReactDOM from 'react-dom/client';
import React from 'react';
import reportWebVitals from './reportWebVitals';

import App from './pages/App';

import { AuthProvider } from './hooks/useAuth';
import { UserInfoProvider } from './hooks/useUserInfo';

// Boostrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js'; // Includes Popper.js automatically

// Icons: FontAwesome and Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

// Common CSS
import './styles/_colors.css';
import './styles/_common.css';

import './index.css';


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>

        <AuthProvider>
            <UserInfoProvider>
    
                <App />
    
            </UserInfoProvider>
        </AuthProvider>
    
    </React.StrictMode>
);

reportWebVitals();
