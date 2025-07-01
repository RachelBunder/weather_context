from dash import Dash, html, dash_table, dcc, Output, Input, callback
import plotly.express as px
import pandas as pd
import datetime as dt

app = Dash()

df = pd.read_csv("../../explore/IDCJAC0010_066062_1800_Data.csv")
df['date'] = df.apply(lambda x: dt.datetime(year=x['Year'], month=x["Month"], day=x['Day']), axis=1)

# Requires Dash 2.17.0 or later
app.layout = [
    html.Div(children='Weather Context'),
    dcc.DatePickerSingle(
        id='date-picker',
        min_date_allowed=dt.date(1995, 8, 5),
        max_date_allowed=dt.date(2017, 9, 19),
        initial_visible_month=dt.date(2017, 8, 5),
        date=dt.date(2017, 8, 25),
        clearable=False,
        display_format="DD-MM-YYYY"
    ),
    dcc.Graph(figure={}, id="max_temp_dist_plot"),
    dash_table.DataTable(data=[], page_size=10, id="max_temp_table")
]

@callback(
    Output('max_temp_dist_plot', 'figure'),
    Output('max_temp_table', 'data'),
    Input('date-picker', 'date'))
def update_output(date_value):
    string_prefix = 'You have selected: '
    if date_value is not None:
        date_object = dt.date.fromisoformat(date_value)
        month = date_object.month
        day = date_object.day
        year= date_object.year

        today = df[(df["Month"]==month)&(df["Day"]==day)]

        today["Time"] = "Historical"
        today.loc[today['Year']==year, "Time"] = "Today"

        plot = px.scatter(today, x="Year", y="Maximum temperature (Degree C)", color="Time")
        
        # format table output
        output_df = today[["Year", "Month", "Day", "Maximum temperature (Degree C)"]]
        output_df = output_df.sort_values("Maximum temperature (Degree C)")
        output_dict = output_df.to_dict('records')
        return plot, output_dict

if __name__ == '__main__':
    app.run(debug=True)