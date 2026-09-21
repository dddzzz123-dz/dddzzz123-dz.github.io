"""Build a public, reproducible synthetic batch. No network or private inputs."""
from __future__ import annotations

import hashlib
import json
import random
from collections import deque
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
FAMILIES = {"single": "单钥匙", "parallel": "两把钥匙", "sequence": "顺序解锁"}
THEMES = ["blue", "green", "orange", "ink"]


def neighbors(pos, board):
    x, y = pos
    for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(board) and 0 <= nx < len(board[0]) and board[ny][nx] != "#":
            yield nx, ny


def route(board, start, end, blocked=frozenset()):
    queue, prev = deque([start]), {start: None}
    while queue:
        pos = queue.popleft()
        if pos == end:
            path = []
            while pos is not None:
                path.append(pos)
                pos = prev[pos]
            return path[::-1]
        for nxt in neighbors(pos, board):
            if nxt not in blocked and nxt not in prev:
                prev[nxt] = pos
                queue.append(nxt)
    return []


def component(board, start, blocked):
    seen, queue = {start}, deque([start])
    while queue:
        for nxt in neighbors(queue.popleft(), board):
            if nxt not in blocked and nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def solve(board):
    start = next((x, y) for y, row in enumerate(board) for x, c in enumerate(row) if c == "S")
    queue = deque([(*start, 0)])
    prev = {(*start, 0): None}
    while queue:
        state = queue.popleft()
        x, y, mask = state
        if board[y][x] == "E":
            states = []
            while state is not None:
                states.append(state)
                state = prev[state]
            return states[::-1]
        for nx, ny in neighbors((x, y), board):
            c = board[ny][nx]
            if c in "AB" and not (mask & (1 << (ord(c) - ord("A")))):
                continue
            new_mask = mask | (1 << (ord(c) - ord("a"))) if c in "ab" else mask
            nxt = (nx, ny, new_mask)
            if nxt not in prev:
                prev[nxt] = state
                queue.append(nxt)
    return []


def make_board(seed, family):
    rng = random.Random(seed)
    w, h = [(9, 9), (11, 9), (9, 11), (13, 9)][seed % 4]
    for attempt in range(300):
        grid = [["#"] * w for _ in range(h)]
        start, end = (1, 1), (w - 2, h - 2)
        grid[1][1] = "."
        stack = [start]
        while stack:
            x, y = stack[-1]
            options = [(x + dx, y + dy) for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2)]
                       if 0 < x + dx < w - 1 and 0 < y + dy < h - 1 and grid[y + dy][x + dx] == "#"]
            if not options:
                stack.pop()
                continue
            nx, ny = rng.choice(options)
            grid[(y + ny) // 2][(x + nx) // 2] = "."
            grid[ny][nx] = "."
            stack.append((nx, ny))
        main = route(grid, start, end)
        if len(main) < 15:
            continue
        door_indices = [len(main) // 2] if family == "single" else [len(main) // 3, 2 * len(main) // 3]
        doors = [main[i] for i in door_indices]
        keys = []
        used = {start, end, *doors}
        for i, door in enumerate(doors):
            region = component(grid, start, set(doors[i:]) if family == "sequence" else set(doors))
            if family == "sequence" and i == 1:
                region -= component(grid, start, {doors[0]})
            candidates = sorted(region - used)
            if not candidates:
                break
            # Prefer actual detours so examples are not merely relabeled paths.
            off_path = [p for p in candidates if p not in main]
            candidates = off_path or candidates
            key = max(candidates, key=lambda p: len(route(grid, main[max(0, door_indices[i] - 2)], p)))
            keys.append(key)
            used.add(key)
        if len(keys) != len(doors):
            continue
        for i, ((dx, dy), (kx, ky)) in enumerate(zip(doors, keys)):
            grid[dy][dx] = chr(ord("A") + i)
            grid[ky][kx] = chr(ord("a") + i)
        grid[start[1]][start[0]], grid[end[1]][end[0]] = "S", "E"
        board = ["".join(row) for row in grid]
        states = solve(board)
        if states:
            return board, states
    raise RuntimeError(f"Could not construct {family} with seed {seed}")


def make_steps(board, states):
    steps = [{
        "id": "step-1", "title": "先看清局面",
        "explanation": "从「起」走到「终」。深色格不能通行；字母门需要对应钥匙。先找到门和钥匙的位置，再安排路线。",
        "visual": {"type": "grid_path", "frame": 0, "previous_frame": 0, "focus": "overview"},
    }]
    previous = 0
    visited_doors = set()
    for i, (x, y, mask) in enumerate(states[1:], 1):
        c = board[y][x]
        title = body = None
        if c in "ab" and states[i - 1][2] != mask:
            key = c.upper()
            title = f"先取得钥匙 {key}"
            body = f"沿本步加深的路线移动 {i - previous} 格，到达钥匙 {key}。拿到它之后，才具备通过门 {key} 的条件；此前不能把这扇门当作通路。"
        elif c in "AB" and c not in visited_doors:
            visited_doors.add(c)
            title = f"通过门 {c}"
            body = f"已持有钥匙 {c}，再移动 {i - previous} 格到达门 {c}。这一刻通行条件满足，可以继续探索门后的区域。"
        elif c == "E":
            title = "沿通路到达出口"
            body = f"从上一位置再移动 {i - previous} 格即可到达「终」。全过程共移动 {i} 格，每次过门前都已经取得对应钥匙。"
        if title:
            steps.append({
                "id": f"step-{len(steps) + 1}", "title": title, "explanation": body,
                "visual": {"type": "grid_path", "frame": i, "previous_frame": previous, "focus": c},
            })
            previous = i
    return steps


def validate(sample):
    board, states = sample["board"], sample["solution"]
    assert len({len(row) for row in board}) == 1
    assert states and board[states[0][1]][states[0][0]] == "S"
    assert states[0][2] == 0
    for old, new in zip(states, states[1:]):
        x, y, mask = new
        assert abs(x - old[0]) + abs(y - old[1]) == 1
        c = board[y][x]
        assert c != "#"
        if c in "AB":
            assert old[2] & (1 << (ord(c) - ord("A")))
        expected = old[2] | (1 << (ord(c) - ord("a"))) if c in "ab" else old[2]
        assert mask == expected
    assert board[states[-1][1]][states[-1][0]] == "E"
    assert len(states) == len(solve(board)), "Route is not shortest"
    assert sample["moves"] == len(states) - 1
    assert len(sample["steps"]) == 2 * sample["keys"] + 2
    assert sample["steps"][-1]["visual"]["frame"] == len(states) - 1
    assert [s["visual"]["frame"] for s in sample["steps"]] == sorted(s["visual"]["frame"] for s in sample["steps"])
    assert len({s["id"] for s in sample["steps"]}) == len(sample["steps"])
    return True


def grid_svg(sample, frame=0, previous=0):
    board, states = sample["board"], sample["solution"]
    cell, pad = 32, 12
    w, h = len(board[0]) * cell + 2 * pad, len(board) * cell + 2 * pad
    title = f'{sample["id"]}：第 {frame} 步的局面'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">',
             f'<rect width="{w}" height="{h}" rx="8" fill="#f2f4f8"/>']
    for y, row in enumerate(board):
        for x, c in enumerate(row):
            fill = "#c5ccd9" if c == "#" else "#ffffff"
            parts.append(f'<rect x="{pad + x * cell + 1}" y="{pad + y * cell + 1}" width="30" height="30" rx="3" fill="{fill}"/>')
    def poly(points, color, width, opacity):
        coords = " ".join(f"{pad + x * cell + 16},{pad + y * cell + 16}" for x, y, _ in points)
        return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"/>'
    if frame > 0:
        parts.append(poly(states[:frame + 1], "#284ed8", 6, .23))
        parts.append(poly(states[previous:frame + 1], "#284ed8", 5, .95))
    for y, row in enumerate(board):
        for x, c in enumerate(row):
            cx, cy = pad + x * cell + 16, pad + y * cell + 16
            if c in "ab":
                acquired = states[frame][2] & (1 << (ord(c) - ord("a")))
                parts.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="{"#e4ad38" if c == "a" else "#9b73cc"}" stroke="#fff" stroke-width="2"/>')
                text = c.upper() + ("✓" if acquired else "")
                parts.append(f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-family="sans-serif" font-weight="700" font-size="11" fill="#252a36">{text}</text>')
            elif c in "AB":
                parts.append(f'<rect x="{cx - 12}" y="{cy - 12}" width="24" height="24" rx="3" fill="{"#f8e8ba" if c == "A" else "#ece1fa"}" stroke="{"#a06b00" if c == "A" else "#8051b7"}" stroke-width="2"/>')
                parts.append(f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="700">{c}</text>')
            elif c in "SE":
                parts.append(f'<rect x="{cx - 12}" y="{cy - 12}" width="24" height="24" rx="6" fill="{"#284ed8" if c == "S" else "#176654"}"/>')
                parts.append(f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-family="Microsoft YaHei,sans-serif" font-size="12" fill="white">{"起" if c == "S" else "终"}</text>')
    if frame > 0:
        x, y, _ = states[frame]
        parts.append(f'<circle cx="{pad + x * cell + 16}" cy="{pad + y * cell + 16}" r="14" fill="none" stroke="#e96040" stroke-width="3"/>')
    parts.append("</svg>")
    return "".join(parts)


def render_html(sample, baseline=False):
    rows = []
    for i, step in enumerate(sample["steps"]):
        v = step["visual"]
        rows.append(f'<section class="reason-step" data-step="{i}"><div class="step-heading"><span>{i + 1:02}</span><h2>{escape(step["title"])}</h2></div><figure>{grid_svg(sample, v["frame"], v["previous_frame"])}<figcaption>图 {i + 1} · {"观察局面" if i == 0 else "加深线条为本步路线，橙色圈为当前位置"}</figcaption></figure><p>{escape(step["explanation"])}</p></section>')
    css_path = "../../assets/export.css"
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(sample["title"])} · 合成图文样本</title><link rel="stylesheet" href="{css_path}"></head><body class="export-body"><article class="paper theme-{sample["theme"]} {"baseline" if baseline else "adaptive"}" data-sample="{sample["id"]}">
<header class="paper-head"><div class="paper-meta"><span>图文推演 / SYNTHETIC EXAMPLE</span><span>{sample["id"]}</span></div><h1>{escape(sample["title"])}</h1><p>{escape(sample["problem"])}</p><div class="legend">圆形 A / B：钥匙　方形 A / B：门　深色格：障碍</div></header>
<main class="reasoning">{''.join(rows)}</main><footer class="answer"><span>结论</span><p>{escape(sample["answer"])}</p></footer><div class="paper-footer">虚构关卡 · 合成数据 · 路线经规则程序校验<span>{sample["moves"]} 次移动 / {len(sample["steps"])} 个图文单元</span></div></article></body></html>'''


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    for name in ["data/samples", "samples/html", "samples/svg", "samples/jpg", "samples/thumbs", "comparison", "assets"]:
        (SITE / name).mkdir(parents=True, exist_ok=True)
    batch = []
    for group, family in enumerate(FAMILIES):
        for i in range(8):
            seed = 1101 + group * 100 + i
            board, states = make_board(seed, family)
            sample_id = f"EX-{group * 8 + i + 1:03}"
            themes = ["blue", "green", "orange", "ink"]
            title_prefix = {"single": "先拿钥匙，再找出口", "parallel": "两把钥匙，怎样安排", "sequence": "一扇门之后，还有一扇"}[family]
            sample = {
                "id": sample_id, "family": family, "family_label": FAMILIES[family],
                "title": f"{title_prefix} · {i + 1:02}", "seed": seed, "theme": themes[(group + i) % 4],
                "problem": "从「起」出发到达「终」，每次只能向上、下、左、右移动一格。取得字母钥匙后才能通过同名字母门，钥匙可重复使用。如何安排路线？",
                "board": board, "solution": states, "keys": 1 if family == "single" else 2,
                "moves": len(states) - 1, "steps": make_steps(board, states),
            }
            order = " → ".join(s["title"].replace("先取得", "取得") for s in sample["steps"][1:])
            sample["answer"] = f"{order}。共移动 {sample['moves']} 格；在本例规则下，这是最短可行路线之一。"
            sample["checks"] = {"structure": True, "legal_moves": True, "key_before_door": True, "shortest_route": True}
            validate(sample)
            dump(SITE / "data/samples" / f"{sample_id}.json", sample)
            (SITE / "samples/html" / f"{sample_id}.html").write_text(render_html(sample), encoding="utf-8")
            (SITE / "samples/svg" / f"{sample_id}.svg").write_text(grid_svg(sample, len(states) - 1), encoding="utf-8")
            for si, step in enumerate(sample["steps"], 1):
                v = step["visual"]
                (SITE / "samples/svg" / f"{sample_id}-step-{si}.svg").write_text(grid_svg(sample, v["frame"], v["previous_frame"]), encoding="utf-8")
            batch.append({k: sample[k] for k in ["id", "family", "family_label", "title", "theme", "moves", "keys", "checks"]} | {
                "units": len(sample["steps"]), "shape": [len(board[0]), len(board)],
                "json": f"data/samples/{sample_id}.json", "html": f"samples/html/{sample_id}.html",
                "jpg": f"samples/jpg/{sample_id}.jpg", "thumb": f"samples/thumbs/{sample_id}.webp",
            })
    comparison = json.loads((SITE / "data/samples/EX-017.json").read_text(encoding="utf-8"))
    # Same inputs, deliberately fixed six-column layout vs content-aware layout.
    (SITE / "samples/html/EX-017-baseline.html").write_text(render_html(comparison, True), encoding="utf-8")
    digest = hashlib.sha256("".join((SITE / s["json"]).read_text(encoding="utf-8") for s in batch).encode()).hexdigest()
    dump(SITE / "data/batch.json", {
        "id": "PUBLIC-DEMO-01", "count": len(batch), "families": FAMILIES, "samples": batch,
        "provenance": "本次公开演示由确定性规则程序生成局面、求解并组装文本，未调用在线模型批量推理。",
        "validation": {"checked": len(batch), "passed": len(batch), "scope": "结构、移动合法性、先取钥匙后过门、最短路线"},
        "content_sha256": digest,
    })
    # A direct-file fallback keeps the portable copy useful without a web server.
    sample_map = {s["id"]: json.loads((SITE / s["json"]).read_text(encoding="utf-8")) for s in batch}
    batch_data = json.loads((SITE / "data/batch.json").read_text(encoding="utf-8"))
    (SITE / "data/batch.js").write_text("window.DEMO_BATCH=" + json.dumps(batch_data, ensure_ascii=False) + ";\nwindow.DEMO_SAMPLES=" + json.dumps(sample_map, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"Built and verified {len(batch)} samples; content SHA256 {digest[:16]}")


if __name__ == "__main__":
    main()
