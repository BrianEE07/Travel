import fs from 'node:fs/promises';
import { parseTrip } from './trip-parser.mjs';

export const defaultNotePath = '/Users/ywfan/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecondBrain/01_Inbox_Notes/福岡之旅 20260827~0903.md';

// Does not depend on Astro, website assets or generated website data.
export async function readPublicSource(notePath) {
  if (!notePath) throw new Error('Specify the source note explicitly.');
  const result = parseTrip(await fs.readFile(notePath, 'utf8'));
  result.trip.updatedAt = (await fs.stat(notePath)).mtime.toISOString();
  return result;
}

export function publicScanAllowances(trips) {
  const prices = [];
  const images = [];
  for (const trip of trips) {
    for (const entity of trip.entities ?? []) {
      if (entity.image?.url) images.push(entity.image.url);
      if (entity.type === 'stay' && entity.price?.text) prices.push(entity.price.text);
      if (entity.type === 'transport') {
        for (const segment of entity.segments ?? []) if (segment.price?.text) prices.push(segment.price.text);
      }
    }
  }
  return { prices, images };
}
