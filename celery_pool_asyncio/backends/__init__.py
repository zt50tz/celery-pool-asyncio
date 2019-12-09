from . import amqp
from . import rpc

from ..environment_variables import monkey_available


def patch_backends():
    if monkey_available('AMQP_BACKEND'):
        amqp.patch_backend()

    if monkey_available('RPC_BACKEND'):
        rpc.patch_backend()
