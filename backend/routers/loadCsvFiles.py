from fastapi import APIRouter
from pathlib import Path
from fastapi import HTTPException
import os
from process.LoadCsvToPi import LoadCsvToPi

router = APIRouter()

@router.get("/list-csv")
def list_csv_files():
    data_dir = Path(__file__).resolve().parent.parent / "SavedData"
    files = [f.name for f in data_dir.glob("*.csv")]
    return {"files": files}

@router.delete("/delete-csv/{filename}")
def delete_csv_file(filename: str):
    data_dir = Path(__file__).resolve().parent.parent / "SavedData"
    file_path = data_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.remove(file_path)
        return {"message": f"{filename} deleted successfully"}
    except Exception as e:
        print(f"exception occured:{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/load-file")
def load_file(filename: str):
    try:
        message = LoadCsvToPi(filename)
        return {
            "success": True,
            "message": message,
            "filename": filename
        }
    except FileNotFoundError as e:
        return {
            "success": False,
            "message": str(e),
            "filename": filename
        }
    except PermissionError as e:
        return {
            "success": False,
            "message": str(e),
            "filename": filename
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "filename": filename
        }
