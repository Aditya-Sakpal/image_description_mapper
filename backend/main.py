from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import traceback
import os 
from prompts import TEXT_EXTRACTION_PROMPT , DESCRIPTION_MAPPING_PROMPT
from rag_pipeline import VectorSearch
from dotenv import load_dotenv
from schemas import ExpectedOutput, ImageUrlRequest , TextExtractionOutput

vector_search = VectorSearch()
load_dotenv()


model = ChatOpenAI(
    model="gpt-4.1", 
    api_key=os.getenv("OPENAI_API_KEY"), 
    temperature=0, 
)

prompt = ""

with open("prompt.txt", "r") as file:
    prompt = file.read()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

descriptions = []

@app.post("/upload-descriptions")
async def upload_descriptions(file: UploadFile = File(...)):
    """
    Upload a text file containing descriptions (one per line)
    and store them in the global descriptions list.
    """
    # Check if the file is a text file
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")
    
    try:
        # Read the file content
        contents = await file.read()
        
        # Decode the content to string
        content_str = contents.decode('utf-8')
        
        # Split by lines and filter out empty lines
        lines = [line.strip() for line in content_str.splitlines() if line.strip()]
        
        # Add each line to the global descriptions list
        descriptions.extend(lines)
        
        return JSONResponse(
            content={
                "message": f"Successfully uploaded {len(lines)} descriptions",
                "total_descriptions": len(descriptions),
                "uploaded_descriptions": lines
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
@app.post("/map-description")
async def map_description(request: ImageUrlRequest):
    try:
        content = [
            {
                "type": "text",
                "text": prompt.format(descriptions="\n".join(descriptions))
            },
            {
                "type": "image",
                "source_type": "url",
                "url": request.image_url,
            },            
        ]
        message = HumanMessage(content=content)
        response = model.with_structured_output(ExpectedOutput)
        response = response.invoke([message])
        response = response.dict()
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mapping description: {str(e)}")
    

@app.post("/map-description-v2")
async def map_description(request: ImageUrlRequest):
    try:
        content = [
            {
                "type": "text",
                "text": TEXT_EXTRACTION_PROMPT
            },
            {
                "type": "image",
                "source_type": "url",
                "url": request.image_url,
            },            
        ]
        message = HumanMessage(content=content)
        response = model.with_structured_output(TextExtractionOutput)
        response = response.invoke([message])
        response = response.dict()
        extracted_text = response['text']

        if extracted_text:
            chunks = vector_search.search_similar_chunks(
                query_text=extracted_text
            )
            
            chunks_data = ""

            for chunk in chunks :
                chunks_data = chunk['text'] + '\n'

            content = [
                {
                    "type": "text",
                    "text": DESCRIPTION_MAPPING_PROMPT.format(
                        descriptions="\n".join(descriptions),
                        extracted_text=extracted_text,
                        chunks= chunks_data
                    )
                },
                {
                    "type": "image",
                    "source_type": "url",
                    "url": request.image_url,
                },            
            ]
            message = HumanMessage(content=content)
            response = model.with_structured_output(ExpectedOutput)
            response = response.invoke([message])
            response = response.dict()
        else:
            response = ""
        
        return JSONResponse(content=response)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error mapping description: {str(e)}")