cat > app.py << 'EOF'
from fastapi import FastAPI
from pydantic import BaseModel
import os
import tempfile
import shutil
import git
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RepoRequest(BaseModel):
    repo_url: str

def clone_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(repo_url, temp_dir)
    return temp_dir

def read_files(repo_path):
    code_data = ""
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith((".py", ".js", ".ts", ".md", ".json", ".yml")):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        code_data += f"\n\n# File: {file}\n"
                        code_data += f.read()[:2000]
                except:
                    pass
    return code_data[:12000]

def generate_readme(code):
    prompt = f"""
You are a senior DevOps engineer.

Analyze this repository code and generate a professional README.md with:
- Project Overview
- Tech Stack
- Features
- Setup Instructions
- API Details
- Folder Structure

Code:
{code}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

@app.post("/generate-readme")
def generate(repo: RepoRequest):
    path = clone_repo(repo.repo_url)
    try:
        code = read_files(path)
        readme = generate_readme(code)
        return {"readme": readme}
    finally:
        shutil.rmtree(path)
EOF