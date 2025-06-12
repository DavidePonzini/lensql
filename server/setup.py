from server import db

from dav_tools import messages

if __name__ == '__main__':
    for user, password, is_teacher, is_admin in [
        ('lens', 'l', False, True),
        ('dav', 'd', True, True),
        ('giovanna', 'g', True, False),
        ('barbara', 'b', True, False),
        ('student', 's', False, False),
    ]:
        if db.register_user(user, password, is_teacher=is_teacher, is_admin=is_admin):
            messages.info(f'User {user} registered successfully')

    for teacher, students in [
        ('dav', ['student']),
        ('giovanna', ['barbara', 'dav', 'student']),
        ('barbara', ['giovanna', 'dav', 'student']),
    ]:
        for student in students:
            db.admin.teachers.add_student(teacher, student)
            messages.info(f'Added teacher {teacher} for student {student}')

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

