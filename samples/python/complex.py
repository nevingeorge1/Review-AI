"""Complex Python sample module featuring classes, async functions, deep nesting, and control flow."""

import asyncio
from typing import Dict, List, Optional


class BaseTaskRunner:
    """Base class for asynchronous task workers."""

    def __init__(self, worker_name: str) -> None:
        self.worker_name = worker_name
        self.processed_count: int = 0

    def get_stats(self) -> Dict[str, int]:
        """Return worker statistics."""
        return {"processed": self.processed_count}


class DataPipeline(BaseTaskRunner):
    """Data processing pipeline with high cyclomatic complexity and nested loops."""

    def __init__(self, worker_name: str, batch_size: int = 10) -> None:
        super().__init__(worker_name)
        self.batch_size = batch_size
        self.results: List[Dict[str, int]] = []

    async def process_batch(self, items: List[int], strict: bool = False) -> List[int]:
        """Process item batches with branching, error handling, and loops."""
        transformed: List[int] = []

        try:
            for item in items:
                if item > 0:
                    if item % 2 == 0:
                        transformed.append(item * 2)
                    else:
                        transformed.append(item + 1)
                elif item < 0:
                    if strict:
                        raise ValueError(f"Negative value rejected: {item}")
                    transformed.append(abs(item))
                else:
                    transformed.append(0)

                self.processed_count += 1
        except Exception as err:
            if strict:
                raise err
            print(f"Error encountered: {err}")

        return transformed
