from server import db

from dav_tools import messages

if __name__ == '__main__':
    for user, password in [
        ('dav', 'd'),
        ('giovanna', 'g'),
        ('barbara', 'b'),
        ('student', 's'),
    ]:
        db.register_user(user, password)

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
        db.admin.teachers.add_student(teacher, student)
        messages.info(f'Added teacher {teacher} for student {student}')

    for title, request, learning_objectives in [
        ('0) Progetto', 'Esegui qui tutte le query relative al tuo progetto finale', ['Simple Select']),
        ('0) Modalità libera', 'Se hai delle query che non sono state richieste, ma che vuoi comunque eseguire, puoi farlo qui', []),
        ('0) Versione vecchia LensQL', 'Esegui qui le tue query', []),
    ]:
        db.admin.exercises.create(
            title=title,
            request=request,
            dataset_id=None,
            expected_answer='',
            is_ai_generated=False,
            learning_objectives=learning_objectives
        )
        messages.info(f'Exercise {title} created')

