import { spawnSync } from 'node:child_process';

function git(root, args) {
  const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
  if (result.status !== 0) throw new Error(`Cannot verify Git state: git ${args.join(' ')}`);
  return result.stdout.trim();
}

export function assertEmptyIndex(root) {
  if (git(root, ['diff', '--cached', '--name-only'])) {
    throw new Error('Publish refused: staged changes already exist. Preserve them; publish only an explicitly reviewed scope.');
  }
}

export function assertNotePublishSafe(root) {
  assertEmptyIndex(root);
  if (git(root, ['branch', '--show-current']) !== 'main') {
    throw new Error('Publish refused: note-only auto-publish requires branch main.');
  }
  const ahead = Number(git(root, ['rev-list', '--count', 'origin/main..HEAD']));
  if (ahead !== 0) throw new Error('Publish refused: existing unpublished commits would also be pushed. Review them explicitly.');
}

export function noteDataPath(slug) {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) throw new Error('Invalid trip slug');
  return `src/data/trips/${slug}.json`;
}
