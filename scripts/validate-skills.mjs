import { readdir, readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const skillsRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const e of entries) {
    const p = join(dir, e.name);
    if (e.isDirectory()) {
      if (e.name === "node_modules" || e.name === "public" || e.name === "scripts") continue;
      files.push(...(await walk(p)));
    } else if (e.name === "SKILL.md") files.push(p);
  }
  return files;
}

const skillFiles = await walk(skillsRoot);
let ok = true;

for (const file of skillFiles) {
  const text = await readFile(file, "utf8");
  if (!text.includes("name:") || !text.includes("description:")) {
    console.error(`[invalid] ${file}: missing frontmatter name/description`);
    ok = false;
  } else if (!text.includes("tags:")) {
    console.error(`[invalid] ${file}: missing metadata tags field`);
    ok = false;
  } else {
    console.log(`[ok] ${file}`);
  }
}

if (!ok) process.exit(1);
console.log(`Validated ${skillFiles.length} skill(s).`);
