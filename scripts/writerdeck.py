#!/usr/bin/env python3
"""
writerdeck — a minimal TUI writing program for a dedicated writing device.
Requires: Python 3.7+, curses (standard library)
"""

import curses
import json
import os
import sys
import time
import threading
import locale
locale.setlocale(locale.LC_ALL, '')

# ── Config ──────────────────────────────────────────────────────────────────

DOCS_DIR = os.path.expanduser("~/documents")

# ── Dropbox sync ─────────────────────────────────────────────────────────────

DROPBOX_TOKEN_FILE = os.path.expanduser("~/.dropbox_token.json")
DROPBOX_APP_KEY    = "qaawugjaftf21d6"
DROPBOX_APP_SECRET = "sk4vs8gmyu91q8g"

def load_dropbox_client():
    """Charge le client Dropbox depuis le fichier de token permanent."""
    import dropbox
    with open(DROPBOX_TOKEN_FILE, 'r') as f:
        data = json.load(f)
    return dropbox.Dropbox(
        oauth2_refresh_token=data["refresh_token"],
        app_key=data["app_key"],
        app_secret=data["app_secret"]
    )

def dropbox_configured():
    """Vérifie si Dropbox est configuré."""
    return os.path.exists(DROPBOX_TOKEN_FILE)

def dropbox_upload(filepath):
    """Upload silencieux vers Dropbox en arrière-plan (si configuré)."""
    if not dropbox_configured():
        return
    def _upload():
        try:
            import dropbox
            dbx = load_dropbox_client()
            dest = f"/{os.path.basename(filepath)}"
            with open(filepath, 'rb') as f:
                dbx.files_upload(f.read(), dest,
                                 mode=dropbox.files.WriteMode.overwrite)
        except Exception:
            pass
    threading.Thread(target=_upload, daemon=True).start()

def dropbox_setup(stdscr):
    """Flow d'autorisation Dropbox en TUI."""
    try:
        import dropbox as dbx_module
        from dropbox import DropboxOAuth2FlowNoRedirect
    except ImportError:
        return False

    curses.curs_set(0)
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    lines = [
        "",
        "  Configuration Dropbox",
        "",
        "  1. Va sur : https://www.dropbox.com/developers/apps",
        "  2. Crée une app (Scoped Access > Full Dropbox)",
        "  3. Renseigne APP_KEY et APP_SECRET dans writerdeck.py",
        "",
        "  Appuie sur une touche pour lancer l'autorisation...",
        "",
    ]
    for i, line in enumerate(lines):
        try:
            stdscr.addstr(i + 2, 0, line[:w])
        except curses.error:
            pass
    stdscr.refresh()
    stdscr.getch()

    # Générer l'URL d'autorisation
    auth_flow = DropboxOAuth2FlowNoRedirect(
        DROPBOX_APP_KEY,
        DROPBOX_APP_SECRET,
        token_access_type="offline"
    )
    url = auth_flow.start()

    stdscr.erase()
    url_lines = [
        "",
        "  Ouvre ce lien dans un navigateur :",
        "",
        f"  {url}",
        "",
        "  Clique sur 'Autoriser', copie le code,",
        "  puis reviens ici et colle-le.",
        "",
    ]
    for i, line in enumerate(url_lines):
        try:
            stdscr.addstr(i + 1, 0, line[:w])
        except curses.error:
            pass
    stdscr.refresh()

    # Saisie du code
    curses.curs_set(1)
    prompt = "  Code d'autorisation : "
    try:
        stdscr.addstr(len(url_lines) + 2, 0, prompt)
    except curses.error:
        pass
    stdscr.refresh()

    code = ""
    while True:
        try:
            ch = stdscr.get_wch()
        except curses.error:
            continue
        if ch in (curses.KEY_ENTER, '\n', '\r'):
            break
        elif ch in (curses.KEY_BACKSPACE, '\x7f', '\x08'):
            code = code[:-1]
        elif isinstance(ch, str) and ch >= ' ':
            code += ch
        display = prompt + code
        try:
            stdscr.addstr(len(url_lines) + 2, 0, display[:w])
            stdscr.move(len(url_lines) + 2, min(len(display), w - 1))
        except curses.error:
            pass
        stdscr.refresh()

    curses.curs_set(0)

    # Finaliser
    try:
        result = auth_flow.finish(code.strip())
        token_data = {
            "access_token":  result.access_token,
            "refresh_token": result.refresh_token,
            "app_key":       DROPBOX_APP_KEY,
            "app_secret":    DROPBOX_APP_SECRET,
        }
        with open(DROPBOX_TOKEN_FILE, "w") as f:
            json.dump(token_data, f)
        os.chmod(DROPBOX_TOKEN_FILE, 0o600)

        stdscr.erase()
        try:
            stdscr.addstr(3, 0, "  ✓ Dropbox configuré ! La sync est active.")
            stdscr.addstr(5, 0, "  Appuie sur une touche pour continuer...")
        except curses.error:
            pass
        stdscr.refresh()
        stdscr.getch()
        return True
    except Exception as e:
        stdscr.erase()
        try:
            stdscr.addstr(3, 0, f"  ✗ Erreur : {str(e)[:w-6]}")
            stdscr.addstr(5, 0, "  Appuie sur une touche pour continuer sans Dropbox...")
        except curses.error:
            pass
        stdscr.refresh()
        stdscr.getch()
        return False
CURSOR_FILE = os.path.join(DOCS_DIR, ".cursors.json")
FILE_EXT = ".txt"
TAB_WIDTH = 4

# ── Helpers ─────────────────────────────────────────────────────────────────

def ensure_docs_dir():
    os.makedirs(DOCS_DIR, exist_ok=True)

def list_docs():
    """Return sorted list of document filenames."""
    ensure_docs_dir()
    files = [f for f in os.listdir(DOCS_DIR)
             if os.path.isfile(os.path.join(DOCS_DIR, f))
             and not f.startswith(".")]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(DOCS_DIR, f)), reverse=True)
    return files

def word_count(lines):
    return sum(len(line.split()) for line in lines)

def char_count(lines):
    return sum(len(line) for line in lines)

# ── Cursor Persistence ─────────────────────────────────────────────────────

def load_cursor(filepath):
    """Load saved cursor position for a file. Returns (cy, cx)."""
    try:
        with open(CURSOR_FILE, 'r') as f:
            data = json.load(f)
        pos = data.get(filepath, [0, 0])
        return pos[0], pos[1]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return 0, 0

def save_cursor(filepath, cy, cx):
    """Persist cursor position for a file."""
    try:
        with open(CURSOR_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data[filepath] = [cy, cx]
    with open(CURSOR_FILE, 'w') as f:
        json.dump(data, f)

# ── Word Wrap Engine ───────────────────────────────────────────────────────

def wrap_line(line, width):
    """
    Wrap a single logical line into visual rows.
    Returns a list of (start_col, end_col) ranges into the original line.
    Wraps at word boundaries when possible, hard-wraps if a word exceeds width.
    An empty line produces one visual row.
    """
    if width <= 0:
        return [(0, len(line))]
    if len(line) == 0:
        return [(0, 0)]

    segments = []
    pos = 0
    length = len(line)

    while pos < length:
        if length - pos <= width:
            segments.append((pos, length))
            break

        chunk_end = pos + width
        break_at = line.rfind(' ', pos, chunk_end)

        if break_at > pos:
            segments.append((pos, break_at))
            pos = break_at + 1
        else:
            segments.append((pos, chunk_end))
            pos = chunk_end

    return segments


def build_wrap_map(lines, width):
    """
    Build a complete mapping from logical lines to visual rows.
    Returns a list of (line_idx, start_col, end_col) for each visual row.
    """
    vrows = []
    for li, line in enumerate(lines):
        segs = wrap_line(line, width)
        for start, end in segs:
            vrows.append((li, start, end))
    return vrows


def logical_to_visual(vrows, cy, cx):
    """
    Given a logical cursor (cy, cx), find the visual row index and
    screen column within that row.
    """
    for vi, (li, scol, ecol) in enumerate(vrows):
        if li == cy and scol <= cx <= ecol:
            if cx == ecol and ecol > scol:
                if vi + 1 < len(vrows) and vrows[vi + 1][0] == li:
                    continue
            return vi, cx - scol
    if vrows:
        vi = len(vrows) - 1
        li, scol, ecol = vrows[vi]
        return vi, min(cx - scol, ecol - scol)
    return 0, 0


def visual_to_logical(vrows, vi, screen_cx):
    """
    Given a visual row index and screen column, find the logical (cy, cx).
    Clamps screen_cx to the segment length.
    """
    if not vrows:
        return 0, 0
    vi = max(0, min(vi, len(vrows) - 1))
    li, scol, ecol = vrows[vi]
    max_cx = ecol - scol
    screen_cx = max(0, min(screen_cx, max_cx))
    return li, scol + screen_cx

# ── Status Bar ──────────────────────────────────────────────────────────────

def draw_status(stdscr, left="", right="", style=None):
    h, w = stdscr.getmaxyx()
    if style is None:
        style = curses.A_REVERSE
    bar = left + " " * max(0, w - len(left) - len(right)) + right
    bar = bar[:w]
    try:
        stdscr.addstr(h - 1, 0, bar, style)
    except curses.error:
        pass

def draw_help_bar(stdscr, text):
    h, w = stdscr.getmaxyx()
    text = text[:w]
    try:
        stdscr.addstr(h - 2, 0, text + " " * max(0, w - len(text)), curses.A_DIM)
    except curses.error:
        pass

# ── Prompt ──────────────────────────────────────────────────────────────────

def prompt_input(stdscr, label):
    """Show a single-line prompt at the bottom and return user input (or None on Esc)."""
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()
    draw_status(stdscr, left=f" {label}")
    stdscr.move(h - 1, len(label) + 2)
    stdscr.clrtoeol()
    stdscr.refresh()

    buf = ""
    while True:
        try:
            ch = stdscr.get_wch()
        except curses.error:
            continue
        if ch == 27:  # Esc
            curses.curs_set(0)
            return None
        elif ch in (curses.KEY_ENTER, '\n', '\r'):
            curses.curs_set(0)
            return buf
        elif ch in (curses.KEY_BACKSPACE, '\x7f', '\x08'):
            buf = buf[:-1]
        elif isinstance(ch, str) and ch >= ' ':
            buf += ch
        display = f" {label}{buf}"
        try:
            stdscr.addstr(h - 1, 0, display + " " * max(0, w - len(display)), curses.A_REVERSE)
            stdscr.move(h - 1, len(display))
        except curses.error:
            pass
        stdscr.refresh()

def confirm(stdscr, message):
    """Yes/no confirmation. Returns True if 'y'."""
    h, w = stdscr.getmaxyx()
    draw_status(stdscr, left=f" {message} (y/n)")
    stdscr.refresh()
    while True:
        ch = stdscr.getch()
        if ch in (ord('y'), ord('Y')):
            return True
        if ch in (ord('n'), ord('N'), 27):
            return False

# ── File Browser ────────────────────────────────────────────────────────────

def file_browser(stdscr):
    """
    Main file browser loop.
    Returns a filepath to edit, or None to quit the program.
    """
    curses.curs_set(0)
    sel = 0
    scroll_off = 0
    message = ""

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        usable = h - 3

        files = list_docs()

        header = " Writerdeck"
        stdscr.addstr(0, 0, header + " " * max(0, w - len(header)), curses.A_BOLD)

        if not files:
            empty_msg = "Appuyez sur [N] pour créer un nouveau document."
            y = h // 2
            x = max(0, (w - len(empty_msg)) // 2)
            stdscr.addstr(y, x, empty_msg, curses.A_DIM)
        else:
            sel = max(0, min(sel, len(files) - 1))
            if sel < scroll_off:
                scroll_off = sel
            if sel >= scroll_off + usable:
                scroll_off = sel - usable + 1

            for i in range(usable):
                idx = scroll_off + i
                if idx >= len(files):
                    break
                fname = files[idx]
                fpath = os.path.join(DOCS_DIR, fname)
                size = os.path.getsize(fpath)
                mtime = time.strftime("%b %d %H:%M", time.localtime(os.path.getmtime(fpath)))

                if size < 1024:
                    size_str = f"{size}B"
                else:
                    size_str = f"{size // 1024}K"

                name_col = 3
                meta = f"{size_str:>6}  {mtime}"
                max_name = w - name_col - len(meta) - 2
                display_name = fname[:max_name]

                row = i + 1
                if idx == sel:
                    style = curses.A_REVERSE
                    prefix = " › "
                else:
                    style = curses.A_NORMAL
                    prefix = "   "

                line = prefix + display_name + " " * max(0, w - name_col - len(display_name) - len(meta)) + meta
                line = line[:w]
                try:
                    stdscr.addstr(row, 0, line, style)
                except curses.error:
                    pass

        draw_help_bar(stdscr, " [Entrer] Ouvrir  [N] Nouveau  [S] Supprimer  [R] Renommer  [Q] Quitter")
        if message:
            draw_status(stdscr, left=f" {message}")
            message = ""
        else:
            doc_count = f"{len(files)} document{'s' if len(files) != 1 else ''}"
            draw_status(stdscr, left=f" {DOCS_DIR}", right=f"{doc_count} ")

        stdscr.refresh()
        ch = stdscr.getch()

        if ch == ord('q'):
            return None

        elif ch == curses.KEY_UP or ch == ord('k'):
            sel = max(0, sel - 1)
        elif ch == curses.KEY_DOWN or ch == ord('j'):
            sel = min(len(files) - 1, sel + 1)
        elif ch == curses.KEY_HOME:
            sel = 0
        elif ch == curses.KEY_END:
            sel = max(0, len(files) - 1)

        elif ch in (curses.KEY_ENTER, 10, 13):
            if files:
                return os.path.join(DOCS_DIR, files[sel])

        elif ch == ord('n'):
            name = prompt_input(stdscr, "Titre du nouveau document : ")
            if name:
                name = name.strip()
                if name and not name.startswith("."):
                    if not os.path.splitext(name)[1]:
                        name += FILE_EXT
                    fpath = os.path.join(DOCS_DIR, name)
                    if os.path.exists(fpath):
                        message = f"'{name}' already exists"
                    else:
                        open(fpath, 'w').close()
                        return fpath

        elif ch == ord('s'):
            if files:
                fname = files[sel]
                if confirm(stdscr, f"delete '{fname}'?"):
                    os.remove(os.path.join(DOCS_DIR, fname))
                    message = f"deleted '{fname}'"
                    sel = max(0, sel - 1)

        elif ch == ord('r'):
            if files:
                fname = files[sel]
                new_name = prompt_input(stdscr, f"rename '{fname}' to: ")
                if new_name and new_name.strip():
                    new_name = new_name.strip()
                    if not os.path.splitext(new_name)[1]:
                        new_name += FILE_EXT
                    old_path = os.path.join(DOCS_DIR, fname)
                    new_path = os.path.join(DOCS_DIR, new_name)
                    if os.path.exists(new_path):
                        message = f"'{new_name}' already exists"
                    else:
                        os.rename(old_path, new_path)
                        message = f"renamed → '{new_name}'"

# ── Editor ──────────────────────────────────────────────────────────────────

def editor(stdscr, filepath):
    """
    Minimal curses text editor with word wrap.
    Always saves on close. Remembers cursor position between sessions.
    """
    # Load file
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        with open(filepath, 'r', errors='replace') as f:
            lines = f.read().split('\n')
        if lines and lines[-1] == '':
            lines = lines[:-1]
        if not lines:
            lines = ['']
    else:
        lines = ['']

    # Restore cursor position
    cy, cx = load_cursor(filepath)
    cy = max(0, min(cy, len(lines) - 1))
    cx = max(0, min(cx, len(lines[cy])))

    scroll_y = 0
    target_screen_cx = None  # sticky column for up/down navigation
    dirty = False
    message = ""
    msg_time = 0

    def save():
        nonlocal dirty, message, msg_time
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines) + '\n')
        save_cursor(filepath, cy, cx)
        dirty = False
        message = "saved"
        msg_time = time.time()
        dropbox_upload(filepath)

    def save_and_close():
        save()
        curses.curs_set(0)

    curses.curs_set(1)

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        text_h = h - 2

        # Clamp cursor
        cy = max(0, min(cy, len(lines) - 1))
        cx = max(0, min(cx, len(lines[cy])))

        # Build wrap map
        vrows = build_wrap_map(lines, w)
        vi_cursor, scx_cursor = logical_to_visual(vrows, cy, cx)

        # Scroll to keep cursor visible
        if vi_cursor < scroll_y:
            scroll_y = vi_cursor
        if vi_cursor >= scroll_y + text_h:
            scroll_y = vi_cursor - text_h + 1
        scroll_y = max(0, min(scroll_y, max(0, len(vrows) - text_h)))

        # Draw wrapped text
        for i in range(text_h):
            vi = scroll_y + i
            if vi >= len(vrows):
                break
            li, scol, ecol = vrows[vi]
            segment = lines[li][scol:ecol]
            try:
                stdscr.addstr(i, 0, segment)
            except curses.error:
                pass

        # Help bar
        draw_help_bar(stdscr, " ^S Sauvegarder  ^Q Sauvegarder et fermer  ^F Rechercher  ^L Aller au numéro de ligne")

        # Status bar
        fname = os.path.basename(filepath)
        mod = " [+]" if dirty else ""
        left_str = f" {fname}{mod}"
        wc = word_count(lines)
        cc = char_count(lines)
        right_str = f"ln {cy + 1}/{len(lines)}  col {cx + 1}  {wc}w {cc}c "

        if message and (time.time() - msg_time < 2):
            left_str = f" {message}"

        draw_status(stdscr, left=left_str, right=right_str)

        # Position cursor
        screen_row = vi_cursor - scroll_y
        try:
            stdscr.move(screen_row, scx_cursor)
        except curses.error:
            pass

        stdscr.refresh()

        try:
            ch = stdscr.get_wch()
        except curses.error:
            continue

        continue_sticky = False

        # ── Navigation ──

        if ch == curses.KEY_UP:
            if vi_cursor > 0:
                if target_screen_cx is None:
                    target_screen_cx = scx_cursor
                cy, cx = visual_to_logical(vrows, vi_cursor - 1, target_screen_cx)
            continue_sticky = True

        elif ch == curses.KEY_DOWN:
            if vi_cursor < len(vrows) - 1:
                if target_screen_cx is None:
                    target_screen_cx = scx_cursor
                cy, cx = visual_to_logical(vrows, vi_cursor + 1, target_screen_cx)
            continue_sticky = True

        elif ch == curses.KEY_LEFT:
            if cx > 0:
                cx -= 1
            elif cy > 0:
                cy -= 1
                cx = len(lines[cy])

        elif ch == curses.KEY_RIGHT:
            if cx < len(lines[cy]):
                cx += 1
            elif cy < len(lines) - 1:
                cy += 1
                cx = 0

        elif ch == curses.KEY_HOME:
            li, scol, ecol = vrows[vi_cursor]
            cx = scol

        elif ch == curses.KEY_END:
            li, scol, ecol = vrows[vi_cursor]
            cx = ecol

        elif ch == curses.KEY_PPAGE:
            target_vi = max(0, vi_cursor - text_h)
            if target_screen_cx is None:
                target_screen_cx = scx_cursor
            cy, cx = visual_to_logical(vrows, target_vi, target_screen_cx)
            continue_sticky = True

        elif ch == curses.KEY_NPAGE:
            target_vi = min(len(vrows) - 1, vi_cursor + text_h)
            if target_screen_cx is None:
                target_screen_cx = scx_cursor
            cy, cx = visual_to_logical(vrows, target_vi, target_screen_cx)
            continue_sticky = True

        # ── Editing ──

        elif ch in (curses.KEY_BACKSPACE, '\x7f', '\x08'):
            if cx > 0:
                lines[cy] = lines[cy][:cx - 1] + lines[cy][cx:]
                cx -= 1
                dirty = True
            elif cy > 0:
                cx = len(lines[cy - 1])
                lines[cy - 1] += lines[cy]
                lines.pop(cy)
                cy -= 1
                dirty = True

        elif ch == curses.KEY_DC:
            if cx < len(lines[cy]):
                lines[cy] = lines[cy][:cx] + lines[cy][cx + 1:]
                dirty = True
            elif cy < len(lines) - 1:
                lines[cy] += lines[cy + 1]
                lines.pop(cy + 1)
                dirty = True

        elif ch in (curses.KEY_ENTER, '\n', '\r'):
            rest = lines[cy][cx:]
            lines[cy] = lines[cy][:cx]
            cy += 1
            lines.insert(cy, rest)
            cx = 0
            dirty = True

        elif ch == '\t':  # Tab
            spaces = " " * TAB_WIDTH
            lines[cy] = lines[cy][:cx] + spaces + lines[cy][cx:]
            cx += TAB_WIDTH
            dirty = True

        # ── Commands (Ctrl keys) ──

        elif ch == '\x13':  # Ctrl+S
            save()

        elif ch == '\x17':  # Ctrl+W — save & close
            save_and_close()
            return

        elif ch == '\x11':  # Ctrl+Q — save & close
            save_and_close()
            return

        elif ch == '\x1b':  # Esc — save & close
            save_and_close()
            return

        elif ch == '\x0c':  # Ctrl+L — aller à la ligne n°
            num = prompt_input(stdscr, "aller au numéro de ligne : ")
            curses.curs_set(1)
            if num and num.strip().isdigit():
                target = int(num.strip()) - 1
                cy = max(0, min(target, len(lines) - 1))
                cx = 0

        elif ch == '\x06':  # Ctrl+F — rechercher
            query = prompt_input(stdscr, "rechercher : ")
            curses.curs_set(1)
            if query and query.strip():
                q = query.strip().lower()
                # Collecter toutes les occurrences
                occurrences = []
                for li, line in enumerate(lines):
                    start = 0
                    while True:
                        idx = line.lower().find(q, start)
                        if idx == -1:
                            break
                        # Vérifier que c'est un mot entier
                        before = idx == 0 or not line[idx - 1].isalnum()
                        after = idx + len(q) >= len(line) or not line[idx + len(q)].isalnum()
                        if before and after:
                            occurrences.append((li, idx))
                        start = idx + 1
                if not occurrences:
                    message = f"'{query}' introuvable"
                    msg_time = time.time()
                else:
                    # Trouver l'occurrence suivante par rapport au curseur
                    occ_idx = 0
                    for i, (li, idx) in enumerate(occurrences):
                        if (li, idx) > (cy, cx):
                            occ_idx = i
                            break
                    else:
                        occ_idx = 0  # boucle au début
                    # Naviguer avec Entrée
                    while True:
                        cy, cx = occurrences[occ_idx]
                        message = f"'{query}'  {occ_idx + 1}/{len(occurrences)}  [entrée] Suivant  [esc] Quitter"
                        msg_time = time.time()
                        # Redessiner
                        stdscr.erase()
                        vrows = build_wrap_map(lines, w)
                        vi_cursor, scx_cursor = logical_to_visual(vrows, cy, cx)
                        if vi_cursor < scroll_y:
                            scroll_y = vi_cursor
                        if vi_cursor >= scroll_y + text_h:
                            scroll_y = vi_cursor - text_h + 1
                        for i in range(text_h):
                            vi = scroll_y + i
                            if vi >= len(vrows):
                                break
                            li, scol, ecol = vrows[vi]
                            segment = lines[li][scol:ecol]
                            try:
                                stdscr.addstr(i, 0, segment)
                            except curses.error:
                                pass
                        left_str = f" {message}"
                        draw_status(stdscr, left=left_str)
                        draw_help_bar(stdscr, " ^S Sauvegarder  ^Q Fermer  ^F Rechercher  ^L Aller au numéro de ligne")
                        screen_row = vi_cursor - scroll_y
                        try:
                            stdscr.move(screen_row, scx_cursor)
                        except curses.error:
                            pass
                        stdscr.refresh()
                        nav = stdscr.get_wch()
                        if nav in ('\n', '\r', curses.KEY_ENTER):
                            occ_idx = (occ_idx + 1) % len(occurrences)
                        elif nav == '\x1b':  # Esc — quitter la recherche
                            break
                        else:
                            break

        # ── Printable characters (including accents) ──

        elif isinstance(ch, str) and ch >= ' ':
            lines[cy] = lines[cy][:cx] + ch + lines[cy][cx:]
            cx += 1
            dirty = True

        # Reset sticky column on non-vertical movement
        if not continue_sticky:
            target_screen_cx = None

# ── Main ────────────────────────────────────────────────────────────────────

def main(stdscr):
    locale.setlocale(locale.LC_ALL, '')
    curses.start_color()
    curses.raw()
    stdscr.keypad(True)
    curses.use_default_colors()
    curses.set_escdelay(25)
    curses.curs_set(0)

    ensure_docs_dir()

    # Proposer la configuration Dropbox si pas encore fait
    if not dropbox_configured():
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        msg1 = " Dropbox non configuré. Activer la sync ?"
        msg2 = " [o] Configurer maintenant   [n] Continuer sans"
        try:
            stdscr.addstr(h // 2 - 1, 0, msg1[:w], curses.A_BOLD)
            stdscr.addstr(h // 2 + 1, 0, msg2[:w], curses.A_DIM)
        except curses.error:
            pass
        stdscr.refresh()
        ch = stdscr.getch()
        if ch in (ord('o'), ord('O'), ord('y'), ord('Y')):
            dropbox_setup(stdscr)

    while True:
        filepath = file_browser(stdscr)
        if filepath is None:
            break
        editor(stdscr, filepath)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("bye.")
