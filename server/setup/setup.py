from server import db

from dav_tools import messages

if __name__ == '__main__':
    users = [
        ('lens', 'l', True, 'DIBRIS'),
        ('dav', 'd', True, 'DIBRIS'),
        ('giovanna', 'g', False, 'DIBRIS'),
        ('barbara', 'b', False, 'DIBRIS'),
        ('student', 's', False, 'DIBRIS'),
    ]

    # Create sample users
    for user, password, is_admin, school in users:
        if db.register_user(user, password, is_admin=is_admin, school=school):
            messages.info(f'User {user} registered successfully')

    classes = [
        ('server/setup/miedema.sql', 'Sample Class (Miedema)', [
            {
                'name': 'Exercise 1',
                'request': 'List all IDs&names of customer living in Eindhoven.',
                'solution': 'SELECT cID, cName FROM customer WHERE city = \'Eindhoven\';',
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 2',
                'request': 'List all pairs of customer IDs who live on a street with the same name but in a different city.',
                'solution': 'SELECT c1.cid AS id1, c2.cid AS id2 FROM customer c1 JOIN customer c2 ON c1.street = c2.street AND c1.city <> c2.city WHERE c1.cID < c2.cID;',
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 3',
                'request': 'List all customer IDs, dates and quantities of transactions containing products named Apples.',
                'solution': 'SELECT t.cID, t.date, t.quantity FROM transaction t JOIN product p ON t.pID = p.pID WHERE p.pName = \'Apples\';',
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 4',
                'request': 'Find the names of all inventory items that have a higher unit price than Bananas.',
                'solution': 'SELECT DISTINCT pname FROM product p JOIN inventory i ON i.pid = p.pid WHERE i.unit_price > ALL( SELECT i.unit_price FROM product p JOIN inventory i ON i.pid = p.pid WHERE p.pname = \'Banana\' );',
                'solution2': 'SELECT DISTINCT pname FROM product p JOIN inventory i ON i.pid = p.pid WHERE i.unit_price > ANY( SELECT i.unit_price FROM product p JOIN inventory i ON i.pid = p.pid WHERE p.pname = \'Banana\' );',
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 5',
                'request': 'Return a list of the number of stores per city.',
                'solution': 'SELECT city, COUNT(sID) AS num_stores FROM store GROUP BY city;',
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 6',
                'request': 'Return the stores table ordered alphabetically on city.',
                'solution': 'SELECT * FROM store ORDER BY city;',
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 7',
                'request': 'A store-chain consists of at least two stores with the same name but different IDs. Find the names of the store-chains that on average sell product in quantities of more than 4.',
                'solution': 'SELECT s.sName FROM store s JOIN transaction t ON s.sID = t.sID GROUP BY s.sName HAVING COUNT(DISTINCT s.sID) >= 2 AND AVG(t.quantity) > 4;',                'search_path': 'miedema',
            }
        ]),
    ]
    for class_file, class_name, exercises in classes:
        with open(class_file) as f:
            dataset = f.read()
        class_id = db.admin.classes.create(class_name, dataset=dataset)

        db.admin.classes.make_teacher('lens', class_id)
        
        for user, _, is_admin, _ in users:
            db.admin.classes.join(user, class_id)
            messages.info(f'User {user} enrolled in class {class_name}')

        for exercise in exercises:
            exercise_id = db.admin.exercises.create(username='lens', class_id=class_id, title=exercise['name'], request=exercise['request'], solution=exercise['solution'], search_path=exercise['search_path'])
            db.admin.exercises.unhide(exercise_id)
            messages.info(f'Exercise {exercise["name"]} added to class {class_name}')



