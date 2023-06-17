from .generator import DefaultIdGenerator
from .id_register import Register
from .options import IdGeneratorOptions

options = IdGeneratorOptions(worker_id=Register.get_worker_id())

id_gen = DefaultIdGenerator()
id_gen.set_id_generator(options)

__all__ = ("id_gen",)
