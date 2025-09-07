from google.cloud import storage, bigquery
import functions_framework

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    print("func Started...")

    request_json = request.get_json(silent=True)
    request_args = request.args

    bucket_name = request_json.get("bucket")
    file_name = request_json.get("file_name")
    dataset_id = request_json.get("dataset_id")
    table_id = request_json.get("table_id")

    print(request_json)
    print(request_args)

    storage_client = storage.Client()
    bq_client = bigquery.Client()

    uri = f"gs://{bucket_name}/data/{file_name}"
    table_ref = f"{bq_client.project}.{dataset_id}.{table_id}"

    print(table_ref)

    job_config = bigquery.LoadJobConfig(
        source_format = bigquery.SourceFormat.CSV,
        skip_leading_rows = 1,
        autodetect = True,
        write_disposition = bigquery.WriteDisposition.WRITE_APPEND,
    )

    load_job = bq_client.load_table_from_uri(uri, table_ref, job_config=job_config)
    load_job.result()

    
    
    print("func ended...")

    return f"Loaded {file_name} into {table_ref}"
    # if request_json and 'name' in request_json:
    #     name = request_json['name']
    # elif request_args and 'name' in request_args:
    #     name = request_args['name']
    # else:
    #     name = 'World'
    # return 'Hello {}!'.format(name)
