import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js'; // includes Popper automatically

import ReactDOM from 'react-dom/client';
import reportWebVitals from './reportWebVitals';

import App from './pages/App';

// Boostrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js'; // Includes Popper.js automatically

// Icons: FontAwesome and Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

// Custom CSS
import './styles/_common.css';
import './styles/_colors.css';
// import './styles/_code.css';


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <App />
);

reportWebVitals();
