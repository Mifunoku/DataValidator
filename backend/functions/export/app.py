import boto3, csv, io, os, json, datetime

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
RESULT_BUCKET = os.environ["RESULT_BUCKET"]
TABLE_NAME = os.environ["TABLE_NAME"]


def lambda_handler(event, context):
    dataset_id = json.loads(event["Records"][0]["body"])["dataset_id"]
    table = dynamodb.Table(TABLE_NAME)

    rows = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={":pk": f"DATASET#{dataset_id}", ":prefix": "ROW#"},
    )["Items"]

    out_key = f"results/{dataset_id}.csv"
    with io.StringIO() as fp:
        writer = csv.DictWriter(fp, fieldnames=["product_text", "model_category", "fixed_category"])
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "product_text": r["product_text"],
                    "model_category": r["model_category"],
                    "fixed_category": r["fixed_category"] or "",
                }
            )
        s3.put_object(Body=fp.getvalue(), Bucket=RESULT_BUCKET, Key=out_key)

    url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": RESULT_BUCKET, "Key": out_key}, ExpiresIn=60 * 60
    )
    table.update_item(
        Key={"PK": f"DATASET#{dataset_id}", "SK": "METRICS"},
        UpdateExpression="SET download_url = :url, finished_at = :ts",
        ExpressionAttributeValues={":url": url, ":ts": int(datetime.datetime.utcnow().timestamp())},
    )
