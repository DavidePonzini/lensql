import { useTranslation } from 'react-i18next';
import './Footer.css';
import './FooterSocial.css';

function FooterSocial() {
    const { t } = useTranslation();

    return (
        <>
            <a href="https://ponzidav.com" target="_blank" rel="noreferrer noopener" className="bi bi-globe social social-website">
                <span className="visually-hidden">{t('footer.social.website')}</span>
            </a>
            <a href="https://github.com/DavidePonzini" target="_blank" rel="noreferrer noopener" className="bi bi-github social social-github">
                <span className="visually-hidden">{t('footer.social.github')}</span>
            </a>
            <a href="mailto:davide.ponzini@edu.unige.it" target="_blank" rel="noreferrer noopener" className="bi bi-envelope-at social social-email">
                <span className="visually-hidden">{t('footer.social.email')}</span>
            </a>
        </>
    );
}

function Footer() {
    const { t } = useTranslation();
    const year = new Date().getFullYear();

    return (
        <footer className="footer">
            <div className="container-fluid">
                <div className="center monospace">
                    {t('footer.developed_by')}
                </div>

                <div className="center">
                    © {year} LensQL · {t('footer.license')} ·&nbsp;
                    <a href='mailto:davide.ponzini@edu.unige.it' className='link'>
                        {t('footer.contact')}
                    </a>
                </div>

                <div className="center">
                    <FooterSocial />
                </div>
            </div>
        </footer>
    );
}

export default Footer;
