import asyncio
from datetime import datetime as dt
import uvloop
from random import randint

from libs.config import get_config
from libs.consts import PARTITION_KEY_NAME, SECONDARY_IDX_NAME, SORT_KEY_NAME
from libs.connection import get_connection
from libs.dynamodb import create_table, add_association

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def prepare_data(create_data: bool = False, clean_data: bool = False):
    conf = get_config('config.toml')
    conn = await get_connection(conf['aws'])

    try:
        ddb_table = await create_table(
            conn,
            conf['dynamodb']['table_name'],
            ((PARTITION_KEY_NAME, 'S', 'HASH'), (SORT_KEY_NAME, 'S', 'RANGE')),
            None,
            {SECONDARY_IDX_NAME: (SORT_KEY_NAME, 'HASH')},
            recreate=clean_data,
        )

        if create_data:
            invoices = [f'Invoice-{i:04d}' for i in range(1, conf['data']['num_of_invoices'] + 1)]
            bills = [f'Bill-{i:04d}' for i in range(1, conf['data']['num_of_bills'] + 1)]

            associations = []

            for _ in range(conf['data']['num_of_associations']):
                associations.append(
                    (
                        randint(0, conf['data']['num_of_bills'] - 1),
                        randint(0, conf['data']['num_of_invoices'] - 1),
                    )
                )

            start = dt.now()
            n = 0
            for bill_idx, invoice_idx in associations:
                await add_association(
                    ddb_table,
                    bills[bill_idx],
                    invoices[invoice_idx],
                )
                n += 1
                if n % int(len(associations) / 10) == 0:
                    print(f'{n} associations created')
            print(f'All assotiations created in {(dt.now() - start).total_seconds()} seconds')
    finally:
        await conn.close()


if __name__ == '__main__':
    from sys import argv

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(
            prepare_data(
                argv[1].lower() in ('true', 'yes', '1') if len(argv) > 1 else False,
                argv[2].lower() in ('true', 'yes', '1') if len(argv) > 2 else False,
            )
        )
    finally:
        loop.close()
