"""Gradio Web 鐣岄潰 鈥?Dragon Fruit AI Vision Monitoring System"""

import tempfile
import os
from pathlib import Path

import cv2
import gradio as gr
import numpy as np

from dragon_fruit.config import MonitoringConfig
from dragon_fruit.pipeline.orchestrator import DragonFruitMonitor

_monitor = None


def get_monitor() -> DragonFruitMonitor:
    global _monitor
    if _monitor is None:
        config = MonitoringConfig()
        config.output_dir = Path("runs/dragon_fruit/web")
        config.log_dir = config.output_dir / "logs"
        _monitor = DragonFruitMonitor(config)
    return _monitor


def analyze(image: np.ndarray):
    if image is None:
        return (None, "Upload an image to begin analysis.", "",
                "", "", "", "", None, None)

    monitor = get_monitor()

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        cv2.imwrite(f.name, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        temp_path = f.name

    try:
        result = monitor.process_and_save(temp_path)
    finally:
        os.unlink(temp_path)

    annotated = cv2.imread(result.annotated_image_path) if result.annotated_image_path else image
    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    # Maturity
    maturity_rows = []
    for d in result.maturity_detections:
        maturity_rows.append(
            f'<tr><td>{d["label_en"]}</td>'
            f'<td><span class="badge {"badge-ripe" if d.get("maturity") == "ripe" else "badge-unripe"}">'
            f'{d["maturity"]}</span></td>'
            f'<td>{d["confidence"]:.1%}</td>'
            f'<td class="mono">[{d["bbox"][0]:.0f}, {d["bbox"][1]:.0f}, {d["bbox"][2]:.0f}, {d["bbox"][3]:.0f}]</td></tr>'
        )
    maturity_html = (
        '<table><thead><tr><th>Class</th><th>Maturity</th><th>Confidence</th><th>BBox</th></tr></thead><tbody>'
        + "".join(maturity_rows) + "</tbody></table>"
    ) if maturity_rows else '<div class="empty-state">No dragon fruit detected</div>'

    # Pest & disease
    pest_rows = []
    if result.pest_disease_results:
        for r in result.pest_disease_results:
            if isinstance(r, dict):
                label = r.get("label_en", "-")
                conf = r.get("confidence", 0)
                note = r.get("note", "")
                cls = "badge-warn" if label in ("Aphids", "Anthracnose") else "badge-ok"
                pest_rows.append(
                    f'<tr><td>{label}</td><td>{conf:.1%}</td>'
                    f'<td><span class="badge {cls}">{note or ("Detected" if conf > 0 else "N/A")}</span></td></tr>'
                )
            elif isinstance(r, list) and r:
                label = r[0].get("label_en", "-")
                conf = r[0].get("confidence", 0)
                cls = "badge-warn" if label in ("Aphids", "Anthracnose") else "badge-ok"
                pest_rows.append(
                    f'<tr><td>{label}</td><td>{conf:.1%}</td>'
                    f'<td><span class="badge {cls}">Detected</span></td></tr>'
                )
    pest_html = (
        '<table><thead><tr><th>Category</th><th>Confidence</th><th>Status</th></tr></thead><tbody>'
        + "".join(pest_rows) + "</tbody></table>"
    ) if pest_rows else '<div class="empty-state">Pest model not loaded or no anomaly detected</div>'

    # Growth
    ga = result.growth_anomalies
    g_ok = '<span class="badge badge-ok">Normal</span>'
    g_warn = '<span class="badge badge-warn">Attention</span>'
    growth_html = f'''<table><thead><tr><th>Metric</th><th>Value</th><th>Status</th></tr></thead><tbody>
<tr><td>Greenness Index</td><td>{ga.get("greenness_index", 0):.1%}</td><td>{g_warn if ga.get("greenness_status") == "low" else g_ok}</td></tr>
<tr><td>Yellowness Ratio</td><td>{ga.get("yellowness_ratio", 0):.1%}</td><td>{g_warn if ga.get("yellowness_alert") else g_ok}</td></tr>
<tr><td>Tilt Angle</td><td>{ga.get("tilt_angle_degrees", 0):.1f}&deg;</td><td>{g_warn if ga.get("tilt_alert") else g_ok}</td></tr>
</tbody></table>'''

    # Recommendations
    recs = ga.get("recommendations", [])
    rec_html = ("<ul class='rec-list'>" + "".join(f"<li>{r}</li>" for r in recs) + "</ul>"
                ) if recs else '<div class="empty-state">No issues detected</div>'

    # Alerts
    alert_rows = []
    for a in result.alerts:
        lvl = a.level.value
        cls = "alert-critical" if lvl == "CRITICAL" else ("alert-warning" if lvl == "WARNING" else "alert-info")
        dot = {"CRITICAL": "#dc2626", "WARNING": "#d97706", "INFO": "#059669"}.get(lvl, "#78756e")
        alert_rows.append(
            f'<tr class="{cls}"><td><span class="alert-dot" style="background:{dot}"></span> {lvl}</td>'
            f'<td>{a.message}</td></tr>'
        )
    alert_html = (
        '<table><thead><tr><th>Level</th><th>Message</th></tr></thead><tbody>'
        + "".join(alert_rows) + "</tbody></table>"
    ) if alert_rows else '<div class="empty-state">No alerts</div>'

    # Downloads
    stem = Path(temp_path).stem
    json_path = monitor.config.output_dir / f"{stem}_result.json"
    json_download = str(json_path) if json_path.exists() else None
    img_download = result.annotated_image_path if result.annotated_image_path else None

    return (
        annotated_rgb,
        result.summary,
        maturity_html,
        pest_html,
        growth_html,
        rec_html,
        alert_html,
        json_download,
        img_download,
    )


def build_interface():
    css = """
    * { box-sizing: border-box; }

    body, .gradio-container {
        background: #f5f4f1 !important;
    }

    /* ---- Header ---- */
    .app-header {
        text-align: center;
        padding: 48px 24px 32px 24px;
        margin-bottom: 24px;
        border-bottom: 1px solid #ddd9d1;
    }
    .app-header h1 {
        font-size: 2em;
        font-weight: 700;
        color: #1a1714;
        margin: 0 0 6px 0;
        letter-spacing: -0.02em;
    }
    .app-header p {
        font-size: 1em;
        color: #6b6560;
        margin: 0;
    }

    /* ---- Tables ---- */
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
        background: #ffffff !important;
    }
    th {
        text-align: left;
        padding: 10px 14px;
        font-weight: 600;
        color: #5c5651;
        font-size: 0.8em;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid #ede8e1;
        background: #faf9f6 !important;
    }
    td {
        padding: 10px 14px;
        border-bottom: 1px solid #f0ede7;
        color: #1a1714;
        background: #ffffff !important;
    }

    /* ---- Badges ---- */
    .badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 100px;
        font-size: 0.8em;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .badge-ripe {
        background: #d1fae5 !important;
        color: #064e3b !important;
    }
    .badge-unripe {
        background: #fef3c7 !important;
        color: #78350f !important;
    }
    .badge-ok {
        background: #d1fae5 !important;
        color: #064e3b !important;
    }
    .badge-warn {
        background: #fef3c7 !important;
        color: #78350f !important;
    }

    /* ---- Alert dot ---- */
    .alert-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }

    /* ---- Alert rows ---- */
    .alert-critical td {
        background: #fef2f2 !important;
    }
    .alert-warning td {
        background: #fffbf0 !important;
    }
    .alert-info td {
        background: #f0fdf4 !important;
    }
    .alert-critical td:first-child {
        border-left: 3px solid #dc2626;
    }
    .alert-warning td:first-child {
        border-left: 3px solid #d97706;
    }
    .alert-info td:first-child {
        border-left: 3px solid #059669;
    }

    /* ---- Empty state ---- */
    .empty-state {
        text-align: center;
        padding: 32px 16px;
        color: #9c9690;
        font-size: 0.95em;
    }

    /* ---- Recommendations ---- */
    .rec-list {
        margin: 0;
        padding-left: 0;
        list-style: none;
    }
    .rec-list li {
        position: relative;
        padding: 8px 0 8px 22px;
        color: #1a1714;
        font-size: 0.92em;
        line-height: 1.5;
    }
    .rec-list li::before {
        content: "";
        position: absolute;
        left: 0; top: 15px;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #d97706;
    }

    /* ---- Mono text ---- */
    .mono {
        font-family: "Consolas", "Menlo", monospace;
        font-size: 0.85em;
        color: #4a4540;
    }

    /* ---- Footer ---- */
    .app-footer {
        text-align: center;
        padding: 36px 24px;
        color: #9c9690;
        font-size: 0.85em;
        border-top: 1px solid #ddd9d1;
        margin-top: 48px;
    }

    /* ---- Hide Gradio branding ---- */
    footer { display: none !important; }

    /* ---- Image rounded corners ---- */
    .gr-image img {
        border-radius: 10px;
    }

    /* ---- Accordions ---- */
    .gr-accordion {
        border: 1px solid #ddd9d1 !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        background: #ffffff !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }
    .gr-accordion > .label-wrap {
        color: #1a1714 !important;
        font-weight: 600 !important;
    }
    .gr-accordion > div {
        background: #ffffff !important;
    }

    /* ---- General labels ---- */
    label, .label-text, .gr-button {
        color: #1a1714 !important;
        font-weight: 600 !important;
    }

    /* ---- Accordion header labels ---- */
    .label-wrap span, .label-wrap {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* ---- Textbox ---- */
    textarea, input[type="text"] {
        color: #1a1714 !important;
        background: #ffffff !important;
    }

    /* ---- Accordion + HTML content area ---- */
    .gr-accordion > div,
    .gr-accordion .panel,
    .gr-accordion [class*="panel"],
    .gr-html,
    .html-container,
    .prose {
        background: #ffffff !important;
    }
    .gr-accordion .label-wrap {
        background: #faf9f6 !important;
    }

    /* ---- File component label ---- */
    .gr-file > label, .gr-file .file-label {
        color: #1a1714 !important;
        font-weight: 600 !important;
    }

    /* ---- Image component label ---- */
    .input-image label, .output-image label,
    .input-image span, .output-image span {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95em !important;
    }

    /* ---- Download file label ---- */
    .download-file label, .download-file span {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95em !important;
    }
    .download-file p, .download-file div, .download-file button {
        color: #1a1714 !important;
    }

    /* ---- Accordion header ---- */
    .gr-accordion > .label-wrap {
        color: #ffffff !important;
        background: #ffffff !important;
    }
    .gr-accordion > .label-wrap span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    """

    head_js = """<script>
    function walkAll(root, fn) {
        fn(root);
        root.querySelectorAll('*').forEach(function(child) {
            fn(child);
            if (child.shadowRoot) walkAll(child.shadowRoot, fn);
        });
    }
    function fixFileColors() {
        document.querySelectorAll('.download-file').forEach(function(w) {
            walkAll(w, function(el) {
                if (el.tagName === 'LABEL') return;
                if (!el.children || el.children.length > 0) return;
                var t = (el.textContent || '').trim();
                if (t.length > 0) {
                    el.style.setProperty('color', '#1a1714', 'important');
                    el.style.setProperty('font-weight', '500', 'important');
                }
            });
        });
    }
    fixFileColors();
    setInterval(fixFileColors, 600);
    </script>"""

    with gr.Blocks(title="Dragon Fruit AI Vision Monitor", css=css, head=head_js) as demo:
        gr.HTML(
            '<div class="app-header">'
            "<h1>Dragon Fruit AI Vision Monitor</h1>"
            "<p>Maturity Detection &middot; Pest &amp; Disease Identification &middot; Growth Anomaly Analysis</p>"
            "</div>"
        )

        with gr.Row(equal_height=True):
            with gr.Column(scale=5):
                input_img = gr.Image(label="Upload Image", type="numpy", height=420, elem_classes="input-image")
                btn = gr.Button("Analyze", variant="primary", size="lg")
            with gr.Column(scale=5):
                output_img = gr.Image(label="Detection Result", type="numpy", height=420, elem_classes="output-image")

        summary = gr.Textbox(label="Summary", lines=2, interactive=False)

        with gr.Row():
            with gr.Column():
                with gr.Accordion("Maturity Detection", open=True):
                    maturity_table = gr.HTML("Awaiting analysis...")
            with gr.Column():
                with gr.Accordion("Pest & Disease", open=True):
                    pest_table = gr.HTML("Awaiting analysis...")

        with gr.Row():
            with gr.Column():
                with gr.Accordion("Growth Anomaly Analysis", open=True):
                    growth_table = gr.HTML("Awaiting analysis...")
            with gr.Column():
                with gr.Accordion("Recommendations", open=True):
                    recommendations = gr.HTML("Awaiting analysis...")

        with gr.Accordion("Alerts", open=True):
            alert_table = gr.HTML("Awaiting analysis...")

        with gr.Row():
            with gr.Column():
                json_file = gr.File(label="Download Results (JSON)", elem_classes="download-file")
            with gr.Column():
                img_file = gr.File(label="Download Annotated Image (JPG)", elem_classes="download-file")

        btn.click(
            fn=analyze,
            inputs=[input_img],
            outputs=[output_img, summary, maturity_table, pest_table, growth_table,
                     recommendations, alert_table, json_file, img_file],
        )

        gr.HTML('<div class="app-footer">Dragon Fruit AI Vision Monitoring System &copy; 2026 · Modified YOLOv5 components · AGPL-3.0 · No warranty · <a href="https://github.com/FaiyuetCik/dragon-fruit-ai-monitor" target="_blank">Source and license</a></div>')

    return demo


def run_server(port: int = 5000, share: bool = True):
    os.environ.setdefault("NO_PROXY", "localhost,127.0.0.1")
    os.environ.setdefault("no_proxy", "localhost,127.0.0.1")
    demo = build_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=port,
        share=share,
        show_error=True,
    )
