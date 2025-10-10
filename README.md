# POC_MINIRAG
video from experience of application 
https://drive.google.com/file/d/1xXSD1sZYEyaz_tDUclYaLZyNWoYtWrTO/view?usp=sharing

## Overview
This project is a FastAPI-based MVP for document upload, processing, and retrieval using vector databases (FAISS) and MongoDB.  
It is structured for easy deployment and extension.

---

## Features
- Upload and process files (PDF, images, text, Word, etc.)
- Store file metadata and chunks in MongoDB
- Vector search using FAISS
- Modular codebase (controllers, routes, models, helpers)
- Docker-ready for local or cloud deployment

---

## Requirements

- Python 3.8 or later (recommended: use [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main))
- Docker & Docker Compose (for containerized deployment)
- MongoDB (local or via Docker)

---

## Setup (Local Development)

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd poc/src
```

### 2. Create and activate a virtual environment (recommended: conda)
```bash
conda create -n mini_rag00 python=3.8
conda activate mini_rag00
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
- Copy `.env.example` to `.env` and update values as needed.
- **Important:** Remove any invalid lines (like `/localhost`) from `.env`.

### 5. Run MongoDB (if not using Docker)
```bash
docker run -d -p 27007:27017 --name poc_mongo mongo:6.0
```

### 6. Run the FastAPI app
```bash
uvicorn main:app --reload
```
The API will be available at [http://localhost:8000](http://localhost:8000).

---

## Setup (Docker)

### 1. Build and run with Docker Compose
```bash
docker-compose up --build
```
- The API will be available at [http://localhost:8000](http://localhost:8000).
- MongoDB will run on port `27007`.

---

## Project Structure

```
src/
  assets/           # Uploaded files and assets
  chunked_results/  # Chunked file results
  controllers/      # Business logic
  helpers/          # Config and utility functions
  models/           # Pydantic models and DB schemas
  routes/           # API endpoints and schemas
  routesindex/      # FAISS index files
  main.py           # FastAPI app entrypoint
  requirements.txt  # Python dependencies
  .env              # Environment variables
```

---

## Environment Variables

See `.env.example` for all available variables.  
**Example:**
```
APP_NAME=MyPOCApp
APP_VERSION=1.0.0
FILE_ALLOWED_TYPES=["image/jpeg","image/png","application/pdf","text/plain","application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
FILE_MAX_SIZE=10485760
FILE_SIZE_CHUNK=1024
DEEPSEEK_API_KEY=your_deepseek_api_key
QWEN_API_KEY=your_qwen_api_key
MONGODB_URI=mongodb://localhost:27007
MONGODB_NAME=poc
```

---

## Usage

- Access the interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs)
- Use `/api/v1/upload/data/{file_id}` to upload files
- Use `/api/v1/upload/process/{project_id}` to process files

---

## Notes

- Make sure MongoDB is running and accessible at the URI specified in `.env`.
- Uploaded files are stored in `assets/Files/` by default.
- For production, update all secrets and sensitive values in `.env`.

---

## License

This project is for internal MVP/demo purposes.

---

## Contact

For questions or support, contact the project maintainer.