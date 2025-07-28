import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import translationEN from './locales/en/translation.json';
import translationIT from './locales/it/translation.json';

const resources = {
    en: { translation: translationEN },
    it: { translation: translationIT },
};

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        fallbackLng: 'en',
        detection: {
            // Order of detection
            order: ['localStorage', 'htmlTag'],
            // Where to store the selected language
            caches: ['localStorage'],
        },
        interpolation: {
            escapeValue: false,
        },
    });


export default i18n;
