#!/usr/bin/env node
/** 静态导出 Hermes well-known Skill 目录（CDN / GitHub Pages / nginx） */
import { cp, mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const skillsRoot = root;
const outRoot = join(root, "public", ".well-known", "skills");

const SKILL_NAME_RE = /^[a-z0-9][a-z0-9-]*$/;
const SKIP_DIRS = new Set(["node_modules", "public", "scripts", ".git"]);

function parseFrontmatter(text) {
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};
  const out = {};
  for (const line of match[1].split("\n")) {
    const m = line.match(/^([A-Za-z0-9_-]+):\s*(.+)$/);
    if (m) out[m[1]] = m[2].trim();
  }
  return out;
}

async function walkSkillMd(dir) {
  const out = [];
  async function walk(d) {
    for (const e of await readdir(d, { withFileTypes: true })) {
      if (e.isDirectory()) {
        if (SKIP_DIRS.has(e.name)) continue;
        await walk(join(d, e.name));
      } else if (e.name === "SKILL.md") out.push(join(d, e.name));
    }
  }
  await walk(dir);
  return out.sort();
}

async function listFiles(skillDir) {
  const files = [];
  async function walk(d, prefix = "") {
    for (const e of await readdir(d, { withFileTypes: true })) {
      const rel = prefix ? `${prefix}/${e.name}` : e.name;
      if (e.isDirectory()) await walk(join(d, e.name), rel);
      else files.push(rel);
    }
  }
  await walk(skillDir);
  return files.sort();
}

async function readManifest() {
  try {
    const raw = await readFile(join(skillsRoot, "_manifest.yaml"), "utf8");
    const pick = (key) => raw.match(new RegExp(`^${key}:\\s*["']?([^"'\\n]+)["']?`, "m"))?.[1]?.trim();
    return {
      package: pick("package") ?? "vidau-creative-skills",
      version: pick("version") ?? "0.1.0",
      description: pick("description") ?? "VidAU Creative Agent — Hermes Skill 包",
    };
  } catch {
    return {
      package: "vidau-creative-skills",
      version: "0.1.0",
      description: "VidAU Creative Agent — Hermes Skill 包",
    };
  }
}

async function main() {
  const manifest = await readManifest();
  const entries = [];

  for (const skillMd of await walkSkillMd(skillsRoot)) {
    const text = await readFile(skillMd, "utf8");
    const fm = parseFrontmatter(text);
    const name = fm.name?.trim();
    const description = fm.description?.trim();
    if (!name || !description) continue;
    if (!SKILL_NAME_RE.test(name)) throw new Error(`Invalid skill name: ${name}`);

    const skillDir = resolve(skillMd, "..");
    const files = await listFiles(skillDir);
    entries.push({ name, description, files, skillDir });
  }

  entries.sort((a, b) => a.name.localeCompare(b.name));
  await mkdir(outRoot, { recursive: true });

  await writeFile(
    join(outRoot, "index.json"),
    `${JSON.stringify({ ...manifest, skills: entries.map(({ name, description, files }) => ({ name, description, files })) }, null, 2)}\n`
  );

  for (const skill of entries) {
    const destDir = join(outRoot, skill.name);
    await mkdir(destDir, { recursive: true });
    for (const rel of skill.files) {
      const src = join(skill.skillDir, rel);
      const dest = join(destDir, rel);
      await mkdir(dirname(dest), { recursive: true });
      await cp(src, dest);
    }
  }

  console.info(`[skills:build] ${entries.length} skill(s) → ${outRoot}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
