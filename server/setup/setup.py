from server import db

from dav_tools import messages

ADMIN_USER = db.admin.User('lens')

if __name__ == '__main__':

    # region Admin user
    if ADMIN_USER.exists():
        messages.warning(f'Admin user {ADMIN_USER} already exists, skipping creation.')
    elif db.register_user(ADMIN_USER, 'l', school='ADMIN', is_admin=True):
        messages.success(f'Admin user {ADMIN_USER} registered successfully')
    else:
        messages.critical_error(f'Failed to register admin user {ADMIN_USER}')
    # endregion

    # region Datasets and Exercises
    datasets = [
        ('explore.sql', '_EXPLORE', 'Explore SQL', [
            {
                'name': 'Explore SQL',
                'request': 'You can write any SQL query here',
                'solutions': [],
                'search_path': 'public',
            },
        ]),
        ('miedema.sql', 'WELCOME_MIEDEMA', 'Sample Dataset: Miedema', [
            {
                'name': 'Exercise 1',
                'request': 'List all IDs&names of customer living in Eindhoven.',
                'solutions': ['SELECT cID, cName FROM customer WHERE city = \'Eindhoven\';'],
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 2',
                'request': 'List all pairs of customer IDs who live on a street with the same name but in a different city.',
                'solutions': ['SELECT c1.cid AS id1, c2.cid AS id2 FROM customer c1 JOIN customer c2 ON c1.street = c2.street AND c1.city <> c2.city WHERE c1.cID < c2.cID;'],
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 3',
                'request': 'List all customer IDs, dates and quantities of transactions containing products named Apples.',
                'solutions': ['SELECT t.cID, t.date, t.quantity FROM transaction t JOIN product p ON t.pID = p.pID WHERE p.pName = \'Apples\';'],
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 4',
                'request': 'Find the names of all inventory items that have a higher unit price than Bananas.',
                'solutions': ['SELECT DISTINCT pname FROM product p JOIN inventory i ON i.pid = p.pid WHERE i.unit_price > ALL( SELECT i.unit_price FROM product p JOIN inventory i ON i.pid = p.pid WHERE p.pname = \'Banana\' );',
                              'SELECT DISTINCT pname FROM product p JOIN inventory i ON i.pid = p.pid WHERE i.unit_price > ANY( SELECT i.unit_price FROM product p JOIN inventory i ON i.pid = p.pid WHERE p.pname = \'Banana\' );'],
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 5',
                'request': 'Return a list of the number of stores per city.',
                'solutions': ['SELECT city, COUNT(sID) AS num_stores FROM store GROUP BY city;'],
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 6',
                'request': 'Return the stores table ordered alphabetically on city.',
                'solutions': ['SELECT * FROM store ORDER BY city;'],
                'search_path': 'miedema',
            },
            {
                'name': 'Exercise 7',
                'request': 'A store-chain consists of at least two stores with the same name but different IDs. Find the names of the store-chains that on average sell product in quantities of more than 4.',
                'solutions': ['SELECT s.sName FROM store s JOIN transaction t ON s.sID = t.sID GROUP BY s.sName HAVING COUNT(DISTINCT s.sID) >= 2 AND AVG(t.quantity) > 4;'],
                'search_path': 'miedema',
            }
        ]),
    ]
    for dataset_file, dataset_id, dataset_name, exercises in datasets:
        messages.info(f'Creating dataset {dataset_name}...')

        with open(f'server/setup/datasets/{dataset_file}') as f:
            dataset_str = f.read()

        dataset = db.admin.Dataset(dataset_id)
        if dataset.exists():
            messages.warning(f'  Dataset {dataset_name} already exists, skipping creation.')
            db_exists = True
        else:
            dataset = db.admin.Dataset.create(dataset_name, dataset_str=dataset_str, dataset_id=dataset_id)
            db_exists = False
            messages.success(f'  Dataset {dataset_name} created successfully.')

        dataset.add_participant(ADMIN_USER)
        dataset.set_teacher_status(ADMIN_USER, True)

        # Create exercises if dataset was just created
        if db_exists:
            messages.info(f'  Skipping exercise creation for class {dataset_name} as it already exists.')
        else:
            for exercise_data in exercises:
                exercise = db.admin.Exercise.create(
                    title=exercise_data['name'],
                    user=ADMIN_USER,
                    dataset_id=dataset.dataset_id,
                    request=exercise_data['request'],
                    solutions=exercise_data['solutions'],
                    search_path=exercise_data['search_path'],
                )

                messages.success(f'  Exercise {exercise_data["name"]} added to dataset {dataset_name}')
    # endregion

    # region Default users
    users = [
        (db.admin.User('dav'), 'd', 'DIBRIS'),
        (db.admin.User('giovanna'), 'g', 'DIBRIS'),
        (db.admin.User('barbara'), 'b', 'DIBRIS'),
        (db.admin.User('student'), 's', 'DIBRIS'),
    ]

    # Create sample users
    messages.info('Creating users...')

    for user, password, school in users:
        if user.exists():
            messages.warning(f'  User {user} already exists, skipping creation.')
        elif db.register_user(user, password, school=school, datasets=[
            db.admin.Dataset('_EXPLORE'),
            db.admin.Dataset('WELCOME_MIEDEMA'),
        ]):
            messages.success(f'  User {user} registered successfully')
        else:
            messages.error(f'  Failed to register user {user}')
    # endregion

        
            


