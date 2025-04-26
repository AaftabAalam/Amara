# from fastapi import File, HTTPException, Request, UploadFile, Form
# import os
# import json
from pathlib import Path

UPLOAD_DIR = "uploaded_files"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# # async def upload_json_file(
# #     file: UploadFile = File(...),
# #     reference_id: str = Form(...)
# # ):
# #     try:
# #         if not reference_id:
# #             return {"error": "Reference ID not found in the JSON data"}

# #         if file.content_type != "application/json":
# #             raise HTTPException(status_code=400, detail="Only JSON files are allowed.")

# #         file_path = os.path.join(UPLOAD_DIR, reference_id+".json")
# #         with open(file_path, "wb") as f:
# #             content = await file.read()
# #             f.write(content)

# #         return {    
# #             "message": "File uploaded successfully.",
# #             "path": file_path,
# #         }
# #     except Exception as e:
# #         return{
# #             "error":e.msg
# #         }

# async def upload_json_file(file: UploadFile = File(...), reference_id: str = Form(...)):  
#     try:
#         if not reference_id:
#             return {"error": "Reference ID not found in the JSON data"}

#         if file.content_type != "application/json":
#             raise HTTPException(status_code=400, detail="Only JSON files are allowed.")

#         file_path = os.path.join(UPLOAD_DIR, f"{reference_id}.json")

#         with open(file_path, "wb") as f:
#             content = await file.read()
#             f.write(content)

#         file_name = os.path.basename(file_path)
#         recent_file_name = file_name

#         return {    
#             "message": "File uploaded successfully.",
#             "path": file_path,
#         }
#     except HTTPException as e:
#         return{
#             "error":e.msg
#         }
#     except Exception as e:
#         return{
#             "error":e.msg
#         }


# async def upload_raw_json(request: Request):
#     try:
#         print("This is the:",request)
#         data = await request.json()
    
#         if "reference_id" not in data:
#             return {"error": "Reference ID not found in the JSON data"}

#         if "json_data" not in data:
#             return {"error": "Json_data key is not found in the request."}

#         reference_id = data["reference_id"]
#         json_data = data["json_data"]

#         file_name = f"{reference_id}.json"

#         file_path = os.path.join(UPLOAD_DIR, file_name)
#         with open(file_path, "w") as json_file:
#         #json.dump(data, json_file, indent=4)
#             json.dump(json_data, json_file, indent=4)

#         return {
#             "message": "File uploaded successfully.",
#             "path": file_path,
#         }
#     except Exception as e:
#         return{
#             "error":e
#         }