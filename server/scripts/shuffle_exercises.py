'''Sfhuffle exercise order in a dataset.'''

import dav_tools
import random
from tqdm import tqdm

from server.db.admin import Dataset


if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('dataset', help='ID of the dataset to shuffle exercises for')
    dav_tools.argument_parser.add_argument('prefix', nargs='?', default='Exercise ', help='Prefix for the shuffled exercise titles')
    dav_tools.argument_parser.parse_args()

    dataset = Dataset(dav_tools.argument_parser.args.dataset)

    all_exercises = dataset.list_all_exercises()
    random.shuffle(all_exercises)

    for i, exercise in enumerate(tqdm(all_exercises, ncols=100), start=1):
        new_title = f"{dav_tools.argument_parser.args.prefix}{i}"
        exercise.update(
            title=new_title,
            request=exercise.request,
            solutions=exercise.solutions,
        )

    dav_tools.messages.success(f"Shuffled {len(all_exercises)} exercises in dataset '{dataset.dataset_id}'")