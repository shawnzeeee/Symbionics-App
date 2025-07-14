# Symbionics Frontend

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
- [Pinia](https://pinia.vuejs.org/)
- [Vue Router](https://router.vuejs.org/)

## License

&copy; 2025 Symbionics. All rights reserved.
