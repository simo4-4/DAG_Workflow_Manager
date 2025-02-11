import csv
from datetime import datetime
import logging
from typing import List
import aiohttp
import polars as pl
from pydantic import BaseModel
import asyncio

logger = logging.getLogger()


def extract_task(file_path):
    df = pl.read_csv(file_path)
    return df, len(df)

def transform_task(extracted_data):
    dropped_nulls_df = extracted_data.drop_nulls()

    date_time_converted_df = dropped_nulls_df.with_columns(
        pl.col("lastTransactionUtcTs").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").alias("LAST_TRANSACTION_TS")
    )

    member_aggregated_df = date_time_converted_df.group_by("memberId").agg([
        (pl.col("lastTransactionPointsBought").sum() / pl.len()).alias("AVG_POINTS_BOUGHT"),
        (pl.col("lastTransactionRevenueUSD").sum() / pl.len()).alias("AVG_REVENUE_USD"),
        (pl.col("lastTransactionType")
                .filter(pl.col("lastTransactionType") == "gift")
                .len()
        / pl.len())
                .alias("PCT_GIFT_TRANSACTIONS"),
        (pl.col("lastTransactionType")
                .filter(pl.col("lastTransactionType") == "redeem")
                .len()
        / pl.len())
                .alias("PCT_REDEEM_TRANSACTIONS"),
        (pl.col("lastTransactionType")
                .filter(pl.col("lastTransactionType") == "buy")
                .len()
        / pl.len())
                .alias("PCT_BUY_TRANSACTIONS")
    ])

    member_time_sorted_df = date_time_converted_df.sort(by=["memberId", "LAST_TRANSACTION_TS"], descending=[False, False])

    current_day = datetime.utcnow()
    member_aggregated_df_last_3 = member_time_sorted_df.group_by("memberId").agg([
        pl.col("lastTransactionPointsBought").tail(3).mean().alias("LAST_3_TRANSACTIONS_AVG_POINTS_BOUGHT"),
        pl.col("lastTransactionRevenueUSD").tail(3).mean().alias("LAST_3_TRANSACTIONS_AVG_REVENUE_USD"),
        (pl.lit(current_day).cast(pl.Datetime) - (pl.first("LAST_TRANSACTION_TS"))).dt.total_days().alias("DAYS_SINCE_LAST_TRANSACTION")
    ])

    joined_member_df = member_aggregated_df_last_3.join(member_aggregated_df, on="memberId", how="left")

    transformed_df = joined_member_df

    return transformed_df, len(transformed_df)
    
def combiner_task(*results, output_format: type[BaseModel]):
    zipped_results = zip(*results)
    validated_results = [dict(zip(output_format.model_fields.keys(), values)) for values in zipped_results]
    return validated_results, len(validated_results)

# def load_task(*args):
#     # Placeholder for load task
#     return "", 0

def load_task(transform_result: pl.DataFrame, ats_resp_result: List, offer_result: List, output_file="output.csv"):
    logger.info(f"Writing transformed data to {output_file}")
    transform_result.write_csv(output_file)
    return "load", len(transform_result)