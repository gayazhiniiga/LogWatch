
import hashlib
from io import StringIO
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from main import analyze_login_logs


st.set_page_config(
    page_title="LogWatch",
    layout="wide",
)

is_dark_theme = st.context.theme.type == "dark"
theme_palette = {
    "text": "#E7EDF5" if is_dark_theme else "#202B3C",
    "muted": "#A9B6C7" if is_dark_theme else "#687486",
    "teal_bright": "#42AFA4" if is_dark_theme else "#278C81",
    "chart_grid": (
        "rgba(148,163,184,0.16)"
        if is_dark_theme
        else "rgba(104,116,134,0.16)"
    ),
    "chart_hover_surface": "#17243A" if is_dark_theme else "#F8F7F2",
}


st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&display=swap" rel="stylesheet">
""")

st.markdown("""
<style>
  @property --lw-grid-row {
    syntax: "<color>";
    inherits: true;
    initial-value: #F8F7F2;
  }

  @property --lw-grid-header {
    syntax: "<color>";
    inherits: true;
    initial-value: #E9E6DD;
  }

  @property --lw-grid-header-hover {
    syntax: "<color>";
    inherits: true;
    initial-value: #E2DED4;
  }

  @property --lw-grid-text {
    syntax: "<color>";
    inherits: true;
    initial-value: #202B3C;
  }

  @property --lw-grid-muted {
    syntax: "<color>";
    inherits: true;
    initial-value: #687486;
  }

  @property --lw-grid-border {
    syntax: "<color>";
    inherits: true;
    initial-value: #D8D5CC;
  }

  html,
  body,
  .stApp,
  .stApp * {
    font-family: "Source Sans Pro", "Segoe UI", Arial, sans-serif !important;
  }

  .logwatch-brand,
  .logwatch-brand * {
    font-family: "Libre Baskerville", Georgia, "Times New Roman", serif !important;
  }

  .logwatch-header-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: fit-content;
    max-width: 100%;
  }

  .stApp {
    --lw-page: light-dark(#F1EFE8, #0E1A2B);
    --lw-page-gradient:
      radial-gradient(
        ellipse at 12% 0%,
        light-dark(transparent, rgba(53, 168, 155, 0.075)),
        transparent 38%
      ),
      linear-gradient(
        160deg,
        light-dark(transparent, rgba(21, 36, 57, 0.3)),
        transparent 58%
      );
    --lw-sidebar: light-dark(#E9E6DD, #111F32);
    --lw-sidebar-gradient: linear-gradient(
      180deg,
      light-dark(#EEECE4, #142238) 0%,
      light-dark(#E9E6DD, #111F32) 54%,
      light-dark(#E9E6DD, #101D2F) 100%
    );
    --lw-surface: light-dark(#F8F7F2, #17243A);
    --lw-control: light-dark(#F7F5EF, #142338);
    --lw-text: light-dark(#202B3C, #E7EDF5);
    --lw-muted: light-dark(#687486, #A9B6C7);
    --lw-border: light-dark(#D8D5CC, #34465E);
    --lw-sidebar-border: light-dark(#D8D5CC, rgba(119, 146, 174, 0.18));
    --lw-sidebar-control: light-dark(#F1EFE8, #142338);
    --lw-teal: light-dark(#287A70, #64B5AC);
    --lw-teal-bright: light-dark(#278C81, #42AFA4);
    --lw-coral: light-dark(#A9564E, #D98F87);
    --lw-coral-soft: rgba(203, 122, 113, 0.14);
    --lw-chart-axis-text: light-dark(#202B3C, #A9B6C7);
    --lw-chart-title-text: light-dark(#202B3C, #E7EDF5);
    --lw-grid-row: light-dark(#F8F7F2, #142338);
    --lw-grid-header: light-dark(#E9E6DD, #17243A);
    --lw-grid-header-hover: light-dark(#E2DED4, #22344E);
    --lw-grid-text: light-dark(#202B3C, #E7EDF5);
    --lw-grid-muted: light-dark(#687486, #A9B6C7);
    --lw-grid-border: light-dark(#D8D5CC, #34465E);
    --lw-slider-track: light-dark(
      rgba(102, 112, 133, 0.24),
      rgba(148, 163, 184, 0.3)
    );
    --lw-metric-gradient: linear-gradient(
      145deg,
      light-dark(rgba(39, 140, 129, 0.045), rgba(53, 168, 155, 0.1)),
      light-dark(rgba(248, 247, 242, 0.98), rgba(23, 36, 58, 0.94)) 58%,
      light-dark(rgba(248, 247, 242, 0.98), rgba(20, 32, 51, 0.98))
    );
    --lw-toolbar-gradient: linear-gradient(
      135deg,
      light-dark(rgba(39, 140, 129, 0.04), rgba(53, 168, 155, 0.09)),
      light-dark(rgba(233, 230, 221, 0.94), rgba(23, 36, 58, 0.95)) 72%
    );
    --lw-toolbar-surface: light-dark(#E9E6DD, #17243A);
    --lw-suspicious-gradient: linear-gradient(
      135deg,
      light-dark(rgba(169, 86, 78, 0.04), rgba(203, 122, 113, 0.105)),
      light-dark(rgba(248, 247, 242, 0.98), rgba(23, 36, 58, 0.96)) 58%,
      light-dark(#F1EFE8, #192940)
    );
    --lw-uploader-gradient: linear-gradient(
      145deg,
      light-dark(rgba(39, 140, 129, 0.04), rgba(53, 168, 155, 0.075)),
      light-dark(rgba(248, 247, 242, 0.82), rgba(53, 168, 155, 0.025))
    );
    --lw-shadow:
      0 8px 20px light-dark(rgba(70, 60, 42, 0.065), rgba(3, 10, 21, 0.22)),
      inset 0 1px 0 light-dark(transparent, rgba(231, 237, 245, 0.025));
    --lw-suspicious-shadow:
      inset 3px 0 0 light-dark(rgba(169, 86, 78, 0.32), rgba(203, 122, 113, 0.48)),
      0 8px 20px light-dark(rgba(70, 60, 42, 0.065), rgba(3, 10, 21, 0.24)),
      inset 0 1px 0 light-dark(transparent, rgba(231, 237, 245, 0.025));
    color: var(--lw-text) !important;
    background-color: var(--lw-page) !important;
    background-image: var(--lw-page-gradient) !important;
  }

  [data-testid="stSidebar"] {
    color: var(--lw-text) !important;
    background-color: var(--lw-sidebar) !important;
    background-image: var(--lw-sidebar-gradient) !important;
    border-right-color: var(--lw-sidebar-border) !important;
  }

  [data-testid="stSidebarContent"] {
    padding-top: 0.5rem !important;
  }

  [data-testid="stSidebarHeader"] {
    height: 2rem;
    min-height: 2rem;
    margin-bottom: 0 !important;
  }

  [data-testid="stLogoSpacer"] {
    height: 2rem;
  }

  .stApp h1,
  .stApp h2,
  .stApp h3,
  .stApp h4,
  .stApp h5,
  .stApp h6,
  .stApp [data-testid="stWidgetLabel"],
  .stApp [data-testid="stMarkdownContainer"] p,
  .stApp [data-testid="stMarkdownContainer"] li {
    color: var(--lw-text) !important;
  }

  .stApp [data-testid="stCaptionContainer"],
  .stApp [data-testid="stCaptionContainer"] p,
  .stApp [data-testid="stMetricLabel"] {
    color: var(--lw-muted) !important;
  }

  .stApp [data-testid="stAlert"] {
    color: var(--lw-text) !important;
  }

  [data-testid="stSidebar"] [data-testid="stAlert"] {
    color: var(--lw-text) !important;
    background-color: var(--lw-sidebar-control) !important;
    border: 1px solid var(--lw-sidebar-border) !important;
    border-radius: 10px;
  }

  [data-testid="stSidebar"] [data-testid="stAlertContainer"] {
    color: var(--lw-text) !important;
    background-color: var(--lw-sidebar-control) !important;
    border-color: var(--lw-sidebar-border) !important;
  }

  [data-testid="stSidebar"] [data-testid^="stAlertContent"] {
    color: var(--lw-text) !important;
    background-color: transparent !important;
  }

  [data-testid="stSidebar"] [data-testid^="stAlertContent"] svg {
    color: var(--lw-teal) !important;
  }

  .stApp input:not([type="range"]),
  .stApp textarea,
  .stApp [data-baseweb="select"] > div,
  .stApp [role="listbox"] {
    color: var(--lw-text) !important;
    background-color: var(--lw-control) !important;
    border-color: var(--lw-border) !important;
  }

  .stApp [role="option"] {
    color: var(--lw-text) !important;
  }

  [data-testid="stSidebar"] input:not([type="range"]),
  [data-testid="stSidebar"] textarea,
  [data-testid="stSidebar"] [data-baseweb="select"] > div,
  [data-testid="stSidebar"] [role="listbox"] {
    color: var(--lw-text) !important;
    background-color: var(--lw-sidebar-control) !important;
    border-color: var(--lw-sidebar-border) !important;
  }

  [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background-color: var(--lw-sidebar-control);
    background-image: none;
    border-color: var(--lw-sidebar-border);
  }

  [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    background-color: var(--lw-sidebar-control) !important;
    border-color: var(--lw-sidebar-border) !important;
  }

  .stApp input::placeholder,
  .stApp textarea::placeholder {
    color: var(--lw-muted) !important;
    opacity: 1;
  }

  .stApp [data-baseweb="select"] *,
  .stApp [role="listbox"] *,
  .stApp [role="option"] * {
    color: var(--lw-text) !important;
  }

  .logwatch-brand {
    position: relative;
    flex: 0 0 auto;
    font-size: 46px;
    line-height: 1.15;
    font-weight: 700;
    letter-spacing: -0.035em;
  }

  .logwatch-brand::after {
    position: absolute;
    bottom: -10px;
    left: 0;
    display: block;
    width: 42px;
    height: 3px;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--lw-teal-bright), transparent);
    content: "";
  }

  [data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded" !important;
    font-size: 20px;
    font-style: normal;
    font-weight: 400;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    font-feature-settings: "liga";
    -webkit-font-feature-settings: "liga";
    -webkit-font-smoothing: antialiased;
  }

  [data-testid="stSidebar"] hr {
    margin: 0.55rem 0;
    border-color: var(--lw-border);
  }

  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
  [data-testid="stSidebar"] [data-testid="stHeadingWithActionElements"] h2,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3 {
    font-size: 1rem;
    line-height: 1.25;
    margin-bottom: 0.45rem;
  }

  [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.65rem;
  }

  [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    font-size: 0.78rem;
    line-height: 1.35;
  }

  [data-testid="stFileUploader"] {
    width: 100%;
  }

  [data-testid="stFileUploaderDropzone"] {
    min-height: 78px;
    height: auto;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px dashed var(--lw-border);
    background-color: var(--lw-surface);
    background-image: var(--lw-uploader-gradient);
    transition: border-color 140ms ease, background-color 140ms ease;
  }

  [data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--lw-teal);
  }

  [data-testid="stFileUploaderDropzoneInstructions"] {
    min-width: 0;
    gap: 4px;
  }

  [data-testid="stFileUploaderDropzoneInstructions"] span,
  [data-testid="stFileUploaderDropzoneInstructions"] small {
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
  }

  [data-testid="stFileUploaderDropzoneInstructions"] small {
    font-size: 0.72rem;
    line-height: 1.25;
  }

  [data-testid="stFileUploaderDropzone"] button {
    min-height: 34px;
    padding: 6px 12px;
    white-space: nowrap;
    color: var(--lw-text) !important;
    background-color: var(--lw-control) !important;
    border-color: var(--lw-border) !important;
  }

  [data-testid="stFileUploaderDropzone"] span,
  [data-testid="stFileUploaderDropzone"] small {
    color: var(--lw-muted);
  }

  [data-testid="stMetricValue"] {
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -0.035em;
    font-variant-numeric: tabular-nums;
    color: var(--lw-text) !important;
  }

  [data-testid="stMetricLabel"] {
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    color: var(--lw-muted) !important;
  }

  [data-testid="stMetricLabel"] .stMarkdownEllipsis {
    overflow: visible !important;
    white-space: normal !important;
    text-overflow: clip;
  }

  [data-testid="stMetricLabel"] p {
    display: block;
    line-height: 1.2;
    white-space: normal !important;
  }

  [data-testid="stMetric"] {
    position: relative;
    min-height: 108px;
    overflow: hidden;
    padding: 0 !important;
    border: 1px solid var(--lw-border) !important;
    border-radius: 14px;
    background-color: var(--lw-surface) !important;
    background-image: var(--lw-metric-gradient) !important;
    box-shadow: var(--lw-shadow);
  }

  [data-testid="stMetric"]::before {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    width: 3px;
    background: linear-gradient(180deg, var(--lw-teal-bright), transparent);
    content: "";
  }

  .logwatch-monitoring {
    flex: 0 0 auto;
    font-family: "Source Sans Pro", "Segoe UI", Arial, sans-serif !important;
    font-size: 1.05rem;
    font-weight: 600;
    line-height: 1.2;
    white-space: nowrap;
  }

  .logwatch-monitoring {
    color: var(--lw-teal) !important;
  }

  .st-key-suspicious_activity_toolbar {
    margin-bottom: 0.25rem;
    padding: 0.8rem 1rem 0.35rem;
    border: 1px solid var(--lw-border) !important;
    border-radius: 14px !important;
    background-color: var(--lw-toolbar-surface) !important;
    background-image: var(--lw-toolbar-gradient) !important;
    box-shadow: var(--lw-shadow);
  }

  .st-key-suspicious_activity_toolbar input,
  .st-key-suspicious_activity_toolbar [role="combobox"] {
    border-radius: 10px;
  }

  .st-key-suspicious_activity_cards .stVerticalBlock[class*="st-key-suspicious_ip_card_"] {
    position: relative;
    gap: 0.7rem;
    padding: 1rem 1.1rem;
    border-color: var(--lw-border) !important;
    border-radius: 15px !important;
    background-color: var(--lw-surface) !important;
    background-image: var(--lw-suspicious-gradient) !important;
    box-shadow: var(--lw-suspicious-shadow);
    color: var(--lw-text) !important;
  }

  .st-key-suspicious_activity_cards [data-testid="stMetric"] {
    min-height: auto;
    padding: 0.15rem 0;
    border: 0;
    border-radius: 0;
    background: transparent;
    box-shadow: none;
  }

  .st-key-suspicious_activity_cards [data-testid="stMetric"]::before {
    display: none;
  }

  .st-key-suspicious_activity_cards [data-testid="stMetricValue"] {
    font-size: 2.2rem;
  }

  .st-key-suspicious_activity_cards [data-testid="stMetricLabel"] {
    color: var(--lw-muted) !important;
  }

  .st-key-suspicious_activity_cards [data-testid="stProgressBarTrack"] {
    height: 8px;
    overflow: hidden;
    border-radius: 999px;
  }

  .st-key-suspicious_activity_cards [data-testid="stProgressBarTrack"] > div {
    border-radius: 999px;
  }

  .suspicious-status {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 3px 9px;
    background-color: var(--lw-coral-soft);
    color: var(--lw-coral) !important;
    font-size: 0.8rem;
    font-weight: 600;
    line-height: 1.4;
  }

  [data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--lw-border);
    border-radius: 13px;
    box-shadow: var(--lw-shadow);
    background-color: var(--lw-surface);
  }

  [data-testid="stDataFrame"] .stDataFrameGlideDataEditor {
    --gdg-bg-cell: var(--lw-grid-row) !important;
    --gdg-bg-cell-medium: var(--lw-grid-row) !important;
    --gdg-bg-header: var(--lw-grid-header) !important;
    --gdg-bg-header-has-focus: var(--lw-grid-header-hover) !important;
    --gdg-bg-header-hovered: var(--lw-grid-header-hover) !important;
    --gdg-bg-group-header: var(--lw-grid-header) !important;
    --gdg-bg-group-header-hovered: var(--lw-grid-header-hover) !important;
    --gdg-text-dark: var(--lw-grid-text) !important;
    --gdg-text-medium: var(--lw-grid-muted) !important;
    --gdg-text-light: var(--lw-grid-muted) !important;
    --gdg-text-header: var(--lw-grid-text) !important;
    --gdg-text-group-header: var(--lw-grid-text) !important;
    --gdg-border-color: var(--lw-grid-border) !important;
    --gdg-horizontal-border-color: var(--lw-grid-border) !important;
  }

  .st-key-failed_login_chart {
    border: 1px solid var(--lw-border) !important;
    border-radius: 13px !important;
    background-color: var(--lw-surface) !important;
  }

  .stPlotlyChart .xtick text,
  .stPlotlyChart .ytick text {
    fill: var(--lw-chart-axis-text) !important;
  }

  .stPlotlyChart .g-ytitle {
    fill: var(--lw-chart-title-text) !important;
  }

  @media (max-width: 760px) {
    .logwatch-brand {
      font-size: 40px;
    }

    .logwatch-header-row {
      gap: 0.5rem;
    }

    .st-key-suspicious_activity_toolbar {
      padding: 0.65rem 0.75rem 0.25rem;
    }
  }
</style>
""", unsafe_allow_html=True)


st.html(
    f'<div class="logwatch-header-row">'
    f'<div class="logwatch-brand">LogWatch</div>'
    f'<span class="logwatch-monitoring">Monitoring</span>'
    f'</div>'
)

st.caption("Authentication security overview")


threshold_minimum = 1
threshold_maximum = 10
threshold_slider_key = "failed_login_threshold"
threshold_input_key = "failed_login_threshold_input"

st.session_state.setdefault(threshold_slider_key, 3)
st.session_state.setdefault(
    threshold_input_key,
    st.session_state[threshold_slider_key],
)
threshold_value = max(
    threshold_minimum,
    min(threshold_maximum, int(st.session_state[threshold_slider_key])),
)
st.session_state[threshold_slider_key] = threshold_value
st.session_state[threshold_input_key] = threshold_value


def _sync_threshold_input() -> None:
    st.session_state[threshold_input_key] = st.session_state[threshold_slider_key]


def _sync_threshold_slider() -> None:
    st.session_state[threshold_slider_key] = st.session_state[threshold_input_key]


with st.sidebar:
    st.subheader("Analysis settings")

    threshold = st.slider(
        "Failed login threshold",
        min_value=threshold_minimum,
        max_value=threshold_maximum,
        help="Flag IP addresses reaching this number of failed attempts.",
        key=threshold_slider_key,
        on_change=_sync_threshold_input,
    )
    st.number_input(
        "Exact threshold",
        min_value=threshold_minimum,
        max_value=threshold_maximum,
        step=1,
        format="%d",
        key=threshold_input_key,
        on_change=_sync_threshold_slider,
    )
    threshold_progress = (
        (threshold - threshold_minimum)
        / (threshold_maximum - threshold_minimum)
        * 100
    )
    st.html(f"""
<style>
  .st-key-failed_login_threshold
  [data-orientation="horizontal"] > div:first-child > div:first-child {{
    background-image: linear-gradient(
      to right,
      var(--lw-coral) 0%,
      var(--lw-coral) {threshold_progress:.4f}%,
      var(--lw-slider-track) {threshold_progress:.4f}%,
      var(--lw-slider-track) 100%
    ) !important;
    border-radius: 999px;
  }}

  .st-key-failed_login_threshold
  [data-orientation="horizontal"] > div:first-child > div[data-rac][style*="left"] {{
    background-color: var(--lw-coral) !important;
    border: 2px solid var(--lw-control);
    border-radius: 50%;
    box-shadow: 0 0 0 2px rgba(203, 122, 113, 0.15);
  }}

  .st-key-failed_login_threshold
  [data-orientation="horizontal"] > div:first-child > div[data-rac][style*="left"]:focus-within {{
    box-shadow: 0 0 0 3px rgba(203, 122, 113, 0.22);
  }}

  .st-key-failed_login_threshold
  [data-orientation="horizontal"] > div:first-child > div[data-rac][style*="left"] > div:last-child {{
    color: var(--lw-text) !important;
    border-color: var(--lw-coral) !important;
  }}

  .st-key-failed_login_threshold
  [data-orientation="horizontal"] > div:first-child > div[data-rac][style*="left"] > div:last-child p {{
    color: var(--lw-text) !important;
  }}
</style>
""")

    st.markdown("---")
    st.subheader("Upload login logs")

    uploaded_files = st.file_uploader(
        "Choose CSV files",
        type=["csv"],
        key="login_log_upload",
        label_visibility="collapsed",
        accept_multiple_files=True,
        width="stretch",
    )

    st.caption("CSV format - 200 MB maximum per file")
    st.caption("Required columns: timestamp, ip_address, status")

    if uploaded_files:
        file_label = "file" if len(uploaded_files) == 1 else "files"
        st.success(f"{len(uploaded_files)} CSV {file_label} selected")
    else:
        st.info("Using built-in sample data")

    st.markdown("---")
    st.subheader("Detection rule")
    st.info(
        f"An IP is flagged at {threshold} or more failed login attempts.",
        icon=None,
    )
    st.caption("LogWatch 1.0")


if uploaded_files:
    required_columns = ("timestamp", "ip_address", "status")
    valid_frames = []
    upload_errors = []

    for uploaded_file in uploaded_files:
        try:
            file_df = pd.read_csv(
                StringIO(uploaded_file.getvalue().decode("utf-8-sig")),
                dtype=str,
                keep_default_na=False,
            )
        except (
            UnicodeDecodeError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            ValueError,
        ) as error:
            upload_errors.append(
                (uploaded_file.name, f"could not read CSV: {error}")
            )
            continue

        normalized_columns = [
            str(column).strip().lower()
            for column in file_df.columns
        ]
        duplicate_required = [
            column
            for column in required_columns
            if normalized_columns.count(column) > 1
        ]
        if duplicate_required:
            upload_errors.append(
                (
                    uploaded_file.name,
                    "duplicate required columns: "
                    + ", ".join(duplicate_required),
                )
            )
            continue

        missing_columns = [
            column
            for column in required_columns
            if column not in normalized_columns
        ]
        if missing_columns:
            upload_errors.append(
                (
                    uploaded_file.name,
                    "missing required columns: "
                    + ", ".join(missing_columns),
                )
            )
            continue

        file_df.columns = normalized_columns
        valid_frames.append(file_df.loc[:, list(required_columns)].copy())

    if upload_errors:
        st.warning("Some uploaded files could not be used.", icon=None)
        for file_name, reason in upload_errors:
            st.text(f"{file_name}: {reason}")

    if not valid_frames:
        file_label = "file" if len(uploaded_files) == 1 else "files"
        st.caption(
            f"{len(uploaded_files)} CSV {file_label} uploaded | "
            "0 records analysed"
        )
        st.error(
            "No valid CSV files could be analysed. Upload a readable CSV "
            "containing timestamp, ip_address, and status columns."
        )
        st.stop()

    combined_data = pd.concat(valid_frames, ignore_index=True)
    parsed_timestamps = pd.to_datetime(
        combined_data["timestamp"],
        errors="coerce",
        utc=True,
    )
    if parsed_timestamps.notna().any():
        combined_data = (
            combined_data.assign(_parsed_timestamp=parsed_timestamps)
            .sort_values(
                "_parsed_timestamp",
                kind="stable",
                na_position="last",
            )
            .drop(columns="_parsed_timestamp")
        )
    source = StringIO(combined_data.to_csv(index=False))
else:
    source = Path(__file__).with_name("login_logs.csv").open(
        "r",
        encoding="utf-8",
    )


try:
    report = analyze_login_logs(source, threshold)
except (ValueError, UnicodeDecodeError) as error:
    st.error(f"Unable to analyse file: {error}")
    st.stop()
except Exception as error:
    st.error(f"An unexpected error occurred: {error}")
    st.stop()
finally:
    source.close()


if uploaded_files:
    file_label = "file" if len(uploaded_files) == 1 else "files"
    st.caption(
        f"{len(uploaded_files)} CSV {file_label} uploaded | "
        f"{report['total_attempts']} records analysed"
    )


st.subheader("Security overview")

metric_columns = st.columns(4)
metric_columns[0].metric(
    "Total attempts",
    report["total_attempts"],
    border=True,
)
metric_columns[1].metric(
    "Successful logins",
    report["success_count"],
    border=True,
)
metric_columns[2].metric(
    "Failed logins",
    report["failed_count"],
    border=True,
)
metric_columns[3].metric(
    "Suspicious IPs",
    len(report["suspicious_ips"]),
    border=True,
)


if report["invalid_records"] > 0:
    st.warning(
        f"{report['invalid_records']} invalid or incomplete records were skipped.",
        icon=None,
    )


st.subheader("Suspicious activity")

suspicious_ips = report["suspicious_ips"]
total_flagged_ips = len(suspicious_ips)
total_flagged_failed_attempts = sum(suspicious_ips.values())

summary_columns = st.columns(3)
summary_columns[0].metric(
    "Total flagged IPs",
    total_flagged_ips,
    border=True,
)
summary_columns[1].metric(
    "Failed attempts from flagged IPs",
    total_flagged_failed_attempts,
    border=True,
)
summary_columns[2].metric(
    "Configured threshold",
    threshold,
    border=True,
)

with st.container(border=True, key="suspicious_activity_toolbar"):
    control_columns = st.columns([2, 1, 1], vertical_alignment="bottom")
    search_query = control_columns[0].text_input(
        "Search by IP address",
        placeholder="Enter an IP address",
        key="suspicious_ip_search",
    )
    sort_order = control_columns[1].selectbox(
        "Sort by",
        options=["Highest failed attempts", "Lowest failed attempts"],
        key="suspicious_ip_sort",
    )
    page_size = control_columns[2].selectbox(
        "Cards per page",
        options=[5, 10],
        format_func=lambda size: f"{size} per page",
        key="suspicious_ip_page_size",
    )

search_term = (search_query or "").strip().casefold()
matching_ips = [
    (ip, count)
    for ip, count in suspicious_ips.items()
    if search_term in ip.casefold()
]

if sort_order == "Highest failed attempts":
    matching_ips.sort(key=lambda item: (-item[1], item[0]))
else:
    matching_ips.sort(key=lambda item: (item[1], item[0]))

matching_ip_count = len(matching_ips)
page_count = max(1, (matching_ip_count + page_size - 1) // page_size)
page_context = (
    threshold,
    page_size,
    sort_order,
    search_term,
    tuple(matching_ips),
)
page_key = "suspicious_activity_page_" + hashlib.sha256(
    repr(page_context).encode("utf-8")
).hexdigest()[:12]

if matching_ip_count == 0:
    if total_flagged_ips == 0:
        empty_title = "No suspicious IPs detected"
        empty_message = (
            f"No IP addresses reached the configured threshold of {threshold} "
            "failed login attempts."
        )
    else:
        empty_title = "No matching IP addresses"
        empty_message = "Try another search term to find flagged IP addresses."

    with st.container(border=True):
        st.markdown(f"**{empty_title}**")
        st.caption(empty_message)
else:
    current_page = st.pagination(
        num_pages=page_count,
        key=page_key,
        width="stretch",
    ) if page_count > 1 else 1

    start_index = (current_page - 1) * page_size
    page_ips = matching_ips[start_index : start_index + page_size]
    end_index = start_index + len(page_ips)

    st.caption(
        f"Showing {start_index + 1}-{end_index} of "
        f"{matching_ip_count} matching IPs"
    )

    with st.container(key="suspicious_activity_cards"):
        with st.grid("auto", min_column_width=300, gap="small"):
            for index, (ip, count) in enumerate(page_ips):
                with st.container(
                    border=True,
                    key=f"suspicious_ip_card_{index}",
                ):
                    st.markdown(f"**{ip}**")
                    st.metric("Failed attempts", count)

                    share_of_flagged_attempts = (
                        count / total_flagged_failed_attempts
                    )
                    st.progress(
                        share_of_flagged_attempts,
                        text=(
                            f"{share_of_flagged_attempts:.0%} of flagged-IP "
                            "failed attempts"
                        ),
                    )

                    status = (
                        "At threshold"
                        if count == threshold
                        else "Above threshold"
                    )
                    st.markdown(
                        f'<span class="suspicious-status">{status}</span>',
                        unsafe_allow_html=True,
                    )

st.subheader("Failed login attempts by IP")

if report["ip_attempts"]:
    chart_data = pd.DataFrame(
        list(report["ip_attempts"].items()),
        columns=["IP Address", "Failed Attempts"],
    )

    text_color = theme_palette["text"]
    grid_color = theme_palette["chart_grid"]
    bar_color = theme_palette["teal_bright"]
    surface_color = theme_palette["chart_hover_surface"]
    axis_text_color = (
        theme_palette["text"]
        if not is_dark_theme
        else theme_palette["muted"]
    )

    chart = go.Figure(
        go.Bar(
            x=chart_data["IP Address"],
            y=chart_data["Failed Attempts"],
            marker={
                "color": bar_color,
                "cornerradius": 8,
                "line": {"width": 0},
            },
            hovertemplate=(
                "<b>%{x}</b><br>%{y:,} failed attempts<extra></extra>"
            ),
        )
    )

    chart.update_layout(
        height=340,
        bargap=0.34,
        showlegend=False,
        hovermode="closest",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=44, r=22, t=18, b=44),
        hoverlabel=dict(
            bgcolor=surface_color,
            bordercolor=bar_color,
            font=dict(
                family="Source Sans Pro, Segoe UI, Arial, sans-serif",
                size=13,
                color=text_color,
            ),
            align="left",
        ),
        font=dict(
            family="Source Sans Pro, Segoe UI, Arial, sans-serif",
            size=12,
            color=text_color,
        ),
        xaxis=dict(
            title=None,
            showgrid=False,
            zeroline=False,
            ticks="",
            tickfont=dict(color=axis_text_color),
        ),
        yaxis=dict(
            title=dict(
                text="Attempts",
                font=dict(color=text_color),
            ),
            gridcolor=grid_color,
            griddash="dot",
            zeroline=False,
            rangemode="tozero",
            tickformat=",d",
            ticks="",
            tickfont=dict(color=axis_text_color),
        ),
    )

    with st.container(border=True, key="failed_login_chart"):
        st.plotly_chart(
            chart,
            width="stretch",
            alt="Failed login attempts grouped by IP address",
        )
else:
    st.info("No failed login attempts found.", icon=None)


st.subheader("Authentication records")

if report["records"]:
    records_df = pd.DataFrame(report["records"])
    failed_text = "#D98F87" if is_dark_theme else "#A9564E"
    success_text = "#78BDB3" if is_dark_theme else "#287A70"
    records_style = records_df.style.map(
        lambda status: (
            f"color: {failed_text}; font-weight: 700;"
            if status == "FAILED"
            else f"color: {success_text}; font-weight: 700;"
        ),
        subset=["status"],
    )

    st.dataframe(
        records_style,
        width="stretch",
        hide_index=True,
        row_height=40,
        column_config={
            "timestamp": st.column_config.TextColumn(
                "Timestamp",
                width="medium",
            ),
            "ip_address": st.column_config.TextColumn(
                "IP address",
                width="medium",
            ),
            "status": st.column_config.TextColumn(
                "Status",
                width="small",
            ),
        },
        alt="Authentication log records",
    )
else:
    st.info("No valid authentication records available.", icon=None)
