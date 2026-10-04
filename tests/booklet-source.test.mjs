import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';

const root = path.resolve(import.meta.dirname, '..');
// Reuse the maintained schema fixture without copying another schema example.
const fixture = fs.readFileSync(path.join(root, 'tests/parser.test.mjs'), 'utf8').match(/const fixture = `([\s\S]*?)`;/)[1];

test('booklet export works for a new trip without website data or cover assets', (t) => {
  const slug = `booklet-independent-test-${randomUUID()}`;
  const temporary = path.join(root, 'booklet/tmp', slug);
  assert.equal(fs.existsSync(temporary), false);
  fs.mkdirSync(temporary, { recursive: true });
  const sourceDirectory = fs.mkdtempSync(path.join(os.tmpdir(), 'travel-booklet-source-'));
  t.after(() => {
    fs.rmSync(temporary, { recursive: true, force: true });
    fs.rmSync(sourceDirectory, { recursive: true, force: true });
  });
  const note = path.join(sourceDirectory, 'source.md');
  fs.writeFileSync(note, fixture.replace('trip_slug: test-trip', `trip_slug: ${slug}`));
  const data = path.join(root, 'src/data/trips', `${slug}.json`);
  assert.equal(fs.existsSync(data), false);
  assert.equal(fs.existsSync(path.join(root, 'public/test-cover.png')), false);
  const result = spawnSync(process.execPath, ['booklet/export-source.mjs', '--note', note], { cwd: root, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  const publicData = fs.readFileSync(path.join(temporary, 'trip.json'), 'utf8');
  assert.equal(JSON.parse(publicData).slug, slug);
  assert.equal(publicData.includes('AB12345678'), false);
  assert.equal(fs.existsSync(data), false, 'Booklet export must not create website JSON');

  const verify = () => spawnSync(process.execPath, ['booklet/export-source.mjs', '--note', note, '--verify'], { cwd: root, encoding: 'utf8' });
  assert.notEqual(verify().status, 0, 'Cannot certify privacy before extracting PDFs');
  const payload = { sourceHash: JSON.parse(publicData).sourceHash, artifacts: [{ text: '公開手冊', links: [] }] };
  fs.writeFileSync(path.join(temporary, 'book-privacy.json'), JSON.stringify(payload));
  assert.equal(verify().status, 0);
  payload.artifacts[0].links = ['https://example.invalid/?auth=hidden'];
  fs.writeFileSync(path.join(temporary, 'book-privacy.json'), JSON.stringify(payload));
  assert.notEqual(verify().status, 0, 'Secret URL annotation must be caught');
  payload.artifacts[0] = { text: 'AB12345678' };
  fs.writeFileSync(path.join(temporary, 'book-privacy.json'), JSON.stringify(payload));
  assert.notEqual(verify().status, 0, 'Source private fingerprint must be caught');
  payload.artifacts[0] = { text: '公開手冊' };
  payload.sourceHash = 'stale';
  fs.writeFileSync(path.join(temporary, 'book-privacy.json'), JSON.stringify(payload));
  assert.notEqual(verify().status, 0, 'Stale PDF source must be caught');
});
