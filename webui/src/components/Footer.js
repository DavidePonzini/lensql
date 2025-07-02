import './Footer.css';
import './FooterSocial.css';

function FooterSocial() {
    return (
        <>
            <a href="https://ponzidav.com" target="_blank" rel="noreferrer noopener" className="bi bi-globe social social-website">
                <span className="visually-hidden">Website</span>
            </a>
            <a href="https://github.com/DavidePonzini" target="_blank" rel="noreferrer noopener" className="bi bi-github social social-github">
                <span className="visually-hidden">GitHub</span>
            </a>
            <a href="mailto:davide.ponzini@edu.unige.it" target="_blank" rel="noreferrer noopener" className="bi bi-envelope-at social social-email">
                <span className="visually-hidden">Email</span>
            </a>
        </>
    );
}

function Footer() {
    const year = new Date().getFullYear();

    return (
        <footer className="footer">
            <div className="container-fluid">
                <div className="center monospace">
                    Developed by Davide Ponzini.
                </div>

                <div className="center">
                    © {year} LensQL · GNU General Public License ·&nbsp;
                    <a href='mailto:davide.ponzini@edu.unige.it' className='link'>Contact</a>
                </div>

                <div className="center">
                    <FooterSocial />
                </div>
            </div>
        </footer>
    );
}

export default Footer;