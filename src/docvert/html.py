from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def render_template(template_path, context):
    """Render a template using Jinja2."""
    template_dir = Path(template_path).parent
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template(Path(template_path).name)
    return template.render(context)
