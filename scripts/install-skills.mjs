#!/usr/bin/env node
/**
 * Batch-install all Creative Agent skills.
 *
 * Local mode (default): copy skill dirs from this repo into ~/.hermes/skills/.
 *   No raw.githubusercontent.com requests — avoids GitHub CDN 429 rate limits.
 *
 * Remote mode (--remote): install via GitHub identifier (Contents API).
 * From-GitHub mode (--from-github): fetch _manifest.yaml via GitHub API (no clone, no raw CDN).
 *
 * After skills install, also installs the local Jianying draft compiler
 * (`tools/jianying-draft-compiler` → `jy-compile`) unless `--skip-compiler`.
 *
 * Usage:
 *   pnpm skills:install
 *   node scripts/install-skills.mjs --force
 *   node scripts/install-skills.mjs --remote --force
 *   node scripts/install-skills.mjs --from-github --remote --force
 *   node scripts/install-skills.mjs --skip-compiler
 */
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { cp, mkdir, readFile, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

const repo = (process.env.SKILLS_GITHUB_REPO ?? "vidaudeveloper/creative-agent").replace(
  /\/+$/,
  ""
);
const category = process.env.SKILLS_INSTALL_CATEGORY ?? "vidau-creative";
const force = process.argv.includes("--force") || process.env.SKILLS_INSTALL_FORCE === "1";
const remote = process.argv.includes("--remote") || process.env.SKILLS_INSTALL_REMOTE === "1";
const fromGithub =
  process.argv.includes("--from-github") || process.env.SKILLS_INSTALL_FROM_GITHUB === "1";
const skipCompiler =
  process.argv.includes("--skip-compiler") || process.env.SKILLS_INSTALL_SKIP_COMPILER === "1";
const cli = process.env.SKILLS_CLI?.trim() || "hermes";
const hermesHome = process.env.HERMES_HOME?.trim() || join(homedir(), ".hermes");

async function parseManifestFromRaw(raw) {
  const skills = [];
  let current = null;

  for (const line of raw.split("\n")) {
    const idMatch = line.match(/^\s+-\s+id:\s+(\S+)/);
    const pathMatch = line.match(/^\s+path:\s+(\S+)/);
    if (idMatch) {
      current = { id: idMatch[1] };
      skills.push(current);
    } else if (pathMatch && current && !current.path) {
      current.path = pathMatch[1];
    }
  }

  return skills.filter((s) => s.id && s.path);
}

async function parseManifest() {
  const raw = await readFile(join(repoRoot, "_manifest.yaml"), "utf8");
  return parseManifestFromRaw(raw);
}

async function fetchManifestFromGitHub() {
  const branch = process.env.SKILLS_GITHUB_BRANCH ?? "main";
  const url = `https://api.github.com/repos/${repo}/contents/_manifest.yaml?ref=${branch}`;
  const resp = await fetch(url, {
    headers: {
      Accept: "application/vnd.github+json",
      "User-Agent": "creative-agent-skill-install",
      ...(process.env.GITHUB_TOKEN ? { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` } : {}),
    },
  });
  if (!resp.ok) {
    throw new Error(`GitHub API returned ${resp.status} for _manifest.yaml`);
  }
  const data = await resp.json();
  const raw = Buffer.from(data.content, "base64").toString("utf8");
  return parseManifestFromRaw(raw);
}

async function installLocal(skill) {
  const src = join(repoRoot, skill.path);
  const dest = join(hermesHome, "skills", category, skill.id);
  await rm(dest, { recursive: true, force: true });
  await mkdir(dirname(dest), { recursive: true });
  await cp(src, dest, { recursive: true });
}

function installRemote(skill) {
  const identifier = `${repo}/${skill.path}`;
  const args = ["skills", "install", identifier, "--yes", "--category", category];
  if (force) args.push("--force");
  return spawnSync(cli, args, { stdio: "inherit", encoding: "utf8" });
}

/**
 * Install jy-compile from tools/ in this checkout, or git-clone the skill repo.
 * Avoids raw.githubusercontent.com (CDN 429).
 */
function installCompiler() {
  const localInstall = join(repoRoot, "tools", "install-jy-compile.sh");
  const localCompiler = join(
    repoRoot,
    "tools",
    "jianying-draft-compiler",
    "scripts",
    "install_local.sh"
  );

  console.info("\n[skills:install] installing jianying-draft-compiler (jy-compile)…");

  let script = null;
  if (existsSync(localInstall)) {
    script = localInstall;
  } else if (existsSync(localCompiler)) {
    script = localCompiler;
  }

  if (script) {
    const r = spawnSync("bash", [script], {
      stdio: "inherit",
      encoding: "utf8",
      env: { ...process.env },
    });
    if (r.status !== 0) {
      console.error(`[skills:install] compiler install failed (exit ${r.status})`);
      console.error("  Fix: install uv (https://docs.astral.sh/uv/) then re-run, or:");
      console.error("  bash tools/install-jy-compile.sh");
      return false;
    }
  } else {
    // No tools/ in this checkout (e.g. --from-github only fetched manifest) → clone monorepo
    const branch = process.env.SKILLS_GITHUB_BRANCH ?? process.env.VIDAU_JY_COMPILER_REF ?? "main";
    const repoUrl = process.env.VIDAU_JY_COMPILER_REPO ?? `https://github.com/${repo}.git`;
    const cache = join(homedir(), ".vidau", "cache", "creative-agent");
    console.info(`[skills:install] tools/ missing locally; cloning ${repoUrl} (${branch})…`);
    const clone = spawnSync(
      "bash",
      [
        "-lc",
        [
          `mkdir -p "$(dirname '${cache}')"`,
          `if [ -d '${cache}/.git' ]; then git -C '${cache}' fetch --depth 1 origin '${branch}' && (git -C '${cache}' checkout -q '${branch}' 2>/dev/null || git -C '${cache}' checkout -q FETCH_HEAD); git -C '${cache}' pull --ff-only origin '${branch}' 2>/dev/null || true;`,
          `else rm -rf '${cache}' && git clone --depth 1 --branch '${branch}' '${repoUrl}' '${cache}'; fi`,
          `bash '${cache}/tools/jianying-draft-compiler/scripts/install_local.sh'`,
        ].join(" "),
      ],
      { stdio: "inherit", encoding: "utf8", env: { ...process.env } }
    );
    if (clone.status !== 0) {
      console.error(`[skills:install] compiler install via git failed (exit ${clone.status})`);
      return false;
    }
  }

  console.info('[skills:install] compiler OK — add to shell: export PATH="$HOME/.vidau/bin:$PATH"');
  return true;
}

async function main() {
  const skills = fromGithub ? await fetchManifestFromGitHub() : await parseManifest();
  const mode = fromGithub
    ? "GitHub API manifest + remote install"
    : remote
      ? "remote (GitHub API)"
      : "local copy";
  console.info(`[skills:install] ${mode}: ${skills.length} skill(s) → ${hermesHome}/skills/${category}/\n`);

  let failed = 0;
  const useRemote = remote || fromGithub;
  for (const skill of skills) {
    console.info(`→ ${skill.id}`);
    if (useRemote) {
      const r = installRemote(skill);
      if (r.status !== 0) {
        console.error(`✗ ${skill.id} failed (exit ${r.status})`);
        failed += 1;
      } else {
        console.info(`✓ ${skill.id}\n`);
      }
    } else {
      try {
        await installLocal(skill);
        console.info(`✓ ${skill.id}\n`);
      } catch (err) {
        console.error(`✗ ${skill.id}: ${err.message}`);
        failed += 1;
      }
    }
  }

  if (failed) {
    console.error(`[skills:install] done with ${failed} failure(s)`);
    process.exit(1);
  }

  // Category blurb for Hermes system-prompt skill index (DESCRIPTION.md)
  const catDescSrc = join(repoRoot, "DESCRIPTION.md");
  const catDescDest = join(hermesHome, "skills", category, "DESCRIPTION.md");
  if (existsSync(catDescSrc)) {
    await mkdir(dirname(catDescDest), { recursive: true });
    await cp(catDescSrc, catDescDest);
    console.info(`[skills:install] ✓ ${category}/DESCRIPTION.md`);
  }

  console.info("[skills:install] all skills installed");

  if (!skipCompiler) {
    const ok = installCompiler();
    if (!ok) {
      console.error(
        "[skills:install] skills are installed, but jy-compile failed — jianying-remix will not work until compiler is fixed."
      );
      process.exit(1);
    }
  } else {
    console.info("[skills:install] skipped compiler (--skip-compiler)");
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
