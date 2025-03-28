from pathlib import Path
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile, File
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
# from db import Base, async_engine, get_async_db

import torch
from joblib import load
from schema import InferenceInput, InferenceOutput
from model import Model
from predict import predict_disease
from config import CONFIG
from tempfile import NamedTemporaryFile
import shutil
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).parent.parent / '.env')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model
    model = Model(num_classes=42)
    
    # Load the state dict from the fine-tuned ResNet18
    state_dict = torch.load(CONFIG['MODEL_PATH'], map_location=torch.device(CONFIG['DEVICE']))
    
    # Add 'model.' prefix to keys since our Model class wraps ResNet18 in self.model
    prefixed_state_dict = {'model.' + k: v for k, v in state_dict.items()}
    
    model.load_state_dict(prefixed_state_dict)
    model.eval()

    # add model and other preprocess tools too app state
    app.package = {
        "model": model,
        "device": CONFIG['DEVICE']  # Also add device to package
    }
    yield

    # Clean up the model
    pass

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web-crop-disease-detection.vercel.app", 
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# redis_client = aioredis.from_url(settings.redis_url)

@app.get("/")
async def root():
    return {"message": "This is a FastAPI app that uses CoinGecko API"}

@app.post('/predict', response_model=InferenceOutput)
async def predict_endpoint(request: Request, file: UploadFile = File(...)):
    # Create a temporary file to store the uploaded image
    try:
        with NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            # Save the uploaded file to a temporary location
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Make sure to close the file
        file.file.close()
        
        # Process the image using the temporary file path
        disease, confidence = predict_disease(temp_file_path, app.package)
        
        # Create response from the prediction results
        response = {
            "disease": disease,
            "confidence": confidence,
        }
        
        CropDiseaseSolution = {
            "American Bollworm on Cotton": {
                "Cause": "Larvae of Helicoverpa armigera feeding on cotton bolls.",
                "Peak Season": "Summer and early monsoon.",
                "Remedy": "Use pheromone traps and insecticides like Spinosad or Bacillus thuringiensis."
            },
            "Anthracnose on Cotton": {
                "Cause": "Fungal infection caused by Colletotrichum species.",
                "Peak Season": "High humidity periods, usually post-monsoon.",
                "Remedy": "Apply copper-based fungicides and ensure good field drainage."
            },
            "Army worm": {
                "Cause": "Larvae of Spodoptera species attacking foliage.",
                "Peak Season": "Rainy season and post-monsoon.",
                "Remedy": "Use neem oil or Bacillus thuringiensis-based biopesticides."
            },
            "Bacterial Blight": {
                "Cause": "Xanthomonas citri bacteria spreading through infected seeds and water.",
                "Peak Season": "Warm and humid conditions.",
                "Remedy": "Use resistant varieties and copper-based fungicides."
            },
            "Brownspot": {
                "Cause": "Drechslera oryzae fungus causing lesions on leaves.",
                "Peak Season": "High humidity and excessive nitrogen fertilization.",
                "Remedy": "Use balanced fertilization and Mancozeb fungicide spray."
            },
            "Common Rust": {
                "Cause": "Puccinia sorghi fungus spreading through wind-borne spores.",
                "Peak Season": "Warm, humid conditions during late summer.",
                "Remedy": "Plant rust-resistant varieties and use sulfur-based fungicides."
            },
            "Cotton Curl Virus": {
                "Cause": "Cotton leaf curl virus transmitted by whiteflies.",
                "Peak Season": "Warm seasons with high whitefly populations.",
                "Remedy": "Control whitefly populations and plant resistant varieties."
            },
            "Flag Smut": {
                "Cause": "Urocystis agropyri fungus affecting wheat seedlings.",
                "Peak Season": "Cool and moist conditions during early growth.",
                "Remedy": "Use disease-free seeds and treat seeds with fungicides before planting."
            },
            "Gray_Leaf_Spot": {
                "Cause": "Fungal infection caused by Cercospora species.",
                "Peak Season": "Late summer and early autumn.",
                "Remedy": "Use strobilurin-based fungicides and improve air circulation in the field."
            },
            "Healthy": {
                "Cause": "No disease detected.",
                "Peak Season": "N/A",
                "Remedy": "Crop is healthy, no diagnosis required."
            },
            "Healthy Maize": {
                "Cause": "No disease detected.",
                "Peak Season": "N/A",
                "Remedy": "Crop is healthy, no diagnosis required."
            },
            "Healthy Wheat": {
                "Cause": "No disease detected.",
                "Peak Season": "N/A",
                "Remedy": "Crop is healthy, no diagnosis required."
            },
            "Healthy cotton": {
                "Cause": "No disease detected.",
                "Peak Season": "N/A",
                "Remedy": "Crop is healthy, no diagnosis required."
            },
            "Leaf Curl": {
                "Cause": "Begomovirus transmitted by whiteflies.",
                "Peak Season": "Monsoon and early winter.",
                "Remedy": "Control whiteflies, as they spread the virus, and use resistant plant varieties."
            },
            "Leaf smut": {
                "Cause": "Fungal infection caused by Entyloma oryzae.",
                "Peak Season": "Humid conditions in early growth stages.",
                "Remedy": "Use seed treatment with Thiram or Captan before sowing."
            },
            "Mosaic sugarcane": {
                "Cause": "Sugarcane mosaic virus (SCMV) spread by aphids.",
                "Peak Season": "Monsoon and post-monsoon.",
                "Remedy": "Use virus-free planting material and remove infected plants."
            },
            "RedRot sugarcane": {
                "Cause": "Fungal disease caused by Colletotrichum falcatum.",
                "Peak Season": "Warm and humid conditions.",
                "Remedy": "Apply Trichoderma viride-based biofungicides and remove infected stalks."
            },
            "Rice Blast": {
                "Cause": "Fungal infection caused by Magnaporthe oryzae.",
                "Peak Season": "High humidity with temperature between 24-28°C.",
                "Remedy": "Use resistant varieties and apply fungicides like Tricyclazole."
            },
            "Sugarcane healthy": {
                "Cause": "No disease detected.",
                "Peak Season": "N/A",
                "Remedy": "Crop is healthy, no diagnosis required."
            },
            "Tungro": {
                "Cause": "Rice tungro virus transmitted by green leafhoppers.",
                "Peak Season": "Rainy season with high humidity.",
                "Remedy": "Control leafhopper vectors and use resistant rice varieties."
            },
            "Wheat Brown leaf Rust": {
                "Cause": "Fungal infection caused by Puccinia triticina.",
                "Peak Season": "Cool, moist conditions in spring.",
                "Remedy": "Use resistant varieties and apply propiconazole-based fungicides."
            },
            "Wheat Stem Fly": {
                "Cause": "Infestation by Atherigona species damaging wheat stems.",
                "Peak Season": "Early growth stage during warm weather.",
                "Remedy": "Early sowing and application of insecticides like imidacloprid."
            },
            "Wheat aphid": {
                "Cause": "Infestation by various aphid species sucking sap from wheat plants.",
                "Peak Season": "Cool, dry weather during tillering and heading stages.",
                "Remedy": "Apply neem-based insecticides or introduce natural predators."
            },
            "Wheat Black Rust": {
                "Cause": "Fungal infection caused by Puccinia graminis.",
                "Peak Season": "Late winter and early spring.",
                "Remedy": "Apply triazole fungicides and use rust-resistant wheat varieties."
            },
            "Wheat leaf rust": {
                "Cause": "Fungal infection caused by Puccinia recondita.",
                "Peak Season": "Mild temperatures and high humidity during growth.",
                "Remedy": "Use resistant varieties and apply azoxystrobin-based fungicides."
            },
            "Wheat midge": {
                "Cause": "Infestation by Sitodiplosis mosellana larvae damaging wheat kernels.",
                "Peak Season": "Warm evenings during wheat heading.",
                "Remedy": "Time planting to avoid peak midge periods and use insecticides if necessary."
            },
            "Wheat powdery mildew": {
                "Cause": "Fungal infection caused by Blumeria graminis.",
                "Peak Season": "Cool, humid conditions with dense crop canopy.",
                "Remedy": "Apply sulfur or triazole fungicides and ensure proper spacing."
            },
            "Wheat Scab": {
                "Cause": "Fungal infection caused by Fusarium species.",
                "Peak Season": "Wet conditions during flowering.",
                "Remedy": "Use resistant varieties and apply triazole fungicides during flowering."
            },
            "Wheat_Yellow_Rust": {
                "Cause": "Fungal infection caused by Puccinia striiformis.",
                "Peak Season": "Cool and moist conditions in early spring.",
                "Remedy": "Use resistant varieties and apply strobilurin fungicides."
            },
            "Wilt": {
                "Cause": "Fungal infection caused by Fusarium oxysporum.",
                "Peak Season": "Hot and dry conditions.",
                "Remedy": "Use disease-free seeds and practice crop rotation."
            },
            "Yellow Rust Sugarcane": {
                "Cause": "Fungal infection caused by Puccinia kuehnii.",
                "Peak Season": "Cool and humid conditions.",
                "Remedy": "Use resistant varieties and sulfur fungicides."
            },
            "bacterial blight cotton": {
                "Cause": "Xanthomonas axonopodis pv. malvacearum bacteria infecting cotton plants.",
                "Peak Season": "Rainy season with high humidity.",
                "Remedy": "Use resistant varieties and copper oxychloride sprays."
            },
            "bollrot on Cotton": {
                "Cause": "Fungal pathogens affecting cotton bolls, primarily Rhizopus nigricans.",
                "Peak Season": "Rainy season with high humidity.",
                "Remedy": "Apply carbendazim-based fungicides and improve field drainage."
            },
            "bollworm on cotton": {
                "Cause": "Various species of bollworm larvae including Helicoverpa and Pectinophora.",
                "Peak Season": "Flowering and fruiting stages during warm weather.",
                "Remedy": "Use Bt cotton varieties and integrated pest management techniques."
            },
            "cotton mealy bug": {
                "Cause": "Phenacoccus solenopsis insects covering cotton plants with waxy secretions.",
                "Peak Season": "Hot and dry conditions.",
                "Remedy": "Apply insecticidal soaps and release natural predators like ladybugs."
            },
            "cotton whitefly": {
                "Cause": "Bemisia tabaci insects sucking sap and transmitting viruses.",
                "Peak Season": "Warm and dry conditions.",
                "Remedy": "Use yellow sticky traps and neem oil sprays."
            },
            "jassid on cotton": {
                "Cause": "Amrasca biguttula biguttula insects causing leaf curling and yellowing.",
                "Peak Season": "Hot and humid conditions.",
                "Remedy": "Apply imidacloprid or acetamiprid insecticides."
            },
            "maize ear rot": {
                "Cause": "Fungal infection caused by Fusarium species.",
                "Peak Season": "High moisture conditions during grain filling.",
                "Remedy": "Harvest early and ensure proper drying of maize cobs."
            },
            "maize fall armyworm": {
                "Cause": "Spodoptera frugiperda larvae feeding on maize leaves.",
                "Peak Season": "Warm and humid conditions.",
                "Remedy": "Use biological control like parasitoid wasps and neem oil sprays."
            },
            "maize stem borer": {
                "Cause": "Chilo partellus larvae boring into maize stems.",
                "Peak Season": "Warm weather during vegetative growth.",
                "Remedy": "Apply carbofuran granules in whorls and use resistant varieties."
            },
            "pink bollworm in cotton": {
                "Cause": "Pectinophora gossypiella larvae burrowing into cotton bolls.",
                "Peak Season": "Warm and dry conditions during boll formation.",
                "Remedy": "Use pheromone traps and Bt cotton varieties."
            },
            "red cotton bug": {
                "Cause": "Dysdercus cingulatus sucking sap from cotton plants.",
                "Peak Season": "Post-monsoon and dry weather.",
                "Remedy": "Use insecticides like Malathion and remove plant debris after harvest."
            },
            "mites in cotton": {
                "Cause": "Tetranychus urticae and related species damaging cotton leaves.",
                "Peak Season": "Hot and dry conditions.",
                "Remedy": "Apply sulfur-based miticides and maintain field moisture."
            }
        }
        # Add disease solution if available
        if disease in CropDiseaseSolution:
            response["solution"] = CropDiseaseSolution[disease]
            
        # Clean up the temporary file
        os.unlink(temp_file_path)
            
        return response
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        # Clean up temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")



