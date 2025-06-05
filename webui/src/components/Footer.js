import './Footer.css';
import './FooterSocial.css';


function FooterSocial() {
    return (
          <>
              <a href="https://ponzidav.com" target="_blank" rel="noreferrer" className="bi bi-globe social social-website">
                <span className="visually-hidden">Website</span>
              </a>
              <a href="https://github.com/DavidePonzini" target="_blank" rel="noreferrer" className="bi bi-github social social-github">
                <span className="visually-hidden">GitHub</span>
              </a>
              <a href="mailto:davide.ponzini@edu.unige.it" target="_blank" rel="noreferrer" className="bi bi-envelope-at social social-email">
                <span className="visually-hidden">Email</span>
              </a>
          </>
      );
  }

function Footer() {
    return (

        <div className="footer">
            <div className="container-fluid">
                <div className="center monospace">
                    Developed by Davide Ponzini.
                </div>

                <div className="center">
                    <FooterSocial />
                </div>
            </div>
        </div>
    );
}

export default Footer;