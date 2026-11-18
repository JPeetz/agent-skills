import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtempSync, readFileSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { cleanEnv } from './transports.mjs';

export const git = (cwd, args, options = {}) => execFileSync('git', args, { cwd, env: cleanEnv(), encoding: options.buffer ? 'buffer' : 'utf8', stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 256 * 1024 * 1024 });

// Worktrees this invocation created. Destructive operations accept only these paths.
const owned = new Map();

export function createWorktree(repo, { baseRef = 'HEAD', root = tmpdir() } = {}) {
  const top = realpathSync(git(repo, ['rev-parse', '--show-toplevel']).trim());
  const parent = mkdtempSync(join(realpathSync(root), 'agent-cli-harness-'));
  const dir = join(parent, 'work');
  const branch = `harness/${basename(parent).replace('agent-cli-harness-', '')}`;
  let branchCreated = false;
  try {
    git(top, ['branch', branch, baseRef]);
    branchCreated = true;
    git(top, ['worktree', 'add', dir, branch]);
    const identity = { branch, head: git(dir, ['rev-parse', 'HEAD']).trim() };
    const workdir = realpathSync(dir);
    owned.set(workdir, identity);
    return { workdir, ...identity };
  } catch (error) {
    // Remove only what this call created: its worktree, branch and temp parent.
    try { git(top, ['worktree', 'remove', '--force', dir]); } catch { /* not registered */ }
    if (branchCreated) try { git(top, ['branch', '-D', branch]); } catch { /* not created */ }
    rmSync(parent, { recursive: true, force: true });
    throw error;
  }
}

// Discard partial edits between fallback attempts, only in a worktree this invocation created.
export function resetOwnedWorktree(workdir) {
  const real = realpathSync(resolve(workdir));
  const identity = owned.get(real);
  if (!identity) throw new Error(`Refusing destructive reset outside a worktree created by this invocation: ${workdir}`);
  const now = { branch: git(real, ['rev-parse', '--abbrev-ref', 'HEAD']).trim(), head: git(real, ['rev-parse', 'HEAD']).trim() };
  if (now.branch !== identity.branch || now.head !== identity.head) throw new Error('Worker changed branch or history; reset refused');
  git(real, ['reset', '--hard', identity.head]);
  git(real, ['clean', '-fdxq']);
}

// Content fingerprint of HEAD, tracked diff, and untracked files.
export function fingerprint(cwd) {
  const hash = createHash('sha256');
  hash.update(git(cwd, ['rev-parse', 'HEAD']));
  hash.update(git(cwd, ['diff', 'HEAD', '--binary'], { buffer: true }));
  const untracked = git(cwd, ['ls-files', '-o', '--exclude-standard', '-z']).split('\0').filter(Boolean).sort();
  for (const path of untracked) { hash.update(path); try { hash.update(readFileSync(join(cwd, path))); } catch { hash.update('unreadable'); } }
  return hash.digest('hex');
}

// Porcelain v1 -z: "XY path\0", and renames/copies add a second "origPath\0" record.
export function changedPaths(cwd) {
  const records = git(cwd, ['status', '--porcelain=v1', '-z']).split('\0');
  const paths = [];
  for (let i = 0; i < records.length; i++) {
    const entry = records[i];
    if (!entry) continue;
    paths.push(entry.slice(3));
    if (/[RC]/.test(entry.slice(0, 2))) paths.push(records[++i]);
  }
  return paths;
}
