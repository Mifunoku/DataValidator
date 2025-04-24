import boto3, os, csv, io, uuid, datetime
import pandas as pd

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
RAW_BUCKET = os.environ["RAW_BUCKET"]
TABLE_NAME = os.environ["TABLE_NAME"]


def lambda_handler(event, context):
    # EventBridge/S3 notification supplies bucket & key
    key = event["Records"][0]["s3"]["object"]["key"]
    dataset_id = key.split("/")[1].split(".")[0]
    obj = s3.get_object(Bucket=RAW_BUCKET, Key=key)
    df = pd.read_csv(io.BytesIO(obj["Body"].read()))

    table = dynamodb.Table(TABLE_NAME)
    with table.batch_writer() as batch:
        for i, row in df.iterrows():
            pk = f"DATASET#{dataset_id}"
            sk = f"ROW#{i}"
            batch.put_item(
                Item={
                    "PK": pk,
                    "SK": sk,
                    "product_text": row["product_text"],
                    "model_category": row["model_category"],
                    "fixed_category": None,
                }
            )

    wrong = (df["product_category"] != df["model_category"]).sum()
    metrics = {
        "PK": f"DATASET#{dataset_id}",
        "SK": "METRICS",
        "total": len(df),
        "wrong_initial": int(wrong),
        "accuracy_initial": round(100 * (1 - wrong / len(df)), 2),
        "wrong_current": int(wrong),
        "accuracy_current": round(100 * (1 - wrong / len(df)), 2),
        "updated_at": datetime.datetime.utcnow().isoformat(),
    }
    table.put_item(Item=metrics)
