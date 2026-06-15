"""Domain Availability Checker & Generator Tool.

A GUI application to bulk-check domain availability using the RDAP protocol
and generate domain name suggestions by country, topic, or custom input.

Usage:
    python main.py

Dependencies:
    - requests (pip install requests)
    - tkinter  (bundled with Python)

For more info, see README.md
"""

import os
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import random
import time as _time

# Resolve paths relative to the script's directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DOMAINS_FILE = os.path.join(_SCRIPT_DIR, "domains.txt")
_RESULT_FILE = os.path.join(_SCRIPT_DIR, "result.txt")

# ==================== THEME ====================
BG       = "#eaf4fb"
BG2      = "#d6eaf8"
BGPANEL  = "#ddeef7"
FG       = "#1a2e3b"
FG2      = "#4a6572"
ENTRY_BG = "#f5fafd"
BORDER   = "#b0d0e8"
BTN_FG   = "#ffffff"

def _btn(parent, text, cmd, color, small=False):
    return tk.Button(parent, text=text, command=cmd, bg=color, fg=BTN_FG,
                     font=("Segoe UI", 9 if small else 10, "bold"),
                     padx=10, pady=3, relief=tk.FLAT, activebackground=color, cursor="hand2")

def _lf(parent, text):
    return tk.LabelFrame(parent, text=text, bg=BG2, fg=FG,
                         font=("Segoe UI", 9, "bold"), padx=8, pady=6, relief=tk.GROOVE, bd=1)

def _lbl(parent, text, small=False, fg=None):
    return tk.Label(parent, text=text, bg=BG2, fg=fg or FG,
                    font=("Segoe UI", 8 if small else 9))

def _entry(parent, var, width=6):
    return tk.Entry(parent, textvariable=var, width=width, font=("Segoe UI", 10),
                    bg=ENTRY_BG, fg=FG, relief=tk.FLAT,
                    highlightthickness=1, highlightbackground=BORDER)

def _chk(parent, text, var, bold=False, cmd=None, bg=None):
    return tk.Checkbutton(parent, text=text, variable=var, command=cmd,
                          bg=bg or BG2, fg=FG, selectcolor=ENTRY_BG, activebackground=bg or BG2,
                          font=("Segoe UI", 9, "bold" if bold else "normal"))

# ==================== DATA ====================
RDAP_ENDPOINTS = {
    'com': 'https://rdap.verisign.com/com/v1/domain/',
    'net': 'https://rdap.verisign.com/net/v1/domain/',
    'org': 'https://rdap.publicinterestregistry.org/rdap/domain/',
    'io':  'https://rdap.nic.io/domain/',
    'ai':  'https://rdap.nic.ai/domain/',
    'co':  'https://rdap.nic.co/domain/',
    'us':  'https://rdap.neustar.us/domain/',
    'vn':  'https://rdap.vnnic.vn/rdap/domain/',
    'de':  'https://rdap.denic.de/domain/',
    'fr':  'https://rdap.nic.fr/domain/',
    'jp':  'https://rdap.jp/domain/',
    'sg':  'https://rdap.sgnic.sg/domain/',
    'in':  'https://rdap.registry.in/domain/',
}

NAMES_BY_COUNTRY = {
    'Vietnam':      ['tuananh','phuong','minh','hoang','linh','nam','duc','hung','tuan','long',
                     'hai','thu','lan','hoa','quang','bao','khanh','trung','dat','phong',
                     'viet','thanh','cuong','dung','hieu','thien','son','ngan','van','khoa'],
    'USA':          ['james','john','robert','michael','william','david','richard','joseph',
                     'thomas','charles','chris','daniel','matthew','anthony','mark',
                     'steven','paul','andrew','joshua','kevin','brian','george','edward'],
    'UK':           ['oliver','harry','jack','george','noah','charlie','jacob','alfie','freddie',
                     'oscar','archie','henry','leo','arthur','louie','theo','ethan','tommy',
                     'william','lucas','mason','james','edward','sebastian','harrison'],
    'Japan':        ['haruto','yuto','sota','yuki','hayato','koki','riku','ren','kakeru','souta',
                     'aoi','hina','yua','koharu','sakura','rio','miyu','nana','mio','hinata',
                     'tatsuya','shota','daiki','ryota','kenji'],
    'Korea':        ['minjun','seogun','junho','jisoo','hyun','taehyung','jungkook','namjoon',
                     'yoongi','seokjin','hoseok','jimin','minho','chanwoo','donghyun',
                     'suji','yuna','chaeyeon','eunha','soyeon','dahyun','nayeon','jihyo'],
    'China':        ['wei','fang','yang','xin','jing','ming','lei','tao','hao','yu',
                     'jun','rui','chen','lin','qian','zhen','xiang','hua','long','feng',
                     'ling','ping','gang','bo','nan'],
    'India':        ['aarav','arjun','vivaan','aditya','vihaan','ananya','diya','ishaan',
                     'kavya','krishna','priya','rahul','riya','rohan','sai','sakshi',
                     'siddharth','tanvi','vedant','yash','aman','harsh','nikhil'],
    'Germany':      ['luca','finn','jonas','leon','paul','felix','elias','noah','ben','luis',
                     'mia','emma','hanna','lena','lea','anna','emilia','laura','julia','sarah',
                     'maximilian','alexander','michael','stefan','thomas'],
    'France':       ['gabriel','leo','raphael','louis','hugo','lucas','arthur','jules','adam',
                     'ethan','emma','jade','louise','alice','lena','manon','camille',
                     'clara','sarah','antoine','baptiste','clement','maxime','nicolas'],
}

TOPICS = {
    'Global (Tech)':  ['nova','bolt','flux','pulse','spark','core','edge','node','link','sync',
                       'cloud','data','grid','wave','loop','shift','peak','apex','zenith','nexus',
                       'hub','grow','scale','rise','smart','prime','elite','forge','craft','build'],
    'AI / ML':        ['neural','tensor','infer','vector','model','train','deploy','predict','classify',
                       'cluster','embed','token','prompt','llm','gpt','bert','diffuse','latent',
                       'epoch','gradient','dataset','pipeline','automl','genai','agentai'],
    'SaaS / Dev':     ['devops','gitops','cicd','deploy','stack','api','sdk','repo','docker','kube',
                       'serverless','lambda','micro','monolith','webhook','oauth','saas','paas',
                       'iaas','cron','queue','cache','proxy','gateway','cli'],
    'Fintech':        ['pay','wallet','bank','cash','fund','invest','trade','ledger','defi','crypto',
                       'token','coin','swap','yield','stake','vault','loan','credit','remit','fx',
                       'neobank','fintech','wealth','asset','portfolio'],
    'Health / Bio':   ['health','med','care','clinic','pharma','bio','gene','dna','rna','cell',
                       'therapy','tele','patient','doctor','nurse','lab','diag','scan','vital','pulse',
                       'monitor','fit','wellness','nutri','mental'],
    'E-commerce':     ['shop','store','mart','deal','buy','sell','cart','order','ship','track',
                       'return','review','price','brand','vendor','supplier','dropship','retail',
                       'wholesale','market','bazaar','auction','flash','promo','coupon'],
    'Game / Web3':    ['game','play','quest','arena','guild','clan','meta','verse','nft','dao',
                       'defi','chain','block','mint','stake','loot','drop','rank','badge','xp',
                       'pixel','voxel','world','realm','dungeon'],
    'Media / Content':['news','blog','post','media','press','cast','pod','stream','clip','reel',
                       'viral','trend','buzz','brand','story','feed','digest','weekly','daily','live',
                       'studio','creator','channel','publish','editorial'],
    'Education':      ['learn','edu','course','class','tutor','skill','quiz','grade','cert','degree',
                       'campus','study','exam','mentor','coach','academy','school','boot','camp',
                       'lecture','note','flash','card','mind','map'],
    'Travel / Local': ['trip','tour','travel','stay','hotel','book','fly','route','guide','map',
                       'local','spot','place','visit','explore','discover','venture','journey',
                       'nomad','remote','cabin','beach','mountain','city','escape'],
}

TLD_OPTIONS = [
    '.com', '.net', '.org', '.io', '.ai', '.co',
    '.us', '.co.uk', '.vn', '.de', '.fr', '.jp',
    '.com.au', '.ca', '.in', '.sg', '.id', '.com.br',
]

THREADS = 20
TIMEOUT = 15

# RDAP status values that mean "registered but about to drop — may be re-registerable soon"
_EXPIRING_STATUSES = {
    'pendingdelete', 'redemptionperiod', 'pendingretention',
    'autorenewperiod', 'transferperiod',
}

# ==================== LOGIC ====================
def check_domain(domain):
    domain = domain.strip().lower()
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('//')[1].split('/')[0]
    tld = domain.rsplit('.', 1)[-1] if '.' in domain else ''
    rdap_url = RDAP_ENDPOINTS.get(tld)
    result = {'domain': domain, 'status': 'UNKNOWN', 'year': 'N/A', 'error': ''}
    if not rdap_url:
        result['status'] = 'NO_RDAP'; result['error'] = f'TLD .{tld} not supported'
        return result
    try:
        r = requests.get(rdap_url + domain, timeout=TIMEOUT, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            data = r.json()
            creation_date = next(
                (e.get('eventDate') for e in data.get('events', []) if e.get('eventAction') == 'registration'),
                data.get('registrationDate') or data.get('createdDate')
            )
            result['year'] = creation_date[:4] if creation_date else 'N/A'
            # check if domain is in a dropping/expiring state
            rdap_statuses = {s.lower().replace(' ', '') for s in data.get('status', [])}
            if rdap_statuses & _EXPIRING_STATUSES:
                matched = rdap_statuses & _EXPIRING_STATUSES
                result['status'] = 'EXPIRING'
                result['error'] = ', '.join(matched)
            else:
                result['status'] = 'REGISTERED'
        elif r.status_code == 404:
            result['status'] = 'AVAILABLE'
        else:
            result['status'] = 'ERROR'; result['error'] = f'HTTP {r.status_code}'
    except requests.exceptions.Timeout:
        result['status'] = 'ERROR'; result['error'] = 'Timeout'
    except requests.exceptions.ConnectionError:
        result['status'] = 'ERROR'; result['error'] = 'Connection Error'
    except Exception as e:
        result['status'] = 'ERROR'; result['error'] = str(e)[:50]
    return result

# ==================== ROOT ====================
root = tk.Tk()
root.title("Domain Tool")
root.geometry("1380x760")
root.resizable(True, True)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use('clam')
style.configure("Treeview", background=ENTRY_BG, fieldbackground=ENTRY_BG,
                foreground=FG, rowheight=22, font=("Segoe UI", 9))
style.configure("Treeview.Heading", background=BG2, foreground=FG,
                font=("Segoe UI", 9, "bold"), relief="flat")
style.map("Treeview", background=[('selected', '#c8dff0')])
style.configure("blue.Horizontal.TProgressbar", troughcolor=BG2, background="#3a8fc9")
style.configure("TNotebook", background=BG)
style.configure("TNotebook.Tab", background=BG2, foreground=FG,
                font=("Segoe UI", 10, "bold"), padding=[14, 6])
style.map("TNotebook.Tab", background=[('selected', BG)], foreground=[('selected', '#1a5a8a')])

nb = ttk.Notebook(root)
nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

# ============================================================
# TAB 1 — CHECKER
# ============================================================
tab_check = tk.Frame(nb, bg=BG)
nb.add(tab_check, text="  Check Domain  ")

domain_vars = {}

# TLD filter
tld_frame = _lf(tab_check, "Lọc theo TLD — tick để chọn/bỏ chọn cả nhóm")
tld_frame.pack(fill=tk.X, padx=10, pady=(10, 2))

SUPPORTED_TLDS = list(RDAP_ENDPOINTS.keys())
tld_filter_vars = {}

def toggle_tld(tld):
    val = tld_filter_vars[tld].get()
    for d, var in domain_vars.items():
        if d.rsplit('.', 1)[-1] == tld:
            var.set(val); _refresh_row(d)

tld_btn_row = tk.Frame(tld_frame, bg=BG2)
tld_btn_row.pack(fill=tk.X)
for i, tld in enumerate(SUPPORTED_TLDS):
    var = tk.BooleanVar(value=True)
    tld_filter_vars[tld] = var
    _chk(tld_btn_row, f'.{tld}', var, cmd=lambda t=tld: toggle_tld(t)).grid(
        row=0, column=i, padx=4, pady=2, sticky='w')

# Controls
top = tk.Frame(tab_check, bg=BG, padx=10, pady=4)
top.pack(fill=tk.X)

def load_domains():
    try:
        with open(_DOMAINS_FILE, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    except FileNotFoundError:
        messagebox.showerror("Lỗi", "Không tìm thấy domains.txt"); return
    for row in tree.get_children():
        tree.delete(row)
    domain_vars.clear()
    for d in lines:
        var = tk.BooleanVar(value=True)
        domain_vars[d] = var
        tree.insert('', tk.END, iid=d, values=('☑ ' + d, '', '', ''))
    lbl_count.config(text=f"{len(lines)} domain")

def _refresh_row(d):
    checked = domain_vars[d].get()
    vals = list(tree.item(d, 'values'))
    name_part = vals[0][2:] if vals[0][:2] in ('☑ ', '☐ ') else vals[0]
    vals[0] = ('☑ ' if checked else '☐ ') + name_part
    tree.item(d, values=vals)

def select_all():
    for d, var in domain_vars.items(): var.set(True); _refresh_row(d)

def deselect_all():
    for d, var in domain_vars.items(): var.set(False); _refresh_row(d)

def toggle_row(event):
    item = tree.identify_row(event.y)
    if not item or item not in domain_vars: return
    domain_vars[item].set(not domain_vars[item].get())
    _refresh_row(item)

_btn(top, "Load domains.txt", load_domains, "#3a8fc9").pack(side=tk.LEFT, padx=(0,6))
_btn(top, "Chọn tất cả",     select_all,   "#5aabb0", small=True).pack(side=tk.LEFT, padx=(0,4))
_btn(top, "Bỏ chọn tất cả",  deselect_all, "#7a9fb5", small=True).pack(side=tk.LEFT, padx=(0,12))
tk.Label(top, text="Luồng:", font=("Segoe UI", 9), bg=BG, fg=FG).pack(side=tk.LEFT)
thread_var = tk.StringVar(value=str(THREADS))
tk.Entry(top, textvariable=thread_var, width=4, font=("Segoe UI", 9),
         bg=ENTRY_BG, fg=FG, relief=tk.FLAT,
         highlightthickness=1, highlightbackground=BORDER).pack(side=tk.LEFT, padx=(2,10))
lbl_count = tk.Label(top, text="", font=("Segoe UI", 9), bg=BG, fg=FG2)
lbl_count.pack(side=tk.LEFT)

# Body
body = tk.Frame(tab_check, bg=BG)
body.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

frame_tree = tk.Frame(body, bg=BG)
frame_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

cols = ('Domain', 'Status', 'Năm tạo', 'Lỗi')
tree = ttk.Treeview(frame_tree, columns=cols, show='headings', selectmode='none')
for c, w in zip(cols, [260, 110, 75, 200]):
    tree.heading(c, text=c); tree.column(c, width=w, anchor='w')

tree.tag_configure('AVAILABLE',  foreground='#1a7a40', background='#e8f8ee')
tree.tag_configure('REGISTERED', foreground='#8b1a1a', background='#fceaea')
tree.tag_configure('EXPIRING',   foreground='#7a5000', background='#fff5cc')
tree.tag_configure('ERROR',      foreground='#7a4500', background='#fef6e8')
tree.tag_configure('NO_RDAP',    foreground='#7a8f9a', background=ENTRY_BG)

vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
vsb.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(fill=tk.BOTH, expand=True)
tree.bind('<Button-1>', toggle_row)

# ---- Sort by column ----
_sort_state = {}  # col -> ascending bool

def _sort_col(col):
    asc = not _sort_state.get(col, False)
    _sort_state[col] = asc
    rows = [(tree.set(k, col), k) for k in tree.get_children('')]
    rows.sort(key=lambda x: x[0], reverse=not asc)
    for i, (_, k) in enumerate(rows):
        tree.move(k, '', i)
    # update heading arrow
    for c in ('Domain', 'Status', 'Năm tạo', 'Lỗi'):
        label = c + (' ▲' if c == col and asc else ' ▼' if c == col else '')
        tree.heading(c, text=label, command=lambda _c=c: _sort_col(_c))

for c in ('Domain', 'Status', 'Năm tạo', 'Lỗi'):
    tree.heading(c, text=c, command=lambda _c=c: _sort_col(_c))

# ---- Right-click context menu ----
_ctx_menu = tk.Menu(root, tearoff=0, bg=BG2, fg=FG, activebackground="#3a8fc9",
                    activeforeground=BTN_FG, font=("Segoe UI", 9))

def _ctx_copy_domain():
    item = tree.focus()
    if not item: return
    vals = tree.item(item, 'values')
    domain_raw = vals[0].lstrip('☑☐ ') if vals else item
    root.clipboard_clear(); root.clipboard_append(domain_raw)

def _ctx_copy_all_available():
    available = [tree.item(k,'values')[0].lstrip('☑☐ ')
                 for k in tree.get_children()
                 if tree.item(k,'values')[1] in ('AVAILABLE','EXPIRING')]
    root.clipboard_clear(); root.clipboard_append('\n'.join(available))

_ctx_menu.add_command(label="Copy domain này",           command=_ctx_copy_domain)
_ctx_menu.add_command(label="Copy tất cả Available",     command=_ctx_copy_all_available)
_ctx_menu.add_separator()
_ctx_menu.add_command(label="Sắp xếp theo Tên ▲",  command=lambda: _sort_col('Domain'))
_ctx_menu.add_command(label="Sắp xếp theo Năm ▲",  command=lambda: _sort_col('Năm tạo'))
_ctx_menu.add_command(label="Sắp xếp theo Status", command=lambda: _sort_col('Status'))

def _show_ctx(event):
    item = tree.identify_row(event.y)
    if item:
        tree.selection_set(item)
        tree.focus(item)
    _ctx_menu.tk_popup(event.x_root, event.y_root)

tree.bind('<Button-3>', _show_ctx)

# Right panel
frame_right = tk.Frame(body, width=290, bg=BGPANEL, relief=tk.GROOVE, bd=1)
frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
frame_right.pack_propagate(False)

tk.Label(frame_right, text="Kết quả realtime", font=("Segoe UI", 10, "bold"),
         bg=BGPANEL, fg=FG).pack(pady=(10, 4))

stat_frame = tk.Frame(frame_right, bg=BGPANEL)
stat_frame.pack(fill=tk.X, padx=10, pady=4)

lbl_avail = tk.Label(stat_frame, text="Available: 0",  font=("Segoe UI", 11, "bold"), fg="#1a7a40", bg=BGPANEL)
lbl_reg   = tk.Label(stat_frame, text="Registered: 0", font=("Segoe UI", 11, "bold"), fg="#8b1a1a", bg=BGPANEL)
lbl_err   = tk.Label(stat_frame, text="Error: 0",      font=("Segoe UI", 10),         fg="#7a4500", bg=BGPANEL)
lbl_done  = tk.Label(stat_frame, text="Done: 0 / 0",   font=("Segoe UI", 10),         fg=FG,        bg=BGPANEL)
lbl_speed = tk.Label(stat_frame, text="Speed: — /s",   font=("Segoe UI", 9),          fg=FG2,       bg=BGPANEL)
for w in (lbl_done, lbl_speed, lbl_avail, lbl_reg, lbl_err):
    w.pack(anchor='w', pady=1)

ttk.Separator(frame_right, orient='horizontal').pack(fill=tk.X, padx=8, pady=6)
tk.Label(frame_right, text="Available domains:", font=("Segoe UI", 9, "bold"),
         bg=BGPANEL, fg=FG).pack(anchor='w', padx=8)

avail_box = tk.Listbox(frame_right, font=("Consolas", 9), fg="#1a7a40",
                       bg=ENTRY_BG, selectbackground="#c8dff0",
                       selectmode=tk.SINGLE, activestyle='none', relief=tk.FLAT, bd=0, highlightthickness=0)
avail_sb = ttk.Scrollbar(frame_right, orient='vertical', command=avail_box.yview)
avail_box.configure(yscrollcommand=avail_sb.set)
avail_sb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,4))
avail_box.pack(fill=tk.BOTH, expand=True, padx=(8,0), pady=(2,8))

# Bottom
bot = tk.Frame(tab_check, bg=BG, padx=10, pady=6)
bot.pack(fill=tk.X)

progress_var = tk.DoubleVar()
ttk.Progressbar(bot, variable=progress_var, maximum=100,
                style="blue.Horizontal.TProgressbar").pack(fill=tk.X, pady=(0, 4))

lbl_status = tk.Label(bot, text="", font=("Segoe UI", 9), bg=BG, fg=FG2, anchor='w')
lbl_status.pack(fill=tk.X)

btn_row = tk.Frame(bot, bg=BG)
btn_row.pack(fill=tk.X, pady=(4, 0))

_stats = {'avail': 0, 'reg': 0, 'err': 0, 'done': 0, 'total': 0, 'start': 0.0}

def start_check():
    selected = [d for d, var in domain_vars.items() if var.get()]
    if not selected:
        messagebox.showwarning("Trống", "Chọn ít nhất 1 domain để check"); return
    btn_check.config(state=tk.DISABLED)
    btn_save_r.config(state=tk.DISABLED)
    progress_var.set(0)
    avail_box.delete(0, tk.END)
    _stats.update(avail=0, reg=0, err=0, done=0, total=len(selected), start=_time.time())
    _refresh_stats()
    n = int(thread_var.get()) if thread_var.get().isdigit() else THREADS
    threading.Thread(target=_run_check, args=(selected, n), daemon=True).start()

def _run_check(domains, n):
    results = []
    with ThreadPoolExecutor(max_workers=n) as ex:
        futures = {ex.submit(check_domain, d): d for d in domains}
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            root.after(0, _update_row, res)
    root.after(0, _on_done, results)

def _refresh_stats():
    elapsed = _time.time() - _stats['start'] if _stats['start'] else 0
    speed = _stats['done'] / elapsed if elapsed > 0 else 0
    lbl_avail.config(text=f"Available: {_stats['avail']}")
    lbl_reg.config(text=f"Registered: {_stats['reg']}")
    lbl_err.config(text=f"Error: {_stats['err']}")
    lbl_done.config(text=f"Done: {_stats['done']} / {_stats['total']}")
    lbl_speed.config(text=f"Speed: {speed:.1f} /s")

def _update_row(res):
    d = res['domain']; status = res['status']
    _stats['done'] += 1
    if status == 'AVAILABLE':   _stats['avail'] += 1; avail_box.insert(0, d)
    elif status == 'REGISTERED': _stats['reg'] += 1
    elif status == 'ERROR':      _stats['err'] += 1
    checked = domain_vars.get(d, tk.BooleanVar(value=True)).get()
    tree.item(d, values=(('☑ ' if checked else '☐ ') + d, status, res['year'], res['error']),
              tags=(status,))
    progress_var.set(_stats['done'] / _stats['total'] * 100)
    lbl_status.config(text=f"[{_stats['done']}/{_stats['total']}] {d} → {status}")
    _refresh_stats()

def _on_done(results):
    lbl_status.config(text=f"Xong!  Available: {_stats['avail']}   Registered: {_stats['reg']}   Error: {_stats['err']}")
    btn_check.config(state=tk.NORMAL); btn_save_r.config(state=tk.NORMAL)
    root.check_results = results

def save_results():
    results = getattr(root, 'check_results', [])
    if not results:
        messagebox.showwarning("Trống", "Chưa có kết quả"); return
    with open(_RESULT_FILE, "w", encoding="utf-8") as f:
        f.write("Domain\tStatus\tYear\tError\n" + "-" * 60 + "\n")
        for r in sorted(results, key=lambda x: (x['status'], x['domain'])):
            f.write(f"{r['domain']}\t{r['status']}\t{r['year']}\t{r['error']}\n")
    messagebox.showinfo("Đã lưu", f"Lưu vào {_RESULT_FILE} thành công")

btn_check  = _btn(btn_row, "Check Domain",   start_check,  "#3aab7a")
btn_check.pack(side=tk.LEFT, padx=(0, 6))
btn_save_r = _btn(btn_row, "Lưu result.txt", save_results, "#7a9fb5")
btn_save_r.pack(side=tk.LEFT)

# ============================================================
# TAB 2 — GENERATOR
# ============================================================
tab_gen = tk.Frame(nb, bg=BG)
nb.add(tab_gen, text="  Tạo Domain  ")

# --- helpers scoped to tab_gen ---
def _get_suffix_numbers():
    if not g_num_enable.get(): return ['']
    try:
        lo, hi = int(g_num_from.get()), int(g_num_to.get())
    except ValueError:
        return ['']
    if lo > hi: lo, hi = hi, lo
    full = list(range(lo, hi + 1))
    if len(full) > 500: full = random.sample(full, 500)
    return [str(n) for n in full]

def _get_names():
    raw = g_name_text.get("1.0", tk.END).strip()
    if raw:
        base = [w.strip().lower() for w in raw.replace(',', '\n').splitlines() if w.strip()]
    else:
        sel_c = [c for c, v in g_country_vars.items() if v.get()]
        sel_t = [t for t, v in g_topic_vars.items() if v.get()]

        if not sel_c and not sel_t:
            messagebox.showwarning("Thiếu", "Chọn ít nhất 1 quốc gia / chủ đề hoặc nhập tên")
            return []

        count = int(g_rand_count.get()) if g_rand_count.get().isdigit() else 30
        base = set()

        country_names = [n for c in sel_c for n in NAMES_BY_COUNTRY[c]]
        topic_words   = [n for t in sel_t for n in TOPICS[t]]

        if sel_c and sel_t:
            # kết hợp: tên quốc gia + từ chủ đề ghép liền
            pairs = [(cn, tw) for cn in country_names for tw in topic_words]
            sample = random.sample(pairs, min(count, len(pairs)))
            for cn, tw in sample:
                base.add(cn + tw)
        elif sel_c:
            base = set(random.sample(country_names, min(count, len(country_names))))
        else:
            base = set(random.sample(topic_words, min(count, len(topic_words))))

        base = list(base)

    suffixes = _get_suffix_numbers()
    return [f"{n}{s}" for n in base for s in suffixes]

def _get_tlds():
    raw = g_tld_entry.get().strip()
    if raw:
        return [(t if t.startswith('.') else '.'+t).lower() for t in raw.replace(',',' ').split() if t]
    return [t for t, v in g_tld_vars.items() if v.get()]

def on_generate():
    names = _get_names()
    if not names: return
    tlds = _get_tlds()
    if not tlds:
        messagebox.showwarning("Thiếu TLD", "Nhập TLD hoặc chọn ít nhất 1"); return
    domains = sorted({f"{n}{t}" for n in names for t in tlds})
    g_output.config(state=tk.NORMAL)
    g_output.delete("1.0", tk.END)
    g_output.insert(tk.END, "\n".join(domains))
    g_output.config(state=tk.DISABLED)
    g_count_lbl.config(text=f"Tổng: {len(domains)} domain")

def on_save_gen():
    content = g_output.get("1.0", tk.END).strip()
    if not content:
        messagebox.showwarning("Trống", "Chưa có domain để lưu"); return
    with open(_DOMAINS_FILE, "w", encoding="utf-8") as f:
        f.write(content + "\n")
    messagebox.showinfo("Đã lưu", f"Lưu vào {_DOMAINS_FILE} thành công")

def on_copy_gen():
    root.clipboard_clear()
    root.clipboard_append(g_output.get("1.0", tk.END).strip())

def on_save_and_switch():
    on_save_gen()
    nb.select(tab_check)

# --- NAME ---
fn = _lf(tab_gen, "Tên domain  (nhập tay mỗi dòng 1 tên, hoặc để trống → random theo quốc gia / chủ đề)")
fn.pack(fill=tk.X, padx=10, pady=(10, 4))

g_name_text = scrolledtext.ScrolledText(fn, height=3, font=("Segoe UI", 10),
                                         wrap=tk.WORD, bg=ENTRY_BG, fg=FG, relief=tk.FLAT,
                                         highlightthickness=1, highlightbackground=BORDER)
g_name_text.pack(fill=tk.X)

rrow = tk.Frame(fn, bg=BG2); rrow.pack(fill=tk.X, pady=(5,0))
_lbl(rrow, "Số tên random:").pack(side=tk.LEFT)
g_rand_count = tk.StringVar(value="30")
_entry(rrow, g_rand_count).pack(side=tk.LEFT, padx=4)

nrow = tk.Frame(fn, bg=BG2); nrow.pack(fill=tk.X, pady=(4,0))
g_num_enable = tk.BooleanVar(value=False)
_chk(nrow, "Thêm số sau tên  (vd: viet2347)", g_num_enable, bold=True).pack(side=tk.LEFT)
_lbl(nrow, "  Từ:").pack(side=tk.LEFT)
g_num_from = tk.StringVar(value="0")
_entry(nrow, g_num_from).pack(side=tk.LEFT, padx=2)
_lbl(nrow, "đến:").pack(side=tk.LEFT)
g_num_to = tk.StringVar(value="999")
_entry(nrow, g_num_to).pack(side=tk.LEFT, padx=2)
_lbl(nrow, "(tối đa 500 nếu range lớn)", small=True, fg=FG2).pack(side=tk.LEFT, padx=6)

# --- COUNTRY + TOPIC side by side ---
mid = tk.Frame(tab_gen, bg=BG)
mid.pack(fill=tk.X, padx=10, pady=4)

# Country (left)
fc = _lf(mid, "Quốc gia")
fc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,4))

g_country_vars = {}
g_all_country = tk.BooleanVar(value=False)
cbc = tk.Frame(fc, bg=BG2); cbc.pack(fill=tk.X)

def toggle_all_country():
    v = g_all_country.get()
    for var in g_country_vars.values(): var.set(v)

_chk(cbc, "Tất cả", g_all_country, bold=True, cmd=toggle_all_country).grid(row=0, column=0, sticky="w", padx=4)
CC = 3
for i, country in enumerate(NAMES_BY_COUNTRY.keys()):
    var = tk.BooleanVar(value=False)
    g_country_vars[country] = var
    _chk(cbc, country, var).grid(row=(i//CC)+1, column=i%CC, sticky="w", padx=4, pady=1)

# Topic (right)
ft = _lf(mid, "Chủ đề công nghệ  (có thể kết hợp nhiều chủ đề)")
ft.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4,0))

g_topic_vars = {}
g_all_topic = tk.BooleanVar(value=False)
cbt = tk.Frame(ft, bg=BG2); cbt.pack(fill=tk.X)

def toggle_all_topic():
    v = g_all_topic.get()
    for var in g_topic_vars.values(): var.set(v)

_chk(cbt, "Tất cả", g_all_topic, bold=True, cmd=toggle_all_topic).grid(row=0, column=0, sticky="w", padx=4)
TC = 3
for i, topic in enumerate(TOPICS.keys()):
    var = tk.BooleanVar(value=False)
    g_topic_vars[topic] = var
    _chk(cbt, topic, var).grid(row=(i//TC)+1, column=i%TC, sticky="w", padx=4, pady=1)

# --- TLD ---
ftld = _lf(tab_gen, "TLD / Đuôi domain")
ftld.pack(fill=tk.X, padx=10, pady=4)

trow = tk.Frame(ftld, bg=BG2); trow.pack(fill=tk.X, pady=(0,6))
_lbl(trow, "Nhập TLD (ưu tiên, vd: .com .net .vn):").pack(side=tk.LEFT)
g_tld_entry = tk.StringVar()
tk.Entry(trow, textvariable=g_tld_entry, width=36, font=("Segoe UI", 10),
         bg=ENTRY_BG, fg=FG, relief=tk.FLAT,
         highlightthickness=1, highlightbackground=BORDER).pack(side=tk.LEFT, padx=6)

cbf = tk.Frame(ftld, bg=BG2); cbf.pack(fill=tk.X)
g_tld_vars = {}
g_all_tld = tk.BooleanVar(value=False)

def toggle_all_tld():
    v = g_all_tld.get()
    for var in g_tld_vars.values(): var.set(v)

_chk(cbf, "Tất cả", g_all_tld, bold=True, cmd=toggle_all_tld).grid(row=0, column=0, sticky="w", padx=4)
TCOLS = 6
for i, tld in enumerate(TLD_OPTIONS):
    var = tk.BooleanVar(value=False)
    g_tld_vars[tld] = var
    _chk(cbf, tld, var).grid(row=(i//TCOLS)+1, column=i%TCOLS, sticky="w", padx=4, pady=1)

# --- Buttons ---
fbtn = tk.Frame(tab_gen, bg=BG, padx=10, pady=6)
fbtn.pack(fill=tk.X)

_btn(fbtn, "Tạo Domain",              on_generate,      "#3a8fc9").pack(side=tk.LEFT, padx=(0,6))
_btn(fbtn, "Lưu domains.txt",         on_save_gen,      "#3aab7a").pack(side=tk.LEFT, padx=(0,6))
_btn(fbtn, "Lưu & Chuyển sang Check", on_save_and_switch, "#5a7abf").pack(side=tk.LEFT, padx=(0,6))
_btn(fbtn, "Copy",                    on_copy_gen,      "#7a9fb5").pack(side=tk.LEFT)
g_count_lbl = tk.Label(fbtn, text="", font=("Segoe UI", 10), bg=BG, fg=FG2)
g_count_lbl.pack(side=tk.RIGHT)

# --- Output ---
tk.Label(tab_gen, text="Kết quả:", font=("Segoe UI", 10, "bold"),
         bg=BG, fg=FG, anchor="w", padx=10).pack(fill=tk.X)
g_output = scrolledtext.ScrolledText(tab_gen, font=("Consolas", 10), wrap=tk.NONE,
                                      state=tk.DISABLED, bg=ENTRY_BG, fg=FG, relief=tk.FLAT,
                                      highlightthickness=1, highlightbackground=BORDER)
g_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

if __name__ == "__main__":
    root.mainloop()
