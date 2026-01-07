from pathlib import Path

Path("notes.txt").write_text("Hello world !\n", encoding="utf-8")
print(Path("notes.txt").read_text(encoding="utf-8"))

from pathlib import Path

raw = Path("raw_logs")
raw.mkdir(exist_ok=True)
errors_out = Path("errors.log")

with errors_out.open("w", encoding="utf-8") as out:
    for log in raw.glob("*.log"):
        for line in log.read_text(encoding="utf-8").splitlines():
            if "ERROR" in line:
                out.write(f"{log.name}: {line}\n")
