"""Keep decorative Unicode glyphs out of the static interface."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CLOSE = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.25" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>'
PLUS = '<svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.25" aria-hidden="true"><path d="M10 3v14M3 10h14"/></svg>'

def refine():
    for page in (ROOT / 'dist').rglob('*.html'):
        text = page.read_text(encoding='utf-8')
        text = re.sub(r'<span aria-hidden="true">\s*[↗↓←→]\s*</span>', '', text)
        text = re.sub(r'<span class="arrow"[^>]*>.*?</span>', '', text)
        text = re.sub(r'<span class="service-no">.*?</span>', '', text)
        text = text.replace('<span class="plus" aria-hidden="true">+</span>', '<span class="plus" aria-hidden="true">'+PLUS+'</span>')
        text = re.sub(r'(<button[^>]*class="close"[^>]*>)×(</button>)', lambda m:m[1]+CLOSE+m[2], text)
        for char in ('↗','↓','←','→','★','✓','✦'):
            text = text.replace(char, '')
        text = re.sub(r'<span>0[123] / (Understand|Clarify|Preserve)</span>', r'<span>\1</span>', text)
        if page == ROOT / 'dist/index.html':
            text = re.sub(r'\s*<div class="makes-head">.*?</div>', '', text)
            text = text.replace('aria-labelledby="makes-title"', 'aria-label="Vehicle makes"')
            directory_links = re.findall(r'<div class="service-directory-link porcelain">.*?</div>', text, flags=re.S)
            if len(directory_links) > 1:
                first = True
                def keep_first(match):
                    nonlocal first
                    if first:
                        first = False
                        return match[0]
                    return ''
                text = re.sub(r'<div class="service-directory-link porcelain">.*?</div>', keep_first, text, flags=re.S)
        text = text.replace('/style.css?v=3', '/style.css?v=4').replace('/app.js?v=3','/app.js?v=4').replace('/config.js?v=3','/config.js?v=4')
        page.write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n',encoding='utf-8')
    from polish_booking import polish
    polish()

if __name__ == '__main__':
    refine()
