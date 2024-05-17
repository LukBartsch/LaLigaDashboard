import time
import os

from dash import (
    Dash,
    DiskcacheManager,
    CeleryManager,
    Input,
    Output,
    html,
    dcc,
    callback,
    set_props,
)

import dash_ag_grid as dag

from plotly.express import data


options = [0]
counter = 0

if "REDIS_URL" in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery

    celery_app = Celery(
        __name__, broker=os.environ["REDIS_URL"], backend=os.environ["REDIS_URL"]
    )
    background_callback_manager = CeleryManager(celery_app)

else:
    # Diskcache for non-production apps when developing locally
    import diskcache

    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)

app = Dash(background_callback_manager=background_callback_manager)

app.layout = [
    html.H2(id='table-title', children="Tytuł strony"),
    html.Button(id="button_id", children="Get data"),
    html.Button(id="cancel_button_id", children="Cancel Running Job!"),
    dcc.Dropdown(
        id = 'id-dropdown',
        options = options,
        value = 0,
        clearable = False
    ),
    dag.AgGrid(
        id="ag-grid-updating",
        dashGridOptions={
            "pagination": True,
        },
    ),
]


@callback(
    Input("button_id", "n_clicks"),
    #Input("table-title", "children"),
    background=True,
    running=[
        (Output("button_id", "disabled"), True, False),
        (Output("cancel_button_id", "disabled"), False, True),
    ],
    cancel=[Input("cancel_button_id", "n_clicks")],
)
def update_progress(n_clicks):
    df = data.gapminder()
    columnDefs = [{"field": col} for col in df.columns]
    # Simulate 100 rows of data being returned every 2 seconds
    rows_per_step = 100
    total_rows = len(df)

    #while total_rows > 0:
    options = [0]
    for i in range(0, 5):
        end = len(df) - total_rows + rows_per_step
        total_rows -= rows_per_step
        time.sleep(2)
        
        set_props(
            "ag-grid-updating",
            {"rowData": df[:end].to_dict("records"), "columnDefs": columnDefs},
        )

        
        options.append(i)


        set_props("id-dropdown",
                  {"options": options}
        )


if __name__ == "__main__":
    app.run(debug=True)
