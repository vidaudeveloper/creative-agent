#!/usr/bin/env node
/**
 * 从 well-known 端点批量安装全部 Skill 到 Hermes
 *
 * 用法:
 *   pnpm skills:install
 *   SKILLS_BASE_URL=https://creative.vidau.info pnpm skills:install
 */
import { spawnSync } from "node:child_process";

const base = (process.env.SKILLS_BASE_URL ?? "https://creative.vidau.info").replace(/\/$/, "");
const indexUrl = `${base}/.well-known/skills/index.json`;
const force = process.argv.includes("--force") || process.env.SKILLS_INSTALL_FORCE === "1";

async function main() {
  const res = await fetch(indexUrl);
  if (!res.ok) {
    console.error(`[skills:install] 无法读取 ${indexUrl} (${res.status})`);
    process.exit(1);
  }

  const data = await res.json();
  const skills = Array.isArray(data.skills) ? data.skills : [];
  if (!skills.length) {
    console.error("[skills:install] index.json 里没有 skill");
    process.exit(1);
  }

  const order = [
    "creative-platform",
    "creative-job-runner",
    "creative-direct",
    "creative-script2film",
    "creative-script2film-keyframes",
    "creative-batch-orchestrator",
    "trend-viral-short",
    "product-url-to-video",
  ];
  const byName = new Map(skills.map((s) => [s.name, s]));
  const sorted = [
    ...order.filter((n) => byName.has(n)).map((n) => byName.get(n)),
    ...skills.filter((s) => !order.includes(s.name)),
  ];

  console.info(`[skills:install] 从 ${base} 安装 ${sorted.length} 个 skill...\n`);

  let failed = 0;
  for (const skill of sorted) {
    const id = `well-known:${base}/.well-known/skills/${skill.name}`;
    const args = ["skills", "install", id];
    if (force) args.push("--force");

    console.info(`→ ${skill.name}`);
    const r = spawnSync("hermes", args, { stdio: "inherit", encoding: "utf8" });
    if (r.status !== 0) {
      console.error(`✗ ${skill.name} 安装失败 (exit ${r.status})`);
      failed += 1;
    } else {
      console.info(`✓ ${skill.name}\n`);
    }
  }

  if (failed) {
    console.error(`[skills:install] 完成，${failed} 个失败`);
    process.exit(1);
  }
  console.info("[skills:install] 全部安装完成");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
