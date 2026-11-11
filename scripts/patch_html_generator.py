import sys
from pathlib import Path

target = Path(r"C:\Users\LENOVO\Desktop\int396 tb project\scripts\generate_aerotb_html.py")
text = target.read_text(encoding="utf-8")

# Update portal card clicks to call navigateTo
text = text.replace(
    'onclick="alert(\'Module 01: AI Cluster Lab - Open from the sidebar or navigate to State Pattern Groups.\')"',
    'onclick="navigateTo(\'clusters\')"'
)
text = text.replace(
    'onclick="alert(\'Module 02: Compare States - Open from the sidebar or navigate to Compare States.\')"',
    'onclick="navigateTo(\'compare\')"'
)
text = text.replace(
    'onclick="alert(\'Module 03: AI Data Explainer - Open from the sidebar or navigate to AI Explainer.\')"',
    'onclick="navigateTo(\'explainer\')"'
)

# Replace the scroll logic with bulletproof multi-environment scroll handler
old_script_scroll = """  const scrollSource = (window.parent && window.parent !== window) ? window.parent : window;
  scrollSource.addEventListener('scroll', () => {{
    if (!storyTrack) return;
    const rect = storyTrack.getBoundingClientRect();
    const vHeight = scrollSource.innerHeight || window.innerHeight;
    const trackHeight = storyTrack.offsetHeight - vHeight;
    if (trackHeight <= 0) return;
    const scrollY = -rect.top;
    const progress = Math.max(0, Math.min(1, scrollY / trackHeight));"""

new_script_scroll = """  function navigateTo(pageKey) {{
    try {{
      if (window.parent && window.parent !== window) {{
        window.parent.location.href = '/?page=' + pageKey;
      }} else {{
        window.location.href = 'http://localhost:8501/?page=' + pageKey;
      }}
    }} catch(e) {{
      window.location.href = 'http://localhost:8501/?page=' + pageKey;
    }}
  }}

  const handleScroll = () => {{
    if (!storyTrack) return;
    const rect = storyTrack.getBoundingClientRect();
    let iframeTop = 0;
    try {{
      if (window.frameElement) iframeTop = window.frameElement.getBoundingClientRect().top;
    }} catch(e) {{}}
    const vHeight = (window.parent && window.parent.innerHeight) ? window.parent.innerHeight : window.innerHeight;
    const trueTop = rect.top + iframeTop;
    const trackHeight = storyTrack.offsetHeight - vHeight;
    if (trackHeight <= 0) return;
    const progress = Math.max(0, Math.min(1, -trueTop / trackHeight));"""

if old_script_scroll in text:
    text = text.replace(old_script_scroll, new_script_scroll)
    print("Replaced scroll start")

old_bind = """    }
  });
</script>"""

new_bind = """    }
  };

  try {{
    if (window.parent && window.parent !== window) {{
      const pMain = window.parent.document.querySelector('section.main') || window.parent.document.querySelector('.main');
      if (pMain) pMain.addEventListener('scroll', handleScroll);
      window.parent.addEventListener('scroll', handleScroll);
    }}
  }} catch(e) {{}}
  window.addEventListener('scroll', handleScroll);
</script>"""

if old_bind in text:
    text = text.replace(old_bind, new_bind)
    print("Replaced scroll bind")

target.write_text(text, encoding="utf-8")
print("Finished patching generator!")
