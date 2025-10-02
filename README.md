### Overview
- A search API over ~280k medicine records.  
- Built with **FastAPI + PostgreSQL**.  
- Supports 4 types of queries:
  1. **Prefix search** – autocomplete style.
  2. **Substring search** – find anywhere in the text.
  3. **Full-text search** – semantic search over medicine names, descriptions, etc.
  4. **Fuzzy search** – typo-tolerant queries.  
- Optimized for **speed and accuracy** using indexes and extensions.

## Prerequisites
Make sure these are installed:
1. **Python 3.10+**
2. **PostgreSQL (v14 or later)**
3. **VS Code or any IDE**

## Setup Instructions  
  
### Step 1. Install Dependencies  
install in python venv in your ide  
pip install -r requirements.txt  
(or manually: pip install fastapi uvicorn psycopg2-binary)  
  
### Step 2: Setup PostgreSQL Database  
Open psql (PostgreSQL shell).    
Server [localhost]:Press Enter  
Database [your_username]: postgres    
Port [5432]:Press Enter  
Username [your_windows_user]: postgres  
Password: what you have set during installation  
  
Run this in your terminal:  
psql -U postgres  
  
Inside psql, create the database:  
CREATE DATABASE pharmacy;  
\c pharmacy  
  
Load the schema (tables + indexes):  
\i 'path/to/your/schema.sql'  
  
At this point, your database is ready but empty.  
  
### Step 3: Import the Dataset
Back in VS Code terminal,  
First, set your database connection string:  
For Windows:  
$env:DB_DSN = "dbname=pharmacy user=postgres password=yourpassword host=localhost port=5432"  
For Mac:  
export DB_DSN="dbname=pharmacy user=postgres password=yourpassword host=localhost port=5432"  
  
Then run:  
python import_data.py  
  
This will read JSON files from the data/ folder.  
Inserts 280,277 medicine records into PostgreSQL.  
When done, you’ll see messages like:  
Inserted 37589 from a.json (total=37589)....z.json  
Done Import.  

Now your DB has all medicines loaded.

### Step 4: Run the API Server
Start the FastAPI server (in VS Code terminal):  
uvicorn app.main:app --reload  

If successful, you’ll see:
Uvicorn running on http://127.0.0.1:8000

### Step 5: Open Swagger UI
1.Open your browser.  
2.Go to: http://127.0.0.1:8000/docs  
3.You’ll see an interface with:  
  /search/prefix  
  /search/substring  
  /search/fulltext  
  /search/fuzzy  

Example Searches
In Swagger UI, try:  
1.Prefix search → type Para → returns Paracetamol.  
2.Substring search → type Injection → returns all injections.  
3.Full-text search → type antibiotic → returns antibiotic medicines.  
4.Fuzzy search → type Avastn → still returns Avastin.  

### How It Works (Performance Notes)
1.Prefix Search → B-tree index, fast ILIKE 'Para%'.  
2.Substring Search → pg_trgm trigram index, efficient for ILIKE '%Injection%'.  
3.Full-text Search → to_tsvector + GIN index, ignores accents, allows natural queries.  
4.Fuzzy Search → trigram similarity, tolerates typos.  
5.VACUUM ANALYZE keeps indexes updated for performance.  



