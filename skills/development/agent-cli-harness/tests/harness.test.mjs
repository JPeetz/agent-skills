import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { chmodSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const scripts = join(fileURLToPath(new URL('.', import.meta.url)), '..', 'scripts');
const harness = join(scripts, 'harness.mjs');
const sh = (cwd, ...args) => execFileSync('git', args, { cwd, encoding: 'utf8' }).trim();

function fixture() {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'harness-test-')));
  const repo = join(root, 'repo');
  mkdirSync(repo);
  sh(repo, 'init', '-q');
  sh(repo, 'config', 'user.email', 't@example.invalid');
  sh(repo, 'config', 'user.name', 't');
  writeFileSync(join(repo, 'a.txt'), 'a\n');
  sh(repo, 'add', '.');
  sh(repo, 'commit', '-qm', 'init');
  const bin = join(root, 'bin');
  mkdirSync(bin);
  return { root, repo, bin };
}

function fake(bin, name, body) {
  writeFileSync(join(bin, name), `#!/usr/bin/env node\n${body}`);
  chmodSync(join(bin, name), 0o755);
}

function run(f, lanes, env = {}) {
  const config = join(f.root, 'lanes.json');
  writeFileSync(config, JSON.stringify({ lanes }));
  const result = spawnSync(process.execPath, [harness, f.repo, config], { encoding: 'utf8', env: { ...process.env, ...env, PATH: `${f.bin}:${process.env.PATH}` } });
  return { ...result, receipt: result.stdout ? JSON.parse(result.stdout) : null };
}

const codexMessage = text => `console.log(JSON.stringify({type:'item.completed',item:{type:'agent_message',text:${JSON.stringify(text)}}}));console.log(JSON.stringify({type:'turn.completed'}));`;
const lane = (mode, candidates, extra = {}) => ({ name: 'lane', mode, prompt: 'Do the task.', timeoutMs: 20000, candidates, ...extra });

test('strips inherited Git environment at startup', () => {
  const f = fixture();
  fake(f.bin, 'codex', codexMessage('x').replace('x', '') + `console.error(JSON.stringify(Object.keys(process.env).filter(k => k.startsWith('GIT_'))));`);
  const poisoned = { GIT_DIR: join(f.root, 'nowhere'), GIT_WORK_TREE: f.root, GIT_COMMON_DIR: f.root, GIT_INDEX_FILE: join(f.root, 'idx'), GIT_OBJECT_DIRECTORY: f.root, GIT_ALTERNATE_OBJECT_DIRECTORIES: f.root };
  const r = run(f, [lane('read', [{ transport: 'codex' }])], poisoned);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.receipt.lanes[0].attempts[0].stderr.trim(), '[]');
});

test('read mode builds advisory flags without auto-approval options', async () => {
  const { commandFor } = await import(join(scripts, 'transports.mjs'));
  for (const transport of ['codex', 'claude', 'omp']) {
    const [, args] = commandFor({ transport, model: 'm' }, 'read', 'prompt');
    const text = args.join(' ');
    assert.doesNotMatch(text, /yolo|auto-approve|dangerously|bypass|acceptEdits|approval-mode/i, transport);
  }
  assert.ok(commandFor({ transport: 'codex' }, 'read', 'p')[1].includes('read-only'));
  assert.ok(commandFor({ transport: 'claude' }, 'read', 'p')[1].includes('--restricted'));
  assert.ok(commandFor({ transport: 'omp' }, 'read', 'p')[1].includes('--tools=read,grep,glob'));
  assert.doesNotMatch(commandFor({ transport: 'codex' }, 'write', 'p')[1].join(' '), /dangerously|yolo/);
});

test('refuses transports without an enforced read-only mode', async () => {
  const { commandFor } = await import(join(scripts, 'transports.mjs'));
  for (const transport of ['opencode', 'unknown']) assert.throws(() => commandFor({ transport }, 'read', 'p'), /no enforced read-only mode or is unsupported/);
  const f = fixture();
  const r = run(f, [lane('read', [{ transport: 'opencode' }])]);
  assert.equal(r.status, 1);
  assert.match(r.receipt.lanes[0].error, /unsupported/);
});

test('assistant prose mentioning quota does not trigger fallback', () => {
  const f = fixture();
  fake(f.bin, 'codex', codexMessage('The code mishandles a 429 rate limit and quota exceeded response.'));
  fake(f.bin, 'omp', `console.log('should not run');`);
  const r = run(f, [lane('read', [{ transport: 'codex' }, { transport: 'omp' }])]);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.receipt.lanes[0].attempts.length, 1);
  assert.match(r.receipt.lanes[0].attempts[0].text, /quota/);
});

test('structured quota error falls back to the next candidate', () => {
  const f = fixture();
  fake(f.bin, 'codex', `console.log(JSON.stringify({type:'turn.failed',error:{message:'429 rate limit reached'}}));`);
  fake(f.bin, 'omp', `console.log(JSON.stringify({type:'message_end',message:{role:'assistant',content:[{type:'text',text:'fallback ok'}]}}));`);
  const r = run(f, [lane('read', [{ transport: 'codex' }, { transport: 'omp' }])]);
  assert.equal(r.status, 0, r.stderr);
  assert.deepEqual(r.receipt.lanes[0].attempts.map(a => a.transport), ['codex', 'omp']);
  assert.equal(r.receipt.lanes[0].attempts[1].text, 'fallback ok');
});

test('non-zero exit stderr quota falls back; auth failure does not', () => {
  const quota = fixture();
  fake(quota.bin, 'codex', `console.error('Error: usage limit reached');process.exit(1);`);
  fake(quota.bin, 'omp', `console.log(JSON.stringify({type:'message_end',message:{role:'assistant',content:[{type:'text',text:'ok'}]}}));`);
  assert.equal(run(quota, [lane('read', [{ transport: 'codex' }, { transport: 'omp' }])]).receipt.lanes[0].attempts.length, 2);
  const auth = fixture();
  fake(auth.bin, 'codex', `console.error('401 unauthorized');process.exit(1);`);
  fake(auth.bin, 'omp', `console.log('{}');`);
  assert.equal(run(auth, [lane('read', [{ transport: 'codex' }, { transport: 'omp' }])]).receipt.lanes[0].attempts.length, 1);
});

test('destructive reset runs only in worktrees this invocation created', async () => {
  const f = fixture();
  const git = await import(join(scripts, 'git.mjs'));
  writeFileSync(join(f.repo, 'keep.txt'), 'caller work');
  assert.throws(() => git.resetOwnedWorktree(f.repo), /Refusing destructive reset/);
  assert.equal(readFileSync(join(f.repo, 'keep.txt'), 'utf8'), 'caller work');
  const foreign = join(f.root, 'foreign');
  sh(f.repo, 'worktree', 'add', '-q', '-b', 'foreign', foreign);
  writeFileSync(join(foreign, 'keep.txt'), 'foreign work');
  assert.throws(() => git.resetOwnedWorktree(foreign), /Refusing destructive reset/);
  assert.equal(readFileSync(join(foreign, 'keep.txt'), 'utf8'), 'foreign work');
  const created = git.createWorktree(f.repo, { root: f.root });
  writeFileSync(join(created.workdir, 'junk.txt'), 'x');
  writeFileSync(join(created.workdir, 'a.txt'), 'changed');
  git.resetOwnedWorktree(created.workdir);
  assert.equal(readFileSync(join(created.workdir, 'a.txt'), 'utf8'), 'a\n');
  assert.throws(() => readFileSync(join(created.workdir, 'junk.txt')));
});

test('write fallback resets partial edits in its own worktree and spares the caller tree', () => {
  const f = fixture();
  writeFileSync(join(f.repo, 'dirty.txt'), 'uncommitted caller edit');
  fake(f.bin, 'codex', `import('node:fs').then(fs => { fs.writeFileSync('partial.txt','x'); console.log(JSON.stringify({type:'turn.failed',error:'429 quota'})); });`);
  fake(f.bin, 'omp', `import('node:fs').then(fs => { console.log(JSON.stringify({type:'message_end',message:{role:'assistant',content:[{type:'text',text:String(fs.existsSync('partial.txt'))}]}})); });`);
  const r = run(f, [lane('write', [{ transport: 'codex' }, { transport: 'omp' }])]);
  assert.equal(r.status, 0, r.stderr);
  const [first, second] = r.receipt.lanes[0].attempts;
  assert.deepEqual(first.changedPaths, ['partial.txt']);
  assert.equal(second.text, 'false');
  assert.equal(readFileSync(join(f.repo, 'dirty.txt'), 'utf8'), 'uncommitted caller edit');
  assert.match(r.receipt.lanes[0].worktree.branch, /^harness\//);
});

test('read lane fails when the worker modifies the tree', () => {
  const f = fixture();
  fake(f.bin, 'codex', `require('node:fs').writeFileSync('${join(f.repo, 'a.txt')}','tampered');` + codexMessage('done'));
  const r = run(f, [lane('read', [{ transport: 'codex' }])]);
  assert.equal(r.status, 1);
  assert.equal(r.receipt.lanes[0].attempts[0].ok, false);
});

test('OMP option-like and file-like prompts remain literal tasks', async () => {
  const { commandFor, runProcess } = await import(join(scripts, 'transports.mjs'));
  const f = fixture();
  fake(f.bin, 'omp', `let s='';process.stdin.on('data',c=>s+=c);process.stdin.on('end',()=>console.log(JSON.stringify({args:process.argv.slice(2),stdin:s})));`);
  for (const prompt of ['--help', '--auto-approve', '@/etc/hosts']) {
    const [, args, input] = commandFor({ transport: 'omp' }, 'read', prompt);
    const result = await runProcess(join(f.bin, 'omp'), args, f.repo, 5000, input);
    const record = JSON.parse(result.stdout);
    const task = record.args.at(-1);
    assert.ok(task.endsWith(prompt), 'prompt text arrives unchanged');
    assert.match(task, /^[^-@]/, 'positional never starts like an option or @file');
    assert.deepEqual(record.args.slice(0, -1).filter(a => a.includes(prompt)), []);
  }
});

test('all GIT_ variables are absent from worker and harness Git calls', () => {
  const f = fixture();
  const gitPath = execFileSync('which', ['git'], { encoding: 'utf8' }).trim();
  const log = join(f.root, 'git-env.log');
  fake(f.bin, 'git', `const fs=require('node:fs'), cp=require('node:child_process');fs.appendFileSync(${JSON.stringify(log)},JSON.stringify(Object.keys(process.env).filter(k=>k.startsWith('GIT_')))+'\\n');const r=cp.spawnSync(${JSON.stringify(gitPath)},process.argv.slice(2),{stdio:'inherit'});process.exit(r.status??1);`);
  fake(f.bin, 'codex', `console.error(JSON.stringify(Object.keys(process.env).filter(k=>k.startsWith('GIT_'))));` + codexMessage('ok'));
  const env = { GIT_CONFIG_COUNT: '1', GIT_CONFIG_KEY_0: 'core.bare', GIT_CONFIG_VALUE_0: 'false', GIT_NAMESPACE: 'test', GIT_SSH_COMMAND: 'false' };
  const r = run(f, [lane('read', [{ transport: 'codex' }])], env);
  assert.equal(r.status, 0, r.stderr);
  assert.deepEqual(JSON.parse(r.receipt.lanes[0].attempts[0].stderr), []);
  for (const line of readFileSync(log, 'utf8').trim().split('\n')) assert.deepEqual(JSON.parse(line), []);
});

test('failed write receipt retains worktree path, branch and attempts', () => {
  const f = fixture();
  fake(f.bin, 'codex', `require('node:fs').unlinkSync('.git');` + codexMessage('done'));
  const r = run(f, [lane('write', [{ transport: 'codex' }])]);
  assert.equal(r.status, 1);
  const receipt = r.receipt.lanes[0];
  assert.ok(receipt.worktree.workdir);
  assert.match(receipt.worktree.branch, /^harness\//);
  assert.equal(receipt.attempts.length, 1);
  assert.ok(receipt.error);
});

test('a failed createWorktree leaves no temp directory, worktree or branch', async () => {
  const f = fixture();
  const { createWorktree } = await import(join(scripts, 'git.mjs'));
  const root = join(f.root, 'empty'); mkdirSync(root);
  assert.throws(() => createWorktree(f.repo, { root, baseRef: 'no-such-ref' }));
  assert.deepEqual(readdirSync(root), []);
  assert.equal(sh(f.repo, 'branch', '--list', 'harness/*'), '');
  assert.equal(sh(f.repo, 'worktree', 'list', '--porcelain').split('\n').filter(l => l.startsWith('worktree ')).length, 1);
});

test('changedPaths reports both names of staged renames including spaces', async () => {
  const f = fixture();
  writeFileSync(join(f.repo, 'x'), 'short');
  writeFileSync(join(f.repo, 'old name'), 'spaces');
  sh(f.repo, 'add', '.'); sh(f.repo, 'commit', '-qm', 'files');
  sh(f.repo, 'mv', 'x', 'y'); sh(f.repo, 'mv', 'old name', 'new name');
  const { changedPaths } = await import(join(scripts, 'git.mjs'));
  assert.deepEqual(changedPaths(f.repo).sort(), ['new name', 'old name', 'x', 'y']);
});

test('creation failure after branch creation removes the owned branch and temp directory', () => {
  const f = fixture();
  const gitPath = execFileSync('which', ['git'], { encoding: 'utf8' }).trim();
  fake(f.bin, 'git', `const cp=require('node:child_process');const a=process.argv.slice(2);if(a[0]==='worktree'&&a[1]==='add')process.exit(1);const r=cp.spawnSync(${JSON.stringify(gitPath)},a,{stdio:'inherit'});process.exit(r.status??1);`);
  const root = join(f.root, 'empty'); mkdirSync(root);
  const script = `import {createWorktree} from ${JSON.stringify(new URL('../scripts/git.mjs', import.meta.url).href)};try { createWorktree(${JSON.stringify(f.repo)},{root:${JSON.stringify(root)}});process.exit(2) } catch {}`;
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', script], { encoding: 'utf8', env: { ...process.env, PATH: `${f.bin}:${process.env.PATH}` } });
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(readdirSync(root), []);
  assert.equal(sh(f.repo, 'branch', '--list', 'harness/*'), '');
});
