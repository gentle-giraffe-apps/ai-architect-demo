#!/usr/bin/env python3
"""Generate 6-slide PDF presentation: From AI Assistant to AI Architect"""

from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

# 16:9 landscape slide dimensions
SLIDE_W = 13.333 * inch
SLIDE_H = 7.5 * inch

# Colors
WHITE = HexColor("#FFFFFF")
DARK = HexColor("#1a1a2e")
GRAY = HexColor("#4a4a6a")
ACCENT = HexColor("#3a86ff")
BOX_BG = HexColor("#e8edf5")

OUTPUT = "/Users/jonathanritchey/gentle_github/ai-architect-demo/presentation/ai-architect-slides.pdf"

# Margins
MARGIN = 80
CONTENT_W = SLIDE_W - 2 * MARGIN
BOTTOM_MSG_Y = 50  # y for bottom message text


def draw_rounded_rect(c, x, y, w, h, r=8, fill_color=BOX_BG, stroke_color=None):
    c.saveState()
    c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(1.5)
    else:
        c.setStrokeColor(fill_color)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1 if stroke_color else 0)
    c.restoreState()


def _draw_triangle(c, points):
    p = c.beginPath()
    p.moveTo(points[0][0], points[0][1])
    p.lineTo(points[1][0], points[1][1])
    p.lineTo(points[2][0], points[2][1])
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def draw_arrow_down(c, x, y, length=40):
    c.saveState()
    c.setStrokeColor(ACCENT)
    c.setFillColor(ACCENT)
    c.setLineWidth(2.5)
    c.line(x, y, x, y - length + 10)
    _draw_triangle(c, [(x - 6, y - length + 12), (x + 6, y - length + 12), (x, y - length)])
    c.restoreState()


def draw_arrow_right(c, x, y, length=60):
    c.saveState()
    c.setStrokeColor(ACCENT)
    c.setFillColor(ACCENT)
    c.setLineWidth(2.5)
    c.line(x, y, x + length - 10, y)
    _draw_triangle(c, [(x + length - 12, y - 6), (x + length - 12, y + 6), (x + length, y)])
    c.restoreState()


def draw_flow_box(c, text, cx, cy, w=160, h=44, font_size=16):
    draw_rounded_rect(c, cx - w/2, cy - h/2, w, h, r=8, fill_color=BOX_BG, stroke_color=ACCENT)
    c.saveState()
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", font_size)
    c.drawCentredString(cx, cy - font_size * 0.35, text)
    c.restoreState()


def slide_background(c):
    c.setFillColor(WHITE)
    c.rect(0, 0, SLIDE_W, SLIDE_H, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0, 0, SLIDE_W, 4, fill=1, stroke=0)


def slide_title(c, title, y=None):
    if y is None:
        y = SLIDE_H - 80
    c.saveState()
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 40)
    words = title.split()
    lines = []
    line = ""
    max_w = SLIDE_W - 2 * MARGIN
    for w in words:
        test = line + " " + w if line else w
        if c.stringWidth(test, "Helvetica-Bold", 40) > max_w:
            lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)
    for i, ln in enumerate(lines):
        c.drawCentredString(SLIDE_W / 2, y - i * 50, ln)
    c.restoreState()
    return y - len(lines) * 50


def bottom_message(c, text, font_size=24):
    c.saveState()
    c.setFillColor(GRAY)
    c.setFont("Helvetica", font_size)
    c.drawCentredString(SLIDE_W / 2, BOTTOM_MSG_Y, text)
    c.restoreState()


# ── Slide 1: The Frustration ──
def slide_1(c):
    slide_background(c)
    btm = slide_title(c, "AI Feels Powerful... But Why Are We Still Babysitting It?")

    # Flow diagram - fit within margins
    cy = (btm + BOTTOM_MSG_Y + 60) / 2 + 20  # vertically center in available space
    boxes = ["prompt", "AI output", "fix & repeat"]
    n = len(boxes)
    box_w = 180
    arrow_len = 80
    total_w = n * box_w + (n - 1) * arrow_len
    start_x = (SLIDE_W - total_w) / 2 + box_w / 2

    for i, label in enumerate(boxes):
        bx = start_x + i * (box_w + arrow_len)
        draw_flow_box(c, label, bx, cy, w=box_w, h=44)
        if i < n - 1:
            draw_arrow_right(c, bx + box_w/2, cy, length=arrow_len)

    # Loop-back arrow underneath — centered under first box, arrow points up into bottom center
    c.saveState()
    c.setStrokeColor(ACCENT)
    c.setFillColor(ACCENT)
    c.setLineWidth(2)
    first_x = start_x  # center of first box
    last_x = start_x + (n - 1) * (box_w + arrow_len)  # center of last box
    arr_y = cy - 55
    # down from last box bottom
    c.line(last_x, cy - 22, last_x, arr_y)
    # across to first box center
    c.line(last_x, arr_y, first_x, arr_y)
    # up toward first box bottom (stop short of the box)
    box_bottom = cy - 22
    c.line(first_x, arr_y, first_x, box_bottom - 14)
    # arrowhead pointing up, tip just touches box bottom
    _draw_triangle(c, [
        (first_x - 6, box_bottom - 14),
        (first_x + 6, box_bottom - 14),
        (first_x, box_bottom - 2),
    ])
    c.restoreState()

    bottom_message(c, "Engineers are stuck supervising AI instead of delegating work.")


# ── Slide 2: The Permission Trap ──
def slide_2(c):
    slide_background(c)
    btm = slide_title(c, "The Permission Loop")

    # Available vertical space: from btm down to BOTTOM_MSG_Y + 60
    avail_top = btm - 30
    avail_bot = BOTTOM_MSG_Y + 70
    avail_h = avail_top - avail_bot

    steps = ["AI wants to run command", "permission request", "human approves", "repeat"]
    n = len(steps)
    step_gap = avail_h / (n - 1)
    cx = SLIDE_W / 2
    box_h = min(46, step_gap * 0.5)

    for i, label in enumerate(steps):
        cy = avail_top - i * step_gap
        draw_flow_box(c, label, cx, cy, w=280, h=box_h)
        if i < n - 1:
            draw_arrow_down(c, cx, cy - box_h/2, length=step_gap - box_h)

    # Loop-back arrow on right side
    c.saveState()
    c.setStrokeColor(ACCENT)
    c.setFillColor(ACCENT)
    c.setLineWidth(2)
    loop_x = cx + 170
    top_box_y = avail_top
    bot_box_y = avail_top - (n - 1) * step_gap
    c.line(loop_x, bot_box_y, loop_x + 35, bot_box_y)
    c.line(loop_x + 35, bot_box_y, loop_x + 35, top_box_y)
    c.line(loop_x + 35, top_box_y, loop_x, top_box_y)
    _draw_triangle(c, [(loop_x + 2, top_box_y - 6), (loop_x + 2, top_box_y + 6), (loop_x - 8, top_box_y)])
    c.restoreState()

    bottom_message(c, "Developers either babysit the tool or disable safety with dangerous flags.", font_size=22)


# ── Slide 2b: Permissions Gotcha ──
def slide_2b(c):
    slide_background(c)
    btm = slide_title(c, "Gotcha! Permissions Galore")

    # Terminal box showing permission prompts
    term_margin = 120
    term_x = term_margin
    term_w = SLIDE_W - 2 * term_margin
    term_top = btm - 25
    term_h = 300
    term_y = term_top - term_h

    TERM_BG = HexColor("#1e1e1e")
    TERM_YELLOW = HexColor("#dcdcaa")
    TERM_GRAY = HexColor("#808080")
    TERM_WHITE = HexColor("#d4d4d4")

    draw_rounded_rect(c, term_x, term_y, term_w, term_h, r=12, fill_color=TERM_BG)

    # File path header
    TERM_GRAY = HexColor("#808080")
    TERM_WHITE = HexColor("#d4d4d4")
    TERM_GREEN = HexColor("#4ec9b0")
    TERM_YELLOW = HexColor("#dcdcaa")
    TERM_ORANGE = HexColor("#ce9178")
    TERM_BLUE = HexColor("#569cd6")

    tx = term_x + 24
    ty = term_y + term_h - 30
    line_h = 18

    c.saveState()
    c.setFont("Courier", 11)
    c.setFillColor(TERM_GRAY)
    c.drawString(tx, ty, '// .claude/settings.json')
    ty -= line_h * 1.2

    json_lines = [
        (TERM_WHITE,  '{'),
        (TERM_WHITE,  '  "permissions": {'),
        (TERM_WHITE,  '    "allow": ['),
        (TERM_GREEN,  '      "Read", "Write", "Edit", "Glob", "Grep",'),
        (TERM_GREEN,  '      "Bash(git *)", "Bash(npm *)", "Bash(node *)",'),
        (TERM_GREEN,  '      "Bash(python3 *)", "Bash(pip3 *)",'),
        (TERM_GREEN,  '      "Bash(ls *)", "Bash(mkdir *)", "Bash(gh *)",'),
        (TERM_ORANGE, '      ...  // add more as needed'),
        (TERM_WHITE,  '    ],'),
        (TERM_WHITE,  '    "deny": ['),
        (TERM_YELLOW, '      "Read(.env)", "Read(.env.*)", "Read(secrets/**)"'),
        (TERM_WHITE,  '    ]'),
        (TERM_WHITE,  '  }'),
        (TERM_WHITE,  '}'),
    ]

    for color, line in json_lines:
        c.setFillColor(color)
        c.drawString(tx, ty, line)
        ty -= line_h
    c.restoreState()

    # Solution section
    sol_y = term_y - 35
    c.saveState()
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(DARK)
    c.drawCentredString(SLIDE_W / 2, sol_y, "The fix:  .claude/settings.json")
    c.restoreState()

    # Bold tagline
    c.saveState()
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(ACCENT)
    c.drawCentredString(SLIDE_W / 2, sol_y - 38, "Configure once \u2192 loops run unattended.")
    c.restoreState()

    # Advice lines
    advice = [
        "Allow common dev commands. Block secrets.",
        "Iterate the allowlist over time as you discover gaps.",
    ]
    c.saveState()
    c.setFont("Helvetica", 19)
    c.setFillColor(GRAY)
    for i, line in enumerate(advice):
        c.drawCentredString(SLIDE_W / 2, sol_y - 72 - i * 28, line)
    c.restoreState()


# ── Slide 2c: Teaching Your AI the Rules ──
def slide_2c(c):
    slide_background(c)
    btm = slide_title(c, "Teaching Your AI the Rules")

    # Two-column layout: left = CLAUDE.md snippet, right = key principles
    col_gap = 40
    col_w = (SLIDE_W - 2 * MARGIN - col_gap) / 2
    left_x = MARGIN
    right_x = MARGIN + col_w + col_gap

    # Left column: CLAUDE.md terminal snippet
    term_top = btm + 30
    term_h = 350
    term_y = term_top - term_h

    TERM_BG = HexColor("#1e1e1e")
    TERM_WHITE = HexColor("#d4d4d4")
    TERM_GREEN = HexColor("#4ec9b0")
    TERM_YELLOW = HexColor("#dcdcaa")
    TERM_ORANGE = HexColor("#ce9178")
    TERM_GRAY = HexColor("#808080")

    draw_rounded_rect(c, left_x, term_y, col_w, term_h, r=12, fill_color=TERM_BG)

    tx = left_x + 18
    ty = term_y + term_h - 28
    line_h = 17

    c.saveState()
    c.setFont("Courier", 10)

    claude_md_lines = [
        (TERM_GRAY,   "# CLAUDE.md"),
        (TERM_WHITE,  ""),
        (TERM_GREEN,  "## Commands to Avoid"),
        (TERM_WHITE,  ""),
        (TERM_WHITE,  "| Avoid       | Workaround          |"),
        (TERM_WHITE,  "|-------------|---------------------|"),
        (TERM_ORANGE, "| curl, wget  | Use WebFetch tool   |"),
        (TERM_ORANGE, "| ssh, scp    | Ask user to run     |"),
        (TERM_ORANGE, "| docker      | Ask user to run     |"),
        (TERM_ORANGE, "| git --force | Use safe variants   |"),
        (TERM_ORANGE, "| kill        | Ask user to run     |"),
        (TERM_WHITE,  ""),
        (TERM_GREEN,  "## General Rules"),
        (TERM_WHITE,  ""),
        (TERM_YELLOW, "- Prefer tools over Bash"),
        (TERM_YELLOW, "  (Read not cat, Grep not grep)"),
        (TERM_YELLOW, "- When in doubt, don't run it"),
        (TERM_YELLOW, "- Never guess at permissions"),
    ]

    for color, line in claude_md_lines:
        c.setFillColor(color)
        c.drawString(tx, ty, line)
        ty -= line_h

    c.restoreState()

    # Right column: key principles
    right_cx = right_x + col_w / 2
    principle_top = term_top - 10

    c.saveState()
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(ACCENT)
    c.drawCentredString(right_cx, principle_top, "Two-Layer Defense")
    c.restoreState()

    # Layer 1 box
    box_w = col_w - 40
    box_x = right_x + 20
    box1_y = principle_top - 80
    box1_h = 70
    draw_rounded_rect(c, box_x, box1_y, box_w, box1_h, r=10, fill_color=HexColor("#f0f8ff"), stroke_color=ACCENT)
    c.saveState()
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(DARK)
    c.drawCentredString(right_cx, box1_y + box1_h - 28, "Layer 1: settings.json")
    c.setFont("Helvetica", 15)
    c.setFillColor(GRAY)
    c.drawCentredString(right_cx, box1_y + box1_h - 52, "Blocks dangerous commands")
    c.restoreState()

    # Arrow between boxes
    draw_arrow_down(c, right_cx, box1_y, length=30)

    # Layer 2 box
    box2_y = box1_y - 30 - box1_h
    draw_rounded_rect(c, box_x, box2_y, box_w, box1_h, r=10, fill_color=HexColor("#f0fff0"), stroke_color=HexColor("#27ae60"))
    c.saveState()
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(DARK)
    c.drawCentredString(right_cx, box2_y + box1_h - 28, "Layer 2: CLAUDE.md")
    c.setFont("Helvetica", 15)
    c.setFillColor(GRAY)
    c.drawCentredString(right_cx, box2_y + box1_h - 52, "Teaches AI safe workarounds")
    c.restoreState()

    # Key takeaway bullets below
    takeaway_y = box2_y - 40
    takeaways = [
        "Don't just block — teach",
        "AI learns to self-correct",
        "Loops run longer unattended",
    ]
    c.saveState()
    c.setFont("Helvetica-Bold", 17)
    c.setFillColor(DARK)
    for i, t in enumerate(takeaways):
        c.drawCentredString(right_cx, takeaway_y - i * 28, t)
    c.restoreState()

    bottom_message(c, "CLAUDE.md + settings.json = unattended loops that don't stall.", font_size=22)


# ── Slide 3: The Ralph Loop ──
def slide_3(c):
    slide_background(c)
    btm = slide_title(c, "The Ralph Loop: A Structured Loop You Can Use Today")

    avail_top = btm - 25
    avail_bot = BOTTOM_MSG_Y + 65
    avail_h = avail_top - avail_bot

    steps = ["spec", "tasks", "AI implementation", "tests / judge", "commit"]
    n = len(steps)
    step_gap = avail_h / (n - 1)
    cx = SLIDE_W / 2
    box_h = min(44, step_gap * 0.5)

    for i, label in enumerate(steps):
        cy = avail_top - i * step_gap
        draw_flow_box(c, label, cx, cy, w=240, h=box_h)
        if i < n - 1:
            draw_arrow_down(c, cx, cy - box_h/2, length=step_gap - box_h)

    # Loop-back arrow
    c.saveState()
    c.setStrokeColor(ACCENT)
    c.setFillColor(ACCENT)
    c.setLineWidth(2.5)
    loop_x = cx + 150
    top_box_y = avail_top
    bot_box_y = avail_top - (n - 1) * step_gap
    c.line(loop_x, bot_box_y, loop_x + 40, bot_box_y)
    c.line(loop_x + 40, bot_box_y, loop_x + 40, top_box_y)
    c.line(loop_x + 40, top_box_y, loop_x, top_box_y)
    _draw_triangle(c, [(loop_x + 2, top_box_y - 7), (loop_x + 2, top_box_y + 7), (loop_x - 10, top_box_y)])
    c.restoreState()

    # "repeat" label
    c.saveState()
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(loop_x + 46, (top_box_y + bot_box_y) / 2 + 10, "ralph-loop")
    c.setFont("Helvetica", 14)
    c.drawString(loop_x + 46, (top_box_y + bot_box_y) / 2 - 10, "(max iterations)")
    c.restoreState()

    # Key insight text
    c.saveState()
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(DARK)
    insight_x = MARGIN + 60
    insight_y = (top_box_y + bot_box_y) / 2
    c.drawString(insight_x, insight_y + 10, "Tests fix errors,")
    c.drawString(insight_x, insight_y - 18, "not humans.")
    c.restoreState()

    bottom_message(c, "ralph-loop: a Claude Code plugin you can install and run today.")


# ── Slide 4: Real Example ──
def slide_4(c):
    slide_background(c)
    btm = slide_title(c, "Error Correction Without Babysitting")

    # Terminal box
    term_margin = 120
    term_x = term_margin
    term_w = SLIDE_W - 2 * term_margin
    term_top = btm - 40
    term_h = 220
    term_y = term_top - term_h

    # Black terminal background
    TERM_BG = HexColor("#1e1e1e")
    TERM_GREEN = HexColor("#4ec9b0")
    TERM_WHITE = HexColor("#d4d4d4")
    TERM_YELLOW = HexColor("#dcdcaa")
    TERM_GRAY = HexColor("#808080")

    draw_rounded_rect(c, term_x, term_y, term_w, term_h, r=12, fill_color=TERM_BG)

    # Terminal dots (red, yellow, green)
    dot_y = term_y + term_h - 20
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        c.saveState()
        c.setFillColor(HexColor(color))
        c.circle(term_x + 24 + i * 20, dot_y, 5, fill=1, stroke=0)
        c.restoreState()

    # Terminal content
    tx = term_x + 24
    line_h = 24
    ty = dot_y - 35

    # Line 1: command
    c.saveState()
    c.setFont("Courier", 14)
    c.setFillColor(TERM_GREEN)
    c.drawString(tx, ty, "$ ")
    c.setFillColor(TERM_WHITE)
    c.drawString(tx + 16, ty, '/ralph-loop:ralph-loop "Process specs:')
    ty -= line_h

    # Line 2: requirements
    c.setFillColor(TERM_WHITE)
    c.drawString(tx + 16, ty, '  1. Build auth module  2. Add tests  3. Deploy')
    ty -= line_h

    # Line 3: completion promise
    c.setFillColor(TERM_WHITE)
    c.drawString(tx + 16, ty, '  Print RALPH_FINISHED when all requirements met"')
    ty -= line_h

    # Line 4: flags
    c.setFillColor(TERM_YELLOW)
    c.drawString(tx + 16, ty, '  --max-iterations 20')
    c.setFillColor(TERM_YELLOW)
    c.drawString(tx + 16 + c.stringWidth('  --max-iterations 20  ', "Courier", 14), ty, '--completion-promise "RALPH_FINISHED"')
    ty -= line_h * 1.5

    # Line 5: output
    c.setFillColor(TERM_GRAY)
    c.drawString(tx, ty, 'Ralph loop activated! Iteration: 1 / 20')
    c.restoreState()

    # Observations below terminal
    obs_y = term_y - 40
    observations = [
        "Max iterations — set a budget for how long AI can try.",
        "Completion promise — the loop stops when the system says it's done.",
        "Automated retries — errors trigger the next iteration, not you.",
    ]

    c.saveState()
    c.setFont("Helvetica", 20)
    c.setFillColor(GRAY)
    for i, obs in enumerate(observations):
        c.drawCentredString(SLIDE_W / 2, obs_y - i * 30, obs)
    c.restoreState()


# ── Slide 4b: PAUL – Guided Project Creation ──
def slide_4b(c):
    slide_background(c)
    btm = slide_title(c, "PAUL: Plan-Apply-Unify Loop")

    # Two-column layout: left = what & install, right = interactive flow
    col_gap = 40
    col_w = (SLIDE_W - 2 * MARGIN - col_gap) / 2
    left_x = MARGIN
    right_x = MARGIN + col_w + col_gap

    content_top = btm - 20

    # ── Left column: What is PAUL + Install ──
    c.saveState()
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(ACCENT)
    c.drawString(left_x + 20, content_top, "What is PAUL?")
    c.restoreState()

    desc_lines = [
        "A structured project framework",
        "for Claude Code that replaces",
        "ad-hoc prompting with a repeatable",
        "development loop:",
        "",
        "PLAN  >  APPLY  >  UNIFY",
        "",
        "Tracks milestones, phases, plans,",
        "and tasks — with acceptance criteria",
        "and verification at every step.",
    ]

    c.saveState()
    dy = content_top - 30
    for line in desc_lines:
        if line == "PLAN  >  APPLY  >  UNIFY":
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(ACCENT)
        elif line == "":
            dy -= 6
            continue
        else:
            c.setFont("Helvetica", 15)
            c.setFillColor(GRAY)
        c.drawString(left_x + 20, dy, line)
        dy -= 20
    c.restoreState()

    # Install box
    install_y = dy - 8
    install_h = 58
    TERM_BG = HexColor("#1e1e1e")
    TERM_GREEN = HexColor("#4ec9b0")
    TERM_WHITE = HexColor("#d4d4d4")

    draw_rounded_rect(c, left_x + 10, install_y - install_h, col_w - 20, install_h, r=10, fill_color=TERM_BG)
    c.saveState()
    c.setFont("Courier", 12)
    c.setFillColor(TERM_GREEN)
    c.drawString(left_x + 28, install_y - 24, "$ npx paul-framework")
    c.setFillColor(TERM_WHITE)
    c.drawString(left_x + 28, install_y - 44, "$ /paul:help   # verify install")
    c.restoreState()

    # ── Right column: Interactive Init Flow ──
    c.saveState()
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(ACCENT)
    right_cx = right_x + col_w / 2
    c.drawCentredString(right_cx, content_top, "Interactive to Start")
    c.restoreState()

    # Flow: init → discuss → plan → apply → unify
    flow_steps = [
        ("/paul:init", "PAUL asks: what are you building?"),
        ("/paul:discuss", "Explore vision before committing"),
        ("/paul:plan", "Review tasks & acceptance criteria"),
        ("/paul:apply", "AI executes — you watch or walk away"),
        ("/paul:unify", "Compare plan vs actual, route next"),
    ]

    # Calculate step_gap to fit above bottom message
    flow_top = content_top - 35
    flow_bot = BOTTOM_MSG_Y + 70
    box_h = 42
    step_gap = (flow_top - flow_bot - box_h) / (len(flow_steps) - 1)
    box_w = col_w - 40

    for i, (cmd, desc) in enumerate(flow_steps):
        sy = flow_top - i * step_gap
        box_x = right_x + 20

        draw_rounded_rect(c, box_x, sy - box_h + 8, box_w, box_h, r=8,
                          fill_color=HexColor("#f0f8ff"), stroke_color=ACCENT)

        c.saveState()
        c.setFont("Courier-Bold", 13)
        c.setFillColor(DARK)
        c.drawString(box_x + 10, sy - 8, cmd)

        c.setFont("Helvetica", 11)
        c.setFillColor(GRAY)
        c.drawString(box_x + 10, sy - 24, desc)
        c.restoreState()

        if i < len(flow_steps) - 1:
            draw_arrow_down(c, right_cx, sy - box_h + 8, length=step_gap - box_h)

    bottom_message(c, "Guided setup — PAUL asks questions before writing any code.", font_size=22)


# ── Slide 5: From Assistant to Architect ──
def slide_5(c):
    slide_background(c)
    btm = slide_title(c, "The Engineer's Role Shifts Upward")

    # Two panels with "vs" between them
    panel_w = 340
    panel_h = 230
    gap = 80  # gap between panels for "vs"
    total_w = 2 * panel_w + gap
    left_x = (SLIDE_W - total_w) / 2
    right_x = left_x + panel_w + gap

    panel_top = btm - 30
    panel_bot = panel_top - panel_h

    # Left panel: AI Assistant
    draw_rounded_rect(c, left_x, panel_bot, panel_w, panel_h, r=12, fill_color=HexColor("#fff0f0"), stroke_color=HexColor("#cc4444"))
    left_cx = left_x + panel_w / 2

    c.saveState()
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(HexColor("#cc4444"))
    c.drawCentredString(left_cx, panel_top - 40, "AI Assistant")

    # prompt -> output flow
    c.setFont("Helvetica", 20)
    c.setFillColor(GRAY)
    flow_y = panel_top - 110
    prompt_w = c.stringWidth("prompt", "Helvetica", 20)
    total_flow = prompt_w + 50 + c.stringWidth("output", "Helvetica", 20)
    flow_start = left_cx - total_flow / 2
    c.drawString(flow_start, flow_y, "prompt")
    c.restoreState()
    draw_arrow_right(c, flow_start + prompt_w + 5, flow_y + 6, length=40)
    c.saveState()
    c.setFont("Helvetica", 20)
    c.setFillColor(GRAY)
    c.drawString(flow_start + prompt_w + 50, flow_y, "output")

    c.setFont("Helvetica", 16)
    c.setFillColor(GRAY)
    c.drawCentredString(left_cx, panel_bot + 40, "Manual, one-shot interaction")
    c.restoreState()

    # "vs" between panels
    c.saveState()
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(ACCENT)
    c.drawCentredString(left_x + panel_w + gap / 2, panel_bot + panel_h / 2 - 10, "vs")
    c.restoreState()

    # Right panel: AI Architect
    draw_rounded_rect(c, right_x, panel_bot, panel_w, panel_h, r=12, fill_color=HexColor("#f0f8ff"), stroke_color=ACCENT)
    right_cx = right_x + panel_w / 2

    c.saveState()
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(ACCENT)
    c.drawCentredString(right_cx, panel_top - 40, "AI Architect")

    # Flow: spec -> system -> evaluation
    flow_y2 = panel_top - 90
    c.setFont("Helvetica", 18)
    c.setFillColor(DARK)
    labels = ["spec", "system", "evaluation"]
    widths = [c.stringWidth(lb, "Helvetica", 18) for lb in labels]
    arrow_w = 35
    total_flow2 = sum(widths) + 2 * (arrow_w + 10)
    fx = right_cx - total_flow2 / 2
    for i, lb in enumerate(labels):
        c.drawString(fx, flow_y2, lb)
        if i < 2:
            c.restoreState()
            draw_arrow_right(c, fx + widths[i] + 5, flow_y2 + 5, length=arrow_w)
            c.saveState()
            c.setFont("Helvetica", 18)
            c.setFillColor(DARK)
        fx += widths[i] + arrow_w + 10

    # Focus areas
    focuses = ["system design", "task decomposition", "constraints", "quality judgment", "ralph-loop"]
    fy = panel_bot + 20 + len(focuses) * 18
    c.setFont("Helvetica", 14)
    c.setFillColor(GRAY)
    for i, f in enumerate(focuses):
        c.drawCentredString(right_cx, fy - i * 18, f)
    c.restoreState()


# ── Slide 6: How to Start ──
def slide_6(c):
    slide_background(c)
    btm = slide_title(c, "How to Start Changing Now")

    avail_top = btm - 40
    left_margin = MARGIN + 40

    steps = [
        {
            "number": "1",
            "title": "Stop prompting, start looping",
            "detail": "Use /ralph-loop instead of manual prompts.",
            "detail2": "Use AI to help you craft the command.",
        },
        {
            "number": "2",
            "title": "Learn agent orchestration",
            "detail": "Move from single prompts to subagents",
            "detail2": "and agent teams.",
        },
        {
            "number": "3",
            "title": "Let AI configure AI",
            "detail": "Ask Claude to audit your settings.json +",
            "detail2": "CLAUDE.md for loop-friendliness.",
        },
    ]

    step_h = 110
    start_y = avail_top

    for i, step in enumerate(steps):
        sy = start_y - i * step_h

        # Number circle
        circle_x = left_margin + 20
        circle_y = sy - 10
        c.saveState()
        c.setFillColor(ACCENT)
        c.circle(circle_x, circle_y, 22, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(circle_x, circle_y - 9, step["number"])
        c.restoreState()

        # Title
        text_x = circle_x + 40
        c.saveState()
        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(DARK)
        c.drawString(text_x, sy, step["title"])

        # Detail lines
        c.setFont("Helvetica", 20)
        c.setFillColor(GRAY)
        c.drawString(text_x, sy - 32, step["detail"])
        c.drawString(text_x, sy - 56, step["detail2"])
        c.restoreState()

    bottom_message(c, "Each step moves you from AI assistant to AI architect.")


# ── Slide 6b: Important Reminders ──
def slide_6b(c):
    slide_background(c)
    btm = slide_title(c, "Important Reminders")

    avail_top = btm - 40
    left_margin = MARGIN + 40

    reminders = [
        {
            "number": "1",
            "title": "Always start Claude from the root directory",
            "detail": "Otherwise it won't observe .claude/settings.json",
            "detail2": "and every command will trigger a permission prompt.",
        },
        {
            "number": "2",
            "title": "Make CLAUDE.md read settings.json immediately",
            "detail": "Add a prominent rule at the top of CLAUDE.md:",
            "detail2": '"Read .claude/settings.json before anything else."',
        },
        {
            "number": "3",
            "title": "Cancel ralph loops when finished",
            "detail": 'Run /ralph-loop:cancel-ralph after each loop ends.',
            "detail2": "Prevents accidental restarts in the next session.",
        },
    ]

    step_h = 110
    start_y = avail_top

    for i, rem in enumerate(reminders):
        sy = start_y - i * step_h

        # Number circle
        circle_x = left_margin + 20
        circle_y = sy - 10
        c.saveState()
        c.setFillColor(ACCENT)
        c.circle(circle_x, circle_y, 22, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(circle_x, circle_y - 9, rem["number"])
        c.restoreState()

        # Title
        text_x = circle_x + 40
        c.saveState()
        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(DARK)
        c.drawString(text_x, sy, rem["title"])

        # Detail lines
        c.setFont("Helvetica", 20)
        c.setFillColor(GRAY)
        c.drawString(text_x, sy - 32, rem["detail"])
        c.drawString(text_x, sy - 56, rem["detail2"])
        c.restoreState()

    bottom_message(c, "Get these right to reduce interruptions — then iterate as you discover gaps.")


# ── Slide 7: Discussion ──
def slide_7(c):
    slide_background(c)
    btm = slide_title(c, "Open Questions")

    questions = [
        "Are engineers becoming AI team managers?",
        "What skills become more valuable now?",
        'What does "senior engineer" mean',
        "in an AI workflow?",
        "How are you experimenting with AI today?",
    ]

    # Regroup: 4 actual questions, third one spans two lines
    real_questions = [
        "Are engineers becoming AI team managers?",
        "What workflows are you automating with AI?",
        "How are you experimenting with AI today?",
    ]

    avail_top = btm - 40
    avail_bot = BOTTOM_MSG_Y + 70
    q_gap = (avail_top - avail_bot) / (len(real_questions) - 1)
    left_margin = MARGIN + 60

    for i, q in enumerate(real_questions):
        qy = avail_top - i * q_gap
        c.saveState()
        c.setFillColor(DARK)
        c.setFont("Helvetica", 28)
        lines = q.split("\n")
        for j, line in enumerate(lines):
            c.drawString(left_margin, qy - j * 32, line)
        c.restoreState()



def main():
    c = canvas.Canvas(OUTPUT, pagesize=(SLIDE_W, SLIDE_H))

    slides = [slide_1, slide_2, slide_2b, slide_2c, slide_3, slide_4, slide_4b, slide_5, slide_6, slide_6b, slide_7]
    for i, slide_fn in enumerate(slides):
        slide_fn(c)
        if i < len(slides) - 1:
            c.showPage()

    c.save()
    print(f"Generated {len(slides)} slides -> {OUTPUT}")


if __name__ == "__main__":
    main()
