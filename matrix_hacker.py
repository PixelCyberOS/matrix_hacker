# matrix_curses.py
# Çince kelimeler daha uzun ve kırmızı

import curses
import random
import time
import locale
import sys

locale.setlocale(locale.LC_ALL, '')

FRAME_SLEEP = 0.06
TRAIL_LENGTH = 6
CHINESE_PROB = 0.03   # Çince çıkma olasılığı arttırıldı
ENGLISH_PROB = 0.03
DENSITY = 0.9

# Uzun Çince kelimeler
CHINESE_WORDS = [
    "系统入侵检测", "未授权访问尝试", "数据加密失败", "警报:非法操作",
    "黑客攻击已启动", "网络防火墙绕过", "访问密钥丢失", "远程控制激活"
]
ENGLISH_WORDS = ["ACCESS", "DENIED", "PASSWORD", "AUTH", "ERROR", "ROOT", "CONNECT", "OK"]
BINARY = ['0','1']

def safe_addstr(win, y, x, s, attr=0):
    try:
        win.addstr(y, x, s, attr)
    except curses.error:
        pass

def init_colors():
    if not curses.has_colors():
        return False
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)  # parlak yeşil
    curses.init_pair(2, curses.COLOR_GREEN, -1)  # trail yeşil
    curses.init_pair(3, curses.COLOR_RED, -1)    # kırmızı Çince
    curses.init_pair(4, curses.COLOR_BLUE, -1)   # mavi İngilizce
    return True

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    has_colors = init_colors()

    rows, cols = stdscr.getmaxyx()
    rows = max(3, rows - 1)
    cols = max(10, cols)

    drops = []
    reset_offsets = []
    for c in range(cols):
        if random.random() < DENSITY:
            drops.append(random.randint(0, rows))
        else:
            drops.append(-random.randint(1, rows))
        reset_offsets.append(random.randint(2, 20))

    try:
        while True:
            new_rows, new_cols = stdscr.getmaxyx()
            new_rows = max(3, new_rows - 1)
            new_cols = max(10, new_cols)
            if new_rows != rows or new_cols != cols:
                rows, cols = new_rows, new_cols
                drops = drops[:cols] + [-random.randint(1, rows) for _ in range(max(0, cols - len(drops)))]
                reset_offsets = reset_offsets[:cols] + [random.randint(2, 20) for _ in range(max(0, cols - len(reset_offsets)))]
                stdscr.erase()

            stdscr.erase()

            for r in range(rows):
                for c in range(cols):
                    drop_y = drops[c]
                    if drop_y < 0 or drop_y - TRAIL_LENGTH > r or drop_y < r:
                        continue
                    distance = drop_y - r
                    if distance == 0:
                        roll = random.random()
                        if roll < CHINESE_PROB:
                            word = random.choice(CHINESE_WORDS)
                            word = word[:max(1, cols - c)]  # taşmayı önle
                            if has_colors:
                                safe_addstr(stdscr, r, c, word, curses.color_pair(3) | curses.A_BOLD)
                            else:
                                safe_addstr(stdscr, r, c, word)
                        elif roll < CHINESE_PROB + ENGLISH_PROB:
                            word = random.choice(ENGLISH_WORDS)
                            word = word[:max(1, cols - c)]
                            if has_colors:
                                safe_addstr(stdscr, r, c, word, curses.color_pair(4) | curses.A_BOLD)
                            else:
                                safe_addstr(stdscr, r, c, word)
                        else:
                            ch = random.choice(BINARY)
                            if has_colors:
                                safe_addstr(stdscr, r, c, ch, curses.color_pair(1) | curses.A_BOLD)
                            else:
                                safe_addstr(stdscr, r, c, ch)
                    else:
                        ch = random.choice(BINARY)
                        if has_colors:
                            safe_addstr(stdscr, r, c, ch, curses.color_pair(2))
                        else:
                            safe_addstr(stdscr, r, c, ch)

            stdscr.refresh()

            for i in range(cols):
                if drops[i] < 0:
                    if random.random() < 0.02:
                        drops[i] = 0
                else:
                    drops[i] += 1
                    if drops[i] - rows > 0 or random.random() < (1.0 / reset_offsets[i]):
                        drops[i] = -random.randint(1, max(1, rows // 2))
                        reset_offsets[i] = random.randint(2, 20)

            try:
                ch = stdscr.getch()
                if ch in (ord('q'), ord('Q')):
                    break
            except Exception:
                pass

            time.sleep(FRAME_SLEEP)

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print("Hata:", e)
        if sys.platform.startswith("win"):
            print("Windows kullanıyorsanız 'pip install windows-curses' yüklemeyi deneyin.")
