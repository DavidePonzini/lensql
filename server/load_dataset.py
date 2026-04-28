import sys

import dav_tools

from server.db.admin import Dataset


def load_dataset() -> None:
    dataset = Dataset.load_json(sys.stdin.read())
    dav_tools.messages.info(f'Dataset loaded with ID: {dataset.dataset_id}')


if __name__ == '__main__':
    dav_tools.argument_parser.parse_args()
    load_dataset()
