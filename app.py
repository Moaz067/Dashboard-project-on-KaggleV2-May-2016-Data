import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback,dash_table
import os
pie_colors = [ "#0D47A1", "#1976D2", "#42A5F5",
    "#90CAF9", "#B0BEC5", "#78909C",
    "#546E7A", "#263238"]
age_colors = [
    "#FF00FF", "#E35454", "#FF895D",
    "#C75643", "#FFD700", "#FF69B4",
]

medical_blues_greens = [
    "#2E86AB",  # Deep medical blue
    "#5FA8D3",  # Light blue
    "#A7C7E7",  # Very light blue
    "#6AB187",  # Green-blue
    "#88D498",  # Light green
    "#B5EAD7"   # Mint green
]
attendance_medical = [
    "#4CB8B8",  # Attended
    "#9AD1D4",  # Mild attendance
    "#E0F2F1",  # Very light green
    "#F9F9F9",  # Neutral
    "#E57373",  # Missed appointment
    "#D32F2F"   # critical
]



for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# read the file
df = pd.read_csv("\KaggleV2-May-2016.csv")


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


# Create age bins for slider
age_bins = [0, 18, 30, 45, 60, 75, 100]
age_labels = ['0-17', '18-29', '30-44', '45-59', '60-74', '75+']


#dash

# Initialize Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("Medical Appointment Analytics Dashboard",
                style={'textAlign': 'center', 'color': 'black', 'fontSize': '36px', 'marginBottom': '30px'})
    ]),
    dcc.Tabs(
        id="main-tabs",
        value="all",
        children=[
            dcc.Tab(
                label='All Patients',
                value='all',
                style={'backgroundColor': '#61B4FF', 'color': '#C0EEF2'},
                selected_style={'backgroundColor': '#004F80', 'color': 'white'}
            ),
            dcc.Tab(
                label='Male Patients',
                value='male',
                style={'backgroundColor': '#61B4FF', 'color': '#C0EEF2'},
                selected_style={'backgroundColor': '#004F80', 'color': 'white'}
            ),
            dcc.Tab(
                label='Female Patients',
                value='female',
                style={'backgroundColor': '#61B4FF', 'color': '#C0EEF2'},
                selected_style={'backgroundColor': '#004F80', 'color': 'white'}
            ),
        ],
        style={'marginBottom': '20px'}),
    html.Div([
        html.Div([
            html.Label("Age Range :",style={'color': 'white', 'fontSize': '16px', 'marginBottom': '10px'}),
            dcc.RangeSlider(
                id = 'age-slider',
                min=0,
                max=100,
                step=1,
                marks={i: str(i) for i in range(0, 101, 20)},
                value = [0, 100],
                tooltip={"placement": "bottom", "always_visible": True}
            )],style={'width': '48%', 'display': 'inline-block', 'marginBottom': '20px'}),
        html.Div([html.Label("Neighborhood:", style={'color': '#212121', 'fontSize': '20px', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='neighborhood-dropdown',
                options=[{'label': 'All Neighborhoods', 'value': 'all'}] +
                        [{'label': neighborhood, 'value': neighborhood} for neighborhood in df['Neighbourhood'].unique()],
                value='all',
                style={'backgroundColor': 'White', 'color': 'black'}
            )
        ], style={'width': '48%', 'float': 'right', 'marginBottom': '20px'}),
    ], style={'marginBottom': '30px'}),
    html.Div(id="tab-content")

], style={'backgroundColor': '#E8E8E8', 'padding': '20px', 'minHeight': '100vh'})

def attendance_overview(filtered_df):
    yes_att = filtered_df[filtered_df['Attendance'] == 'Yes'].shape[0]
    no_att = filtered_df[filtered_df['Attendance'] == 'No'].shape[0]

    attendance_df = pd.DataFrame({
        'Attendance': ['Yes', 'No'],
        'Count': [yes_att, no_att]
    })
    fig_attendance_bar = px.bar(attendance_df,
                                x='Attendance',
                                y='Count',
                                color='Attendance',
                                color_discrete_sequence=pie_colors[:2],
                                title='Overall Attendance Distribution'
                                )
    fig_attendance_bar.update_layout(
        height=400,
        title_font=dict(size=20, color=pie_colors[0]),
        title_x=0.5
    )

    fig_attendance_pie = px.pie(attendance_df,
                                names='Attendance',
                                values='Count',
                                title='Attendance Percentage',
                                color_discrete_sequence=[pie_colors[1], pie_colors[3]],
                                )
    fig_attendance_pie.update_layout(
        height=400,
        title_font=dict(size=20, color=pie_colors[1]),
        title_x=0.5
    )

    return fig_attendance_bar, fig_attendance_pie


def age_analysis(filtered_df):
    age_attendance = filtered_df.groupby(['Age', 'Attendance']).size().reset_index(name='Count')

    fig_age = px.bar(age_attendance,
                     x='Age',
                     y='Count',
                     color='Attendance',
                     barmode='group',
                     title='Attendance vs Age',
                     color_discrete_sequence=[age_colors[0],age_colors[3]]
                     )
    fig_age.update_layout(
        height=450,
        title_font=dict(size=20, color=age_colors[2]),
        title_x=0.5
    )

    fig_age_box = px.box(filtered_df,
                         x='Attendance',
                         y='Age',
                         title='Age Distribution by Attendance',
                         color='Attendance',
                         color_discrete_sequence=age_colors[1:3])
    fig_age_box.update_layout(
        height=450,
        title_font=dict(size=20, color=age_colors[3]),
        title_x=0.5
    )
    return fig_age, fig_age_box

def day_analysis(filtered_df):
    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    filtered_df['day'] = pd.Categorical(filtered_df['day'], categories=ordered_days, ordered=True)
    attendance_by_day = filtered_df.groupby(['day', 'Attendance'], observed=True).size().reset_index(name='Count')

    fig_day = px.bar(
        attendance_by_day,
        x='day',
        y='Count',
        color='Attendance',
        barmode='group',
        title='Attendance vs Absence by Day of Week',
        color_discrete_sequence=attendance_medical,
    )
    fig_day.update_layout(
        height=450,
        title_font=dict(size=20, color=attendance_medical[1]),
        title_x=0.5
    )
    return fig_day

def medical_analysis(filtered_df):
    attendance_per_disease = filtered_df.groupby(
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

    fig_disease = px.sunburst(df_clean,
                              path=['Attendance', 'Hipertension', 'Diabetes', 'Alcoholism', 'Handicap'],
                              values='Count',
                              title='Attendance by Medical Conditions',
                              color='Count',
                              color_continuous_scale='Blues',
                              )
    fig_disease.update_layout(
        height=500,
        title_font=dict(size=20, color='#0F117A'),
        title_x=0.5
    )
    return fig_disease

def factors(filtered_df):
    scholar_attendance = filtered_df.groupby(['Scholarship', 'Attendance']).size().reset_index(name='Count')
    fig_scholar = px.bar(scholar_attendance,
                         x='Scholarship',
                         y='Count',
                         color='Attendance',
                         barmode='group',
                         title='Attendance vs Scholarship',
                         color_discrete_sequence=age_colors[:4],
                         )
    fig_scholar.update_layout(
        height=400,
        title_font=dict(size=20, color='#d73027'),
        title_x=0.5
    )
    # SMS effect
    sms_effect = filtered_df.groupby(['SMS_received', 'Attendance']).size().reset_index(name='Count')
    fig_sms = px.bar(
        sms_effect,
        x='SMS_received',
        y='Count',
        color='Attendance',
        barmode='group',
        title='Attendance vs SMS Received',
        color_discrete_sequence=medical_blues_greens,
    )
    fig_sms.update_layout(
        height=400,
        title_font=dict(size=20, color=medical_blues_greens[0]),
        title_x=0.5
    )
    fig_delay = px.histogram(
        filtered_df,
        x='DelayDays',
        color='Attendance',
        nbins=30,
        barmode='overlay',
        title='Scheduling and Appointment Attendance',
        color_discrete_sequence=age_colors,
    )
    fig_delay.update_layout(
        height=400,
        title_font=dict(size=20, color=age_colors[0]),
        title_x=0.5
    )
    return fig_scholar, fig_sms, fig_delay


def statistical(filtered_df):
    age_mean = filtered_df['Age'].mean()
    age_median = filtered_df['Age'].median()
    age_std = filtered_df['Age'].std()

    fig_age = px.histogram(
        filtered_df,
        x='Age',
        nbins=30,
        color='Attendance',
        title="Age Distribution with Statistical Measures"
    )
    fig_age.add_vline(x=age_mean, line_dash="dash", line_color="red", annotation_text=f"Mean: {age_mean:.1f}")
    fig_age.add_vline(x=age_median, line_dash="dot", line_color="blue", annotation_text=f"Median: {age_median:.1f}")

    delay_stats = filtered_df.groupby('Attendance')['DelayDays'].agg(['mean', 'median', 'min', 'max']).reset_index()

    fig_delay = px.violin(
        filtered_df,
        y='DelayDays',
        x='Attendance',
        color='Attendance',
        box=True,
        points="all",
        title="Days statistical analysis"
    )

    conditions = ['Hipertension', 'Diabetes', 'Alcoholism', 'Handicap', 'SMS_received', 'Scholarship']
    stats_matrix = []

    for att in conditions:
        attend_yes = filtered_df[filtered_df[att] == 1]['Attendance'].value_counts(normalize=True).get('Yes', 0) * 100
        attend_no = filtered_df[filtered_df[att] == 0]['Attendance'].value_counts(normalize=True).get('Yes', 0) * 100
        stats_matrix.append([attend_yes, attend_no])

    fig_heatmap = px.imshow(
        stats_matrix,
        x=['Has Condition', 'No Condition'],
        y=conditions,
        color_continuous_scale='RdYlBu',
        title="Attendance Rate Heatmap by Medical Conditions"
    )
    return fig_age, fig_delay, fig_heatmap, (age_mean, age_median, age_std), delay_stats
@callback(
    Output("tab-content", "children"),
    [Input("main-tabs", "value"),
     Input("age-slider", "value"),
     Input("neighborhood-dropdown", "value")]
)
def update_content(active_tab, age_range, neighborhood):
    # Filter data based on inputs
    filtered_df = df.copy()

    # Filter by tab (gender)
    if active_tab == "male":
        filtered_df = filtered_df[filtered_df['Gender'] == 'Male']
    elif active_tab == "female":
        filtered_df = filtered_df[filtered_df['Gender'] == 'Female']

    # Filter by age range
    filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]

    # Filter by neighborhood
    if neighborhood != 'all':
        filtered_df = filtered_df[filtered_df['Neighbourhood'] == neighborhood]

    # Create all charts
    fig_att_bar, fig_att_pie = attendance_overview(filtered_df)
    fig_age, fig_age_box = age_analysis(filtered_df)
    fig_day = day_analysis(filtered_df)
    fig_disease = medical_analysis(filtered_df)
    fig_scholar, fig_sms, fig_delay = factors(filtered_df)
    fig_age_dist, fig_delay_violin, fig_heatmap, age_stats, delay_stats = statistical(filtered_df)

    # Create summary stats
    total_patients = len(filtered_df)
    attendance_rate = (len(
        filtered_df[filtered_df['Attendance'] == 'Yes']) / total_patients * 100) if total_patients > 0 else 0
    avg_age = filtered_df['Age'].mean() if total_patients > 0 else 0

    total_appointments = len(filtered_df['AppointmentID'])
    tab_title = f"{'All Patients' if active_tab == 'all' else (active_tab.title() + ' Patients')} Analysis"

    return html.Div([
        html.Div([
            html.Div([
                html.H3(f"{total_patients:,}", style={'color': 'black', 'margin': '0'}),
                html.P("Total Patients", style={'color': 'black', 'margin': '0'})
            ], className="stat-box",
                style={'textAlign': 'center', 'backgroundColor': '#2b2b2b', 'padding': '20px', 'borderRadius': '10px',
                       'width': '30%', 'display': 'inline-block', 'margin': '1.5%'}),

            html.Div([
                html.H3(f"{attendance_rate:.1f}%", style={'color': age_colors[1], 'margin': '0'}),
                html.P("Attendance Rate", style={'color': 'black', 'margin': '0'})
            ], className="stat-box",
                style={'textAlign': 'center', 'backgroundColor': '#2b2b2b', 'padding': '20px', 'borderRadius': '10px',
                       'width': '30%', 'display': 'inline-block', 'margin': '1.5%'}),

            html.Div([
                html.H3(f"{avg_age:.1f}", style={'color': attendance_medical[2], 'margin': '0'}),
                html.P("Average Age", style={'color': 'black', 'margin': '0'})
            ], className="stat-box",
                style={'textAlign': 'center', 'backgroundColor': '#2b2b2b', 'padding': '20px', 'borderRadius': '10px',
                       'width': '30%', 'display': 'inline-block', 'margin': '1.5%'}),
            html.Div([
                html.H3(f"{total_appointments:,}", style={'color': '#4CAF50', 'margin': '0'}),
                html.P("Total Appointments", style={'color': 'black', 'margin': '0'})
            ], className="stat-box",
                style={'textAlign': 'center', 'backgroundColor': '#2b2b2b', 'padding': '20px', 'borderRadius': '10px',
                       'width': '22%', 'display': 'inline-block', 'margin': '1.5%'})
        ], style={'marginBottom': '30px'}),

        # Attendance Overview
        html.H2("Attendance Overview", style={'color': 'black', 'textAlign': 'center', 'marginBottom': '20px'}),
        html.Div([
            html.Div([dcc.Graph(figure=fig_att_bar)], style={'width': '50%', 'display': 'inline-block'}),
            html.Div([dcc.Graph(figure=fig_att_pie)], style={'width': '50%', 'display': 'inline-block'})
        ]),

        # Age Analysis
        html.H2("Age Analysis",
                style={'color': 'black', 'textAlign': 'center', 'marginTop': '30px', 'marginBottom': '20px'}),
        html.Div([
            html.Div([dcc.Graph(figure=fig_age)], style={'width': '50%', 'display': 'inline-block'}),
            html.Div([dcc.Graph(figure=fig_age_box)], style={'width': '50%', 'display': 'inline-block'})
        ]),
        # Day of Week Analysis
        html.H2("Day of Week Analysis",
                style={'color': 'black', 'textAlign': 'center', 'marginTop': '30px', 'marginBottom': '20px'}),
        dcc.Graph(figure=fig_day),
        html.H2("Medical Conditions Analysis",
                style={'color': 'black', 'textAlign': 'center', 'marginTop': '30px', 'marginBottom': '20px'}),
        dcc.Graph(figure=fig_disease),
        # Statistical
        html.H2("Statistical",
                style={'color': 'black', 'textAlign': 'center', 'marginTop': '30px', 'marginBottom': '20px'}),
        html.Div([
            html.Div([dcc.Graph(figure=fig_age_dist)], style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'width': '100%'
    }),
        ]),

        # Detailed Statistics Table
        html.H3("Delay Statistics by Attendance",
                style={'color': 'black', 'textAlign': 'center', 'marginTop': '30px', 'marginBottom': '20px'}),
        html.Div([
            dash_table.DataTable(
                data=delay_stats.to_dict('records'),
                columns=[{"name": i, "id": i, "type": "numeric", "format": {"specifier": ".2f"}} for i in
                         delay_stats.columns],
                style_cell={'textAlign': 'center', 'backgroundColor': '#007CB9', 'color': 'white'},
                style_header={'backgroundColor': '#005689', 'color': attendance_medical[3], 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#005689'},
                style_table={'margin': 'auto', 'width': '80%'}
            )
        ], style={'marginBottom': '30px'}),
        # Other Factors
        html.H2("Other Factors",
                style={'color': 'black', 'textAlign': 'center', 'marginTop': '30px', 'marginBottom': '20px'}),
        html.Div([
            html.Div([dcc.Graph(figure=fig_scholar)], style={'width': '33%', 'display': 'inline-block'}),
            html.Div([dcc.Graph(figure=fig_sms)], style={'width': '33%', 'display': 'inline-block'}),
            html.Div([dcc.Graph(figure=fig_delay)], style={'width': '33%', 'display': 'inline-block'})
        ])
    ])
if __name__ == '__main__':

    app.run(debug=True)
