import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def get_data(table_name):
    data = []
    page_size = 1000
    page = 0

    while True:
        response = (
            supabase
            .table(table_name)
            .select("*")
            .range(page * page_size, (page + 1) * page_size - 1)
            .execute()
        )

        data.extend(response.data)

        if len(response.data) < page_size:
            break

        page += 1

    return pd.DataFrame(data)