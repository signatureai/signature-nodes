import concurrent.futures
import logging
import os
import traceback
from typing import Any, Callable


def parallel_for(
    function: Callable[..., Any],
    items: list[Any],
    max_workers: int | None = None,
    **kwargs,
) -> list[Any]:
    """Execute a function in parallel across multiple items.

    Args:
        function (Callable[..., Any]): Function to execute. Should accept (item, index, worker_id) as arguments.
        items (list[Any]): List of items to process.
        max_workers (int | None): Maximum number of worker threads. If None, uses CPU count.
        **kwargs: Additional keyword arguments passed to the function.

    Returns:
        list[Any]: List of results in the same order as input items.

    Note:
        The function is executed in parallel using ThreadPoolExecutor. Each worker processes
        a batch of items to reduce overhead. Results maintain the original order of items.
    """
    if not items:
        # log.info("No items to process, returning empty list")
        return []

    items = list(items)
    if len(items) == 0:
        # log.info("No items to process, returning empty list")
        return []

    if max_workers is None or max_workers == 0:
        max_workers = os.cpu_count()
        logging.info("No max_workers provided, using %d workers", max_workers)

    total_items = len(items)
    results = [None] * total_items

    actual_workers = min(max_workers or 1, total_items)

    batches = []
    items_per_worker = total_items // actual_workers
    extra_items = total_items % actual_workers

    start = 0
    for worker_id in range(actual_workers):
        batch_size = items_per_worker + (1 if worker_id < extra_items else 0)
        if batch_size > 0:
            end = start + batch_size
            batches.append((worker_id, start, end))
            start = end

    def process_batch(worker_id: int, start_idx: int, end_idx: int) -> list[tuple]:
        batch_results = []
        batch_items = items[start_idx:end_idx]

        for i, item in enumerate(batch_items):
            actual_idx = start_idx + i
            try:
                result = function(item, actual_idx, worker_id, **kwargs)
                batch_results.append((actual_idx, result))
            except Exception as e:
                logging.info(
                    "[red]Error in worker %d processing item %d: %s",
                    worker_id,
                    actual_idx,
                    str(e),
                )
                batch_results.append((actual_idx, {"error": str(e), "traceback": traceback.format_exc()}))
        return batch_results

    logging.info("Starting processing with %d workers", actual_workers)
    logging.info("Total items: %d", total_items)
    for worker_id, start, end in batches:
        logging.info(
            "Worker %d assigned items %d-%d (%d items)",
            worker_id,
            start,
            end - 1,
            end - start,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=actual_workers) as executor:
        futures = []

        for worker_id, start, end in batches:
            futures.append(executor.submit(process_batch, worker_id, start, end))

        for future in concurrent.futures.as_completed(futures):
            try:
                for idx, result in future.result():
                    results[idx] = result
            except Exception as e:
                logging.info("[red]Error collecting results: %s", str(e))
                raise

    logging.info("[green]All processing completed!")
    return results
