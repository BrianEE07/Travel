import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { assertNotePublishSafe, noteDataPath } from '../scripts/lib/publish-safety.mjs';
import { publicScanAllowances } from '../scripts/lib/public-source.mjs';

function repository(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'travel-publish-test-'));
  const git = (...args) => {
    const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
  };
  git('init', '-b', 'main');
  git('config', 'user.name', 'Test');
  git('config', 'user.email', 'test@example.invalid');
  fs.writeFileSync(path.join(root, 'base.txt'), 'base');
  git('add', 'base.txt');
  git('commit', '-m', 'base');
  git('update-ref', 'refs/remotes/origin/main', 'HEAD');
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return { root, git };
}

test('note publisher preserves unstaged work but refuses staged work', (t) => {
  const { root, git } = repository(t);
  fs.writeFileSync(path.join(root, 'base.txt'), 'user edit');
  assert.doesNotThrow(() => assertNotePublishSafe(root));
  git('add', 'base.txt');
  assert.throws(() => assertNotePublishSafe(root), /staged changes/);
  assert.equal(fs.readFileSync(path.join(root, 'base.txt'), 'utf8'), 'user edit');
});

test('note publisher refuses unpublished commits and other branches', (t) => {
  const { root, git } = repository(t);
  git('commit', '--allow-empty', '-m', 'unrelated unpublished work');
  assert.throws(() => assertNotePublishSafe(root), /unpublished commits/);
  git('switch', '-c', 'another-trip');
  assert.throws(() => assertNotePublishSafe(root), /branch main/);
});

test('note publisher restricts target to exactly one safe slug path', () => {
  assert.equal(noteDataPath('kyoto-2027'), 'src/data/trips/kyoto-2027.json');
  for (const value of ['../other', 'x/y', 'a..b', '', '-bad']) assert.throws(() => noteDataPath(value));
});

test('public scan allowances do not admit arbitrary entity fields', () => {
  const allowances = publicScanAllowances([{ entities: [
    { type: 'stay', price: { text: 'JPY 100' }, image: { url: 'https://example.invalid/a.jpg' } },
    { type: 'transport', segments: [{ price: { text: 'JPY 200' } }, {}] },
    { type: 'food', price: { text: 'JPY 999' } },
  ] }]);
  assert.deepEqual(allowances.prices, ['JPY 100', 'JPY 200']);
  assert.deepEqual(allowances.images, ['https://example.invalid/a.jpg']);
});
