import json
import orjson
from typing import Any, Dict, Generator, Iterable, Iterator, List, Tuple, TypeVar
import tqdm
from joblib import Parallel, delayed

T = TypeVar('T')
def chunks(lst: Iterable[T], n: int) -> Generator[List[T], None, None]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

T = TypeVar('T')
def yield_chunks(generator: Iterator[T], n: int) -> Generator[List[T], None, None]:
    """Yield successive n-sized chunks from lst."""
    while True:
        ret = []
        try:
            for i in range(n):
                ret.append(next(generator))
            yield ret
        except StopIteration as e:
            yield ret
            break
    

def write_jsonl(obj_list: Iterable[Any], output_path: str, progress_bar: bool=False):
    with open(output_path, 'w', encoding='utf-8') as f:
        if progress_bar:
            obj_list = tqdm.tqdm(obj_list)
        for each_obj in obj_list:
            f.write(json.dumps(each_obj, ensure_ascii=False) + '\n')

def json_to_dict(lines: List[str]) -> List[Dict[Any, Any]]:
    ret = []
    for line in lines:
        ret.append(orjson.loads(line))
    return ret

def read_jsonl(path: str, multi_thread:bool=False, progress_bar: bool=False):
    dataset = []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

        if not multi_thread:
            if progress_bar:
                lines = tqdm.tqdm(lines)
            for line in lines:
                dataset.append(orjson.loads(line))
        else:
            n_thread = 32
            line_chunks = list(chunks(lines, len(lines) // (n_thread * 10)))
            if progress_bar:
                line_chunks = tqdm.tqdm(line_chunks)
            results = Parallel(n_jobs=n_thread)(delayed(json_to_dict)(chks) for chks in line_chunks)
            for result in results:
                dataset.extend(result)
    return dataset

import csv
import mmap
def get_file_line(path: str) -> int:
    with open(path, 'r', encoding='utf-8') as f:
        count = 0
        for line in tqdm.tqdm(f):
            if not line.rstrip().endswith('\\'):
                count += 1
    return count

def read_csv(path: str) -> Iterable[Tuple[str]]:
    with open(path, 'r', encoding="utf-8") as csvfile:
        # mm_csvfile = mmap.mmap(csvfile.fileno(), 0, prot=mmap.PROT_READ)
        csvreader = csv.reader(csvfile, escapechar='\\', delimiter=',', quotechar='"', lineterminator = '\r\n')
        for row in csvreader:
            yield row

import gzip
def get_file_line_gz(path: str) -> int:
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        count = 0
        for line in tqdm.tqdm(f):
            if not line.rstrip().endswith('\\'):
                count += 1
    return count
def read_csv_gz(path: str) -> Iterable[Tuple[str]]:
    with gzip.open(path, 'rt', encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile, escapechar='\\', delimiter=',', quotechar='"', lineterminator = '\r\n')
        for row in csvreader:
            yield row

