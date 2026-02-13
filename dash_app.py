import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import requests
import plotly.graph_objects as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "AI Mood Chord Progression Generator"

def create_interactive_piano_figure():
    # Build two octaves of piano keys
    keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"] * 2
    fig = go.Figure()
    scatter_data = {"x": [], "y": [], "text": [], "customdata": []}

    for i, note in enumerate(keys):
        color = "white" if "#" not in note else "black"
        if color == "white":
            x0, x1 = i, i + 1
            y0, y1 = 0, 1
            key_width = 1
        else:
            x0, x1 = i, i + 0.7
            y0, y1 = 0, 0.6
            key_width = 0.7

        # Draw the piano key shape
        fig.add_shape(
            type="rect",
            x0=x0,
            x1=x1,
            y0=y0,
            y1=y1,
            line=dict(color="black"),
            fillcolor=color,
        )
        
        # Compute center point for interactive marker
        center_x = x0 + key_width / 2
        center_y = y0 + (y1 - y0) / 2

        scatter_data["x"].append(center_x)
        scatter_data["y"].append(center_y)
        scatter_data["text"].append(note)
        scatter_data["customdata"].append(note)

    # Add an invisible scatter trace on top to capture click events
    fig.add_trace(go.Scatter(
        x=scatter_data["x"],
        y=scatter_data["y"],
        mode="markers",
        marker=dict(size=20, opacity=0),  # invisible markers for click detection
        hoverinfo="text",
        text=scatter_data["text"],
        customdata=scatter_data["customdata"],
    ))
    
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=150,
        clickmode='event+select'
    )
    return fig

def get_music_theory_insights(progression):
    insights = []
    role_mapping = {
        "C": "Tonic (I) - The home chord, representing stability and resolution.",
        "Cm": "Tonic Minor (i) - The home chord in minor mode, conveying a more somber feel.",
        "D": "Supertonic (II) - A stepping-stone chord, often leading to the Dominant.",
        "Dm": "Supertonic Minor (ii) - A minor stepping-stone, commonly used in progressions.",
        "E": "Mediant (III) - A bridge chord, connecting the Tonic to the Dominant.",
        "Em": "Mediant Minor (iii) - A minor version of the bridge chord.",
        "F": "Subdominant (IV) - A preparatory chord, leading back to the Tonic.",
        "Fm": "Subdominant Minor (iv) - A minor variation of the preparatory chord.",
        "G": "Dominant (V) - The tension chord, leading back to the Tonic for resolution.",
        "Gm": "Dominant Minor (v) - A minor tension chord with a softer resolution.",
        "A": "Submediant (VI) - A relative chord, often used to shift to the minor mode.",
        "Am": "Submediant Minor (vi) - A minor relative chord, conveying warmth or sadness.",
        "B": "Leading Tone (VII) - A highly unstable chord, resolving to the Tonic.",
        "Bm": "Leading Tone Minor (vii) - A minor variation of the unstable Leading Tone.",
    }
    for chord in progression:
        role = role_mapping.get(chord, "Unknown role - This chord is not mapped in the current key.")
        insights.append(f"{chord}: {role}")
    return "\n".join(insights)

app.layout = dbc.Container(
    fluid=True,
    children=[
        # Header Section
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Chord Progression Predictor with Mood",
                    className="text-center text-primary my-4",
                    style={"fontSize": "2rem"},
                ),
                width=12,
            )
        ),
        # Input Section
        dbc.Row([
            dbc.Col([
                dbc.Label("Starting Sequence:", className="fw-bold", style={"fontSize": "0.9rem"}),
                dcc.Input(
                    id="input-sequence",
                    type="text",
                    placeholder="e.g., C,G,Am",
                    className="form-control mb-3",
                    style={"fontSize": "0.9rem"},
                ),
            ], width=4),
            dbc.Col([
                dbc.Label("Number of Chords:", className="fw-bold", style={"fontSize": "0.9rem"}),
                dcc.Input(
                    id="input-steps",
                    type="number",
                    min=1,
                    step=1,
                    value=4,
                    className="form-control mb-3",
                    style={"fontSize": "0.9rem"},
                ),
            ], width=2),
            dbc.Col([
                dbc.Label("Select Mood:", className="fw-bold", style={"fontSize": "0.9rem"}),
                dcc.Dropdown(
                    id="input-mood",
                    options=[{"label": mood.capitalize(), "value": mood} for mood in ["happy", "sad", "calm", "excited", "melancholic"]],
                    placeholder="Mood",
                    className="mb-3",
                    style={"fontSize": "0.9rem"},
                ),
            ], width=3),
            dbc.Col(
                html.Div(
                    html.Button(
                        "Generate",
                        id="submit-button",
                        n_clicks=0,
                        className="btn btn-primary",
                        style={"fontSize": "1rem", "width": "100%"},
                    ),
                    className="d-grid gap-2",
                ),
                width=3,
            ),
        ], justify="center"),
        # Output Section
        dbc.Row(
            dbc.Col(
                html.Div(
                    id="output-result",
                    className="text-center text-success mt-3",
                    style={"fontSize": "1rem"},
                ),
                width=12,
            )
        ),
        # MIDI Download Link Section
        dbc.Row(
            dbc.Col(
                html.Div(id="midi-download", className="text-center mt-3"),
                width=12,
            )
        ),
        # Interactive Piano Section with Audio element
        dbc.Row([
            dbc.Col([
                html.H5("Interactive Piano", className="text-primary text-center my-3"),
                dcc.Graph(
                    id="interactive-piano-graph",
                    figure=create_interactive_piano_figure(),
                    config={"displayModeBar": False},
                    style={"height": "150px"}
                ),
                html.Div(
                    id="piano-output",
                    style={"textAlign": "center", "fontSize": "1rem", "marginTop": "10px"}
                ),
                
                html.Audio(id="midi-audio", src="", autoPlay=False, controls=False, style={"display": "none"})
            ], width=6),
        ], justify="center"),
        # Music Theory Insights Section
        dbc.Row(
            dbc.Col(
                html.Div(
                    id="theory-insights",
                    style={
                        "padding": "20px",
                        "border": "1px solid #ccc",
                        "borderRadius": "5px",
                        "backgroundColor": "#f9f9f9",
                        "marginTop": "20px",
                    },
                    children=[
                        html.H5("Music Theory Insights", className="text-primary"),
                        html.Div(
                            "Insights about the selected chords and progression will appear here.",
                            id="theory-content",
                            style={"whiteSpace": "pre-wrap", "fontSize": "14px"},
                        ),
                    ],
                ),
                width=12,
            )
        ),
    ],
)

@app.callback(
    [Output("output-result", "children"),
     Output("midi-download", "children"),
     Output("theory-content", "children")],
    Input("submit-button", "n_clicks"),
    State("input-sequence", "value"),
    State("input-steps", "value"),
    State("input-mood", "value")
)
def generate_progression(n_clicks, input_sequence, steps, mood):
    if n_clicks > 0:
        if not input_sequence or not steps or not mood:
            return "Please provide valid input for sequence, steps, and mood.", "", "No insights available."
        sequence = [chord.strip() for chord in input_sequence.split(",")]
        payload = {"sequence": sequence, "steps": steps, "mood": mood}
        try:
            response = requests.post("http://127.0.0.1:5000/generate-progression", json=payload)
            if response.status_code == 200:
                response_data = response.json()
                progression = response_data.get("full_progression", [])
                midi_file = response_data.get("midi_file", "")
                if not progression or not midi_file:
                    return "Error: Progression or MIDI generation failed.", "", "No insights available."
                midi_link = html.A(
                    "Download MIDI File",
                    href=f"http://127.0.0.1:5000/download-midi/{mood}",
                    target="_blank",
                    className="btn btn-outline-primary"
                )
                theory_insights = get_music_theory_insights(progression)
                return f"Generated Progression: {', '.join(progression)}", midi_link, theory_insights
            error_message = response.json().get("error", "Unknown error occurred.")
            return f"Error: {error_message}", "", "No insights available."
        except Exception as e:
            return f"Error connecting to backend: {str(e)}", "", "No insights available."
    return "Enter the details and click 'Generate Progression'.", "", "No insights available."

app.clientside_callback(
    '''
    function(clickData) {
        if (clickData && clickData.points && clickData.points.length > 0) {
            var note = clickData.points[0].customdata;
            var url = "/play-note/" + note;
            var audioElement = document.getElementById("midi-audio");
            audioElement.src = url;
            audioElement.play();
            return "You clicked on note: " + note;
        }
        return "Click a piano key to select a note.";
    }
    ''',
    Output("piano-output", "children"),
    Input("interactive-piano-graph", "clickData")
)

if __name__ == "__main__":
    app.run_server(debug=True)
