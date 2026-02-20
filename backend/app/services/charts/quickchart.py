# mypy: ignore-errors
"""
QuickChart Integration for Server-Side Chart Generation.

QuickChart is an open-source Chart.js API that generates chart images from URLs.

Features:
- No client-side JavaScript required
- Supports all Chart.js chart types
- Returns PNG/SVG images
- Can be self-hosted

API: https://quickchart.io/
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("neura.charts.quickchart")


@dataclass
class ChartConfig:
    """Configuration for a QuickChart chart."""
    type: str  # bar, line, pie, doughnut, radar, scatter, bubble
    data: Dict[str, Any]
    options: Dict[str, Any] = field(default_factory=dict)
    width: int = 500
    height: int = 300
    background_color: str = "white"
    device_pixel_ratio: float = 2.0
    format: str = "png"  # png, svg, webp, pdf


class QuickChartClient:
    """
    Client for QuickChart API.

    Can use the public API or a self-hosted instance.
    """

    DEFAULT_URL = "https://quickchart.io"

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.base_url = (base_url or self.DEFAULT_URL).rstrip("/")
        self.api_key = api_key

    def get_chart_url(self, config: ChartConfig) -> str:
        """
        Get a URL that renders the chart.

        The URL can be used directly in <img> tags.
        """
        chart_json = self._build_chart_json(config)
        encoded = urllib.parse.quote(json.dumps(chart_json, separators=(',', ':')))

        params = {
            "c": encoded,
            "w": str(config.width),
            "h": str(config.height),
            "bkg": config.background_color,
            "devicePixelRatio": str(config.device_pixel_ratio),
            "f": config.format,
        }

        if self.api_key:
            params["key"] = self.api_key

        query = urllib.parse.urlencode(params)
        return f"{self.base_url}/chart?{query}"

    def get_chart_bytes(self, config: ChartConfig) -> bytes:
        """
        Download the chart as bytes.

        Returns PNG/SVG bytes that can be saved to a file.
        """
        url = self.get_chart_url(config)

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read()
        except Exception as e:
            logger.error(f"Failed to download chart: {e}")
            raise

    def get_short_url(self, config: ChartConfig) -> str:
        """
        Get a short URL for the chart.

        Useful for sharing or embedding.
        """
        chart_json = self._build_chart_json(config)

        payload = json.dumps({
            "chart": chart_json,
            "width": config.width,
            "height": config.height,
            "backgroundColor": config.background_color,
            "devicePixelRatio": config.device_pixel_ratio,
            "format": config.format,
        }).encode("utf-8")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-QuickChart-Api-Key"] = self.api_key

        req = urllib.request.Request(
            f"{self.base_url}/chart/create",
            data=payload,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("url", "")
        except Exception as e:
            logger.error(f"Failed to create short URL: {e}")
            raise

    def _build_chart_json(self, config: ChartConfig) -> Dict[str, Any]:
        """Build the Chart.js configuration JSON."""
        return {
            "type": config.type,
            "data": config.data,
            "options": config.options,
        }


# Convenience functions for common chart types

def create_bar_chart(
    labels: List[str],
    datasets: List[Dict[str, Any]],
    title: Optional[str] = None,
    stacked: bool = False,
    horizontal: bool = False,
    **kwargs,
) -> ChartConfig:
    """
    Create a bar chart configuration.

    Args:
        labels: X-axis labels
        datasets: List of dataset configs with 'label', 'data', and optional 'backgroundColor'
        title: Optional chart title
        stacked: Whether to stack bars
        horizontal: Whether to make horizontal bars

    Returns:
        ChartConfig for use with QuickChartClient
    """
    # Process datasets
    processed_datasets = []
    colors = [
        "rgba(54, 162, 235, 0.8)",
        "rgba(255, 99, 132, 0.8)",
        "rgba(75, 192, 192, 0.8)",
        "rgba(255, 206, 86, 0.8)",
        "rgba(153, 102, 255, 0.8)",
    ]

    for i, ds in enumerate(datasets):
        processed = {
            "label": ds.get("label", f"Dataset {i+1}"),
            "data": ds.get("data", []),
            "backgroundColor": ds.get("backgroundColor", colors[i % len(colors)]),
        }
        processed_datasets.append(processed)

    options: Dict[str, Any] = {
        "responsive": True,
        "plugins": {},
    }

    if title:
        options["plugins"]["title"] = {
            "display": True,
            "text": title,
        }

    if stacked:
        options["scales"] = {
            "x": {"stacked": True},
            "y": {"stacked": True},
        }

    chart_type = "horizontalBar" if horizontal else "bar"

    return ChartConfig(
        type=chart_type,
        data={
            "labels": labels,
            "datasets": processed_datasets,
        },
        options=options,
        **kwargs,
    )


def create_line_chart(
    labels: List[str],
    datasets: List[Dict[str, Any]],
    title: Optional[str] = None,
    fill: bool = False,
    smooth: bool = True,
    **kwargs,
) -> ChartConfig:
    """
    Create a line chart configuration.

    Args:
        labels: X-axis labels
        datasets: List of dataset configs
        title: Optional chart title
        fill: Whether to fill area under line
        smooth: Whether to use curved lines

    Returns:
        ChartConfig
    """
    colors = [
        "rgb(54, 162, 235)",
        "rgb(255, 99, 132)",
        "rgb(75, 192, 192)",
        "rgb(255, 206, 86)",
        "rgb(153, 102, 255)",
    ]

    processed_datasets = []
    for i, ds in enumerate(datasets):
        processed = {
            "label": ds.get("label", f"Dataset {i+1}"),
            "data": ds.get("data", []),
            "borderColor": ds.get("borderColor", colors[i % len(colors)]),
            "backgroundColor": ds.get("backgroundColor", colors[i % len(colors)].replace("rgb", "rgba").replace(")", ", 0.2)")),
            "fill": ds.get("fill", fill),
            "tension": 0.4 if smooth else 0,
        }
        processed_datasets.append(processed)

    options: Dict[str, Any] = {
        "responsive": True,
        "plugins": {},
    }

    if title:
        options["plugins"]["title"] = {
            "display": True,
            "text": title,
        }

    return ChartConfig(
        type="line",
        data={
            "labels": labels,
            "datasets": processed_datasets,
        },
        options=options,
        **kwargs,
    )


def create_pie_chart(
    labels: List[str],
    data: List[Union[int, float]],
    title: Optional[str] = None,
    doughnut: bool = False,
    **kwargs,
) -> ChartConfig:
    """
    Create a pie/doughnut chart configuration.

    Args:
        labels: Slice labels
        data: Slice values
        title: Optional chart title
        doughnut: Whether to create a doughnut chart

    Returns:
        ChartConfig
    """
    colors = [
        "rgba(255, 99, 132, 0.8)",
        "rgba(54, 162, 235, 0.8)",
        "rgba(255, 206, 86, 0.8)",
        "rgba(75, 192, 192, 0.8)",
        "rgba(153, 102, 255, 0.8)",
        "rgba(255, 159, 64, 0.8)",
        "rgba(199, 199, 199, 0.8)",
        "rgba(83, 102, 255, 0.8)",
    ]

    # Extend colors if needed
    while len(colors) < len(data):
        colors.extend(colors)

    options: Dict[str, Any] = {
        "responsive": True,
        "plugins": {},
    }

    if title:
        options["plugins"]["title"] = {
            "display": True,
            "text": title,
        }

    return ChartConfig(
        type="doughnut" if doughnut else "pie",
        data={
            "labels": labels,
            "datasets": [{
                "data": data,
                "backgroundColor": colors[:len(data)],
            }],
        },
        options=options,
        **kwargs,
    )


def create_scatter_chart(
    datasets: List[Dict[str, Any]],
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    **kwargs,
) -> ChartConfig:
    """
    Create a scatter plot configuration.

    Args:
        datasets: List of datasets with 'label' and 'data' (list of {x, y} points)
        title: Optional chart title
        x_label: X-axis label
        y_label: Y-axis label

    Returns:
        ChartConfig
    """
    colors = [
        "rgba(255, 99, 132, 0.8)",
        "rgba(54, 162, 235, 0.8)",
        "rgba(75, 192, 192, 0.8)",
    ]

    processed_datasets = []
    for i, ds in enumerate(datasets):
        processed = {
            "label": ds.get("label", f"Dataset {i+1}"),
            "data": ds.get("data", []),
            "backgroundColor": ds.get("backgroundColor", colors[i % len(colors)]),
            "pointRadius": ds.get("pointRadius", 5),
        }
        processed_datasets.append(processed)

    options: Dict[str, Any] = {
        "responsive": True,
        "plugins": {},
        "scales": {
            "x": {"type": "linear", "position": "bottom"},
            "y": {"type": "linear"},
        },
    }

    if title:
        options["plugins"]["title"] = {
            "display": True,
            "text": title,
        }

    if x_label:
        options["scales"]["x"]["title"] = {"display": True, "text": x_label}
    if y_label:
        options["scales"]["y"]["title"] = {"display": True, "text": y_label}

    return ChartConfig(
        type="scatter",
        data={
            "datasets": processed_datasets,
        },
        options=options,
        **kwargs,
    )


# High-level functions

def generate_chart_url(
    chart_type: str,
    labels: List[str],
    data: Union[List, Dict],
    title: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Quick function to generate a chart URL.

    Args:
        chart_type: bar, line, pie, doughnut, scatter
        labels: Chart labels
        data: Chart data (list for single dataset, dict with 'datasets' for multiple)
        title: Optional title
        **kwargs: Additional options

    Returns:
        URL string for the chart image
    """
    client = QuickChartClient()

    if chart_type == "bar":
        if isinstance(data, list):
            datasets = [{"label": title or "Data", "data": data}]
        else:
            datasets = data.get("datasets", [])
        config = create_bar_chart(labels, datasets, title=title, **kwargs)

    elif chart_type == "line":
        if isinstance(data, list):
            datasets = [{"label": title or "Data", "data": data}]
        else:
            datasets = data.get("datasets", [])
        config = create_line_chart(labels, datasets, title=title, **kwargs)

    elif chart_type in ("pie", "doughnut"):
        config = create_pie_chart(
            labels, data if isinstance(data, list) else [],
            title=title, doughnut=(chart_type == "doughnut"), **kwargs
        )

    elif chart_type == "scatter":
        datasets = data.get("datasets", []) if isinstance(data, dict) else []
        config = create_scatter_chart(datasets, title=title, **kwargs)

    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    return client.get_chart_url(config)


def save_chart_image(
    chart_type: str,
    labels: List[str],
    data: Union[List, Dict],
    output_path: str,
    title: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Generate and save a chart image to a file.

    Args:
        chart_type: bar, line, pie, doughnut, scatter
        labels: Chart labels
        data: Chart data
        output_path: Where to save the image
        title: Optional title

    Returns:
        Path to saved file
    """
    from pathlib import Path

    client = QuickChartClient()

    # Build config based on type
    if chart_type == "bar":
        datasets = [{"label": title or "Data", "data": data}] if isinstance(data, list) else data.get("datasets", [])
        config = create_bar_chart(labels, datasets, title=title, **kwargs)
    elif chart_type == "line":
        datasets = [{"label": title or "Data", "data": data}] if isinstance(data, list) else data.get("datasets", [])
        config = create_line_chart(labels, datasets, title=title, **kwargs)
    elif chart_type in ("pie", "doughnut"):
        config = create_pie_chart(labels, data if isinstance(data, list) else [], title=title, doughnut=(chart_type == "doughnut"), **kwargs)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    # Download and save
    image_bytes = client.get_chart_bytes(config)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)

    return str(output_path)
