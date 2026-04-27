THEMES = {
    "dark": {
        "bg": "#05070A",
        "surface": "#0D1117",
        "card": "#161B22",
        "card_hover": "#1C2128",
        "border": "#30363D",
        "text": "#E6EDF3",
        "text_dim": "#8B949E",
        "accent": "#00F3FF",        # Neon Cyan
        "accent_hover": "#00D1FF",
        "success": "#39FF14",       # Neon Green (New)
        "danger": "#FF0055",        # Neon Pink
        "danger_hover": "#FF3377",
        "warning": "#F2FF00",       # Neon Yellow
        "console_bg": "#010409",
        "status_bar": "#0D1117",
        "scroll_handle": "#30363D",
        "scroll_bg": "#05070A"
    }
}

def generate_qss(colors: dict) -> str:
    """Generates a Neon-styled Dark Mode Qt Stylesheet."""
    return f"""
        QMainWindow, QDialog, QFrame#MainContent, QScrollArea {{
            background-color: {colors['bg']};
            color: {colors['text']};
            font-family: 'Segoe UI', 'Consolas', sans-serif;
            border: none;
        }}
        
        QScrollArea, QScrollArea QWidget {{
            background-color: transparent;
            border: none;
        }}
        
        QFrame#SurfacePanel {{
            background-color: {colors['surface']};
            border-radius: 12px;
            border: 1px solid {colors['border']};
        }}
        
        QFrame#ServiceCard {{
            background-color: {colors['card']};
            border-radius: 10px;
            border: 1px solid {colors['border']};
            margin-bottom: 2px;
        }}
        
        QFrame#ServiceCard:hover {{
            background-color: {colors['card_hover']};
            border: 1px solid {colors['accent']};
        }}
        
        QLabel {{
            color: {colors['text']};
        }}
        
        QLabel#DimText {{
            color: {colors['text_dim']};
        }}
        
        QPushButton {{
            background-color: {colors['card']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors['card_hover']};
            border: 1px solid {colors['accent']};
            color: {colors['accent']};
        }}
        
        QPushButton#AccentButton {{
            background-color: {colors['success']};
            color: #FFFFFF;
            border: none;
            padding: 8px 15px;
            font-size: 10pt;
        }}
        
        QPushButton#AccentButton:hover {{
            background-color: {colors['accent']};
            color: #FFFFFF;
        }}
        
        QPushButton#DangerButton {{
            background-color: {colors['danger']};
            color: #FFFFFF;
            border: none;
            padding: 8px 15px;
            font-size: 10pt;
        }}

        QPushButton#MenuButton {{
            background-color: transparent;
            color: {colors['accent']};
            border: 1px solid {colors['accent']};
            font-size: 14pt;
        }}
        
        QPushButton#MenuButton:hover {{
            background-color: {colors['accent']};
            color: #000000;
        }}
        
        QProgressBar {{
            border: 1px solid {colors['border']};
            background-color: {colors['console_bg']};
            border-radius: 4px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['accent']};
            border-radius: 3px;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            background: {colors['bg']};
            border-radius: 8px;
            top: -1px;
        }}
        
        QTabBar::tab {{
            background: {colors['surface']};
            color: {colors['text_dim']};
            padding: 10px 25px;
            margin-right: 5px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border: 1px solid {colors['border']};
            border-bottom: none;
        }}
        
        QTabBar::tab:selected {{
            background: {colors['bg']};
            color: {colors['accent']};
            font-weight: bold;
            border-bottom: 2px solid {colors['accent']};
        }}
        
        QPlainTextEdit, QTextEdit, QLineEdit, QSpinBox {{
            background-color: {colors['console_bg']};
            color: {colors['accent']};
            border: 1px solid {colors['accent']};
            border-radius: 8px;
            padding: 6px 12px;
            font-family: 'Consolas', 'Courier New';
            selection-background-color: {colors['accent']};
            selection-color: black;
        }}
        
        QSpinBox::up-button, QSpinBox::down-button {{
            width: 20px;
            border: none;
            background: {colors['surface']};
        }}
        
        QComboBox {{
            background-color: {colors['card']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 4px 12px;
            min-width: 80px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {colors['accent']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['card']};
            color: {colors['text']};
            selection-background-color: {colors['accent']};
            border: 1px solid {colors['border']};
            outline: none;
        }}
        
        QMenu {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['accent']};
            border-radius: 8px;
            padding: 5px;
        }}
        
        QMenu::item {{
            padding: 8px 30px 8px 25px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors['accent']};
            color: black;
        }}
        
        QMenu::separator {{
            height: 1px;
            background: {colors['border']};
            margin: 5px 10px;
        }}
        
        QCheckBox {{
            spacing: 12px;
            font-weight: 500;
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {colors['border']};
            border-radius: 6px;
            background: {colors['card']};
        }}
        
        QCheckBox::indicator:checked {{
            background: {colors['accent']};
            border-color: {colors['accent']};
        }}
        
        QScrollBar:vertical {{
            border: none;
            background: {colors['bg']};
            width: 10px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {colors['accent']};
            min-height: 20px;
            border-radius: 5px;
            margin: 2px;
            opacity: 0.5;
        }}
        
        QSplitter::handle {{
            background: {colors['border']};
        }}
    """
