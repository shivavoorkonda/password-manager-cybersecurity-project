import express from 'express';
import { db } from './db.js';
import { users, passwords, categories } from './schema.js';
import { eq, and } from 'drizzle-orm';
import { z } from 'zod';

export const router = express.Router();

// Middleware to check authentication
const requireAuth = (req: express.Request, res: express.Response, next: express.NextFunction) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
};

// ... Zod schemas ...
const registerSchema = z.object({
  email: z.string().email(),
  authHash: z.string(),
  salt: z.string()
});
const loginSchema = z.object({
  email: z.string().email(),
  authHash: z.string()
});
const passwordSchema = z.object({
  siteName: z.string(),
  siteUrl: z.string().optional(),
  username: z.string().optional(),
  encryptedPassword: z.string(),
  iv: z.string(),
  salt: z.string(),
  categoryId: z.number().optional(),
  notes: z.string().optional(),
  isFavorite: z.boolean().default(false)
});
const categorySchema = z.object({
  name: z.string(),
  color: z.string().optional(),
  icon: z.string().optional()
});

// AUTH
router.post('/auth/register', async (req, res) => {
  try {
    const data = registerSchema.parse(req.body);
    const existing = await db.query.users.findFirst({ where: eq(users.email, data.email) });
    if (existing) return res.status(400).json({ error: 'Email already in use' });
    
    const [user] = await db.insert(users).values(data).returning();
    req.session.userId = user.id;
    res.status(201).json({ user: { id: user.id, email: user.email } });
  } catch (err) {
    res.status(400).json({ error: 'Registration failed' });
  }
});

router.post('/auth/login', async (req, res) => {
  try {
    const data = loginSchema.parse(req.body);
    const user = await db.query.users.findFirst({ where: eq(users.email, data.email) });
    
    if (!user || user.authHash !== data.authHash) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    req.session.userId = user.id;
    res.json({ user: { id: user.id, email: user.email, salt: user.salt } });
  } catch (err) {
    res.status(400).json({ error: 'Login failed' });
  }
});

router.post('/auth/logout', (req, res) => {
  req.session.destroy(() => {
    res.json({ success: true });
  });
});

router.get('/auth/me', requireAuth, async (req, res) => {
  try {
    const user = await db.query.users.findFirst({ where: eq(users.id, req.session.userId!) });
    if (!user) return res.status(404).json({ error: 'User not found' });
    res.json({ user: { id: user.id, email: user.email, salt: user.salt } });
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

// PASSWORDS
router.get('/passwords', requireAuth, async (req, res) => {
  try {
    const items = await db.query.passwords.findMany({ where: eq(passwords.userId, req.session.userId!) });
    res.json(items);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch passwords' });
  }
});

router.post('/passwords', requireAuth, async (req, res) => {
  try {
    const data = passwordSchema.parse(req.body);
    const [item] = await db.insert(passwords).values({ ...data, userId: req.session.userId! }).returning();
    res.status(201).json(item);
  } catch (err) {
    res.status(400).json({ error: 'Invalid password data' });
  }
});

router.put('/passwords/:id', requireAuth, async (req, res) => {
  try {
    const data = passwordSchema.parse(req.body);
    const id = parseInt(req.params.id);
    const [item] = await db.update(passwords)
      .set({ ...data, updatedAt: new Date() })
      .where(and(eq(passwords.id, id), eq(passwords.userId, req.session.userId!)))
      .returning();
    if (!item) return res.status(404).json({ error: 'Not found' });
    res.json(item);
  } catch (err) {
    res.status(400).json({ error: 'Update failed' });
  }
});

router.delete('/passwords/:id', requireAuth, async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const [deleted] = await db.delete(passwords)
      .where(and(eq(passwords.id, id), eq(passwords.userId, req.session.userId!)))
      .returning();
    if (!deleted) return res.status(404).json({ error: 'Not found' });
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: 'Deletion failed' });
  }
});

router.patch('/passwords/:id/favorite', requireAuth, async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const isFavorite = z.boolean().parse(req.body.isFavorite);
    const [item] = await db.update(passwords)
      .set({ isFavorite, updatedAt: new Date() })
      .where(and(eq(passwords.id, id), eq(passwords.userId, req.session.userId!)))
      .returning();
    if (!item) return res.status(404).json({ error: 'Not found' });
    res.json(item);
  } catch (err) {
    res.status(400).json({ error: 'Update failed' });
  }
});

// CATEGORIES
router.get('/categories', requireAuth, async (req, res) => {
  try {
    const items = await db.query.categories.findMany({ where: eq(categories.userId, req.session.userId!) });
    res.json(items);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch categories' });
  }
});

router.post('/categories', requireAuth, async (req, res) => {
  try {
    const data = categorySchema.parse(req.body);
    const [item] = await db.insert(categories).values({ ...data, userId: req.session.userId! }).returning();
    res.status(201).json(item);
  } catch (err) {
    res.status(400).json({ error: 'Invalid category data' });
  }
});

// IMPORT / EXPORT
router.post('/export', requireAuth, async (req, res) => {
  try {
    const items = await db.query.passwords.findMany({ where: eq(passwords.userId, req.session.userId!) });
    res.json({ passwords: items });
  } catch (err) {
    res.status(500).json({ error: 'Export failed' });
  }
});

const importSchema = z.object({
  passwords: z.array(passwordSchema)
});

router.post('/import', requireAuth, async (req, res) => {
  try {
    const data = importSchema.parse(req.body);
    const itemsToInsert = data.passwords.map(p => ({ ...p, userId: req.session.userId! }));
    if (itemsToInsert.length > 0) {
      await db.insert(passwords).values(itemsToInsert);
    }
    res.json({ success: true, count: itemsToInsert.length });
  } catch (err) {
    res.status(400).json({ error: 'Import failed' });
  }
});
