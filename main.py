"""Binomind MVP: Binary Analysis & Pseudocode Generator.

Simulates the workflow of extracting assembly, chunking it,
and generating pseudocode using a mock LLM engine.
"""
import re
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Binomind MVP")

# --- Data Models ---
class AnalysisRequest(BaseModel):
    binary_path: str
    target_functions: List[str] = []
    context_size: int = 4096

class AnalysisResult(BaseModel):
    file_name: str
    chunks_processed: int
    functions_found: List[str]
    pseudocode: str
    summary: str

class HealthCheck(BaseModel):
    status: str
    version: str = "0.1.0"

# --- Components ---

class BinaryDisassembler:
    """Simulates extracting assembly from a binary file."""
    def extract(self, path: str) -> str:
        if not path.endswith(".bin") and not path.endswith(".elf"):
            raise ValueError("Unsupported binary format")
        # Mock assembly output
        return f"; Disassembly of {path}\nmov eax, 0x1\nint 0x80\nret\n"

class ContextManager:
    """Splits assembly into chunks for LLM processing."""
    def chunk(self, assembly: str, max_size: int) -> List[str]:
        lines = assembly.strip().split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        for line in lines:
            if current_size + len(line) > max_size:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(line)
            current_size += len(line)
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        return chunks

class LocalLLMEngine:
    """Simulates LLM inference for pseudocode generation."""
    def analyze(self, chunks: List[str]) -> str:
        # Simple heuristic to generate "pseudocode"
        result = "// Generated Pseudocode:\n"
        for i, chunk in enumerate(chunks):
            result += f"// --- Chunk {i+1} ---\n"
            if 'mov' in chunk:
                result += "  load_register(EAX, 1)\n"
            if 'int' in chunk:
                result += "  trigger_system_call()\n"
            if 'ret' in chunk:
                result += "  return\n"
        return result

class OutputFormatter:
    """Formats the final analysis result."""
    def format(self, file_name: str, chunks: List[str], pseudocode: str) -> Dict[str, Any]:
        return {
            "file_name": file_name,
            "chunks_processed": len(chunks),
            "functions_found": ["main", "entry_point"],
            "pseudocode": pseudocode,
            "summary": f"Processed {len(chunks)} chunks from {file_name}."
        }

# --- Service Layer ---

class AnalysisService:
    def __init__(self):
        self.disassembler = BinaryDisassembler()
        self.context_manager = ContextManager()
        self.llm_engine = LocalLLMEngine()
        self.formatter = OutputFormatter()

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        try:
            assembly = self.disassembler.extract(request.binary_path)
            chunks = self.context_manager.chunk(assembly, request.context_size)
            pseudocode = self.llm_engine.analyze(chunks)
            data = self.formatter.format(request.binary_path, chunks, pseudocode)
            return AnalysisResult(**data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

service = AnalysisService()

# --- Routes ---

@app.get("/health", response_model=HealthCheck)
def health():
    return HealthCheck(status="ok")

@app.post("/analyze", response_model=AnalysisResult)
def analyze(request: AnalysisRequest):
    return service.analyze(request)

def demo():
    """Run a local demo without server."""
    req = AnalysisRequest(binary_path="test.bin")
    res = service.analyze(req)
    print(f"Status: {res.summary}")
    print(f"Pseudocode:\n{res.pseudocode}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)