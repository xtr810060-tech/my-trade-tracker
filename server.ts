import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { createServer as createViteServer } from "vite";
import authRoutes from "./src/backend/routes/auth.js";
import tradeRoutes from "./src/backend/routes/trades.js";

dotenv.config();

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(cors());
  app.use(express.json());
  app.use('/uploads', express.static(path.join(process.cwd(), 'uploads')));

  // Connect to MongoDB (or fallback to in-memory array if not provided)
  const mongoUri = process.env.MONGODB_URI?.trim();
  if (mongoUri && (mongoUri.startsWith('mongodb://') || mongoUri.startsWith('mongodb+srv://'))) {
    try {
      await mongoose.connect(mongoUri);
      console.log("Connected to MongoDB");
    } catch (err) {
      console.error("MongoDB connection error:", err);
    }
  } else {
    if (mongoUri) {
      console.warn("MONGODB_URI is provided but has an invalid scheme. Expected 'mongodb://' or 'mongodb+srv://'. Using in-memory store for development.");
    } else {
      console.warn("MONGODB_URI not provided in .env. Using in-memory store for development.");
    }
  }

  // API routes FIRST
  app.use("/api/auth", authRoutes);
  app.use("/api/trades", tradeRoutes);

  app.get("/api/health", (req, res) => {
    res.json({ status: "ok" });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
