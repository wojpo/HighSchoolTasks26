CREATE TABLE "containers" (
	"id" text PRIMARY KEY NOT NULL,
	"user_ip" text,
	"created_at" timestamp DEFAULT now() NOT NULL
);
