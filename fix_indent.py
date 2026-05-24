import sys

def fix_indent():
    with open("c:\\GanoiTouch\\telegram_manager.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # 0-indexed: lines 840 to 895 are lines 841 to 896
    for i in range(840, 896):
        if len(lines[i]) > 4 and lines[i].startswith("    "):
            lines[i] = lines[i][4:]
            
    with open("c:\\GanoiTouch\\telegram_manager.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
        
if __name__ == "__main__":
    fix_indent()
