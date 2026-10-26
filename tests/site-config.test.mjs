import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import path from 'node:path';
import config from '../astro.config.mjs';

const root = path.resolve(import.meta.dirname, '..');

test('public CNAME and canonical site origin agree', () => {
  const site = new URL(config.site);
  assert.equal(site.protocol, 'https:');
  assert.equal(site.href, `${site.origin}/`, 'Site must be a bare HTTPS origin');
  assert.equal(fs.readFileSync(path.join(root, 'public/CNAME'), 'utf8').trim(), site.hostname);
});

test('future booklet links use the current website origin', () => {
  const directory = path.join(root, 'booklet/trips');
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const planPath = path.join(directory, entry.name, 'book-plan.json');
    if (!fs.existsSync(planPath)) continue;
    const plan = JSON.parse(fs.readFileSync(planPath, 'utf8'));
    assert.equal(new URL(plan.webUrl).origin, new URL(config.site).origin, entry.name);
    assert.equal(new URL(plan.webUrl).pathname, `/${entry.name}/`, entry.name);
  }
});
