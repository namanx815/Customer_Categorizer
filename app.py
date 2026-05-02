from fastapi import FastAPI, Request
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from uvicorn import run as app_run
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import logging
import sys

from src.pipeline.prediction_pipeline import PredictionPipeline
from src.pipeline.train_pipeline import TrainPipeline
from src.constant.application import *

import warnings
warnings.filterwarnings('ignore')

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Customer Categorizer API",
    description="ML-powered customer segmentation and personality prediction",
    version="1.0.0"
)

templates = Jinja2Templates(directory='templates')

origins = ["*"]

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DataForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.Age : Optional[str] = None
        self.Education  : Optional[str] = None
        self.Marital_Status  : Optional[str] = None
        self.Parental_Status : Optional[str] = None
        self.Children  : Optional[str] = None
        self.Income  : Optional[str] = None
        self.Total_Spending  : Optional[str] = None
        self.Days_as_Customer  : Optional[str] = None
        self.Recency  : Optional[str] = None
        self.Wines  : Optional[str] = None
        self.Fruits  : Optional[str] = None
        self.Meat : Optional[str] = None
        self.Fish   : Optional[str] = None
        self.Sweets : Optional[str] = None
        self.Gold  : Optional[str] = None
        self.Web  : Optional[str] = None
        self.Catalog  : Optional[str] = None
        self.Store  : Optional[str] = None
        self.Discount_Purchases  : Optional[str] = None
        self.Total_Promo  : Optional[str] = None
        self.NumWebVisitsMonth  : Optional[str] = None
        

    async def get_customer_data(self):
        form =  await self.request.form()
        self.Age = form.get('Age')
        self.Education = form.get('Education')
        self.Marital_Status = form.get('Marital_Status')
        self.Parental_Status = form.get('Parental_Status')
        self.Children = form.get('Children')
        self.Income = form.get('Income')
        self.Total_Spending = form.get('Total_Spending')
        self.Days_as_Customer = form.get('Days_as_Customer')
        self.Recency = form.get('Recency')
        self.Wines = form.get('Wines')
        self.Fruits = form.get('Fruits')
        self.Meat = form.get('Meat')
        self.Fish = form.get('Fish')
        self.Sweets = form.get('Sweets')
        self.Gold = form.get('Gold')
        self.Web = form.get('Web')
        self.Catalog = form.get('Catalog')
        self.Store = form.get('Store')
        self.Discount_Purchases = form.get('Discount_Purchases')
        self.Total_Promo = form.get('Total_Promo')
        self.NumWebVisitsMonth = form.get('NumWebVisitsMonth')


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        logger.info("Health check request received")
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "Customer Categorizer API",
                "version": "1.0.0"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/train", tags=["Training"])
async def trainRouteClient():
    """Train the ML model with fresh data"""
    try:
        logger.info("Training pipeline initiated")
        train_pipeline = TrainPipeline()
        train_pipeline.run_pipeline()
        logger.info("Training completed successfully")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "Training successful!!"}
        )

    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Training failed: {str(e)}"}
        )


@app.get("/", tags=["Prediction"])
async def predictGetRouteClient(request: Request):
    """Render prediction form"""
    try:
        logger.info("Prediction form requested")
        return templates.TemplateResponse(
            "customer.html",
            {"request": request, "context": "Rendering"},
        )

    except Exception as e:
        logger.error(f"Form rendering failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error occurred: {str(e)}"}
        )


@app.post("/", tags=["Prediction"])
async def predictRouteClient(request: Request):
    """Make predictions on customer data"""
    try:
        logger.info("Prediction request received")
        form = DataForm(request)
        
        await form.get_customer_data()
        
        input_data = [form.Age, 
                    form.Education, 
                    form.Marital_Status, 
                    form.Parental_Status, 
                    form.Children, 
                    form.Income, 
                    form.Total_Spending, 
                    form.Days_as_Customer, 
                    form.Recency, 
                    form.Wines, 
                    form.Fruits, 
                    form.Meat, 
                    form.Fish, 
                    form.Sweets, 
                    form.Gold, 
                    form.Web, 
                    form.Catalog, 
                    form.Store, 
                    form.Discount_Purchases, 
                    form.Total_Promo, 
                    form.NumWebVisitsMonth]
        
        logger.info(f"Processing prediction with input data")
        prediction_pipeline = PredictionPipeline()
        predicted_cluster = prediction_pipeline.run_pipeline(input_data=input_data)
        
        logger.info(f"Prediction completed: cluster {predicted_cluster[0]}")
        
        return templates.TemplateResponse(
            "customer.html",
            {"request": request, "context": int(predicted_cluster[0])}
        )

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": False, "error": f"Prediction failed: {str(e)}"}
        )


if __name__ == "__main__":
    logger.info(f"Starting FastAPI server on {APP_HOST}:{APP_PORT}")
    app_run(app, host=APP_HOST, port=APP_PORT)
