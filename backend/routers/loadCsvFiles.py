from fastapi import APIRouter
from pathlib import Path

router = APIRouter()

@router.get("/list-csv")
def list_csv_files():
    print("called loadcsvfiles.py")
    data_dir = Path(__file__).resolve().parent.parent / "SavedData"
    files = [f.name for f in data_dir.glob("*.csv")]
    print(files)
    return {"files": files}
