from pathlib import Path
p=Path(".impeccable/review/judge/write-review.py")
s=p.read_text().replace("fb["+chr(92)+chr(34)+"passed"+chr(92)+chr(34)+"]","fb["+chr(34)+"passed"+chr(34)+"]").replace("fb["+chr(92)+chr(34)+"total"+chr(92)+chr(34)+"]","fb["+chr(34)+"total"+chr(34)+"]")
p.write_text(s)
