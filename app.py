"""Local Streamlit UI for BRAIM Floorplan Generator."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import streamlit as st

from braim_floorplan_generator import FloorplanGenerator, Profile, SVGExporter, JSONExporter, ErgonomicsChecker

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
DEFAULT_CONFIG = ROOT / "configs" / "2room_linear.json"

DEFAULT_DATA: dict[str, Any] = {
    "name": "2-room apartment",
    "perimeter": {"type": "rectangle", "width_mm": 10000, "height_mm": 7000},
    "functional_scheme": "baseline",
    "rooms": [
        {"type": "living", "min_area": 14.0, "preferred_area": 18.0, "preferred_aspect_ratio": 1.2},
        {"type": "bedroom", "min_area": 8.0, "preferred_area": 12.0, "preferred_aspect_ratio": 1.2},
        {"type": "kitchen", "min_area": 8.0, "preferred_area": 10.0, "preferred_aspect_ratio": 1.1},
        {"type": "bathroom", "min_area": 3.0, "preferred_area": 4.0, "preferred_aspect_ratio": 1.0},
        {"type": "toilet", "min_area": 1.5, "preferred_area": 2.0, "preferred_aspect_ratio": 1.0},
        {"type": "hallway", "min_area": 3.0, "preferred_area": 5.0, "preferred_aspect_ratio": 2.0},
    ],
    "constraints": {"min_corridor_width_mm": 1200, "max_aspect_ratio": 4.0},
}


def load_default_text() -> str:
    if DEFAULT_CONFIG.exists():
        return DEFAULT_CONFIG.read_text(encoding="utf-8")
    return json.dumps(DEFAULT_DATA, ensure_ascii=False, indent=2)


def room_color(room_type: str) -> str:
    return {
        "living": "#FFE4B5",
        "bedroom": "#B0E0E6",
        "kitchen": "#FFDAB9",
        "bathroom": "#E6E6FA",
        "toilet": "#F0E68C",
        "hallway": "#F5F5DC",
    }.get(room_type, "#D9D9D9")


def render_svg(layout) -> str:
    scale = 70
    margin = 40
    width = max(layout.width * scale + 2 * margin, 400)
    height = max(layout.height * scale + 2 * margin, 300)
    items = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {width:.0f} {height:.0f}">',
        f'<rect width="{width:.0f}" height="{height:.0f}" fill="white"/>',
        f'<rect x="{margin}" y="{margin}" width="{layout.width*scale:.1f}" height="{layout.height*scale:.1f}" fill="none" stroke="#202020" stroke-width="3"/>',
    ]
    for room in layout.rooms:
        x = margin + room.x * scale
        y = margin + room.y * scale
        w = room.width * scale
        h = room.height * scale
        label_y = y + h / 2 - 8
        size = 13 if min(w, h) > 100 else 10
        items.extend([
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{room_color(room.type)}" stroke="#606060" stroke-width="1.5"/>',
            f'<text x="{x+w/2:.1f}" y="{label_y:.1f}" text-anchor="middle" font-family="Arial" font-size="{size}" font-weight="700">{room.type}</text>',
            f'<text x="{x+w/2:.1f}" y="{label_y+17:.1f}" text-anchor="middle" font-family="Arial" font-size="{size-1}">{room.area:.1f} m²</text>',
            f'<text x="{x+w/2:.1f}" y="{label_y+33:.1f}" text-anchor="middle" font-family="Arial" font-size="{size-2}">{room.width*1000:.0f} × {room.height*1000:.0f}</text>',
        ])
    items.append('</svg>')
    return "\n".join(items)


def generate(config: dict[str, Any]):
    rooms = config.get("rooms", [])
    if not rooms:
        raise ValueError("В конфиге должен быть хотя бы один элемент rooms.")
    apartment_area = float(config.get("apartment_area") or sum(float(r.get("preferred_area", r.get("min_area", 0))) for r in rooms))
    constraints = config.get("constraints", {})
    profile = Profile.from_dict({"apartment_area": apartment_area, "rooms": rooms})
    generator = FloorplanGenerator(profile, max_aspect_ratio=float(constraints.get("max_aspect_ratio", 4.0)))
    return generator.generate(), apartment_area


def git_pull() -> tuple[bool, str]:
    try:
        result = subprocess.run(["git", "pull", "origin", "main"], cwd=ROOT, capture_output=True, text=True, timeout=60)
        text = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode == 0, text or "Git pull completed."
    except FileNotFoundError:
        return False, "Git не найден в PATH. Установите Git for Windows или выполните git pull в терминале."
    except Exception as exc:
        return False, str(exc)


st.set_page_config(page_title="BRAIM Floorplan Generator", layout="wide")
st.title("BRAIM Floorplan Generator")
st.caption("Локальный интерфейс: JSON-конфиг → генерация → SVG/JSON/IFC. Размеры в плане выводятся в мм; площади — в м².")

if "config_text" not in st.session_state:
    st.session_state.config_text = load_default_text()

with st.sidebar:
    st.header("Repository")
    if st.button("Update repository (git pull)", use_container_width=True):
        ok, message = git_pull()
        (st.success if ok else st.error)(message)
    st.caption("После обновления Python-кода перезапустите приложение: Ctrl+C в терминале и снова run_app.bat.")
    st.divider()
    st.header("Output")
    st.write(f"Folder: `{OUTPUT}`")
    st.caption("IFC создаётся только если ifcopenshell доступен в текущем .venv.")

left, right = st.columns([0.9, 1.1], gap="large")
with left:
    st.subheader("Configuration")
    st.session_state.config_text = st.text_area("JSON configuration", st.session_state.config_text, height=590, label_visibility="collapsed")
    a, b = st.columns(2)
    with a:
        generate_clicked = st.button("Generate", type="primary", use_container_width=True)
    with b:
        if st.button("Load example", use_container_width=True):
            st.session_state.config_text = load_default_text()
            st.rerun()

with right:
    st.subheader("Generated plan")
    if generate_clicked:
        try:
            config = json.loads(st.session_state.config_text)
            layout, requested_area = generate(config)
            OUTPUT.mkdir(exist_ok=True)
            JSONExporter().export(layout, str(OUTPUT / "apartment.json"))
            SVGExporter().export(layout, str(OUTPUT / "apartment.svg"))
            svg = render_svg(layout)
            (OUTPUT / "floorplan_preview.svg").write_text(svg, encoding="utf-8")
            checker = ErgonomicsChecker()
            issues = checker.check(layout)
            st.session_state.last_layout = layout
            st.session_state.last_svg = svg
            st.session_state.last_issues = issues
            st.session_state.last_requested_area = requested_area
            try:
                from braim_floorplan_generator import IFCExporter
                IFCExporter().export(layout, str(OUTPUT / "apartment.ifc"))
                st.session_state.ifc_status = "IFC exported"
            except Exception as exc:
                st.session_state.ifc_status = f"IFC not exported: {exc}"
        except json.JSONDecodeError as exc:
            st.error(f"Неверный JSON: {exc}")
        except Exception as exc:
            st.exception(exc)

    if "last_svg" in st.session_state:
        st.components.v1.html(st.session_state.last_svg, height=650, scrolling=True)
        layout = st.session_state.last_layout
        st.metric("Requested area", f"{st.session_state.last_requested_area:.1f} m²")
        st.metric("Generated rooms area", f"{sum(r.area for r in layout.rooms):.1f} m²")
        st.write(f"Overall extents: **{layout.width*1000:.0f} × {layout.height*1000:.0f}**")
        st.caption(st.session_state.ifc_status)
        issues = st.session_state.last_issues
        if issues:
            st.warning(f"Ergonomics issues: {len(issues)}")
            for issue in issues:
                st.write(f"- {issue.room_name}: {issue.description}")
        else:
            st.success("Ergonomics check passed.")
        st.download_button("Download preview SVG", st.session_state.last_svg, "floorplan_preview.svg", "image/svg+xml")
    else:
        st.info("Вставь или отредактируй JSON слева и нажми Generate.")
