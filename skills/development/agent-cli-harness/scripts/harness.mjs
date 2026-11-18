#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createWorktree, resetOwnedWorktree, fingerprint, changedPaths, git } from './git.mjs';
import { commandFor, runProcess, parseOutput, classify, granola, stripGitEnv } from './transports.mjs';

stripGitEnv();

export async function runLane(lane, repo) {
  if (!lane.name || !['read', 'write'].includes(lane.mode) || !Array.isArray(lane.candidates) || !lane.candidates.length) throw new Error('Lane requires name, read/write mode, and candidates');
  if (typeof lane.prompt !== 'string' || !lane.prompt.trim()) throw new Error('Lane prompt required');
  const timeoutMs = lane.timeoutMs ?? 300000;
  if (!Number.isInteger(timeoutMs) || timeoutMs < 1000 || timeoutMs > 3600000) throw new Error('timeoutMs must be 1000–3600000');
  // Validate every candidate before creating a worktree or making a request.
  for (const candidate of lane.candidates) {
    if (candidate.transport === 'granola') {
      if (lane.mode !== 'read' || !lane.evidenceFile) throw new Error('Granola requires read mode and evidenceFile');
    } else commandFor(candidate, lane.mode, lane.prompt);
  }
  const worktree = lane.mode === 'write' ? createWorktree(repo) : null;
  const workdir = worktree?.workdir || repo;
  const attempts = [];
  // After the worktree exists, any failure still returns its identity and the attempts so far.
  try {
    for (const [index, candidate] of lane.candidates.entries()) {
      if (worktree && index > 0) resetOwnedWorktree(workdir);
      const before = fingerprint(workdir);
      const started = Date.now();
      let result;
      if (candidate.transport === 'granola') result = await granola(candidate, resolve(lane.evidenceFile), timeoutMs, lane.prompt);
      else {
        const [command, args, input] = commandFor(candidate, lane.mode, lane.prompt);
        const { stdout, ...processResult } = await runProcess(command, args, workdir, timeoutMs, input);
        result = { ...processResult, ...parseOutput(candidate.transport, stdout) };
      }
      const attempt = { transport: candidate.transport, model: candidate.model || 'default', before, durationMs: Date.now() - started, ok: false, ...result };
      attempts.push(attempt);
      const after = fingerprint(workdir);
      const identityChanged = Boolean(worktree) && (git(workdir, ['rev-parse', 'HEAD']).trim() !== worktree.head || git(workdir, ['rev-parse', '--abbrev-ref', 'HEAD']).trim() !== worktree.branch);
      const ok = result.exitCode === 0 && !result.timedOut && !result.errors.length && !identityChanged && (lane.mode !== 'read' || before === after);
      Object.assign(attempt, { after, changedPaths: changedPaths(workdir), ok });
      if (ok || identityChanged || (lane.mode === 'read' && before !== after) || !classify(result)) break;
    }
  } catch (error) {
    return { name: lane.name, mode: lane.mode, worktree, ok: false, error: error.message, attempts };
  }
  return { name: lane.name, mode: lane.mode, worktree, ok: attempts.at(-1).ok, attempts };
}

export async function main(args) {
  if (args.length !== 2) throw new Error('Usage: node harness.mjs <repository> <lanes.json>');
  const repo = resolve(args[0]);
  const config = JSON.parse(await readFile(args[1], 'utf8'));
  if (!Array.isArray(config.lanes) || !config.lanes.length) throw new Error('Config requires a nonempty lanes array');
  const results = await Promise.all(config.lanes.map(async lane => {
    try { return await runLane(lane, repo); } catch (error) { return { name: lane.name, ok: false, error: error.message }; }
  }));
  console.log(JSON.stringify({ lanes: results }, null, 2));
  return results.every(result => result.ok) ? 0 : 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try { process.exitCode = await main(process.argv.slice(2)); } catch (error) { console.error(error.message); process.exitCode = 1; }
}
