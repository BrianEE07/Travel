import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { readPublicSource, publicScanAllowances } from '../scripts/lib/public-source.mjs';
import { scanPublicPayload } from '../scripts/lib/trip-parser.mjs';

const root = path.dirname(fileURLToPath(import.meta.url));
const { values } = parseArgs({ options: { note: { type: 'string' }, verify: { type: 'boolean' } } });
const { trip, secrets } = await readPublicSource(values.note || process.env.TRAVEL_NOTE_PATH);
const temporary = path.join(root, 'tmp', trip.slug);
if (values.verify) {
  const payload = JSON.parse(await fs.readFile(path.join(temporary, 'book-privacy.json'), 'utf8'));
  if (payload.sourceHash !== trip.sourceHash) throw new Error('Source changed after PDF build. Review and rebuild.');
  const { prices, images } = publicScanAllowances([trip]);
  const findings = scanPublicPayload(payload.artifacts, secrets, prices, images);
  if (findings.length) throw new Error(`Booklet privacy check failed: ${findings.join(', ')}`);
  console.log('PASS: PDF text, links and metadata privacy scan with source fingerprints.');
} else {
  await fs.mkdir(temporary, { recursive: true });
  await fs.writeFile(path.join(temporary, 'trip.json'), `${JSON.stringify(trip, null, 2)}\n`);
  console.log(`Booklet public snapshot: ${trip.slug} · ${trip.days.length} days. No website build required.`);
}
