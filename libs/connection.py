import aioboto3


async def get_connection(config: dict):
    session = aioboto3.Session()
    return await session.resource('dynamodb', **config).__aenter__()
