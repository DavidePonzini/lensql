import { useTranslation } from "react-i18next";

function ChangePasswordButton() {
    const { t } = useTranslation();

    return (
        <button className="btn btn-primary mb-4" disabled>
            {t('pages.profile.profile.change_password')}
        </button>
    );
}

export default ChangePasswordButton;