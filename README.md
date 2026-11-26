# ImageIQ | Digital Image Processing Laboratory

A hands-on laboratory to enhance, analyze and understand digital images through interactive experiments.

## About the Project

**ImageIQ** is a web-based Digital Image Processing laboratory designed to demonstrate fundamental image processing techniques through interactive experiments.

The platform combines a user-friendly frontend with a Python Flask backend to perform image processing operations and visualize their results.

## Experiments

### 01. Image Enhancement
- Contrast stretching
- Spatial smoothing
- Image enhancement techniques

### 02. Object Analysis
- Image preprocessing
- Image segmentation
- Feature extraction

### 03. Shape Recognition
- Shape feature analysis
- Regional descriptors
- Image moments

### 04. Image Processing
- Handwritten digit recognition
- Image preprocessing
- HOG feature extraction
- K-Nearest Neighbors (KNN) classification

## Tech Stack

**Frontend**
- HTML5
- CSS3
- JavaScript

**Backend**
- Python
- Flask
- Flask-CORS

**Image Processing & Machine Learning**
- OpenCV
- NumPy
- Scikit-learn
- Scikit-image
- Matplotlib
- Pillow

## Project Structure

```text
ImageIQ/
│
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── ...
│
├── backend/
│   └── app.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/nayakveda84/ImageIQ.git
```

### 2. Navigate to the project folder

```bash
cd ImageIQ
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Start the Flask backend

```bash
python backend/app.py
```

The backend runs locally at:

`http://127.0.0.1:5000`

### 7. Launch the frontend

Open `frontend/index.html` using VS Code Live Server.

Make sure the Flask backend is running when using features that require image processing.

## Features

- Four interactive DIP experiments
- Image upload and processing
- Visual representation of processing results
- Handwritten digit recognition
- Frontend and backend integration
- Responsive web interface

## Deployment

The frontend is deployed using **GitHub Pages**.

The Flask backend requires separate Python-compatible hosting for live image-processing functionality.

## Repository

[GitHub – ImageIQ](https://github.com/nayakveda84/ImageIQ)

---

**ImageIQ | Digital Image Processing Laboratory**

*Explore. Process. Analyze. Recognize.*
