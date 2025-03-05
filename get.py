import asyncio
import uvloop

from libs.config import get_config
from libs.connection import get_connection
from libs.dynamodb import create_table, get_items

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def get_data(partition_key: str, sort_key: str = None):
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
        return await get_items(ddb_table, partition_key, sort_key)
    finally:
        await conn.close()


if __name__ == '__main__':
    from sys import argv
    if len(argv) < 2:
        raise IndexError('Insert partition key value')
    if len(argv) < 3:
        argv.append(None)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(
            get_data(argv[1], argv[2])
        )
        print(f'Result for {argv[1]} -> {argv[2]} is')
        print('==========')
        print(result)
        print('==========')
    finally:
        loop.close()
