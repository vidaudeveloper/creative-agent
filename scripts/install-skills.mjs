#!/usr/bin/env node
/**
 * 从 GitHub 远程批量安装全部 Skill（无需本地 clone）
 *
 * 用法:
 *   pnpm skills:install
 *   SKILLS_GITHUB_BRANCH=main pnpm skills:install
 */
import { spawnSync } from "node:child_process";

const repo = (process.env.SKILLS_GITHUB_REPO ?? "vidaudeveloper/creative-agent").replace(
  /\/+$/,
  ""
);
const branch = process.env.SKILLS_GITHUB_BRANCH ?? "main";
const category = process.env.SKILLS_INSTALL_CATEGORY ?? "vidau-creative";
const force = process.argv.includes("--force") || process.env.SKILLS_INSTALL_FORCE === "1";
const cli = process.env.SKILLS_CLI?.trim() || "hermes";

const RAW_BASE = `https://raw.githubusercontent.com/${repo}/${branch}`;

const SKILL_PATHS = [
  "L0-foundation/creative-platform",
  "L0-foundation/creative-job-runner",
  "L1-capability/creative-direct",
  "L1-capability/creative-script2film",
  "L1-capability/creative-script2film-keyframes",
  "L1-capability/creative-batch-orchestrator",
  "L2-vertical/trend-viral-short",
  "L2-vertical/product-url-to-video",
];

function skillUrl(path) {
  return `${RAW_BASE}/${path}/SKILL.md`;
}

function main() {
  console.info(
    `[skills:install] 从 GitHub 远程安装 ${SKILL_PATHS.length} 个 skill（${RAW_BASE}）...\n`
  );

  let failed = 0;
  for (const path of SKILL_PATHS) {
    const name = path.split("/").pop();
    const url = skillUrl(path);
    const args = ["skills", "install", url, "--yes", "--category", category];
    if (force) args.push("--force");

    console.info(`→ ${name}`);
    console.info(`  ${url}`);
    const r = spawnSync(cli, args, { stdio: "inherit", encoding: "utf8" });
    if (r.status !== 0) {
      console.error(`✗ ${name} 安装失败 (exit ${r.status})`);
      failed += 1;
    } else {
      console.info(`✓ ${name}\n`);
    }
  }

  if (failed) {
    console.error(`[skills:install] 完成，${failed} 个失败`);
    process.exit(1);
  }
  console.info("[skills:install] 全部安装完成");
}

main();
