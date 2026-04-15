import re
import json
import html
from pathlib import Path

from mkdocs.plugins import BasePlugin
from mkdocs.utils import copy_file


class CommandGeneratorPlugin(BasePlugin):
    RE_BLOCK = re.compile(r'--cmd-gen<--\n(.*?)\n-->cmd-gen--', re.DOTALL)

    def on_config(self, config, **kwargs):
        config["extra_javascript"].append("js/command_generator.js")
        config["extra_css"].append("css/command_generator.css")

    def on_post_build(self, config):
        site_dir = Path(config["site_dir"])
        self.copy_asset("js/command_generator.js", site_dir)
        self.copy_asset("css/command_generator.css", site_dir)

    def copy_asset(self, asset_path: str, site_dir: Path):
        source_path = Path(__file__).parent / asset_path
        dest_path = site_dir / asset_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        copy_file(source_path, dest_path)

    def on_page_markdown(self, markdown, **kwargs):
        def replace_block(match):
            content = match.group(1)
            lines = content.split('\n')

            configs = {}
            current_key = None
            current_val = []

            # Parse the custom syntax
            for line in lines:
                # Check if line starts with "- " and ends with ":"
                stripped = line.strip()
                if stripped.startswith('- ') and stripped.endswith(':'):
                    # Save previous block before starting new one
                    if current_key:
                        configs[current_key] = "\n".join(current_val).strip()

                    # Extract key: remove "- " from start and ":" from end
                    current_key = stripped[2:-1].strip()
                    current_val = []
                else:
                    # Add line to current content block, preserving some indentation if desired
                    # We strip the leading 2 spaces if they exist to clean up the Markdown look
                    cleaned_line = line[2:] if line.startswith('  ') else line
                    current_val.append(cleaned_line)

            # Catch the last block
            if current_key:
                configs[current_key] = "\n".join(current_val).strip()

            all_keys = [k.split(',') for k in configs.keys()]
            if not all_keys: return ""

            num_rows = len(all_keys[0])
            rows_options = []
            for i in range(num_rows):
                seen = set()
                # Preserve original order of options
                options = []
                for k in all_keys:
                    if i < len(k) and k[i] not in seen:
                        seen.add(k[i])
                        options.append(k[i])
                rows_options.append(options)

            safe_json = html.escape(json.dumps(configs))

            res = [f'<div class="cmd-gen" data-configs="{safe_json}">']
            res.append('<div class="cmd-gen-selectors">')
            for i, row in enumerate(rows_options):
                res.append(f'<div class="cmd-gen-row" data-row="{i}">')
                for opt in row:
                    # First option in each row is active by default
                    active = "active" if opt == row[0] else ""
                    res.append(f'<button type="button" class="cmd-gen-btn {active}" data-opt="{opt}">{opt}</button>')
                res.append('</div>')
            res.append('</div>')
            res.append('<div class="cmd-gen-content"></div>')
            res.append('</div>')

            return "\n".join(res)

        return self.RE_BLOCK.sub(replace_block, markdown)
