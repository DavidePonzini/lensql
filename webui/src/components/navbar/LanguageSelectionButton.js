import { useTranslation } from 'react-i18next';

function LanguageSelectionButton({ className = '' }) {
    const { t, i18n } = useTranslation();
    const currentLang = i18n.language;

    const languageOptions = {
        en: { label: t('language.en'), flag: '🇬🇧' },
        it: { label: t('language.it'), flag: '🇮🇹' }
    };

    const changeLanguage = (lng) => {
        i18n.changeLanguage(lng);
        localStorage.setItem('i18nextLng', lng);
    };


    return (
        <div className={`dropdown ${className}`}>
            <button
                className="btn btn-sm btn-outline-secondary dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
            >
                {languageOptions[currentLang]?.flag || '🌐'} {languageOptions[currentLang]?.label || 'Language'}
            </button>
            <ul className="dropdown-menu dropdown-menu-end">
                {Object.entries(languageOptions).map(([code, { label, flag }]) => (
                    <li key={code}>
                        <button className="dropdown-item" onClick={() => changeLanguage(code)}>
                            {flag} {label}
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default LanguageSelectionButton;