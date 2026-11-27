"""GitHub-readable benchmark layout with durable relative image links."""
from pathlib import Path
import hashlib
from run_paths import resolve_artifact


class MarkdownReport:
    def __init__(self, title):
        self.parts = []
        self.tables = []
        self.figures = []

    def add_heading(self, text, level):
        self.parts.append('#' * (level + 1) + ' ' + text)

    def add_paragraph(self, text, style=None):
        self.parts.append(text)

    def table(self, headers, values):
        def line(row):
            return '| ' + ' | '.join(str(v).replace('|', '\\|').replace('\n', '<br>') for v in row) + ' |'
        self.parts.append('\n'.join([line(headers), line(['---'] * len(headers))] + [line(r) for r in values]))
        self.tables.append(values)

    def source(self, title, url):
        self.parts.append(f'Source: [{title}]({url}).')

    def add_figure(self, path, title, caption):
        # Read while the builder's temporary image directory still exists.
        name = f'comparison_{len(self.figures) + 1:02d}.png'
        self.figures.append((name, Path(path).read_bytes()))
        self.parts.append(f'### {title}\n\n![{title}](figures/{name})\n\n{caption}')

    def save(self, target):
        target = Path(target)
        images = target.parent / 'figures'
        images.mkdir(parents=True, exist_ok=True)
        text = '\n\n'.join(self.parts) + '\n'
        for name, data in self.figures:
            destination = resolve_artifact(images / name)
            if destination != (images / name).resolve() and destination.exists():
                if hashlib.sha256(data).digest() != hashlib.sha256(destination.read_bytes()).digest():
                    raise ValueError("Changed figure needs a new artifact identity/provenance entry: " + str(destination))
            destination.write_bytes(data)
            text = text.replace('figures/' + name, 'figures/' + destination.name)
        target.write_text(text)
