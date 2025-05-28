from . import db_admin
from . import add_user

from dav_tools import messages

if __name__ == '__main__':
    for user, password in [
        ('dav', 'd'),
        ('giovanna', 'g'),
        ('barbara', 'b'),
        ('student', 's'),
    ]:
        add_user.add_user(user, password)

    for teacher, student in [
        ('dav', 'dav'),
        ('dav', 'student'),
        ('giovanna', 'giovanna'),
        ('giovanna', 'barbara'),
        ('giovanna', 'dav'),
        ('giovanna', 'student'),
        ('barbara', 'barbara'),
        ('barbara', 'giovanna'),
        ('barbara', 'dav'),
        ('barbara', 'student'),
    ]:
        db_admin.add_student(teacher, student)
        messages.info(f'Added teacher {teacher} for student {student}')

    db_admin.add_exercise(
        title='0) Progetto',
        request='Esegui qui tutte le query relative al tuo progetto finale',
        dataset_id=None,
        expected_answer='')
    messages.info('Esercizio 0) Progetto creato')

    db_admin.add_exercise(
        title='0) Modalità libera',
        request='Se hai delle query che non sono state richieste, ma che vuoi comunque eseguire, puoi farlo qui',
        dataset_id=None,
        expected_answer='')
    messages.info('Esercizio 0) Modalità libera creato')

    db_admin.add_exercise(
        title='0) Versione vecchia LensQL',
        request='Esegui qui le tue query',
        dataset_id=None,
        expected_answer='')        


