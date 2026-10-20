import express from 'express';
import cors from 'cors';
import { rateLimit } from 'express-rate-limit';
import session from 'express-session';
import pgSession from 'connect-pg-simple';
import * as dotenv from 'dotenv';
import { router } from './routes.js';

dotenv.config();

if (!process.env.SESSION_SECRET || process.env.SESSION_SECRET.length < 32) {
  throw new Error('Set SESSION_SECRET to a random value of at least 32 characters.');
}

const app = express();
const PORT = process.env.PORT || 3001;

// Only trust a reverse proxy when the deployment explicitly enables it.
if (process.env.TRUST_PROXY === '1') app.set('trust proxy', 1);

app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true
}));

app.use(express.json({ limit: '10mb' }));

// Setup Session
const PgSession = pgSession(session);
app.use(session({
  store: new PgSession({
    conString: process.env.DATABASE_URL,
    tableName: 'session',
    createTableIfMissing: true
  }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 30 * 24 * 60 * 60 * 1000, // 30 days
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    sameSite: 'lax'
  }
}));

// Add types for session
declare module 'express-session' {
  interface SessionData {
    userId: number;
  }
}

// Rate Limiting
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});

const authLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api', generalLimiter);
app.use('/api/auth', authLimiter);

// Routes
app.use('/api', router);

// Health check
app.get('/health', (req, res) => res.json({ status: 'ok' }));

const server = app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});

// Graceful shutdown
const shutdown = () => {
  console.log('Shutting down server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
};

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
