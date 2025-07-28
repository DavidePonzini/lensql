import { useTranslation } from 'react-i18next';

function Admin() {
    const { t } = useTranslation();

    return (
        <div className="container-md">
            <h1>{t('admin.title')}</h1>
            <p>{t('admin.empty')}</p>
        </div>
    );
}

export default Admin;
