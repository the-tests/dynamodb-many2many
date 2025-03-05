import asyncio
import uvloop

from libs.config import get_config
from libs.connection import get_connection
from libs.dynamodb import add_association, create_table, get_items

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def associcte(partition_key: str, sort_key: str = None):
    conf = get_config('config.toml')
    conn = await get_connection(conf['aws'])

    try:
        ddb_table = await create_table(
            conn,
            conf['dynamodb']['table_name'],
            (('primary_key', 'S', 'HASH'), ('sort_key', 'S', 'RANGE')),
            None,
            {'2ndry_glob_idx': ('sort_key', 'HASH')},
        )
        before = await get_items(ddb_table, partition_key, sort_key)
        await add_association(ddb_table, partition_key, sort_key)
        after = await get_items(ddb_table, partition_key, sort_key)
        return before, after
    finally:
        await conn.close()


if __name__ == '__main__':
    from sys import argv
    if len(argv) < 3:
        raise IndexError('Insert partition key value and sort key value')

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(
            associcte(argv[1], argv[2])
        )
        print(f'Result for {argv[1]} -> {argv[2]} is')
        print('==========')
        print('BEFORE', result[0])
        print('AFTER', result[1])
        print('==========')
    finally:
        loop.close()
