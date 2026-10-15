from pathlib import Path
p=Path(".impeccable/review/judge/browser-probes.py")
s=p.read_text()
s=s.replace("  p.go_back(wait_until=\"load\");p.wait_for_timeout(1000)","  try: p.go_back(wait_until=\"commit\",timeout=5000)\n  except Exception as e: report[\"back_navigation_tool_note\"]=str(e)\n  p.wait_for_timeout(1000)")
p.write_text(s)
