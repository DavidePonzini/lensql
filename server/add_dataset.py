from server import db

from dav_tools import argument_parser, messages


def add_dataset(name: str, path: str):
    """
    Add a dataset to the database.
    :param dataset_name: Name of the dataset
    :param dataset_path: Path to the dataset file
    """
    try:
        with open(path, 'r') as file:
            content = file.read()

        db.admin.dataset.add(name, content)

        messages.info(f'Dataset {name} added successfully.')
    except Exception as e:
        messages.error(f"Error adding dataset {name}: {e}")

if __name__ == '__main__':
    argument_parser.set_description('Add a new dataset to the database')
    argument_parser.add_argument('name', type=str, help='Name of the dataset')
    argument_parser.add_argument('path', type=str, help='Path to the dataset file')

    add_dataset(argument_parser.args.name, argument_parser.args.path)