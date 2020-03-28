import random
import time
from concurrent.futures.thread import ThreadPoolExecutor
from typing import NamedTuple, List, Optional, Dict, Iterable, TypeVar, Tuple

from wikiracer.wikipedia import get_page, get_random_page_name, get_forward_links, get_backward_links


class SearchInfo(NamedTuple):
    path: List[str]
    seconds: float
    start: str
    end: str


class WrappedPage(NamedTuple):
    parent: Optional["WrappedPage"]  # type: ignore
    name: str


def do_forward_work(page: WrappedPage) -> List[WrappedPage]:
    p = get_page(page.name)
    if p is None:
        return []
    forward_links = get_forward_links(p)
    return [WrappedPage(parent=page, name=name) for name in forward_links]


def do_backward_work(page: WrappedPage) -> List[WrappedPage]:
    p = get_page(page.name)
    if p is None:
        return []
    backward_links = get_backward_links(p)
    return [WrappedPage(parent=page, name=name) for name in backward_links]


def get_path(page: Optional[WrappedPage]) -> List[str]:
    path = []

    while page is not None:
        path.append(page.name)
        page = page.parent

    return path


def sample(l: List, k: int) -> Tuple[List, List]:
    if k <= len(l):
        in_sample = random.sample(l, k)
        return in_sample, list(set(l) - set(in_sample))
    else:
        return l, []


T = TypeVar("T")


def flatten(i: Iterable[Iterable[T]]) -> List:
    return [item for sublist in i for item in sublist]


def race(start_name: Optional[str] = None, end_name: Optional[str] = None) -> SearchInfo:
    with ThreadPoolExecutor(max_workers=20) as executor:
        start_name = start_name if start_name is not None else get_random_page_name()
        end_name = end_name if end_name is not None else get_random_page_name()

        start = WrappedPage(parent=None, name=start_name)
        end = WrappedPage(parent=None, name=end_name)

        forward_component: Dict[str, WrappedPage] = {start.name: start}
        backward_component: Dict[str, WrappedPage] = {end.name: end}

        forward_queue: List[WrappedPage] = [start]
        backward_queue: List[WrappedPage] = [end]

        start_time = time.time()

        while True:
            in_sample_forward, out_of_sample_forward = sample(forward_queue, 10)
            in_sample_backward, out_of_sample_backward = sample(backward_queue, 5)

            forward_work = executor.map(do_forward_work, in_sample_forward)
            backward_work = executor.map(do_backward_work, in_sample_backward)

            flattened_forward_work = flatten(forward_work)
            flattened_backward_work = flatten(backward_work)

            forward_queue = out_of_sample_forward + [
                p for p in flattened_forward_work if p.name not in forward_component
            ]
            backward_queue = out_of_sample_backward + [
                p for p in flattened_backward_work if p.name not in backward_component
            ]

            forward_component.update({p.name: p for p in flattened_forward_work})
            backward_component.update({p.name: p for p in flattened_backward_work})

            intersection = forward_component.keys() & backward_component.keys()
            if len(intersection) != 0:
                match = intersection.pop()
                full_path = list(reversed(get_path(forward_component[match]))) + get_path(backward_component[match])[1:]
                return SearchInfo(path=full_path, seconds=time.time() - start_time, start=start.name, end=end.name)
