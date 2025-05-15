import db_admi as db_admin
import add_user

from dav_tools import messages

if __name__ == '__main__':
    add_user.add_user('dav', 'd')
    add_user.add_user('giovanna', 'giovanna')
    add_user.add_user('barbara', 'barbara')

    db_admin.add_exercise(
        title='0) Progetto',
        request='Esegui qui tutte le query relative al tuo progetto finale',
        dataset='-- No dataset',
        expected_answer='')
    messages.info('Esercizio 0) Progetto creato')

    db_admin.add_exercise(
        title='0) Modalità libera',
        request='Se hai delle query che non sono state richieste, ma che vuoi comunque eseguire, puoi farlo qui',
        dataset='-- No dataset',
        expected_answer='')
    messages.info('Esercizio 0) Modalità libera creato')



