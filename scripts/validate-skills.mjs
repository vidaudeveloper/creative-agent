import { readdir, readFile } from "node:fs/promises";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Hermes system-prompt skill index truncates each description to 60 chars
 * (see hermes-agent/agent/skill_utils.py extract_skill_description).
 * Descriptions longer than 60 lose routing signal → poor skill hit rate.
 */
const HERMES_INDEX_DESC_MAX = 60;

const skillsRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const e of entries) {
    const p = join(dir, e.name);
    if (e.isDirectory()) {
      if (
        e.name === "node_modules" ||
        e.name === "public" ||
        e.name === "scripts" ||
        e.name === "tools" ||
        e.name === ".venv" ||
        e.name === "vendor"
      ) {
        continue;
      }
      files.push(...(await walk(p)));
    } else if (e.name === "SKILL.md") {
      files.push(p);
    }
  }
  return files;
}

function parseFrontmatter(text) {
  if (!text.startsWith("---")) return null;
  const end = text.indexOf("\n---", 3);
  if (end < 0) return null;
  const block = text.slice(3, end);
  const out = {};
  let key = null;
  let buf = [];
  const flush = () => {
    if (!key) return;
    let v = buf.join("\n").trim();
    if (v.startsWith(">-") || v.startsWith(">|") || v.startsWith(">") || v.startsWith("|")) {
      v = v.replace(/^>[|-]?\s*/, "").trim();
    }
    out[key] = v.replace(/^["']|["']$/g, "");
    key = null;
    buf = [];
  };
  for (const line of block.split("\n")) {
    const m = line.match(/^([A-Za-z0-9_]+):\s*(.*)$/);
    if (m && !line.startsWith(" ") && !line.startsWith("\t")) {
      flush();
      key = m[1];
      buf = [m[2] ?? ""];
    } else if (key) {
      buf.push(line);
    }
  }
  flush();
  return out;
}

const skillFiles = await walk(skillsRoot);
let ok = true;

for (const file of skillFiles) {
  const rel = relative(skillsRoot, file);
  const text = await readFile(file, "utf8");
  const fm = parseFrontmatter(text);

  if (!fm?.name || !fm?.description) {
    console.error(`[invalid] ${rel}: missing frontmatter name/description`);
    ok = false;
    continue;
  }

  if (!text.includes("tags:")) {
    console.error(`[invalid] ${rel}: missing metadata tags field`);
    ok = false;
  }

  const desc = String(fm.description).replace(/\s+/g, " ").trim();
  if (desc.length > HERMES_INDEX_DESC_MAX) {
    console.error(
      `[invalid] ${rel}: description ${desc.length} chars > Hermes index max ${HERMES_INDEX_DESC_MAX}`
    );
    console.error(`  shown as: "${desc.slice(0, 57)}..."`);
    console.error(`  full:     "${desc}"`);
    ok = false;
  }

  if (!/^Use (when|BEFORE|after|to)\b/i.test(desc)) {
    console.error(
      `[warn] ${rel}: description should start with "Use when/BEFORE/after/to" for Hermes routing`
    );
  }

  if (desc.length <= HERMES_INDEX_DESC_MAX && fm?.name && text.includes("tags:")) {
    console.log(`[ok] ${rel} (${desc.length}c) — ${desc}`);
  }
}

if (!ok) process.exit(1);
console.log(`Validated ${skillFiles.length} skill(s). Hermes index window = ${HERMES_INDEX_DESC_MAX} chars.`);
