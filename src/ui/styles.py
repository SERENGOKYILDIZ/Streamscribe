#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Modern Qt Stylesheet & Theme System
Dark mode, vibrant accents, smooth rounded corners, seamless transparent labels.
"""

DARK_THEME_QSS = """
/* Base Window & Dialogs */
QMainWindow, QDialog, #CentralWidget {
    background-color: #0B1120; /* Deep Slate Background */
    color: #F8FAFC;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* All labels and checkboxes are transparent by default to match parent card background */
QLabel {
    background-color: transparent;
    color: #F8FAFC;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

QCheckBox {
    background-color: transparent;
    spacing: 8px;
    color: #E2E8F0;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #0F172A;
}

QCheckBox::indicator:hover {
    border: 1px solid #3B82F6;
}

QCheckBox::indicator:checked {
    background-color: #2563EB;
    border: 1px solid #2563EB;
}

/* Sidebar */
#SidebarFrame {
    background-color: #070B14;
    border-right: 1px solid #1E293B;
}

#AppLogoTitle {
    color: #FFFFFF;
    font-size: 19px;
    font-weight: bold;
    padding-left: 6px;
    background-color: transparent;
}

#AppVersionLabel {
    color: #64748B;
    font-size: 11px;
    padding-left: 6px;
    background-color: transparent;
}

/* Navigation Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #94A3B8;
    text-align: left;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    border: none;
}

QPushButton.NavButton:hover {
    background-color: #1E293B;
    color: #F1F5F9;
}

QPushButton.NavButton:checked, QPushButton.NavButton.active {
    background-color: #1E3A8A;
    color: #60A5FA;
    font-weight: bold;
}

/* Content Area Header */
#ViewHeaderLabel {
    color: #F8FAFC;
    font-size: 22px;
    font-weight: bold;
    background-color: transparent;
}

#ViewSubHeaderLabel {
    color: #94A3B8;
    font-size: 13px;
    background-color: transparent;
}

/* Cards & Containers */
QFrame.CardFrame {
    background-color: #162032;
    border: 1px solid #283548;
    border-radius: 12px;
}

QFrame.SubCardFrame {
    background-color: #0E1626;
    border: 1px solid #1F2C3F;
    border-radius: 8px;
}

/* Separator Line */
QFrame.SeparatorLine {
    background-color: #283548;
    max-height: 1px;
    border: none;
}

/* Input Fields */
QLineEdit {
    background-color: #0E1626;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 14px;
    color: #FFFFFF;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #3B82F6;
    background-color: #0A101D;
}

QTextEdit {
    background-color: #0E1626;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    color: #FFFFFF;
    font-size: 13px;
}

QTextEdit:focus {
    border: 1px solid #3B82F6;
}

/* Buttons */
QPushButton.PrimaryButton {
    background-color: #2563EB;
    color: #FFFFFF;
    font-weight: 600;
    font-size: 13px;
    border-radius: 8px;
    padding: 10px 20px;
    border: none;
}

QPushButton.PrimaryButton:hover {
    background-color: #1D4ED8;
}

QPushButton.PrimaryButton:pressed {
    background-color: #1E40AF;
}

QPushButton.SecondaryButton {
    background-color: #243144;
    color: #F1F5F9;
    font-weight: 500;
    font-size: 13px;
    border-radius: 8px;
    padding: 10px 16px;
    border: none;
}

QPushButton.SecondaryButton:hover {
    background-color: #33445C;
}

QPushButton.DangerButton {
    background-color: #DC2626;
    color: #FFFFFF;
    font-weight: 600;
    font-size: 12px;
    border-radius: 6px;
    padding: 7px 14px;
    border: none;
}

QPushButton.DangerButton:hover {
    background-color: #B91C1C;
}

QPushButton.SuccessButton {
    background-color: #059669;
    color: #FFFFFF;
    font-weight: 600;
    font-size: 12px;
    border-radius: 6px;
    padding: 7px 14px;
    border: none;
}

QPushButton.SuccessButton:hover {
    background-color: #047857;
}

/* ComboBox */
QComboBox {
    background-color: #0E1626;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    color: #F8FAFC;
    min-width: 140px;
}

QComboBox:hover {
    border: 1px solid #475569;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #162032;
    border: 1px solid #334155;
    color: #FFFFFF;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
    padding: 4px;
    border-radius: 6px;
}

/* SpinBox */
QSpinBox {
    background-color: #0E1626;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px 12px;
    color: #F8FAFC;
}

/* Progress Bar */
QProgressBar {
    background-color: #0E1626;
    border: 1px solid #283548;
    border-radius: 6px;
    text-align: center;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 600;
    height: 12px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #60A5FA);
    border-radius: 5px;
}

/* ScrollArea */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #0B1120;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #283548;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #3B82F6;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tooltips */
QToolTip {
    background-color: #162032;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px;
    font-size: 12px;
}
"""
