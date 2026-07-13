from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalog import list_effects, list_text_intros, list_text_outros, list_transitions
from .compile import compile_edit_plan_file
from .export import export_draft_to_mp4, export_supported, is_windows
from .import_draft import detect_jianying_draft_root, import_draft
from .paths import DEFAULT_OUTPUT_DIR


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jy-compile",
        description="Compile Edit Plan → Jianying draft; Windows can RPA-export MP4",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_compile = sub.add_parser("compile", help="Compile an edit plan")
    p_compile.add_argument("plan", type=Path, help="Path to Edit Plan JSON")
    p_compile.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output root for draft folders",
    )
    p_compile.add_argument("--no-zip", action="store_true", help="Skip zip packaging")

    p_trans = sub.add_parser("transitions", help="List transition catalog names")
    p_trans.add_argument("--limit", type=int, default=0)

    p_fx = sub.add_parser("effects", help="List effect catalog names")
    p_fx.add_argument("--limit", type=int, default=0)
    p_fx.add_argument("--grep", type=str, default="")

    p_text_anim = sub.add_parser(
        "text-animations",
        help="List text intro/outro animation names",
    )
    p_text_anim.add_argument(
        "--kind",
        choices=["intro", "outro", "all"],
        default="all",
        help="Which catalog to list",
    )
    p_text_anim.add_argument("--limit", type=int, default=0)
    p_text_anim.add_argument("--grep", type=str, default="")
    p_text_anim.add_argument("--free", action="store_true", help="Only non-VIP")

    p_validate = sub.add_parser("validate", help="Validate Edit Plan JSON only")
    p_validate.add_argument("plan", type=Path)

    p_where = sub.add_parser("where", help="Print detected Jianying draft root")

    p_import = sub.add_parser("import", help="Copy draft into Jianying and register")
    p_import.add_argument("draft_dir", type=Path, help="Compiled draft folder")
    p_import.add_argument("--name", type=str, default=None, help="Draft display/folder name")
    p_import.add_argument("--jy-root", type=Path, default=None, help="Override Jianying draft root")

    p_export = sub.add_parser(
        "export",
        help="Windows only: RPA-export an imported draft to MP4 (Jianying must be open)",
    )
    p_export.add_argument("draft_name", type=str, help="Draft folder name under Jianying root")
    p_export.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output MP4 path",
    )
    p_export.add_argument("--jy-root", type=Path, default=None)
    p_export.add_argument("--resolution", type=str, default="1080P", help="e.g. 1080P / 720P")
    p_export.add_argument("--framerate", type=str, default=None, help="e.g. 30fps")
    p_export.add_argument("--timeout", type=float, default=600)

    p_check = sub.add_parser("export-check", help="Check whether Windows auto-export is available")

    args = parser.parse_args(argv)

    if args.cmd == "validate":
        from .models import EditPlan

        data = json.loads(args.plan.read_text(encoding="utf-8"))
        plan = EditPlan.model_validate(data)
        w, h = plan.canvas_size()
        print(json.dumps({"ok": True, "clips": len(plan.clips), "canvas": [w, h]}, ensure_ascii=False))
        return 0

    if args.cmd == "transitions":
        items = list_transitions()
        if args.limit > 0:
            items = items[: args.limit]
        for it in items:
            print(it.name)
        print(f"# total={len(list_transitions())}", file=sys.stderr)
        return 0

    if args.cmd == "effects":
        items = list_effects()
        if args.grep:
            items = [i for i in items if args.grep in i.name]
        total = len(items)
        if args.limit > 0:
            items = items[: args.limit]
        for it in items:
            print(it.name)
        print(f"# shown={len(items)} matched={total}", file=sys.stderr)
        return 0

    if args.cmd == "text-animations":
        items = []
        if args.kind in ("intro", "all"):
            items.extend(list_text_intros())
        if args.kind in ("outro", "all"):
            items.extend(list_text_outros())
        if args.free:
            items = [i for i in items if not i.is_vip]
        if args.grep:
            items = [i for i in items if args.grep in i.name]
        total = len(items)
        if args.limit > 0:
            items = items[: args.limit]
        for it in items:
            vip = "VIP" if it.is_vip else "free"
            print(f"{it.name}\t{it.kind}\t{vip}")
        print(f"# shown={len(items)} matched={total}", file=sys.stderr)
        return 0

    if args.cmd == "where":
        root = detect_jianying_draft_root()
        print(root)
        return 0

    if args.cmd == "import":
        result = import_draft(args.draft_dir, jy_root=args.jy_root, draft_name=args.name)
        print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
        if is_windows():
            print(
                "Windows: 导入后请保持剪映专业版打开在首页，再执行 jy-compile export …",
                file=sys.stderr,
            )
        else:
            print("提示: 若剪映已打开，请完全退出后重开，首页才会刷新草稿列表。", file=sys.stderr)
        return 0

    if args.cmd == "export-check":
        ok, reason = export_supported()
        print(json.dumps({"ok": ok, "windows": is_windows(), "reason": reason}, ensure_ascii=False, indent=2))
        return 0 if ok else 2

    if args.cmd == "export":
        try:
            result = export_draft_to_mp4(
                args.draft_name,
                args.output,
                jy_root=args.jy_root,
                resolution=args.resolution,
                framerate=args.framerate,
                timeout=args.timeout,
            )
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False, indent=2))
            return 1
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "compile":
        result = compile_edit_plan_file(
            args.plan,
            output_root=args.output,
            make_zip=not args.no_zip,
        )
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        if result.warnings:
            print("warnings:", file=sys.stderr)
            for w in result.warnings:
                print(f"  - {w}", file=sys.stderr)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
