"""
Visualization & Diagrams Service
Auto-generates charts, diagrams, flowcharts, and other visual representations.
"""
from __future__ import annotations

import logging
import json
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DiagramType(str, Enum):
    """Types of diagrams."""
    FLOWCHART = "flowchart"
    MINDMAP = "mindmap"
    ORG_CHART = "org_chart"
    TIMELINE = "timeline"
    GANTT = "gantt"
    NETWORK = "network"
    KANBAN = "kanban"
    SEQUENCE = "sequence"
    ERD = "erd"
    UML_CLASS = "uml_class"
    ARCHITECTURE = "architecture"
    BPMN = "bpmn"
    TREE = "tree"
    SANKEY = "sankey"
    WORDCLOUD = "wordcloud"


class ChartType(str, Enum):
    """Types of charts."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    DONUT = "donut"
    AREA = "area"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    RADAR = "radar"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    FUNNEL = "funnel"
    GAUGE = "gauge"
    SPARKLINE = "sparkline"
    WATERFALL = "waterfall"
    BOXPLOT = "boxplot"
    HISTOGRAM = "histogram"
    CANDLESTICK = "candlestick"


class DiagramNode(BaseModel):
    """Node in a diagram."""
    id: str
    label: str
    type: Optional[str] = None
    parent: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[Dict[str, float]] = None
    style: Optional[Dict[str, Any]] = None


class DiagramEdge(BaseModel):
    """Edge/connection in a diagram."""
    source: str
    target: str
    label: Optional[str] = None
    type: Optional[str] = None  # arrow, line, dashed
    style: Optional[Dict[str, Any]] = None


class DiagramSpec(BaseModel):
    """Specification for a diagram."""
    diagram_id: str
    type: DiagramType
    title: str
    nodes: List[DiagramNode] = Field(default_factory=list)
    edges: List[DiagramEdge] = Field(default_factory=list)
    layout: str = "auto"  # auto, horizontal, vertical, radial
    theme: str = "default"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    mermaid_code: Optional[str] = None


class ChartSpec(BaseModel):
    """Specification for a chart."""
    chart_id: str
    type: ChartType
    title: str
    data: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)
    theme: str = "default"


class TimelineEvent(BaseModel):
    """Event in a timeline."""
    id: str
    title: str
    date: str
    description: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None


class GanttTask(BaseModel):
    """Task in a Gantt chart."""
    id: str
    name: str
    start: str
    end: str
    progress: float = 0
    dependencies: List[str] = Field(default_factory=list)
    assignee: Optional[str] = None
    color: Optional[str] = None


class VisualizationService:
    """
    Service for generating visualizations and diagrams.
    Supports auto-generation from text descriptions and data.
    """

    def __init__(self):
        self._diagram_cache: Dict[str, DiagramSpec] = {}
        self._chart_cache: Dict[str, ChartSpec] = {}

    async def generate_flowchart(
        self,
        description: str,
        title: Optional[str] = None,
    ) -> DiagramSpec:
        """
        Generate a flowchart from a process description.

        Args:
            description: Natural language process description
            title: Optional title

        Returns:
            DiagramSpec for the flowchart
        """
        diagram_id = self._generate_id(description)

        # Parse description into steps
        nodes, edges = await self._parse_process_description(description)

        spec = DiagramSpec(
            diagram_id=diagram_id,
            type=DiagramType.FLOWCHART,
            title=title or "Process Flowchart",
            nodes=nodes,
            edges=edges,
            layout="vertical",
        )

        self._attach_mermaid(spec)
        self._diagram_cache[diagram_id] = spec
        return spec

    async def generate_mindmap(
        self,
        document_content: str,
        title: Optional[str] = None,
        max_depth: int = 3,
    ) -> DiagramSpec:
        """
        Generate a mind map from document structure.

        Args:
            document_content: Document text content
            title: Central topic
            max_depth: Maximum depth of branches

        Returns:
            DiagramSpec for the mind map
        """
        diagram_id = self._generate_id(document_content)

        # Extract topics and subtopics
        nodes, edges = await self._extract_document_structure(document_content, max_depth)

        # Add central node
        central_node = DiagramNode(
            id="central",
            label=title or "Main Topic",
            type="central",
        )
        nodes.insert(0, central_node)

        spec = DiagramSpec(
            diagram_id=diagram_id,
            type=DiagramType.MINDMAP,
            title=title or "Mind Map",
            nodes=nodes,
            edges=edges,
            layout="radial",
        )

        self._attach_mermaid(spec)
        self._diagram_cache[diagram_id] = spec
        return spec

    async def generate_org_chart(
        self,
        org_data: List[Dict[str, Any]],
        title: Optional[str] = None,
    ) -> DiagramSpec:
        """
        Generate an organization chart.

        Args:
            org_data: List of people with name, role, reports_to
            title: Chart title

        Returns:
            DiagramSpec for the org chart
        """
        diagram_id = self._generate_id(str(org_data))

        nodes = []
        edges = []

        for person in org_data:
            node = DiagramNode(
                id=person.get("id", person.get("name", "").lower().replace(" ", "_")),
                label=person.get("name", ""),
                type="person",
                metadata={
                    "role": person.get("role", ""),
                    "department": person.get("department", ""),
                },
            )
            nodes.append(node)

            if person.get("reports_to"):
                edge = DiagramEdge(
                    source=person["reports_to"],
                    target=node.id,
                    type="line",
                )
                edges.append(edge)

        spec = DiagramSpec(
            diagram_id=diagram_id,
            type=DiagramType.ORG_CHART,
            title=title or "Organization Chart",
            nodes=nodes,
            edges=edges,
            layout="vertical",
        )

        self._attach_mermaid(spec)
        self._diagram_cache[diagram_id] = spec
        return spec

    async def generate_timeline(
        self,
        events: List[TimelineEvent],
        title: Optional[str] = None,
    ) -> DiagramSpec:
        """
        Generate a timeline visualization.

        Args:
            events: List of timeline events
            title: Timeline title

        Returns:
            DiagramSpec for the timeline
        """
        diagram_id = self._generate_id(str([e.model_dump() for e in events]))

        # Sort events by date
        sorted_events = sorted(events, key=lambda e: e.date)

        nodes = []
        edges = []

        prev_id = None
        for event in sorted_events:
            node = DiagramNode(
                id=event.id,
                label=event.title,
                type="event",
                metadata={
                    "date": event.date,
                    "description": event.description,
                    "category": event.category,
                },
                style={"color": event.color} if event.color else None,
            )
            nodes.append(node)

            if prev_id:
                edges.append(DiagramEdge(source=prev_id, target=event.id, type="line"))
            prev_id = event.id

        spec = DiagramSpec(
            diagram_id=diagram_id,
            type=DiagramType.TIMELINE,
            title=title or "Timeline",
            nodes=nodes,
            edges=edges,
            layout="horizontal",
        )

        self._attach_mermaid(spec)
        self._diagram_cache[diagram_id] = spec
        return spec

    async def generate_gantt(
        self,
        tasks: List[GanttTask],
        title: Optional[str] = None,
    ) -> DiagramSpec:
        """
        Generate a Gantt chart.

        Args:
            tasks: List of project tasks
            title: Chart title

        Returns:
            DiagramSpec for the Gantt chart
        """
        diagram_id = self._generate_id(str([t.model_dump() for t in tasks]))

        nodes = []
        edges = []

        for task in tasks:
            node = DiagramNode(
                id=task.id,
                label=task.name,
                type="task",
                metadata={
                    "start": task.start,
                    "end": task.end,
                    "progress": task.progress,
                    "assignee": task.assignee,
                },
                style={"color": task.color} if task.color else None,
            )
            nodes.append(node)

            for dep in task.dependencies:
                edges.append(DiagramEdge(source=dep, target=task.id, type="arrow"))

        spec = DiagramSpec(
            diagram_id=diagram_id,
            type=DiagramType.GANTT,
            title=title or "Project Timeline",
            nodes=nodes,
            edges=edges,
            layout="horizontal",
        )

        self._attach_mermaid(spec)
        self._diagram_cache[diagram_id] = spec
        return spec

    async def generate_network_graph(
        self,
        relationships: List[Dict[str, Any]],
        title: Optional[str] = None,
    ) -> DiagramSpec:
        """
        Generate a network/relationship graph.

        Args:
            relationships: List of {source, target, relationship}
            title: Graph title

        Returns:
            DiagramSpec for the network graph
        """
        diagram_id = self._generate_id(str(relationships))

        # Extract unique nodes
        node_ids = set()
        for rel in relationships:
            node_ids.add(rel["source"])
            node_ids.add(rel["target"])

        nodes = [DiagramNode(id=nid, label=nid, type="entity") for nid in node_ids]
        edges = [
            DiagramEdge(
                source=rel["source"],
                target=rel["target"],
                label=rel.get("relationship", ""),
            )
            for rel in relationships
        ]

        spec = DiagramSpec(
            diagram_id=diagram_id,
            type=DiagramType.NETWORK,
            title=title or "Relationship Network",
            nodes=nodes,
            edges=edges,
            layout="auto",
        )

        self._attach_mermaid(spec)
        self._diagram_cache[diagram_id] = spec
        return spec

    async def generate_kanban(
        self,
        items: List[Dict[str, Any]],
        columns: Optional[List[str]] = None,
        title: Optional[str] = None,
    ) -> DiagramSpec:
        """
        Generate a Kanban board visualization.

        Args:
            items: List of items with status
            columns: Column names (default: To Do, In Progress, Done)
            title: Board title

        Returns:
            DiagramSpec for the Kanban board
        """
        if columns is None:
            columns = ["To Do", "In Progress", "Review", "Done"]

        diagram_id = self._generate_id(str(items))

        nodes = []
        edges = []

        # Add column nodes
        for col in columns:
            nodes.append(DiagramNode(
                id=f"col_{col.lower().replace(' ', '_')}",
                label=col,
                type="column",
            ))

        # Add item nodes
        for item in items:
            status = item.get("status", columns[0])
            col_id = f"col_{status.lower().replace(' ', '_')}"

            node = DiagramNode(
                id=item.get("id", str(hash(item.get("title", "")))),
                label=item.get("title", ""),
                type="card",
                parent=col_id,
                metadata=item,
            )
            nodes.append(node)

        spec = DiagramSpec(
            diagram_id=diagram_id,
            type=DiagramType.KANBAN,
            title=title or "Kanban Board",
            nodes=nodes,
            edges=edges,
            layout="horizontal",
        )

        self._attach_mermaid(spec)
        self._diagram_cache[diagram_id] = spec
        return spec

    async def generate_sequence_diagram(
        self,
        interactions: List[Dict[str, Any]],
        title: Optional[str] = None,
    ) -> DiagramSpec:
        """
        Generate a sequence diagram.

        Args:
            interactions: List of {from, to, message}
            title: Diagram title

        Returns:
            DiagramSpec for the sequence diagram
        """
        diagram_id = self._generate_id(str(interactions))

        # Extract participants
        participants = set()
        for interaction in interactions:
            participants.add(interaction["from"])
            participants.add(interaction["to"])

        nodes = [DiagramNode(id=p, label=p, type="participant") for p in participants]
        edges = [
            DiagramEdge(
                source=i["from"],
                target=i["to"],
                label=i.get("message", ""),
                type="arrow",
            )
            for i in interactions
        ]

        spec = DiagramSpec(
            diagram_id=diagram_id,
            type=DiagramType.SEQUENCE,
            title=title or "Sequence Diagram",
            nodes=nodes,
            edges=edges,
            layout="vertical",
        )

        self._attach_mermaid(spec)
        self._diagram_cache[diagram_id] = spec
        return spec

    async def generate_wordcloud(
        self,
        text: str,
        max_words: int = 100,
        title: Optional[str] = None,
    ) -> DiagramSpec:
        """
        Generate a word cloud from text.

        Args:
            text: Source text
            max_words: Maximum words to include
            title: Cloud title

        Returns:
            DiagramSpec for the word cloud
        """
        diagram_id = self._generate_id(text)

        # Extract word frequencies
        word_freq = self._extract_word_frequencies(text, max_words)

        nodes = [
            DiagramNode(
                id=word,
                label=word,
                type="word",
                metadata={"frequency": freq},
            )
            for word, freq in word_freq
        ]

        spec = DiagramSpec(
            diagram_id=diagram_id,
            type=DiagramType.WORDCLOUD,
            title=title or "Word Cloud",
            nodes=nodes,
            edges=[],
            layout="cloud",
        )

        self._attach_mermaid(spec)
        self._diagram_cache[diagram_id] = spec
        return spec

    async def table_to_chart(
        self,
        data: List[Dict[str, Any]],
        chart_type: ChartType = ChartType.BAR,
        x_column: Optional[str] = None,
        y_columns: Optional[List[str]] = None,
        title: Optional[str] = None,
    ) -> ChartSpec:
        """
        Convert table data to a chart.

        Args:
            data: Table data as list of dicts
            chart_type: Type of chart
            x_column: Column for X axis
            y_columns: Columns for Y axis values
            title: Chart title

        Returns:
            ChartSpec for the chart
        """
        if not data:
            raise ValueError("No data provided")

        # Auto-detect columns if not specified
        columns = list(data[0].keys())
        if not x_column:
            x_column = columns[0]
        if not y_columns:
            y_columns = [c for c in columns if c != x_column and self._is_numeric_column(data, c)]

        chart_id = self._generate_id(str(data))

        # Prepare chart data
        chart_data = {
            "labels": [row.get(x_column, "") for row in data],
            "datasets": [],
        }

        for col in y_columns:
            chart_data["datasets"].append({
                "label": col,
                "data": [row.get(col, 0) for row in data],
            })

        spec = ChartSpec(
            chart_id=chart_id,
            type=chart_type,
            title=title or f"{chart_type.value.title()} Chart",
            data=chart_data,
            options={
                "responsive": True,
                "maintainAspectRatio": True,
            },
        )

        self._chart_cache[chart_id] = spec
        return spec

    async def generate_sparklines(
        self,
        data: List[Dict[str, Any]],
        value_columns: List[str],
    ) -> List[ChartSpec]:
        """
        Generate inline sparkline charts.

        Args:
            data: Data rows
            value_columns: Columns to create sparklines for

        Returns:
            List of ChartSpecs for sparklines
        """
        sparklines = []

        for col in value_columns:
            values = [row.get(col, 0) for row in data if row.get(col) is not None]
            if not values:
                continue

            chart_id = self._generate_id(f"sparkline_{col}")

            spec = ChartSpec(
                chart_id=chart_id,
                type=ChartType.SPARKLINE,
                title=col,
                data={"values": values},
                options={
                    "width": 100,
                    "height": 30,
                    "showMin": True,
                    "showMax": True,
                },
            )
            sparklines.append(spec)

        return sparklines

    async def export_diagram_as_mermaid(self, diagram_id: str) -> str:
        """
        Export diagram as Mermaid.js syntax.

        Args:
            diagram_id: Diagram ID

        Returns:
            Mermaid.js diagram code
        """
        diagram = self._diagram_cache.get(diagram_id)
        if not diagram:
            raise ValueError(f"Diagram {diagram_id} not found")

        if diagram.type == DiagramType.FLOWCHART:
            return self._to_mermaid_flowchart(diagram)
        elif diagram.type == DiagramType.SEQUENCE:
            return self._to_mermaid_sequence(diagram)
        elif diagram.type == DiagramType.GANTT:
            return self._to_mermaid_gantt(diagram)
        else:
            return self._to_mermaid_flowchart(diagram)

    # ==========================================================================
    # PRIVATE METHODS
    # ==========================================================================

    def _generate_id(self, content: str) -> str:
        """Generate unique ID from content."""
        return hashlib.sha256(f"{content}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]

    async def _parse_process_description(
        self,
        description: str,
    ) -> Tuple[List[DiagramNode], List[DiagramEdge]]:
        """Parse a process description into nodes and edges."""
        # Simple parsing - split by numbered steps or bullet points
        import re

        # Try structured formats first (numbered, bullet), fall back to newline split
        steps = re.split(r"(?:\d+\.\s*|\n-\s*|\n\*\s*)", description)
        steps = [s.strip() for s in steps if s.strip()]
        # If only one step remains but has newlines, split on newlines
        if len(steps) <= 1 and "\n" in description:
            steps = [s.strip() for s in description.split("\n") if s.strip()]

        nodes = []
        edges = []

        # Add start node (avoid 'end' — reserved in Mermaid)
        nodes.append(DiagramNode(id="node_start", label="Start", type="terminal"))

        prev_id = "node_start"
        for i, step in enumerate(steps):
            node_id = f"step_{i}"

            # Detect decision points
            if "?" in step or step.lower().startswith(("if", "when", "check")):
                node_type = "decision"
            else:
                node_type = "process"

            nodes.append(DiagramNode(
                id=node_id,
                label=step[:100],
                type=node_type,
            ))

            edges.append(DiagramEdge(source=prev_id, target=node_id))
            prev_id = node_id

        # Add end node (avoid 'end' — reserved in Mermaid)
        nodes.append(DiagramNode(id="node_end", label="End", type="terminal"))
        edges.append(DiagramEdge(source=prev_id, target="node_end"))

        return nodes, edges

    async def _extract_document_structure(
        self,
        content: str,
        max_depth: int,
    ) -> Tuple[List[DiagramNode], List[DiagramEdge]]:
        """Extract hierarchical structure from document."""
        import re

        # Find headings
        heading_pattern = r"^(#{1,6})\s+(.+)$"
        matches = re.findall(heading_pattern, content, re.MULTILINE)

        nodes = []
        edges = []
        parent_stack = ["central"]

        for hashes, title in matches:
            level = len(hashes)
            if level > max_depth:
                continue

            node_id = f"node_{len(nodes)}"
            nodes.append(DiagramNode(
                id=node_id,
                label=title.strip(),
                type=f"level_{level}",
            ))

            # Adjust parent stack
            while len(parent_stack) > level:
                parent_stack.pop()

            if parent_stack:
                edges.append(DiagramEdge(source=parent_stack[-1], target=node_id))

            parent_stack.append(node_id)

        return nodes, edges

    def _extract_word_frequencies(
        self,
        text: str,
        max_words: int,
    ) -> List[Tuple[str, int]]:
        """Extract word frequencies from text."""
        import re
        from collections import Counter

        # Tokenize and clean
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

        # Remove stop words
        stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
                      "her", "was", "one", "our", "out", "has", "have", "been", "this", "that",
                      "with", "they", "from", "will", "what", "when", "where", "which", "their"}
        words = [w for w in words if w not in stop_words]

        counter = Counter(words)
        return counter.most_common(max_words)

    def _is_numeric_column(self, data: List[Dict], column: str) -> bool:
        """Check if column contains numeric data."""
        for row in data[:10]:
            value = row.get(column)
            if value is not None and not isinstance(value, (int, float)):
                try:
                    float(value)
                except (ValueError, TypeError):
                    return False
        return True

    def _attach_mermaid(self, spec: DiagramSpec) -> DiagramSpec:
        """Generate and attach mermaid_code to a DiagramSpec."""
        try:
            spec.mermaid_code = self._to_mermaid(spec)
        except Exception as e:
            logger.warning(f"Mermaid generation failed for {spec.type}: {e}")
        return spec

    def _to_mermaid(self, diagram: DiagramSpec) -> str:
        """Convert any diagram to Mermaid syntax."""
        converters = {
            DiagramType.FLOWCHART: self._to_mermaid_flowchart,
            DiagramType.SEQUENCE: self._to_mermaid_sequence,
            DiagramType.GANTT: self._to_mermaid_gantt,
            DiagramType.MINDMAP: self._to_mermaid_mindmap,
            DiagramType.ORG_CHART: self._to_mermaid_flowchart,  # org charts render well as flowcharts
            DiagramType.TIMELINE: self._to_mermaid_timeline,
            DiagramType.NETWORK: self._to_mermaid_flowchart,  # networks render as flowcharts
            DiagramType.KANBAN: self._to_mermaid_kanban,
            DiagramType.WORDCLOUD: self._to_mermaid_wordcloud,
        }
        converter = converters.get(diagram.type, self._to_mermaid_flowchart)
        return converter(diagram)

    @staticmethod
    def _safe_id(raw_id: str) -> str:
        """Make an ID safe for Mermaid (alphanumeric + underscores only)."""
        import re
        return re.sub(r"[^a-zA-Z0-9_]", "_", raw_id)

    def _to_mermaid_flowchart(self, diagram: DiagramSpec) -> str:
        """Convert diagram to Mermaid flowchart syntax."""
        lines = ["flowchart TD"]

        for node in diagram.nodes:
            nid = self._safe_id(node.id)
            safe = node.label.replace('"', "'")
            if node.type == "terminal":
                lines.append(f'    {nid}(["{safe}"])')
            elif node.type == "decision":
                lines.append(f'    {nid}{{"{safe}"}}')
            else:
                lines.append(f'    {nid}["{safe}"]')

        for edge in diagram.edges:
            src = self._safe_id(edge.source)
            tgt = self._safe_id(edge.target)
            if edge.label:
                safe_label = edge.label.replace('"', "'")
                lines.append(f'    {src} -->|"{safe_label}"| {tgt}')
            else:
                lines.append(f"    {src} --> {tgt}")

        return "\n".join(lines)

    def _to_mermaid_sequence(self, diagram: DiagramSpec) -> str:
        """Convert to Mermaid sequence diagram."""
        lines = ["sequenceDiagram"]

        for node in diagram.nodes:
            nid = self._safe_id(node.id)
            lines.append(f"    participant {nid} as {node.label}")

        for edge in diagram.edges:
            src = self._safe_id(edge.source)
            tgt = self._safe_id(edge.target)
            lines.append(f"    {src}->>{tgt}: {edge.label or ''}")

        return "\n".join(lines)

    def _to_mermaid_gantt(self, diagram: DiagramSpec) -> str:
        """Convert to Mermaid Gantt chart."""
        lines = [
            "gantt",
            f"    title {diagram.title}",
            "    dateFormat YYYY-MM-DD",
        ]

        for node in diagram.nodes:
            meta = node.metadata
            start = meta.get("start", "")
            end = meta.get("end", "")
            lines.append(f"    {node.label} :{node.id}, {start}, {end}")

        return "\n".join(lines)

    def _to_mermaid_mindmap(self, diagram: DiagramSpec) -> str:
        """Convert to Mermaid mindmap syntax."""
        lines = ["mindmap"]
        if diagram.nodes:
            central = diagram.nodes[0]
            lines.append(f"  root(({central.label}))")

        # Build parent-child map from edges
        children: Dict[str, List[str]] = {}
        for edge in diagram.edges:
            children.setdefault(edge.source, []).append(edge.target)

        node_map = {n.id: n for n in diagram.nodes}

        def render(parent_id: str, depth: int):
            for child_id in children.get(parent_id, []):
                child = node_map.get(child_id)
                if child:
                    indent = "  " * (depth + 1)
                    lines.append(f"{indent}{child.label}")
                    render(child_id, depth + 1)

        if diagram.nodes:
            render(diagram.nodes[0].id, 1)

        return "\n".join(lines)

    def _to_mermaid_timeline(self, diagram: DiagramSpec) -> str:
        """Convert to Mermaid timeline syntax."""
        lines = ["timeline", f"    title {diagram.title}"]
        for node in diagram.nodes:
            date = node.metadata.get("date", "")
            lines.append(f"    {date} : {node.label}")
        return "\n".join(lines)

    def _to_mermaid_kanban(self, diagram: DiagramSpec) -> str:
        """Convert kanban to Mermaid flowchart with subgraphs."""
        lines = ["flowchart LR"]

        # Group items by column
        columns: Dict[str, List[DiagramNode]] = {}
        col_nodes = []
        for node in diagram.nodes:
            if node.type == "column":
                col_nodes.append(node)
                columns[node.id] = []
            elif node.parent:
                columns.setdefault(node.parent, []).append(node)

        for col in col_nodes:
            safe_label = col.label.replace('"', "'")
            lines.append(f'    subgraph {col.id}["{safe_label}"]')
            for item in columns.get(col.id, []):
                safe = item.label.replace('"', "'")
                lines.append(f'        {item.id}["{safe}"]')
            lines.append("    end")

        # Add arrows between columns
        for i in range(len(col_nodes) - 1):
            lines.append(f"    {col_nodes[i].id} ~~~ {col_nodes[i+1].id}")

        return "\n".join(lines)

    def _to_mermaid_wordcloud(self, diagram: DiagramSpec) -> str:
        """Convert wordcloud to a simple Mermaid mindmap (closest visual)."""
        lines = ["mindmap", f"  root(({diagram.title}))"]
        for node in diagram.nodes[:20]:
            freq = node.metadata.get("frequency", 1)
            lines.append(f"    {node.label}")
        return "\n".join(lines)


# Singleton instance
visualization_service = VisualizationService()
