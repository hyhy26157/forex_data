from pyspark.sql import SparkSession
from pyspark.sql.functions import window, from_json, col, avg, max, min, sum, count
from pyspark.sql.types import StringType, StructField, StructType, DoubleType, TimestampType


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
    StructField("volume", DoubleType()),
    StructField("timestamp", TimestampType())
])

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{hostname}:{port}") \
    .option("subscribe", topic_name) \
    .load()

# Parse the JSON strings in the "value" column of the DataFrame
stocks = df.select(from_json(df.value.cast("string"), schema).alias("parsed_value"))

# Access the individual fields
# watermark of 60 seconds indicate the age of the data that kafka is willing to hold. 
# if your data is streaming once >60 seconds, you will not get back any data because its deem as old. allowing kafka to just move on.
# without bothering with the old data
row = stocks.select(
    col("parsed_value.symbol").alias("symbol"),
    col("parsed_value.price").alias("price"),
    col("parsed_value.timestamp").alias('timestamp'),  # Cast to timestamp
    col("parsed_value.volume").alias("volume")
).withWatermark("timestamp", "60 seconds")

# Define the sliding window function
# the groupby function group the window df by timestamp of 60 seconds and by symbol column. data is filtered by time, followed by the symbol.

def perform_window(df):
    windowed_df = df \
        .groupBy(window(col("timestamp"), "60 seconds"), col("symbol")) \
        .agg(avg("price").alias("price"), min("price").alias("minPrice"), max("price").alias("maxPrice"), count("price").alias("count")) \
        .select("window.start", "window.end", "symbol", "price", "minPrice", "maxPrice", "count")
    return windowed_df

# Apply sliding window function to stocks dataset
aggregates = perform_window(row)

# Print the schema of the resultant DataFrame
aggregates.printSchema()

# Write the window processing output to the console
writeToConsole = aggregates \
    .writeStream \
    .format("console") \
    .option("truncate", "false") \
    .queryName("kafka spark streaming console") \
    .outputMode("append") \
    .start()

# Write the moving averages into another Kafka topic
writeToKafka = aggregates \
    .selectExpr("CAST(symbol AS STRING) AS key", "to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{hostname}:{port}") \
    .option("topic", "forex_averages") \
    .option("checkpointLocation", "/tmp/sparkcheckpoint/") \
    .queryName("kafka spark streaming kafka") \
    .outputMode("append") \
    .start()

# Wait for the termination of the streams
spark.streams.awaitAnyTermination()

