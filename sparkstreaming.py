from pyspark.sql import SparkSession
from pyspark.sql.functions import window, from_json, col, avg, max, min, sum
from pyspark.sql.types import StringType, StructField, StructType, DoubleType, LongType

hostname = '10.148.0.8'
port = '9092'
topic_name = 'forex'

spark = SparkSession \
    .builder \
    .appName("ForexDataProcessor") \
    .getOrCreate()

# Define the schema that matches the structure of the data in Kafka messages
schema = StructType([
    StructField("symbol", StringType()),
    StructField("price", DoubleType()),
    StructField("timestamp", LongType()),
    StructField("volume", DoubleType())
])

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{hostname}:{port}") \
    .option("subscribe", topic_name) \
    .load()

# Parse the JSON strings in the "value" column of the DataFrame
df = df.select(from_json(df.value.cast("string"), schema).alias("parsed_value"))

# Access the individual fields
df = df.select(
    col("parsed_value.symbol").alias("symbol"),
    col("parsed_value.price").alias("price"),
    (col("parsed_value.timestamp") / 1000).cast('timestamp').alias('timestamp'),  # Cast to timestamp
    col("parsed_value.volume").alias("volume")
)

# Create a window of X minute
def aggregationFunction(df,duration:int):
    windowed_df = df.groupBy(
        window(df.timestamp, f"{duration} minute"),  # Define the window
        df.symbol  # Group by symbol
    ).agg(
        avg(df.price).alias('avg_price'),  # Calculate the average price
        max(df.price).alias('max_price'),  # Calculate the maximum price
        min(df.price).alias('min_price'),  # Calculate the minimum price
        sum(df.volume).alias('total_volume')  # Calculate the total volume
    )
    return windowed_df

aggregationFunction(df,1)
aggregationFunction(df,5)
aggregationFunction(df,15)
aggregationFunction(df,30)


# Now you can write the windowed_df to a sink or perform further operations on it

