import { pgTable, serial, varchar, text, timestamp, boolean, integer } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  authHash: text('auth_hash').notNull(),
  salt: text('salt').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

export const categories = pgTable('categories', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id, { onDelete: 'cascade' }).notNull(),
  name: varchar('name', { length: 100 }).notNull(),
  color: varchar('color', { length: 20 }),
  icon: varchar('icon', { length: 50 }),
});

export const passwords = pgTable('passwords', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id, { onDelete: 'cascade' }).notNull(),
  siteName: varchar('site_name', { length: 255 }).notNull(),
  siteUrl: text('site_url'),
  username: varchar('username', { length: 255 }),
  encryptedPassword: text('encrypted_password').notNull(),
  iv: text('iv').notNull(),
  salt: text('salt').notNull(),
  categoryId: integer('category_id').references(() => categories.id, { onDelete: 'set null' }),
  notes: text('notes'),
  isFavorite: boolean('is_favorite').default(false).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

export const usersRelations = relations(users, ({ many }) => ({
  passwords: many(passwords),
  categories: many(categories),
}));

export const categoriesRelations = relations(categories, ({ one }) => ({
  user: one(users, {
    fields: [categories.userId],
    references: [users.id],
  }),
}));

export const passwordsRelations = relations(passwords, ({ one }) => ({
  user: one(users, {
    fields: [passwords.userId],
    references: [users.id],
  }),
  category: one(categories, {
    fields: [passwords.categoryId],
    references: [categories.id],
  }),
}));
