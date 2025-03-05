from datetime import datetime as dt

from typing import Iterable
from boto3.dynamodb.conditions import Key

from libs.consts import PARTITION_KEY_NAME, SORT_KEY_NAME


async def create_table(
    connection,
    table_name: str,
    # (attr_name, attr_type, key_type)
    # attr_type: 'S'|'N'|'B'
    # key_type: 'HASH'|'RANGE'
    attributes: Iterable[tuple[str, str, str]],
    # {idx_name: (attr_name, key_type)}
    local_secondary_indexes: dict[str, tuple[str, str]] | None = None,
    # {idx_name: (attr_name, key_type)}
    global_secondary_indexes: dict[str, tuple[str, str]] | None = None,
    recreate: bool = False,
):
    if table_name in [t.name async for t in connection.tables.all()]:
        if recreate:
            print('Remove existent table')
            await (await connection.Table(table_name)).delete()
        else:
            print(f'Table {table_name} already exists. Creation skipped')
            return await connection.Table(table_name)
    lsi = None
    if local_secondary_indexes:
        lsi = [
            {
                'IndexName': in_,
                'KeySchema': [
                    {
                        'AttributeName': an_and_kt[0],
                        'KeyType': an_and_kt[1],
                    },
                ],
                'Projection': {
                    'ProjectionType': 'KEYS_ONLY',
                }
            } for in_, an_and_kt in local_secondary_indexes.items()
        ]
    gsi = None
    if global_secondary_indexes:
        gsi = [
            {
                'IndexName': in_,
                'KeySchema': [
                    {
                        'AttributeName': an_and_kt[0],
                        'KeyType': an_and_kt[1],
                    },
                ],
                'Projection': {
                    'ProjectionType': 'KEYS_ONLY',
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 123,
                    'WriteCapacityUnits': 123
                },
                'OnDemandThroughput': {
                    'MaxReadRequestUnits': 123,
                    'MaxWriteRequestUnits': 123
                },
                'WarmThroughput': {
                    'ReadUnitsPerSecond': 123,
                    'WriteUnitsPerSecond': 123
                }
            } for in_, an_and_kt in global_secondary_indexes.items()
        ]
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/service-resource/create_table.html  # noqa: E501
    await connection.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': an,
                'AttributeType': at,
            } for an, at, _ in attributes
        ],
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': an,
                'KeyType': kt,
            } for an, _, kt in attributes
        ],
        BillingMode='PAY_PER_REQUEST',
        ProvisionedThroughput={
            'ReadCapacityUnits': 123,
            'WriteCapacityUnits': 123
        },
        StreamSpecification={
            'StreamEnabled': False,
        },
        SSESpecification={
            'Enabled': False,
        },
        Tags=[
            {
                'Key': 'Purpose',
                'Value': 'Test of many2many relations'
            },
        ],
        TableClass='STANDARD',
        DeletionProtectionEnabled=False,
        WarmThroughput={
            'ReadUnitsPerSecond': 123,
            'WriteUnitsPerSecond': 123
        },
        ResourcePolicy='string',
        OnDemandThroughput={
            'MaxReadRequestUnits': 123,
            'MaxWriteRequestUnits': 123
        },
        **({'LocalSecondaryIndexes': lsi} if lsi else {}),
        **({'GlobalSecondaryIndexes': gsi} if gsi else {}),
    )
    return await connection.Table(table_name)


async def add_association(table, a: str, b: str) -> None:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/table/batch_writer.html  # noqa: E501
    async with table.batch_writer(
        overwrite_by_pkeys=[PARTITION_KEY_NAME, SORT_KEY_NAME],
    ) as batch:
        for association in ((a, b), (b, a)):
            await batch.put_item(
                Item={
                    'primary_key': association[0],
                    'sort_key': association[1],
                    'created_at': int(dt.now().timestamp()),
                },
            )


async def get_items(table, partition_key: str, sort_key: str | None = None) -> dict:
    # TODO: is it possible to get both direct and reverse relations in one query?
    # e.g. if relations for Bill-0001 will be Invoice-0001 and Invoice-0002
    # how to get relations for both Invoices in one query
    if sort_key is None:
        res = await table.query(
            KeyConditionExpression=Key('primary_key').eq(partition_key),
            ReturnConsumedCapacity='TOTAL',
        )
    else:
        condition_1 = Key('primary_key').eq(partition_key)
        condition_2 = Key('sort_key').eq(sort_key)
        res = await table.query(
            KeyConditionExpression=(condition_1 & condition_2),
            ReturnConsumedCapacity='TOTAL',
        )
    print(
        'Capacity units value used for get_items operation is',
        res['ConsumedCapacity']['CapacityUnits'],
    )
    return res['Items']
