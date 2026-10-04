import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defaultNotePath, readPublicSource } from './lib/public-source.mjs';
import { assertNotePublishSafe, assertEmptyIndex, noteDataPath } from './lib/publish-safety.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const run = (command, args) => {
  const result = spawnSync(command, args, {
    cwd: root,
    stdio: 'inherit',
    env: { ...process.env, ASTRO_TELEMETRY_DISABLED: '1' },
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
};

const isRepository = spawnSync('git', ['rev-parse', '--is-inside-work-tree'], { cwd: root, encoding: 'utf8' }).stdout?.trim() === 'true';
if (isRepository) assertNotePublishSafe(root);
const notePath = process.env.TRAVEL_NOTE_PATH || defaultNotePath;
const { trip } = await readPublicSource(notePath);
const target = noteDataPath(trip.slug);
run('npm', ['run', 'sync']);
run('npm', ['run', 'test']);
run('npm', ['run', 'check']);
run('npx', ['astro', 'build']);
run('node', ['scripts/scan-dist.mjs']);
if (!isRepository) {
  console.log('Build is safe and ready. Initialize the Git repository before the first publish.');
  process.exit(0);
}
assertNotePublishSafe(root);
const existsOrTracked = fs.existsSync(path.join(root, target)) ||
  spawnSync('git', ['ls-files', '--error-unmatch', target], { cwd: root, stdio: 'ignore' }).status === 0;
if (!existsOrTracked) {
  console.log('Draft has no public data to publish.');
  process.exit(0);
}
run('git', ['add', '--', target]);
const diff = spawnSync('git', ['diff', '--cached', '--quiet', '--', target], { cwd: root });
if (diff.status === 0) {
  console.log('No public itinerary changes to publish.');
  process.exit(0);
}
const stamp = new Intl.DateTimeFormat('sv-SE', { dateStyle: 'short', timeStyle: 'short', timeZone: 'Asia/Taipei' }).format(new Date());
if (diff.status !== 1) throw new Error('Cannot verify selected trip diff.');
const staged = spawnSync('git', ['diff', '--cached', '--name-only'], { cwd: root, encoding: 'utf8' });
if (staged.status !== 0 || staged.stdout.trim() !== target) throw new Error('Staged scope changed; inspect before publishing.');
run('git', ['commit', '--only', '-m', `Update public itinerary ${trip.slug} ${stamp}`, '--', target]);
assertEmptyIndex(root);
run('git', ['push', 'origin', 'main']);
