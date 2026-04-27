import os
import logging
from jinja2 import Template

class DashboardGenerator:
    def __init__(self, www_dir: str):
        self.www_dir = www_dir
        self.template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pygon Dashboard</title>
    <style>
        :root {
            --bg: #05070A;
            --card: #0F172A;
            --accent: #00F3FF;
            --text: #F8FAFC;
            --dim: #94A3B8;
            --glow: rgba(0, 243, 255, 0.3);
        }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 60px 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container { max-width: 1200px; width: 100%; }
        header { margin-bottom: 50px; text-align: center; }
        h1 { 
            font-size: 3rem; 
            margin: 0; 
            background: linear-gradient(90deg, #00F3FF, #39FF14);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 4px;
            text-transform: uppercase;
        }
        .subtitle { color: var(--dim); margin-top: 10px; font-size: 1.1rem; }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 25px;
        }
        .project-card {
            background: var(--card);
            border-radius: 16px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }
        .project-card::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; height: 4px;
            background: var(--accent);
            opacity: 0;
            transition: opacity 0.3s;
        }
        .project-card:hover {
            border-color: var(--accent);
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 20px var(--glow);
        }
        .project-card:hover::before { opacity: 1; }
        
        .project-name { font-weight: 800; font-size: 1.4rem; margin-bottom: 8px; }
        .project-url { color: var(--dim); font-size: 0.95rem; font-family: monospace; }
        
        .empty-state {
            text-align: center;
            padding: 100px;
            color: var(--dim);
            border: 2px dashed rgba(255, 255, 255, 0.05);
            border-radius: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ PYGON</h1>
            <div class="subtitle">Local Development Dashboard</div>
        </header>
        
        <div class="grid">
            {% if projects %}
                {% for project in projects %}
                <a href="{{ project.url }}" class="project-card">
                    <div class="project-name">{{ project.name }}</div>
                    <div class="project-url">{{ project.domain }}</div>
                </a>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <p>No projects found in www/ directory.</p>
                    <p style="font-size: 0.9rem;">Create a folder to get started!</p>
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

    def generate(self):
        try:
            projects = []
            if not os.path.exists(self.www_dir):
                os.makedirs(self.www_dir, exist_ok=True)

            for item in os.listdir(self.www_dir):
                full_path = os.path.join(self.www_dir, item)
                if os.path.isdir(full_path) and not item.startswith("."):
                    projects.append({
                        "name": item,
                        "domain": f"{item}.pygon",
                        "url": f"http://{item}.pygon"
                    })
            
            template = Template(self.template_str)
            html = template.render(projects=projects)
            
            output_path = os.path.join(self.www_dir, "index.html")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            
            logging.info(f"Modern Dashboard generated with {len(projects)} projects.")
        except Exception as e:
            logging.error(f"Failed to generate dashboard: {e}")
