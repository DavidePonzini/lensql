from server import db

from dav_tools import messages

if __name__ == '__main__':
    for user, password, is_admin, school in [
        ('lens', 'l', True, 'DIBRIS'),
        ('dav', 'd', True, 'DIBRIS'),
        ('giovanna', 'g', False, 'DIBRIS'),
        ('barbara', 'b', False, 'DIBRIS'),
        ('student', 's', False, 'DIBRIS'),
    ]:
        if db.register_user(user, password, is_admin=is_admin, school=school):
            messages.info(f'User {user} registered successfully')

    for title, request in [
        ('0) Progetto', 'Esegui qui tutte le query relative al tuo progetto finale',),
        ('0) Modalità libera', 'Se hai delle query che non sono state richieste, ma che vuoi comunque eseguire, puoi farlo qui'),
        ('0) Versione vecchia LensQL', 'Esegui qui le tue query'),
    ]:
        db.admin.exercises.create(
            title=title,
            request=request,
        )
        messages.info(f'Exercise {title} created')

