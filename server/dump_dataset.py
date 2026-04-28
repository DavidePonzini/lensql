import dav_tools

from server.db.admin import Dataset


def dump_dataset(dataset_id: str) -> None:
    print(Dataset(dataset_id).dump_json())


if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('dataset', help='ID of the dataset to dump')
    dav_tools.argument_parser.parse_args()
    dump_dataset(dav_tools.argument_parser.args.dataset)
