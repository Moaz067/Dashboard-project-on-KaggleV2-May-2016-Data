
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import plotly.express as px
from dash import html,dcc,Dash,dash_table
from dash.dependencies import Input, Output
app = Dash()
colors_no_show = ["#ff00ff", "#00ffff", "#ffff00", "#ff1493", "#00ff00"]
colors_age_gender = ["#ff4500", "#00ced1", "#ff69b4", "#7fff00", "#ffd700"]
colors_day_of_week = ["#9400d3", "#ff6347", "#00fa9a", "#ffdab9", "#1e90ff"]
colors_neighborhood = ["#ff00ff", "#00ffcc", "#ffcc00", "#ff3366", "#00ff99"]
color_disease = ["#ff0066", "#33ffcc", "#ffff66", "#ff9933", "#66ff33"]
colors_delay_appointments = ["#ff33ff", "#00ff66", "#66ccff", "#ffcc66", "#ff3300"]
template_style = 'plotly_dark'

import os


for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

df = pd.read_csv(r"C:\KaggleV2-May-2016.csv")
df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'], dayfirst=True)
df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'], dayfirst=True)
df['DelayDays'] = (df['AppointmentDay'] - df['ScheduledDay']).dt.days
df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay']).dt.strftime('%d-%m-%Y')
df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'], dayfirst = True)
df['day'] = df['AppointmentDay'].dt.day_name()
df = df.rename(columns={"Handcap": "Handicap"})
df['No-show'] = df['No-show'].map({'Yes' : 'No' , 'No' : 'Yes' })
df.rename(columns={"No-show" : "Attendance"},inplace = True)
df['Gender'] = df['Gender'].map({'F' : 'Female' , 'M' : 'Male' })
df.drop(columns = ["PatientId"],inplace = True)
yes_att = df[df['Attendance'] == 'Yes'].shape[0]
no_att  = df[df['Attendance'] == 'No' ].shape[0]

age_attendance = df.groupby(['Age', 'Attendance']).size().reset_index(name='Count')
attendance_df = pd.DataFrame({
    'Attendance': ['Yes', 'No'],
    'Count': [yes_att, no_att]
})
fig_attendance_bar = px.bar(attendance_df,
             x='Attendance',
             y='Count' ,
             color='Attendance',
             color_discrete_sequence=colors_no_show,
             template=template_style,
)
fig_attendance_bar.update_layout(
    height=450,
    title_font=dict(size=20, color=colors_no_show[0]),
    title_x=0.5
)
'''
1.Sum of gender and attendance , then put them in new col
2.total present and absent in one col
3.percentage of present and absent in one col
4.count male and female
5.index to Gender , gender to count
'''
gender_attendance = df.groupby(['Gender','Attendance']).size().reset_index(name = 'count of gender')
total_by_gender = gender_attendance.groupby('Gender')['count of gender'].transform('sum')
gender_attendance['percentage'] = (gender_attendance['count of gender'] / total_by_gender) * 100

# Age group attendance analysis
age_group_attendance = df.groupby(['Age','Attendance']).size().reset_index(name = 'count of age_group')
total_by_age_group = age_group_attendance.groupby('Age')['count of age_group'].transform('sum')
age_group_attendance['percentage'] = (age_group_attendance['count of age_group'] / total_by_age_group) * 100

male_vs_female = df['Gender'].value_counts().reset_index()
male_vs_female.columns = ['Gender','Count']
gender_distribution = male_vs_female.copy()

# Fixed pie charts - showing Age Groups and Gender impact on attendance
pie_charts = []

# Gender-based pie charts
genders_list = ['Male','Female']
for gender in genders_list:
    data = df[df['Gender'] == gender].groupby('Attendance').size().reset_index(name='Count')
    total = data['Count'].sum()
    if total == 0:
        data['percentage'] = 0
    else:
        data['percentage'] = (data['Count'] / total) * 100
    fig = px.pie(
        data,
        names='Attendance',
        values='percentage',
        title=f'Attendance Distribution for {gender}',
        color_discrete_sequence=colors_age_gender,
        template=template_style
    )
    fig.update_layout(height=300, width=400)
    pie_charts.append(dcc.Graph(figure=fig, id=f'pie-gender-{gender}'))
fig_gender_overall = px.pie(
    gender_distribution,
    names='Gender',
    values='Count',
    title='Overall Gender Distribution',
    color_discrete_sequence=colors_age_gender,
    template=template_style
)
fig_gender_overall.update_layout(
    height=450,
    title_font=dict(size=20, color=colors_age_gender[1]),
    title_x=0.5
)
fig_gender_overall.update_layout(
    width=500,
    height=400
)
gender_table = gender_attendance.pivot(index='Gender', columns='Attendance', values='count of gender').fillna(0)
gender_table['Total'] = gender_table.sum(axis=1)
age =age_attendance.groupby('Age').size().reset_index(name = 'Attendance')
fig_age = px.bar(age_attendance,
             x='Age',
             y='Count',
             color='Attendance',
             barmode='group',
             title='Attendance vs Age ',
             color_discrete_sequence=colors_age_gender,
             template=template_style
)
fig_age.update_layout(
    height=450,
    title_font=dict(size=20, color=colors_age_gender[2]),
    title_x=0.5
)
attendance_per_disease = df.groupby(
    ['Hipertension', 'Diabetes', 'Alcoholism', 'Handicap', 'Attendance']
).size().reset_index(name='Count')
fig_age = px.bar(age_attendance,
             x='Age',
             y='Count',
             color='Attendance',
             barmode='group',
             title='Attendance vs Age ',
             color_discrete_sequence=colors_age_gender,
             template=template_style
)
fig_age.update_layout(
    height=450,
    title_font=dict(size=20, color=colors_age_gender[2]),
    title_x=0.5
)
attendance_per_disease = df.groupby(
    ['Hipertension', 'Diabetes', 'Alcoholism', 'Handicap', 'Attendance']
).size().reset_index(name='Count')
df_clean = attendance_per_disease.copy()

df_clean['Hipertension'] = df_clean['Hipertension'].map({0: 'No Hypertension', 1: 'Has Hypertension'})
df_clean['Diabetes'] = df_clean['Diabetes'].map({0: 'No Diabetes', 1: 'Has Diabetes'})
df_clean['Alcoholism'] = df_clean['Alcoholism'].map({0: 'No Alcoholism', 1: 'Has Alcoholism'})
df_clean['Handicap'] = df_clean['Handicap'].map({
    0: 'No Handicap',
    1: 'Mild Handicap',
    2: 'Moderate Handicap',
    3: 'Severe Handicap',
    4: 'Very Severe Handicap'
})
fig_disease= px.sunburst(df_clean,
                  path=['Attendance', 'Hipertension', 'Diabetes', 'Alcoholism', 'Handicap'],
                  values='Count',
                  title='Attendance vs No-show by Disease and Handicap',
                  color='Count',
                  color_continuous_scale='Blues',
                  color_discrete_sequence=color_disease,
                  template=template_style
)
fig_disease.update_layout(
    height=450,
    title_font=dict(size=20, color='#f15bb5'),
    title_x=0.5
)
scholar_attendance = df.groupby(['Scholarship', 'Attendance']).size().reset_index(name='Count')
fig_scholar = px.bar(scholar_attendance,
             x='Scholarship',
             y='Count',
             color='Attendance',
             barmode='group',
             title='Attendance vs Scholarship ',
             color_discrete_sequence=colors_no_show,
             template=template_style
)
fig_scholar.update_layout(
    height=450,
    title_font=dict(size=20, color=colors_no_show[1]),
    title_x=0.5
)
day_counts = df.day.value_counts().reset_index()
day_counts.columns = ['day', 'Count']
ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
df['day'] = pd.Categorical(df['day'], categories=ordered_days, ordered=True)
attendance_by_day = df.groupby(['day', 'Attendance'], observed=True).size().reset_index(name='Count')
fig_day = px.bar(
    attendance_by_day,
    x='day',
    y='Count',
    color='Attendance',
    barmode='group',
    title='Attendance vs Absence by Day of Week',
    color_discrete_sequence=colors_day_of_week,
    template=template_style
)
fig_day.update_layout(
    height=450,
    title_font=dict(size=20, color=colors_day_of_week[1]),
    title_x=0.5
)
fig_dealy = px.histogram(
    df,
    x='DelayDays',
    color='Attendance',
    nbins=30,
    barmode='overlay',
    title='Effect of Delay Between Scheduling and Appointment on Attendance',
    color_discrete_sequence=colors_delay_appointments,
    template=template_style
)
fig_dealy.update_layout(
    height=450,
    title_font=dict(size=20, color=colors_delay_appointments[0]),
    title_x=0.5
)
sms_effect = df.groupby(['SMS_received', 'Attendance'], observed=True).size().reset_index(name='Count')
fig_sms = px.line(
    sms_effect,
    x='SMS_received',
    y='Count',
    color='Attendance',
    title='Attendance vs SMS Delay',
    markers=True,
    color_discrete_map={'Yes': 'green', 'No': 'red'},
    color_discrete_sequence=color_disease,
    template=template_style
)
fig_sms.update_layout(
    height=450,
    title_font=dict(size=20, color=color_disease[0]),
    title_x=0.5
)
neighborhood_attendance = df.groupby(['Neighbourhood', 'Attendance'], observed=True).size().reset_index(name='Count')
fig_neighborhood = px.bar(
    neighborhood_attendance,
    x='Neighbourhood',
    y='Count',
    color='Attendance',
    barmode='group',
    title='Attendance by Neighborhood',
    color_discrete_map={'Yes': 'green', 'No': 'red'},
    color_discrete_sequence=colors_neighborhood,
    template=template_style
)
fig_neighborhood.update_layout(
    height=450,
    title_font=dict(size=20, color=colors_neighborhood[0]),
    title_x=0.5
)
fig_box = px.box(df, y='Age', title='Box Plot of Age',template=template_style)
app = Dash(__name__)

app.layout = html.Div([

    html.H1("Medical Appointment Attendance Dashboard", style={'textAlign': 'center'}),

    # attendance bar
    html.Div(dcc.Graph(figure=fig_attendance_bar), style={'margin-bottom': '20px'}),

    # Overall Gender Pie in center
    html.Div(dcc.Graph(figure=fig_gender_overall), style={'width': '50%', 'margin': '0 auto'}),

    # Two pie charts side by side
    html.Div(
        children=[
            html.Div(pie_charts[0], style={'width': '49%', 'display': 'inline-block'}),
            html.Div(pie_charts[1], style={'width': '49%', 'display': 'inline-block', 'float': 'right'}),
        ],
        style={'display': 'flex', 'justify-content': 'space-between', 'marginTop': '20px'}
    ),
    html.H3("Gender Summary Table"),
    dash_table.DataTable(
        data=gender_table.reset_index().to_dict('records'),
        columns=[{'name': c, 'id': c} for c in gender_table.reset_index().columns],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'center',
            'padding': '6px',
            'backgroundColor': '#000000',
            'color': '#FFFFFF',
            'border': '1px solid #444444'
        },
        style_header={
            'backgroundColor': '#111111',
            'fontWeight': 'bold',
            'color': '#FFFFFF',
            'border': '1px solid #444444'
        }    ),

    # Attendance by Age (Top N)
    html.H3("Attendance by Age (Top Age)"),
    html.Div([
        dcc.Dropdown(
            id='top-n-age-dropdown',
            options=[{'label': str(i), 'value': i} for i in [5, 10, 20, 50]],
            value=10,
            clearable=False,
            style={'width': '200px'}
        )
    ], style={'margin-bottom': '20px'}),
    html.Div(dcc.Graph(id='age-graph'), style={'margin-top': '20px'}),

    # Other charts
    html.Div(dcc.Graph(figure=fig_disease), style={'margin-top': '20px'}),
    html.Div(dcc.Graph(figure=fig_scholar), style={'margin-top': '20px'}),
    html.Div(dcc.Graph(figure=fig_day), style={'margin-top': '20px'}),
    html.Div(dcc.Graph(figure=fig_dealy), style={'margin-top': '20px'}),
    html.Div(dcc.Graph(figure=fig_sms), style={'margin-top': '20px'}),
    html.Div(dcc.Graph(figure=fig_box), style={'margin-top': '20px'}),
    # Attendance by Neighborhood (Top N)
    html.H3("Attendance by Neighborhood (Top N)"),
    html.Div([
        dcc.Dropdown(
            id='top-n-dropdown',
            options=[{'label': str(i), 'value': i} for i in [5, 10, 20, 50]],
            value=10,
            clearable=False,
            style={'width': '200px'}
        ),
        dcc.Graph(id='neighborhood-graph')
    ], style={'marginTop': '10px'}),

], style={
    'maxWidth': '1200px',
    'margin': '0 auto',
    'padding': '20px',
    'backgroundColor': '#000000',
    'color': '#FFFFFF',
    'minHeight': '100vh',
})


# Callback for Neighborhood graph
@app.callback(
    Output('neighborhood-graph', 'figure'),
    Input('top-n-dropdown', 'value')
)
def update_neighborhood(top_n):
    top_neigh = neighborhood_attendance.groupby('Neighbourhood')['Count'].sum().nlargest(top_n).index
    filtered = neighborhood_attendance[neighborhood_attendance['Neighbourhood'].isin(top_neigh)]
    fig = px.bar(filtered, x='Neighbourhood', y='Count', color='Attendance', barmode='group',
                 title=f'Attendance by Neighborhood (Top {top_n})')
    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    return fig


# Callback for Age graph
@app.callback(
    Output('age-graph', 'figure'),
    Input('top-n-age-dropdown', 'value')
)
def update_age_graph(top_n):
    top_age = age_attendance.groupby('Age')['Count'].sum().nlargest(top_n).index
    filtered = age_attendance[age_attendance['Age'].isin(top_age)]
    fig = px.bar(
        filtered,
        x='Age',
        y='Count',
        color='Attendance',
        barmode='group',
        title=f'Attendance by Age (Top {top_n})',
        color_discrete_sequence=colors_age_gender,
        template=template_style
    )
    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    return fig


if __name__ == '__main__':
    app.run(debug=True)
