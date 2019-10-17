from . import amqp
from . import rpc


def patch_backends():
    amqp.patch_backend()
    rpc.patch_backend()
