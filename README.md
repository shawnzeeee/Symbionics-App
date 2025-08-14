# Symbionics Frontend

Symbionics is an application designed to help users connect to a Muse EEG device and configure or calibrate it for use with a robotic glove. The primary goal of this project is to assist individuals with hand paralysis by enabling them to control a robotic glove for improved gripping ability. The app provides an intuitive interface for device connection, signal quality checking, and calibration routines, making advanced assistive technology accessible to those in need.

> This is the frontend for Symbionics, a BCI (Brain-Computer Interface) company. This project uses Vue 3, Vite, Tailwind CSS, and Pinia.

## Prerequisites

Before you begin, make sure you have the following installed:

- [Node.js](https://nodejs.org/) (Recommended: v18.x or v20.x LTS)
- [npm](https://www.npmjs.com/) (comes with Node.js)

## Getting Started

1. **Clone the repository:**

   ```sh
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies:**

   ```sh
   npm install
   ```

3. **Start the development server:**

   ```sh
   npm run dev
   ```

   The app will be available at the local address shown in your terminal (usually http://localhost:5173).

## Backend Setup

1. **Navigate to the backend directory:**

   ```sh
   cd backend
   ```

2. **(Recommended) Create a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server:**

   ```sh
   uvicorn main:app --reload
   ```

## Additional Commands

- **Run unit tests:**
  ```sh
  npm run test:unit
  ```
- **Format code:**
  ```sh
  npm run format
  ```

## Tech Stack

- [Vue 3](https://vuejs.org/)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vue Router](https://router.vuejs.org/)
- [Fast API](https://fastapi.tiangolo.com/)

## Codebase Architecture
# frontend
 - frontend/src/views contains all the Vue files that create the UI, make api calls and open webosockets
 - frontend/src/ws.js contains the functions for opening websocket connection with backend
 - frontend/src/api.js contains the functions for making api calls to backend

# backend
 - backend/routers contains all the api endpoints, all api calls from the frontend will be received here and redirected to its proper function
 - backend/services contains all the functionality for managing threads
 - backend/process contains all the functions that will actually be running on the threads will be targeting


## Calibrate Model

The Calibrate Model feature allows users to tweak the sensitivity of the classifier model using interactive adders and subtractors on the frontend.

### Steps

1. **Frontend Initialization**
   - When `CalibrateModel.vue` mounts, it sends a request to train the SVM by calling the `trainSVM` function from `api.js`.

2. **Backend Training**
   - The request is received by the backend in `calibration_router.py`.
   - `calibration_service.py` handles the request with the `train_classifier`, which trains the classifier model by calling the function in `classifier_process.py`.

3. **WebSocket Connection**
   - Once training is complete, the frontend opens a WebSocket connection by calling `createAttentionThresholdSocket` from `ws.js`.

4. **Backend Attention Threshold Loop**
   - The backend receives the WebSocket connection through `calibration_router`.
   - `calibration_service.py` runs `begin_checking_attention_threshold`, which checks if the pylsl thread exists and starts the classifier loop in `classifier_process.py`.

5. **Classifier Process**
   - The classifier loop and SVM training logic are implemented in `classifier_process.py`.
   - During the loop, the backend sends real-time updates to the frontend via WebSocket:
     ```json
     {
       "gesture": gesture,
       "attention_threshold": attention_threshold
     }
     ```

6. **Frontend Controls**
   - The user can adjust the sensitivity using the adder and subtractor buttons.
   - These adjustments are sent to the backend and reflected in the classifier’s behavior in real time.

### Relevant Files
- **Frontend:** `frontend/src/views/CalibrateModel.vue`
- **Backend:**
  - `backend/routers/calibration_router.py`
  - `backend/services/calibration_service.py`
  - `backend/process/classifier_process.py`

## License

&copy; 2025 Symbionics. All rights reserved.
