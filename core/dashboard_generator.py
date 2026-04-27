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
    <title>Pygon Dashboard | Local Development</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #030406;
            --surface: rgba(15, 23, 42, 0.6);
            --border: rgba(255, 255, 255, 0.08);
            --accent: #00F3FF;
            --accent-glow: rgba(0, 243, 255, 0.2);
            --secondary: #9333EA;
            --text: #F8FAFC;
            --text-dim: #64748B;
        }
        
        * { box-sizing: border-box; }
        
        body {
            background: var(--bg);
            background-image: radial-gradient(circle at 20% 20%, rgba(147, 51, 234, 0.05) 0%, transparent 40%),
                              radial-gradient(circle at 80% 80%, rgba(0, 243, 255, 0.05) 0%, transparent 40%);
            color: var(--text);
            font-family: 'Inter', sans-serif;
            margin: 0;
            display: flex;
            min-height: 100vh;
        }

        /* Sidebar */
        aside {
            width: 280px;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--border);
            padding: 40px 24px;
            display: flex;
            flex-direction: column;
            position: fixed;
            height: 100vh;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -1px;
            background: linear-gradient(135deg, var(--accent), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 50px;
        }

        .nav-section { margin-bottom: 32px; }
        .nav-label { font-size: 0.75rem; font-weight: 700; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; display: block; }
        
        .nav-link {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            color: var(--text);
            text-decoration: none;
            border-radius: 12px;
            margin-bottom: 4px;
            transition: all 0.2s;
            font-size: 0.95rem;
        }

        .nav-link:hover {
            background: var(--surface);
            transform: translateX(4px);
            color: var(--accent);
        }

        .nav-link span { margin-right: 12px; font-size: 1.1rem; }

        /* Main Content */
        main {
            flex: 1;
            margin-left: 280px;
            padding: 60px 80px;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 48px;
        }

        h2 { font-size: 2rem; font-weight: 800; margin: 0; }
        
        .stats {
            display: flex;
            gap: 24px;
            margin-bottom: 48px;
        }

        .stat-card {
            background: var(--surface);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 24px;
            flex: 1;
        }

        .stat-label { color: var(--text-dim); font-size: 0.9rem; margin-bottom: 4px; }
        .stat-value { font-size: 1.8rem; font-weight: 800; }
        .stat-value.active { color: var(--accent); }

        /* Project Grid */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 24px;
        }

        .project-card {
            background: var(--surface);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 32px;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .project-card:hover {
            transform: translateY(-8px);
            border-color: var(--accent);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 15px var(--accent-glow);
        }

        .project-card::after {
            content: "";
            position: absolute;
            top: -50%; left: -50%; width: 200%; height: 200%;
            background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .project-card:hover::after { opacity: 0.1; }

        .project-icon {
            width: 48px; height: 48px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem; margin-bottom: 24px;
            border: 1px solid var(--border);
        }

        .project-name { font-size: 1.4rem; font-weight: 700; margin-bottom: 8px; }
        .project-domain { font-family: monospace; color: var(--text-dim); font-size: 0.9rem; }
        
        .badge {
            position: absolute;
            top: 32px; right: 32px;
            padding: 4px 12px;
            background: rgba(0, 243, 255, 0.1);
            color: var(--accent);
            border-radius: 100px;
            font-size: 0.75rem;
            font-weight: 700;
        }

        .empty-state {
            grid-column: 1 / -1;
            padding: 80px;
            text-align: center;
            background: var(--surface);
            border: 2px dashed var(--border);
            border-radius: 32px;
            color: var(--text-dim);
        }

        @media (max-width: 1024px) {
            aside { width: 80px; padding: 40px 15px; }
            aside .nav-link span { margin-right: 0; }
            aside .nav-link text { display: none; }
            aside .logo, aside .nav-label { display: none; }
            main { margin-left: 80px; padding: 40px; }
        }
    </style>
</head>
<body>
    <aside>
        <div class="logo">⚡ PYGON</div>
        
        <div class="nav-section">
            <span class="nav-label">Developer Tools</span>
            <a href="/phpinfo.php" class="nav-link"><span>🐘</span> <text>PHP Info</text></a>
            <a href="http://127.0.0.1:8025" class="nav-link" target="_blank"><span>✉️</span> <text>Mailpit</text></a>
            <a href="#" class="nav-link"><span>🗄️</span> <text>Database Manager</text></a>
        </div>

        <div class="nav-section">
            <span class="nav-label">Documentation</span>
            <a href="https://github.com/Breakrule/Pygon" class="nav-link" target="_blank"><span>📖</span> <text>GitHub Docs</text></a>
        </div>
    </aside>

    <main>
        <header>
            <div>
                <h2>My Projects</h2>
                <p style="color: var(--text-dim); margin: 8px 0 0;">Managing your local development environment</p>
            </div>
        </header>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Active Projects</div>
                <div class="stat-value active">{{ projects|length }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Environment</div>
                <div class="stat-value">v4.0 Professional</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Server Status</div>
                <div class="stat-value" style="color: #39FF14;">Operational</div>
            </div>
        </div>

        <div class="grid">
            {% if projects %}
                {% for project in projects %}
                <a href="{{ project.url }}" class="project-card">
                    <div class="badge">PHP</div>
                    <div class="project-icon">📂</div>
                    <div class="project-name">{{ project.name }}</div>
                    <div class="project-domain">{{ project.domain }}</div>
                </a>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <p style="font-size: 1.2rem; margin-bottom: 8px;">No projects detected.</p>
                    <p>Create a directory in your <strong>www</strong> folder to see it here.</p>
                </div>
            {% endif %}
        </div>
    </main>
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
