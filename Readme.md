# Demo application illustrating many-to-many relations in dynamodb

Original topic can be found [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-adjacency-graphs.html)

## How to run

1. Install python libraries `pip install -r reqs.txt`
2. Start docker containers: `docker compose up -d`
3. Import random initial data: `python prep.py true true`
   1. First `true` create new data*
   2. Second `true` remove old data before creating new one
4. Get relations by running `python get.py Bill-0001 Invoice-0001`
   1. `Bill-0001` is a primary key value (required)
   2. `Invoice-0001` is a sort key value (optional)
5. Custom relation may be created by running `python associate.py Bill-0001 Invoice-0001`

＊ duplicated associations will be rewrited so total number of associations will be less than set in `config.toml`

## Helpful links

- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html
- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-sort-keys.html
- https://qiita.com/hshimo/items/e5ad98b21786d796f1da
- https://stackoverflow.com/questions/63005311/what-exactly-does-hash-and-range-keys-mean-in-aws-dynamodb
