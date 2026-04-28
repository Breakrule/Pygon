THEMES = {
    "dark": {
        "bg": "#0F172A",
        "surface": "#1E293B",
        "card": "#1E293B",
        "card_hover": "#334155",
        "border": "#334155",
        "text": "#F8FAFC",
        "text_dim": "#94A3B8",
        "text_inv": "#FFFFFF",
        "accent": "#3B82F6",
        "accent_hover": "#60A5FA",
        "success": "#10B981",
        "danger": "#EF4444",
        "danger_hover": "#F87171",
        "warning": "#F59E0B",
        "console_bg": "#020617",
        "console_text": "#A5F3FC",
        "status_bar": "#1E293B",
        "scroll_handle": "#475569",
        "scroll_bg": "#0F172A"
    },
    "light": {
        "bg": "#F9FAFB",
        "surface": "#FFFFFF",
        "card": "#FFFFFF",
        "card_hover": "#F3F4F6",
        "border": "#E5E7EB",
        "text": "#111827",
        "text_dim": "#6B7280",
        "text_inv": "#FFFFFF",
        "accent": "#2563EB",
        "accent_hover": "#3B82F6",
        "success": "#10B981",
        "danger": "#EF4444",
        "danger_hover": "#DC2626",
        "warning": "#F59E0B",
        "console_bg": "#F3F4F6",
        "console_text": "#1F2937",
        "status_bar": "#F9FAFB",
        "scroll_handle": "#D1D5DB",
        "scroll_bg": "#F9FAFB"
    }
}

def generate_qss(colors: dict) -> str:
    """Generates a premium, modern software stylesheet."""
    return f"""
        QMainWindow, QDialog, QFrame#MainContent, QScrollArea {{
            background-color: {colors['bg']};
            color: {colors['text']};
            font-family: 'Inter', 'Segoe UI', sans-serif;
            border: none;
        }}
        
        QScrollArea, QScrollArea QWidget {{
            background-color: transparent;
            border: none;
        }}
        
        QFrame#SurfacePanel {{
            background-color: {colors['surface']};
            border-radius: 8px;
            border: 1px solid {colors['border']};
        }}
        
        QFrame#ServiceCard {{
            background-color: {colors['card']};
            border-radius: 8px;
            border: 1px solid {colors['border']};
            margin-bottom: 4px;
        }}
        
        QFrame#ServiceCard:hover {{
            background-color: {colors['card_hover']};
            border: 1px solid {colors['accent']};
        }}
        
        QPushButton {{
            background-color: {colors['card']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
        }}
        
        QPushButton:hover {{
            background-color: {colors['card_hover']};
            border: 1px solid {colors['accent']};
            color: {colors['accent']};
        }}
        
        QPushButton#AccentButton {{
            background-color: {colors['accent']};
            color: {colors['text_inv']};
            border: none;
            padding: 8px 16px;
        }}
        
        QPushButton#AccentButton:hover {{
            background-color: {colors['accent_hover']};
        }}
        
        QPushButton#DangerButton {{
            background-color: {colors['danger']};
            color: {colors['text_inv']};
            border: none;
            padding: 8px 16px;
        }}
        
        QPushButton#DangerButton:hover {{
            background-color: {colors['danger_hover']};
        }}

        QPushButton#MenuButton {{
            background-color: transparent;
            color: {colors['text_dim']};
            border: 1px solid transparent;
            font-size: 14pt;
            border-radius: 4px;
        }}
        
        QPushButton#MenuButton:hover {{
            color: {colors['accent']};
            background-color: {colors['card_hover']};
            border: 1px solid {colors['border']};
        }}
        
        QProgressBar {{
            border: 1px solid {colors['border']};
            background-color: {colors['console_bg']};
            border-radius: 4px;
            text-align: center;
            font-weight: bold;
            color: {colors['text']};
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['accent']};
            border-radius: 2px;
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
            padding: 8px 20px;
            margin-right: 4px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
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
            border-radius: 6px;
            padding: 6px 10px;
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            selection-background-color: {colors['accent']};
            selection-color: {colors['text_inv']};
        }}
        
        QSpinBox::up-button, QSpinBox::down-button {{
            width: 24px;
            border-left: 1px solid {colors['border']};
            background: {colors['card']};
        }}
        
        QComboBox {{
            background-color: {colors['card']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 4px 30px 4px 12px;
            min-width: 100px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {colors['accent']};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left: none;
        }}

        QComboBox::down-arrow {{
            image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='{colors['text_dim'].replace('#', '%23')}' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            width: 14px;
            height: 14px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['surface']};
            color: {colors['text']};
            selection-background-color: {colors['accent']};
            selection-color: {colors['text_inv']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            outline: none;
            padding: 4px;
        }}
        
        QComboBox QAbstractItemView::item {{
            min-height: 32px;
            padding-left: 10px;
            border-radius: 4px;
        }}
        
        QMenu {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 6px 24px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors['accent']};
            color: {colors['text_inv']};
        }}
        
        QCheckBox, QRadioButton {{
            spacing: 8px;
            color: {colors['text']};
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {colors['border']};
            border-radius: 4px;
            background: {colors['bg']};
        }}
        
        QRadioButton::indicator {{
            border-radius: 9px;
        }}

        QCheckBox::indicator:checked {{
            background: {colors['accent']};
            border-color: {colors['accent']};
            image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white' width='14px' height='14px'%3E%3Cpath d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z'/%3E%3C/svg%3E");
        }}

        QRadioButton::indicator:checked {{
            background: {colors['bg']};
            border-color: {colors['accent']};
            image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='6' fill='{colors['accent'].replace('#', '%23')}'/%3E%3C/svg%3E");
        }}
        
        QScrollBar:vertical {{
            border: none;
            background: {colors['bg']};
            width: 8px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {colors['scroll_handle']};
            min-height: 20px;
            border-radius: 4px;
            margin: 2px;
        }}
        
        QSplitter::handle {{
            background: {colors['border']};
        }}
    """
