#!/usr/bin/env python3
"""
Renders all 14 Mermaid diagrams as PNG images using matplotlib.
Each diagram is drawn as a clean styled box-and-arrow graphic.
Output: /home/path/code/project/9/report/figures/figX_X.png
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

OUT = '/home/path/code/project/9/report/figures'
os.makedirs(OUT, exist_ok=True)

# ── colour palette ──────────────────────────────────────────────────────────
NAVY   = '#1a237e'
BLUE   = '#3949ab'
LBLUE  = '#90caf9'
GREEN  = '#2e7d32'
LGREEN = '#a5d6a7'
TEAL   = '#00695c'
LTEAL  = '#b2dfdb'
ORANGE = '#e65100'
LORANG = '#ffcc80'
GREY   = '#455a64'
LGREY  = '#eceff1'
WHITE  = '#ffffff'
RED    = '#c62828'
LRED   = '#ffcdd2'
PURPLE = '#6a1b9a'
LPURPL = '#e1bee7'

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f'  saved {name}')

def box(ax, x, y, w, h, label, fc='#e3f2fd', ec=NAVY, fontsize=9,
        bold=False, radius=0.04, textcolor='black', sublabel=None):
    rect = FancyBboxPatch((x-w/2, y-h/2), w, h,
                          boxstyle=f'round,pad={radius}',
                          facecolor=fc, edgecolor=ec, linewidth=1.5, zorder=3)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ya = y + h*0.12 if sublabel else y
    ax.text(x, ya, label, ha='center', va='center', fontsize=fontsize,
            fontweight=weight, color=textcolor, zorder=4, wrap=True,
            multialignment='center')
    if sublabel:
        ax.text(x, y - h*0.22, sublabel, ha='center', va='center',
                fontsize=fontsize-1.5, color=textcolor, zorder=4,
                style='italic', multialignment='center')

def arrow(ax, x0, y0, x1, y1, label='', color=NAVY, lw=1.5):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw),
                zorder=5)
    if label:
        mx, my = (x0+x1)/2, (y0+y1)/2
        ax.text(mx+0.02, my+0.02, label, fontsize=7.5, color=color, zorder=6)

def diamond(ax, x, y, w, h, label, fc='#fff9c4', ec='#f9a825'):
    pts = np.array([[x, y+h/2],[x+w/2,y],[x,y-h/2],[x-w/2,y]])
    poly = plt.Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.5, zorder=3)
    ax.add_patch(poly)
    ax.text(x, y, label, ha='center', va='center', fontsize=8,
            fontweight='bold', color='black', zorder=4, multialignment='center')

def oval(ax, x, y, w, h, label, fc=LGREEN, ec=GREEN):
    ell = mpatches.Ellipse((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=1.5, zorder=3)
    ax.add_patch(ell)
    ax.text(x, y, label, ha='center', va='center', fontsize=8.5,
            fontweight='bold', color='black', zorder=4, multialignment='center')

# ════════════════════════════════════════════════════════════════════════════
# Figure 2.1 – TAM Framework
# ════════════════════════════════════════════════════════════════════════════
def fig_2_1():
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(WHITE)
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis('off')
    fig.suptitle('Figure 2.1: Technology Acceptance Model (TAM) Framework',
                 fontsize=12, fontweight='bold', color=NAVY, y=0.98)

    # EV box (left)
    box(ax, 1.3, 2.5, 2.0, 3.2, 'External\nVariables\n\n• System Design\n• Training\n• Institution\n  Support',
        fc='#e8eaf6', ec=NAVY, fontsize=8.5, bold=False)

    # PU
    box(ax, 4.5, 3.6, 2.0, 0.9, 'Perceived\nUsefulness (PU)', fc='#e3f2fd', ec=BLUE, fontsize=9, bold=True)
    # PEOU
    box(ax, 4.5, 1.5, 2.0, 0.9, 'Perceived Ease\nof Use (PEOU)', fc='#e3f2fd', ec=BLUE, fontsize=9, bold=True)
    # ATT
    box(ax, 7.2, 2.5, 1.8, 0.9, 'Attitude\nToward Use', fc='#e8f5e9', ec=GREEN, fontsize=9, bold=True)
    # BI
    box(ax, 9.5, 2.5, 1.8, 0.9, 'Behavioural\nIntention', fc='#fff3e0', ec=ORANGE, fontsize=9, bold=True)
    # AU
    box(ax, 11.3, 2.5, 1.0, 0.9, 'Actual\nUse', fc='#fce4ec', ec=RED, fontsize=9, bold=True)

    for x0,y0,x1,y1,lbl in [
        (2.3,3.6,3.5,3.6,''), (2.3,1.5,3.5,1.5,''),
        (5.5,3.6,6.3,2.9,''), (5.5,1.5,6.3,2.2,''),
        (5.5,3.6,6.3,2.5,''), (5.5,1.5,6.3,3.6,'+ PU'),
        (8.1,2.5,8.6,2.5,''), (9.5,3.6,9.5,2.95,''),
        (10.4,2.5,10.8,2.5,''), (9.5,1.5,9.5,2.05,''),
    ]:
        arrow(ax,x0,y0,x1,y1,lbl)
    arrow(ax,2.3,2.5,8.6,2.5,'Direct effect on BI')

    save(fig, 'fig2_1_TAM.png')

# ════════════════════════════════════════════════════════════════════════════
# Figure 2.2 – Evolution Timeline
# ════════════════════════════════════════════════════════════════════════════
def fig_2_2():
    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor(WHITE); ax.set_xlim(0,14); ax.set_ylim(0,5); ax.axis('off')
    fig.suptitle('Figure 2.2: Evolution of Student Record Management Systems',
                 fontsize=12, fontweight='bold', color=NAVY, y=0.98)

    eras = [
        (1.5, 'Pre-1970s', 'Manual\nPaper Systems', '#fce4ec', RED),
        (4.0, '1970s–1980s', 'Mainframe\nEra', '#fff3e0', ORANGE),
        (6.8, '1990s–2000s', 'Client-Server\nEra', '#e8f5e9', GREEN),
        (9.8, '2000s–2010s', 'Web 1.0\nEra', '#e3f2fd', BLUE),
        (12.5, '2010s–Present', 'Cloud &\nMobile Era', '#e8eaf6', NAVY),
    ]
    # Timeline line
    ax.plot([0.5,13.5],[2.5,2.5], color=GREY, lw=3, zorder=1)

    for x, period, label, fc, ec in eras:
        ax.plot([x,x],[2.5,3.4], color=ec, lw=2, zorder=2)
        box(ax, x, 3.9, 1.9, 0.9, f'{period}\n{label}', fc=fc, ec=ec, fontsize=8.5, bold=False)
        ax.plot(x, 2.5, 'o', color=ec, markersize=10, zorder=3)

    details = [
        (1.5, 1.6, 'Registers,\nLedgers,\nFiling Cabinets'),
        (4.0, 1.6, 'Batch grade\nprocessing,\nPrinted reports'),
        (6.8, 1.6, 'Desktop apps,\nSQL databases,\nLAN networks'),
        (9.8, 1.6, 'PHP/MySQL,\nBrowser access,\nShared hosting'),
        (12.5, 1.6, 'Responsive UI,\nCloud hosting,\nAI analytics'),
    ]
    for x, y, txt in details:
        ax.text(x, y, txt, ha='center', va='top', fontsize=7.5, color=GREY,
                multialignment='center')

    save(fig, 'fig2_2_evolution.png')

# ════════════════════════════════════════════════════════════════════════════
# Figure 2.3 – Key Features Mindmap
# ════════════════════════════════════════════════════════════════════════════
def fig_2_3():
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor(WHITE); ax.set_xlim(0,14); ax.set_ylim(0,10); ax.axis('off')
    fig.suptitle('Figure 2.3: Key Features of a Modern Student Record Management System',
                 fontsize=12, fontweight='bold', color=NAVY, y=0.99)

    cx, cy = 7, 5
    box(ax, cx, cy, 2.2, 1.0, 'Modern\nSRMS', fc=NAVY, ec=NAVY, fontsize=11, bold=True, textcolor=WHITE)

    branches = [
        (2.5, 8.2, 'Student\nManagement', '#e3f2fd', BLUE,
         ['Personal Profiles','Guardian Details','Admission Records','Academic History']),
        (7, 8.5, 'Academic\nManagement', '#e8f5e9', GREEN,
         ['Course Registration','Grade Entry','GPA/CGPA Computation','Transcripts']),
        (11.5, 8.2, 'Attendance\nTracking', '#fff3e0', ORANGE,
         ['Daily Attendance','Attendance Reports','Rate Calculation']),
        (12, 3.5, 'Financial\nManagement', '#fce4ec', RED,
         ['Fee Structures','Payment Recording','Balance Computation','Receipts']),
        (9.5, 1.2, 'Reporting &\nAnalytics', '#e8eaf6', PURPLE,
         ['Dashboard Charts','Class Lists','Performance Reports']),
        (4.5, 1.2, 'User Access\nControl', '#e0f7fa', TEAL,
         ['Role-Based Access','Authentication','Audit Logging']),
        (2, 3.5, 'System\nAdministration', '#f3e5f5', PURPLE,
         ['User Management','System Settings','Department Config']),
    ]
    for bx, by, label, fc, ec, children in branches:
        box(ax, bx, by, 2.2, 0.85, label, fc=fc, ec=ec, fontsize=9, bold=True)
        arrow(ax, cx, cy, bx, by, color=ec)
        # child nodes
        start_y = by - 1.1
        for i, child in enumerate(children):
            cy2 = start_y - i*0.55
            ax.text(bx, cy2, f'• {child}', ha='center', va='center',
                    fontsize=7.5, color=GREY)

    save(fig, 'fig2_3_features.png')

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.1 – Use Case Diagram
# ════════════════════════════════════════════════════════════════════════════
def fig_3_1():
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor(WHITE); ax.set_xlim(0,14); ax.set_ylim(0,10); ax.axis('off')
    fig.suptitle('Figure 3.1: Use Case Diagram – Student Record Management System',
                 fontsize=12, fontweight='bold', color=NAVY, y=0.99)

    # System boundary
    sys_rect = FancyBboxPatch((2.5, 0.5), 9, 9, boxstyle='round,pad=0.1',
                              facecolor='#f5f5f5', edgecolor=NAVY, linewidth=2, linestyle='--')
    ax.add_patch(sys_rect)
    ax.text(7, 9.2, 'SRMS System Boundary', ha='center', fontsize=10, color=NAVY, style='italic')

    actors = [
        (0.8, 7.5, 'Admin', NAVY),
        (0.8, 5.0, 'Registrar', GREEN),
        (0.8, 2.5, 'Teacher', ORANGE),
        (13.2, 5.0, 'Student', BLUE),
    ]
    for ax2, ay, name, color in actors:
        ax.plot(ax2, ay+0.4, 'o', color=color, markersize=14, zorder=4)
        ax.plot([ax2,ax2],[ay-0.1,ay+0.1], color=color, lw=2)
        ax.plot([ax2-0.2,ax2+0.2],[ay+0.05,ay+0.05], color=color, lw=2)
        ax.text(ax2, ay-0.35, name, ha='center', fontsize=9, fontweight='bold', color=color)

    use_cases = {
        'admin': [(4.5,8.5,'Manage Users'),(4.5,7.8,'System Settings'),(4.5,7.1,'View Audit Logs'),(4.5,6.4,'Manage Departments'),(4.5,5.7,'View All Reports'),(4.5,5.0,'Manage Sessions')],
        'registrar': [(7,8.5,'Manage Students'),(7,7.8,'Manage Enrolment'),(7,7.1,'Generate Transcripts'),(7,6.4,'Manage Fee Structures'),(7,5.7,'Record Payments'),(7,5.0,'Generate Class Lists')],
        'teacher': [(4.5,4.0,'Enter Grades'),(4.5,3.3,'Mark Attendance'),(4.5,2.6,'View Class List'),(4.5,1.9,'View Grade Summary')],
        'student': [(10.5,7.5,'View Grades & GPA'),(10.5,6.8,'View Attendance'),(10.5,6.1,'View Fee Balance'),(10.5,5.4,'Download Transcript'),(10.5,4.7,'Update Profile')],
    }
    colors_map = {'admin':NAVY,'registrar':GREEN,'teacher':ORANGE,'student':BLUE}
    actor_x = {'admin':0.8,'registrar':0.8,'teacher':0.8,'student':13.2}
    actor_y = {'admin':7.5,'registrar':5.0,'teacher':2.5,'student':5.0}

    for role, ucs in use_cases.items():
        for ux, uy, label in ucs:
            ell = mpatches.Ellipse((ux, uy), 2.6, 0.5,
                                   facecolor='white', edgecolor=colors_map[role], linewidth=1.5, zorder=3)
            ax.add_patch(ell)
            ax.text(ux, uy, label, ha='center', va='center', fontsize=7.5, zorder=4)
            arrow(ax, actor_x[role], actor_y[role], ux-1.3 if role!='student' else ux+1.3, uy,
                  color=colors_map[role], lw=1)

    save(fig, 'fig3_1_usecase.png')

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.2 – Three-Tier Architecture
# ════════════════════════════════════════════════════════════════════════════
def fig_3_2():
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(WHITE); ax.set_xlim(0,12); ax.set_ylim(0,8); ax.axis('off')
    fig.suptitle('Figure 3.2: Three-Tier System Architecture Diagram',
                 fontsize=12, fontweight='bold', color=NAVY, y=0.99)

    layers = [
        (4, 7.0, 'PRESENTATION LAYER', '#e3f2fd', BLUE,
         ['Web Browser (Chrome, Firefox, Edge, Safari)',
          'Bootstrap 5 — Responsive HTML/CSS/JS',
          'jQuery 3.7 — AJAX & DOM',
          'Chart.js 4 — Dashboard Charts']),
        (4, 4.5, 'APPLICATION LAYER', '#e8f5e9', GREEN,
         ['Apache HTTP Server 2.4  |  PHP 8.1',
          'Authentication • Students • Courses • Grades',
          'Attendance • Fees • Reports • Dashboard',
          'Users • Audit Log • REST-like API Endpoints']),
        (4, 2.0, 'DATA LAYER', '#fff3e0', ORANGE,
         ['MySQL 8.0 Database Server',
          'users • students • courses • grades',
          'attendance • fee_payments • audit_logs',
          'PDO Prepared Statements — ACID Transactions']),
    ]
    for x, y, title, fc, ec, lines in layers:
        box(ax, x, y, 7.5, 1.8, '', fc=fc, ec=ec, fontsize=9, bold=False, radius=0.06)
        ax.text(x, y+0.65, title, ha='center', va='center', fontsize=10,
                fontweight='bold', color=ec, zorder=5)
        for i, line in enumerate(lines):
            ax.text(x, y+0.25-i*0.28, line, ha='center', va='center',
                    fontsize=8, color=GREY, zorder=5)

    # Arrows between layers
    ax.annotate('', xy=(4,5.45), xytext=(4,6.08),
                arrowprops=dict(arrowstyle='<->', color=NAVY, lw=2))
    ax.text(5.0, 5.76, 'HTTPS / HTML / JSON', fontsize=8, color=NAVY)
    ax.annotate('', xy=(4,2.95), xytext=(4,3.58),
                arrowprops=dict(arrowstyle='<->', color=NAVY, lw=2))
    ax.text(5.0, 3.26, 'PDO / SQL / TCP 3306', fontsize=8, color=NAVY)

    # Client devices
    for xi, label in [(1.2,7.0),(1.2,5.5)]:
        pass
    ax.text(0.4, 7.2, '🖥 Desktop', fontsize=8, color=GREY)
    ax.text(0.4, 6.8, '📱 Mobile', fontsize=8, color=GREY)

    save(fig, 'fig3_2_architecture.png')

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.3 – ERD
# ════════════════════════════════════════════════════════════════════════════
def fig_3_3():
    fig, ax = plt.subplots(figsize=(16, 11))
    fig.patch.set_facecolor(WHITE); ax.set_xlim(0,16); ax.set_ylim(0,11); ax.axis('off')
    fig.suptitle('Figure 3.3: Entity-Relationship Diagram (ERD)',
                 fontsize=13, fontweight='bold', color=NAVY, y=0.995)

    tables = {
        'users':        (2.0, 9.5, '#e3f2fd', BLUE, 'users\nPK: id\nusername, email\npassword_hash, role\nfull_name, status'),
        'departments':  (8.0, 9.5, '#e8f5e9', GREEN, 'departments\nPK: id\nname, code\nfaculty'),
        'sessions':     (13.5,9.5, '#fff3e0', ORANGE,'academic_sessions\nPK: id\nsession_name\nstart_date, end_date\nis_current, semester'),
        'students':     (5.0, 6.5, '#e3f2fd', BLUE, 'students\nPK: id\nmatric_number\nfirst_name, last_name\ndepartment_id FK\nlevel, status, user_id FK'),
        'courses':      (11.0,6.5, '#e8f5e9', GREEN,'courses\nPK: id\ncourse_code, title\ncredit_units\ndepartment_id FK\nlevel, semester'),
        'grades':       (2.5, 3.5, '#fce4ec', RED,  'grades\nPK: id\nstudent_id FK\ncourse_id FK\nsession_id FK\nca_score, exam_score\nletter_grade, grade_points'),
        'attendance':   (7.5, 3.5, '#e8f5e9', GREEN,'attendance\nPK: id\nstudent_id FK\ncourse_id FK\nsession_id FK\ndate, status'),
        'sc':           (5.0, 1.2, '#f3e5f5', PURPLE,'student_courses\nPK: id\nstudent_id FK\ncourse_id FK\nsession_id FK'),
        'fee_struct':   (11.0,3.5, '#fff3e0', ORANGE,'fee_structures\nPK: id\nsession_id FK\ndepartment_id FK\nlevel, fee_type, amount'),
        'fee_pay':      (13.5,1.2, '#fce4ec', RED,  'fee_payments\nPK: id\nstudent_id FK\nsession_id FK\nfee_structure_id FK\namount_paid\nreceipt_number'),
        'audit':        (13.5,6.5, '#eceff1', GREY, 'audit_logs\nPK: id\nuser_id FK\naction, module\ndescription, ip_address'),
    }
    coords = {}
    for key, (x, y, fc, ec, label) in tables.items():
        box(ax, x, y, 2.8, 1.6, label, fc=fc, ec=ec, fontsize=7, bold=False, radius=0.05)
        coords[key] = (x, y)

    rels = [
        ('users','students','has'),('departments','students','in'),
        ('departments','courses','offers'),('students','grades','receives'),
        ('courses','grades','graded'),('sessions','grades','for session'),
        ('students','attendance','tracked'),('courses','attendance','course'),
        ('students','sc','enrolled'),('courses','sc','taken'),
        ('departments','fee_struct','fee for'),('sessions','fee_struct','in'),
        ('students','fee_pay','pays'),('fee_struct','fee_pay','→'),
        ('users','audit','generates'),
    ]
    for a, b, lbl in rels:
        if a in coords and b in coords:
            ax.annotate('', xy=coords[b], xytext=coords[a],
                        arrowprops=dict(arrowstyle='->', color='#90a4ae', lw=1.2), zorder=2)

    save(fig, 'fig3_3_erd.png')

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.4 – DFD Level 0 Context Diagram
# ════════════════════════════════════════════════════════════════════════════
def fig_3_4():
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(WHITE); ax.set_xlim(0,12); ax.set_ylim(0,8); ax.axis('off')
    fig.suptitle('Figure 3.4: Data Flow Diagram – Level 0 Context Diagram',
                 fontsize=12, fontweight='bold', color=NAVY, y=0.99)

    # Central process
    ell = mpatches.Ellipse((6, 4), 3.2, 2.0, facecolor='#e3f2fd', edgecolor=BLUE, linewidth=2.5, zorder=3)
    ax.add_patch(ell)
    ax.text(6, 4, 'SRMS\nWeb Application', ha='center', va='center',
            fontsize=11, fontweight='bold', color=NAVY, zorder=4)

    actors = [
        (1.2, 6.8, 'Admin', NAVY, '#e8eaf6'),
        (1.2, 4.0, 'Registrar', GREEN, '#e8f5e9'),
        (1.2, 1.2, 'Teacher', ORANGE, '#fff3e0'),
        (10.8,4.0, 'Student', BLUE, '#e3f2fd'),
    ]
    for x, y, name, ec, fc in actors:
        box(ax, x, y, 1.8, 0.8, name, fc=fc, ec=ec, fontsize=10, bold=True)

    flows = [
        (2.1,6.8,4.4,4.8,'User mgmt commands\nSystem config', NAVY, True),
        (4.4,5.2,2.1,6.8,'Audit logs\nSystem reports', NAVY, False),
        (2.1,4.0,4.4,4.1,'Student data\nEnrolment records\nFee payments', GREEN, True),
        (4.4,3.9,2.1,4.0,'Transcripts\nFee statements', GREEN, False),
        (2.1,1.2,4.4,3.3,'Grade entries\nAttendance records', ORANGE, True),
        (4.4,3.1,2.1,1.2,'Grade summaries\nAttendance reports', ORANGE, False),
        (9.6,4.1,7.6,4.1,'Login, Profile updates', BLUE, True),
        (7.6,3.9,9.6,3.9,'Grades, GPA, Fee balance\nAttendance, Transcript', BLUE, False),
    ]
    for x0,y0,x1,y1,label,color,right in flows:
        ax.annotate('', xy=(x1,y1), xytext=(x0,y0),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.8), zorder=5)
        mx, my = (x0+x1)/2, (y0+y1)/2
        offset = 0.15 if right else -0.12
        ax.text(mx+offset, my, label, fontsize=7, color=color, ha='center', style='italic')

    save(fig, 'fig3_4_dfd.png')

# ════════════════════════════════════════════════════════════════════════════
# Generic flowchart helper
# ════════════════════════════════════════════════════════════════════════════
def flowchart(title, fname, steps, decisions=None, x=5, dx=0.0):
    """
    steps: list of (y, label, fc, ec)
    decisions: list of (y, label, yes_go, no_go)  – not used in simple version
    """
    fig, ax = plt.subplots(figsize=(10, len(steps)*1.1 + 2))
    fig.patch.set_facecolor(WHITE)
    ax.set_xlim(0,10); ax.set_ylim(0, len(steps)*1.4+1); ax.axis('off')
    fig.suptitle(title, fontsize=11, fontweight='bold', color=NAVY, y=0.99)

    max_y = len(steps)*1.4
    ys = []
    for i, (label, fc, ec, shape) in enumerate(steps):
        y = max_y - i*1.4
        ys.append(y)
        if shape == 'oval':
            oval(ax, x, y, 2.8, 0.7, label, fc=fc, ec=ec)
        elif shape == 'diamond':
            diamond(ax, x, y, 3.0, 0.9, label, fc=fc, ec=ec)
        else:
            box(ax, x, y, 3.5, 0.7, label, fc=fc, ec=ec, fontsize=9, bold=False)

    for i in range(len(ys)-1):
        arrow(ax, x, ys[i]-0.35, x, ys[i+1]+0.45, color=GREY)

    save(fig, fname)

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.5 – Login Flowchart
# ════════════════════════════════════════════════════════════════════════════
def fig_3_5():
    steps = [
        ('Start', LGREEN, GREEN, 'oval'),
        ('Display Login Form', '#e3f2fd', BLUE, 'rect'),
        ('User Enters Username & Password', '#e3f2fd', BLUE, 'rect'),
        ('Validate CSRF Token', '#fff3e0', ORANGE, 'rect'),
        ('CSRF Valid?', '#fff9c4', '#f9a825', 'diamond'),
        ('Query Database for Username', '#e3f2fd', BLUE, 'rect'),
        ('User Found?', '#fff9c4', '#f9a825', 'diamond'),
        ('Verify Password (password_verify)', '#e3f2fd', BLUE, 'rect'),
        ('Password Correct?', '#fff9c4', '#f9a825', 'diamond'),
        ('Regenerate Session ID', '#e8f5e9', GREEN, 'rect'),
        ('Set Session Variables\n(user_id, role, name)', '#e8f5e9', GREEN, 'rect'),
        ('Log Login to Audit Log', '#e8f5e9', GREEN, 'rect'),
        ('Redirect to Dashboard / Portal', '#e8f5e9', GREEN, 'rect'),
        ('End', LGREEN, GREEN, 'oval'),
    ]
    flowchart('Figure 3.5: Login Process Flowchart', 'fig3_5_login.png', steps)

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.6 – Student Registration Flowchart
# ════════════════════════════════════════════════════════════════════════════
def fig_3_6():
    steps = [
        ('Start', LGREEN, GREEN, 'oval'),
        ('Registrar Opens Add Student Form', '#e3f2fd', BLUE, 'rect'),
        ('Enter Personal / Guardian /\nAcademic Information', '#e3f2fd', BLUE, 'rect'),
        ('Submit Form', '#e3f2fd', BLUE, 'rect'),
        ('Validate CSRF Token', '#fff3e0', ORANGE, 'rect'),
        ('CSRF & Fields Valid?', '#fff9c4', '#f9a825', 'diamond'),
        ('Check Matric Number Unique?', '#e3f2fd', BLUE, 'rect'),
        ('Matric Unique?', '#fff9c4', '#f9a825', 'diamond'),
        ('Begin Database Transaction', '#e8f5e9', GREEN, 'rect'),
        ('INSERT into students table', '#e8f5e9', GREEN, 'rect'),
        ('COMMIT Transaction', '#e8f5e9', GREEN, 'rect'),
        ('Log Action to Audit Log', '#e8f5e9', GREEN, 'rect'),
        ('Show Success Flash Message', '#e8f5e9', GREEN, 'rect'),
        ('Redirect to Student List', '#e8f5e9', GREEN, 'rect'),
        ('End', LGREEN, GREEN, 'oval'),
    ]
    flowchart('Figure 3.6: Student Registration Process Flowchart', 'fig3_6_registration.png', steps)

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.7 – Grade Entry Flowchart
# ════════════════════════════════════════════════════════════════════════════
def fig_3_7():
    steps = [
        ('Start', LGREEN, GREEN, 'oval'),
        ('Teacher Selects Course & Session', '#e3f2fd', BLUE, 'rect'),
        ('System Loads Enrolled Students', '#e3f2fd', BLUE, 'rect'),
        ('Teacher Enters CA Score & Exam Score', '#e3f2fd', BLUE, 'rect'),
        ('JS Auto-Calculates Total,\nLetter Grade & Grade Points', '#fff3e0', ORANGE, 'rect'),
        ('Teacher Reviews & Submits', '#e3f2fd', BLUE, 'rect'),
        ('Validate CSRF Token', '#fff3e0', ORANGE, 'rect'),
        ('Validate Score Ranges\n(CA: 0–40, Exam: 0–60)', '#fff3e0', ORANGE, 'rect'),
        ('All Scores Valid?', '#fff9c4', '#f9a825', 'diamond'),
        ('Begin Database Transaction', '#e8f5e9', GREEN, 'rect'),
        ('UPSERT Grade Records\n(per student per course)', '#e8f5e9', GREEN, 'rect'),
        ('COMMIT Transaction', '#e8f5e9', GREEN, 'rect'),
        ('Log to Audit Log', '#e8f5e9', GREEN, 'rect'),
        ('Show Success Message', '#e8f5e9', GREEN, 'rect'),
        ('End', LGREEN, GREEN, 'oval'),
    ]
    flowchart('Figure 3.7: Grade Entry Process Flowchart', 'fig3_7_grades.png', steps)

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.8 – Fee Payment Flowchart
# ════════════════════════════════════════════════════════════════════════════
def fig_3_8():
    steps = [
        ('Start', LGREEN, GREEN, 'oval'),
        ('Registrar Opens Add Payment Form', '#e3f2fd', BLUE, 'rect'),
        ('Select Student via AJAX Search', '#e3f2fd', BLUE, 'rect'),
        ('Select Session & Fee Structure', '#e3f2fd', BLUE, 'rect'),
        ('System Shows Fee Amount\n& Current Balance', '#e3f2fd', BLUE, 'rect'),
        ('Enter Amount Paid\n& Payment Method', '#e3f2fd', BLUE, 'rect'),
        ('System Auto-Generates\nReceipt Number (RCP-YYYYMMDD-XXXXXX)', '#fff3e0', ORANGE, 'rect'),
        ('Submit Form', '#e3f2fd', BLUE, 'rect'),
        ('Validate CSRF & Required Fields', '#fff3e0', ORANGE, 'rect'),
        ('Fields Valid?', '#fff9c4', '#f9a825', 'diamond'),
        ('INSERT fee_payment Record', '#e8f5e9', GREEN, 'rect'),
        ('Log to Audit Log', '#e8f5e9', GREEN, 'rect'),
        ('Display Receipt Page', '#e8f5e9', GREEN, 'rect'),
        ('End', LGREEN, GREEN, 'oval'),
    ]
    flowchart('Figure 3.8: Fee Payment Recording Process Flowchart', 'fig3_8_fees.png', steps)

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.9 – Report Generation Flowchart
# ════════════════════════════════════════════════════════════════════════════
def fig_3_9():
    steps = [
        ('Start', LGREEN, GREEN, 'oval'),
        ('User Selects Report Type\n(Transcript / Class List / Attendance / Fee Statement)', '#e3f2fd', BLUE, 'rect'),
        ('Select Report Parameters\n(Student, Course, Session)', '#e3f2fd', BLUE, 'rect'),
        ('Query Database\n(Grades, GPA, Attendance, Fees)', '#e3f2fd', BLUE, 'rect'),
        ('Render Report View\nwith Print CSS Applied', '#e8f5e9', GREEN, 'rect'),
        ('Display Print Preview\nin Browser Window', '#e8f5e9', GREEN, 'rect'),
        ('Browser Print Dialog\n(Ctrl+P)', '#e8f5e9', GREEN, 'rect'),
        ('Physical Print\nor Save as PDF', '#e8f5e9', GREEN, 'rect'),
        ('End', LGREEN, GREEN, 'oval'),
    ]
    flowchart('Figure 3.9: Report Generation Process Flowchart', 'fig3_9_reports.png', steps)

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.10 – Database Schema Diagram
# ════════════════════════════════════════════════════════════════════════════
def fig_3_10():
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor(WHITE); ax.set_xlim(0,14); ax.set_ylim(0,9); ax.axis('off')
    fig.suptitle('Figure 3.10: Database Schema Diagram',
                 fontsize=12, fontweight='bold', color=NAVY, y=0.99)

    tbl = {
        'users':         (2,8.0, '#e3f2fd',BLUE),
        'departments':   (7,8.0, '#e8f5e9',GREEN),
        'sessions':      (12,8.0,'#fff3e0',ORANGE),
        'students':      (2,5.5, '#e3f2fd',BLUE),
        'courses':       (7,5.5, '#e8f5e9',GREEN),
        'grades':        (2,3.0, '#fce4ec',RED),
        'attendance':    (7,3.0, '#e8f5e9',GREEN),
        'student_courses':(4.5,1.2,'#f3e5f5',PURPLE),
        'fee_structures':(10,5.5,'#fff3e0',ORANGE),
        'fee_payments':  (10,3.0,'#fce4ec',RED),
        'audit_logs':    (12,5.5,'#eceff1',GREY),
        'course_assign': (9.5,1.2,'#e8f5e9',GREEN),
    }
    for name,(x,y,fc,ec) in tbl.items():
        short = name.replace('_',' ').replace('course assign','course\nassignments')
        box(ax,x,y,2.6,0.9,short,fc=fc,ec=ec,fontsize=8.5,bold=True)

    fks = [
        ('users','students'),('departments','students'),
        ('students','grades'),('courses','grades'),('sessions','grades'),
        ('students','attendance'),('courses','attendance'),('sessions','attendance'),
        ('students','student_courses'),('courses','student_courses'),('sessions','student_courses'),
        ('departments','fee_structures'),('sessions','fee_structures'),
        ('students','fee_payments'),('fee_structures','fee_payments'),('sessions','fee_payments'),
        ('users','audit_logs'),('courses','course_assign'),('sessions','course_assign'),('users','course_assign'),
    ]
    for a,b in fks:
        if a in tbl and b in tbl:
            x0,y0=tbl[a][0],tbl[a][1]
            x1,y1=tbl[b][0],tbl[b][1]
            ax.annotate('',xy=(x1,y1),xytext=(x0,y0),
                        arrowprops=dict(arrowstyle='->',color='#90a4ae',lw=1.1),zorder=2)

    save(fig, 'fig3_10_schema.png')

# ════════════════════════════════════════════════════════════════════════════
# Figure 3.11 – Deployment Architecture
# ════════════════════════════════════════════════════════════════════════════
def fig_3_11():
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(WHITE); ax.set_xlim(0,12); ax.set_ylim(0,7); ax.axis('off')
    fig.suptitle('Figure 3.11: Deployment Architecture Diagram',
                 fontsize=12, fontweight='bold', color=NAVY, y=0.99)

    # Client
    box(ax,1.5,5.5,2.6,1.6,'CLIENT DEVICES\n\n🖥 Desktop Browser\n📱 Mobile Browser',
        fc='#e3f2fd',ec=BLUE,fontsize=9)
    # CDN
    box(ax,1.5,2.5,2.6,1.2,'CDN\nBootstrap • jQuery\nChart.js',
        fc='#f3e5f5',ec=PURPLE,fontsize=8.5)
    # Web server
    box(ax,5.5,5.5,3.0,1.6,'WEB SERVER\n\nApache 2.4 (HTTPS/TLS)\nPHP 8.1 FPM',
        fc='#e8f5e9',ec=GREEN,fontsize=9)
    # DB
    box(ax,5.5,2.5,3.0,1.2,'DATABASE SERVER\n\nMySQL 8.0\nsrms_db',
        fc='#fff3e0',ec=ORANGE,fontsize=9)
    # Backup
    box(ax,9.5,2.5,2.4,1.2,'BACKUP\n\nDaily mysqldump\nCloud Storage',
        fc='#eceff1',ec=GREY,fontsize=8.5)
    # Institution network
    rect2 = FancyBboxPatch((3.8,0.6),5.8,6.0,boxstyle='round,pad=0.15',
                           facecolor='#f5f5f5',edgecolor=GREY,linewidth=1.5,linestyle='--')
    ax.add_patch(rect2)
    ax.text(6.7,6.4,'Institution / Cloud Network',ha='center',fontsize=8.5,color=GREY,style='italic')

    for x0,y0,x1,y1,lbl in [
        (2.8,5.5,4.0,5.5,'HTTPS'),(2.8,4.9,2.8,3.1,'CDN assets'),
        (7.0,4.7,7.0,3.1,'PDO/SQL'),(8.5,2.5,8.7,2.5,'mysqldump'),
        (8.7,2.5,8.3,2.5,''),
    ]:
        arrow(ax,x0,y0,x1,y1,lbl,color=NAVY)

    save(fig, 'fig3_11_deployment.png')

# ════════════════════════════════════════════════════════════════════════════
# Run all
# ════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Rendering all figures...')
    fig_2_1(); fig_2_2(); fig_2_3()
    fig_3_1(); fig_3_2(); fig_3_3(); fig_3_4()
    fig_3_5(); fig_3_6(); fig_3_7(); fig_3_8(); fig_3_9()
    fig_3_10(); fig_3_11()
    print(f'\nAll 14 figures saved to {OUT}')
