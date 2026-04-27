THEMES = {
    "dark": {
        "bg": "#05070A",
        "surface": "#0D1117",
        "card": "#161B22",
        "card_hover": "#1C2128",
        "border": "#30363D",
        "text": "#E6EDF3",
        "text_dim": "#8B949E",
        "text_inv": "#000000",
        "accent": "#00F3FF",
        "accent_hover": "#00D1FF",
        "success": "#39FF14",
        "danger": "#FF0055",
        "danger_hover": "#FF3377",
        "warning": "#F2FF00",
        "console_bg": "#010409",
        "console_text": "#A8D8A0",
        "status_bar": "#0D1117",
        "scroll_handle": "#30363D",
        "scroll_bg": "#05070A"
    },
    "light": {
        "bg": "#F8FAFC",
        "surface": "#FFFFFF",
        "card": "#F1F5F9",
        "card_hover": "#E2E8F0",
        "border": "#CBD5E1",
        "text": "#0F172A",
        "text_dim": "#3C4552",
        "text_inv": "#0F172A",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "success": "#10B981",
        "danger": "#EF4444",
        "danger_hover": "#DC2626",
        "warning": "#F59E0B",
        "console_bg": "#F1F5F9",
        "console_text": "#1E293B",
        "status_bar": "#E2E8F0",
        "scroll_handle": "#CBD5E1",
        "scroll_bg": "#F8FAFC"
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
            color: {colors['text_inv']};
            border: none;
            padding: 8px 15px;
            font-size: 10pt;
        }}
        
        QPushButton#AccentButton:hover {{
            background-color: {colors['accent']};
            color: {colors['text_inv']};
        }}
        
        QPushButton#DangerButton {{
            background-color: {colors['danger']};
            color: {colors['text_inv']};
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
            color: {colors['text_inv']};
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
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 6px 12px;
            font-family: 'Consolas', 'Courier New';
            selection-background-color: {colors['accent']};
            selection-color: {colors['text_inv']};
        }}
        
        QSpinBox::up-button, QSpinBox::down-button {{
            width: 24px;
            border-left: 1px solid {colors['border']};
            background: {colors['card']};
        }}
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background: {colors['card_hover']};
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
            color: {colors['text_inv']};
        }}
        
        QMenu::separator {{
            height: 1px;
            background: {colors['border']};
            margin: 5px 10px;
        }}
        
        QCheckBox, QRadioButton {{
            spacing: 12px;
            font-weight: 500;
            color: {colors['text']};
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
