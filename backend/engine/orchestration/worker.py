"""Worker pool for job execution."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from .executor import JobExecutor, ExecutorConfig

logger = logging.getLogger("neura.orchestration.worker")


@dataclass
class WorkerPoolConfig:
    """Configuration for worker pool."""

    num_workers: int = 4
    queue_size: int = 100
    shutdown_timeout_seconds: float = 30.0


class WorkerPool:
    """Pool of workers for processing jobs.

    Workers pull jobs from a queue and execute them.
    """

    def __init__(
        self,
        executor: JobExecutor,
        config: Optional[WorkerPoolConfig] = None,
    ) -> None:
        self._executor = executor
        self._config = config or WorkerPoolConfig()
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=self._config.queue_size)
        self._workers: list[asyncio.Task] = []
        self._shutdown = False

    async def start(self) -> None:
        """Start the worker pool."""
        if self._workers:
            return

        self._shutdown = False

        for i in range(self._config.num_workers):
            worker = asyncio.create_task(
                self._worker_loop(i),
                name=f"worker-{i}",
            )
            self._workers.append(worker)

        logger.info(
            "worker_pool_started",
            extra={
                "event": "worker_pool_started",
                "num_workers": len(self._workers),
            },
        )

    async def stop(self) -> None:
        """Stop the worker pool gracefully."""
        self._shutdown = True

        # Cancel all workers
        for worker in self._workers:
            worker.cancel()

        # Wait for workers to finish
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)

        self._workers = []

        logger.info("worker_pool_stopped", extra={"event": "worker_pool_stopped"})

    async def submit(self, job) -> None:
        """Submit a job to the pool."""
        if self._shutdown:
            raise RuntimeError("Worker pool is shutting down")

        await self._queue.put(job)

        logger.debug(
            "job_queued",
            extra={
                "job_id": job.job_id,
                "queue_size": self._queue.qsize(),
            },
        )

    async def _worker_loop(self, worker_id: int) -> None:
        """Worker loop that processes jobs."""
        logger.debug(
            "worker_started",
            extra={"worker_id": worker_id, "event": "worker_started"},
        )

        try:
            while not self._shutdown:
                try:
                    # Get job from queue with timeout
                    job = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=1.0,
                    )
                except asyncio.TimeoutError:
                    continue

                try:
                    await self._executor.submit(job)
                except Exception:
                    logger.exception(
                        "worker_job_failed",
                        extra={
                            "worker_id": worker_id,
                            "job_id": job.job_id,
                        },
                    )
                finally:
                    self._queue.task_done()

        except asyncio.CancelledError:
            pass
        finally:
            logger.debug(
                "worker_stopped",
                extra={"worker_id": worker_id, "event": "worker_stopped"},
            )

    @property
    def queue_size(self) -> int:
        """Get current queue size."""
        return self._queue.qsize()

    @property
    def is_running(self) -> bool:
        """Check if pool is running."""
        return bool(self._workers) and not self._shutdown
