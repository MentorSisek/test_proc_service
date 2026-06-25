import json
import queue
import sys
import threading
import traceback
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime

from config import settings

_context: ContextVar[dict] = ContextVar('log_context', default={})  # noqa: B039

_queue: queue.Queue = queue.Queue()

LEVELS = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
_min_level = LEVELS[settings.logger.level.upper()]


def _worker():
	while True:
		line = _queue.get()
		sys.stdout.write(line + '\n')
		sys.stdout.flush()
		_queue.task_done()


threading.Thread(target=_worker, daemon=True).start()


class Logger:
	def __init__(self, extra: dict | None = None):
		self._extra = extra or {}

	def _log(self, level: str, msg: str, exc_info: bool = False, **kwargs):
		if LEVELS.get(level, 0) < _min_level:
			return
		ctx = _context.get()
		trace_id = ctx.get('trace_id') or str(uuid.uuid4())
		extra = {k: v for k, v in ctx.items() if k != 'trace_id'}
		extra.update(self._extra)
		extra.update(kwargs)
		record: dict = {
			'time': datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
			'level': level,
			'trace_id': trace_id,
			'message': msg,
		}
		if extra:
			record['extra'] = extra
		if exc_info:
			record['exception'] = traceback.format_exc()
		_queue.put(json.dumps(record, ensure_ascii=False, default=str))

	def debug(self, msg: str, **kwargs):
		self._log('DEBUG', msg, **kwargs)

	def info(self, msg: str, **kwargs):
		self._log('INFO', msg, **kwargs)

	def warning(self, msg: str, **kwargs):
		self._log('WARNING', msg, **kwargs)

	def error(self, msg: str, **kwargs):
		self._log('ERROR', msg, **kwargs)

	def exception(self, msg: str, **kwargs):
		self._log('ERROR', msg, exc_info=True, **kwargs)

	def critical(self, msg: str, **kwargs):
		self._log('CRITICAL', msg, exc_info=True, **kwargs)


logger = Logger()


def set_trace_id(trace_id: str) -> None:
	_context.set({**_context.get(), 'trace_id': trace_id})
