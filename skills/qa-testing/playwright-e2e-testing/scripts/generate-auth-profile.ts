#!/usr/bin/env node
/**
 * generate-auth-profile.ts — Generates and saves Playwright authentication profiles
 * Usage: npx tsx generate-auth-profile.ts [--role=admin|customer] [--output=path]
 *
 * Environment variables:
 *   BASE_URL — Application base URL
 *   TEST_USER_EMAIL — Login email
 *   TEST_USER_PASSWORD — Login password
 *   AUTH_OUTPUT_DIR — Output directory for storage state files
 */
import { chromium } from '@playwright/test';

interface AuthConfig {
  role: string;
  email: string;
  password: string;
  loginUrl: string;
  successUrl: string;
  outputPath: string;
}

async function generateAuthProfile(config: AuthConfig): Promise<void> {
  console.log(`🔐 Generating auth profile for role: ${config.role}`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    await page.goto(config.loginUrl);
    console.log(`   Loaded login page: ${config.loginUrl}`);

    await page.getByLabel(/email/i).fill(config.email);
    await page.getByLabel(/password/i).fill(config.password);
    await page.getByRole('button', { name: /sign in|log in|login/i }).click();

    await page.waitForURL(new RegExp(config.successUrl));
    console.log(`   Authentication successful`);

    await context.storageState({ path: config.outputPath });
    console.log(`   Profile saved: ${config.outputPath}`);
  } catch (error) {
    console.error(`❌ Auth failed for ${config.role}:`, error);
    // Take a screenshot for debugging
    await page.screenshot({ path: `auth-debug-${config.role}.png` });
    throw error;
  } finally {
    await browser.close();
  }
}

async function main() {
  const args = process.argv.slice(2);
  const role = args.find(a => a.startsWith('--role='))?.split('=')[1] || 'admin';
  const outputDir = process.env.AUTH_OUTPUT_DIR || 'playwright/.auth';

  const baseUrl = process.env.BASE_URL || 'http://localhost:3000';
  const email = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;

  if (!email || !password) {
    console.error('❌ TEST_USER_EMAIL and TEST_USER_PASSWORD must be set');
    process.exit(1);
  }

  // Ensure output directory exists
  const fs = await import('fs');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const configs: AuthConfig[] = [];

  switch (role) {
    case 'all':
    case 'admin':
      configs.push({
        role: 'admin',
        email,
        password,
        loginUrl: `${baseUrl}/login`,
        successUrl: 'dashboard',
        outputPath: `${outputDir}/admin.json`,
      });
      break;
    case 'all':
    case 'customer':
      configs.push({
        role: 'customer',
        email: process.env.TEST_CUSTOMER_EMAIL || email,
        password: process.env.TEST_CUSTOMER_PASSWORD || password,
        loginUrl: `${baseUrl}/login`,
        successUrl: 'dashboard',
        outputPath: `${outputDir}/customer.json`,
      });
      break;
    default:
      configs.push({
        role,
        email,
        password,
        loginUrl: `${baseUrl}/login`,
        successUrl: 'dashboard',
        outputPath: `${outputDir}/${role}.json`,
      });
  }

  for (const config of configs) {
    await generateAuthProfile(config);
  }

  console.log(`\n✅ All auth profiles generated in ${outputDir}/`);
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
