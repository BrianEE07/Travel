import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { scanPublicPayload } from './lib/trip-parser.mjs';
import { defaultNotePath, readPublicSource, publicScanAllowances } from './lib/public-source.mjs';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const roots = [path.join(projectRoot, 'src/data/trips'), path.join(projectRoot, 'dist')];
const files = [];
const trips = [];
let secrets = [];
try {
  const source = await readPublicSource(process.env.TRAVEL_NOTE_PATH || defaultNotePath);
  secrets = source.secrets;
} catch (error) {
  // Private Vault is absent in CI. Explicit sources must always be readable.
  if (process.env.TRAVEL_NOTE_PATH || error.code !== 'ENOENT') throw error;
}

for (const entry of await fs.readdir(path.join(projectRoot, 'src/data/trips'))) {
  if (!entry.endsWith('.json')) continue;
  const trip = JSON.parse(await fs.readFile(path.join(projectRoot, 'src/data/trips', entry), 'utf8'));
  trips.push(trip);
}
const { prices: allowedPrices, images: allowedImageUrls } = publicScanAllowances(trips);

async function walk(target) {
  const stat = await fs.stat(target);
  if (stat.isFile()) return files.push(target);
  for (const entry of await fs.readdir(target, { withFileTypes: true })) {
    if (entry.isDirectory()) await walk(path.join(target, entry.name));
    else if (/\.(?:html|js|json|xml|txt|webmanifest)$/.test(entry.name)) files.push(path.join(target, entry.name));
  }
}

for (const root of roots) await walk(root);
const findings = [];
for (const file of files) {
  const content = await fs.readFile(file, 'utf8');
  for (const finding of scanPublicPayload(content, secrets, allowedPrices, allowedImageUrls)) findings.push(`${path.relative(projectRoot, file)}: ${finding}`);
}
if (findings.length) throw new Error(`Secret scan failed:\n${findings.join('\n')}`);
console.log(`Secret scan passed across ${files.length} public files (${secrets.length ? 'with local source fingerprints' : 'CI pattern scan; no source fingerprints'}).`);
