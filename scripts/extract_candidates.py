"""Re-run saved extraction prompts with an OpenAI-compatible chat API.

The original tracked candidate outputs came from locally served Qwen through Pi.
This optional script lets readers generate comparison candidates with their own
OpenAI or OpenRouter account. It never changes the reviewed ontology records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts" / "pi-qwen"
PROVIDERS = {
    "openai": ("https://api.openai.com/v1/chat/completions", "OPENAI_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1/chat/completions", "OPENROUTER_API_KEY"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=PROVIDERS)
    parser.add_argument("--model", required=True, help="A chat-completions model ID offered by the selected provider")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", help="Prompt stem, for example art70 or article16")
    group.add_argument("--all", action="store_true", help="Run every saved prompt")
    parser.add_argument("--output-dir", type=Path, help="Defaults to reproduced/<provider>/")
    parser.add_argument("--dry-run", action="store_true", help="List prompts without using an API key or making requests")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prompts = sorted(PROMPTS.glob("*-prompt.txt")) if args.all else [PROMPTS / f"{args.prompt}-prompt.txt"]
    missing = [str(path) for path in prompts if not path.is_file()]
    if not prompts or missing:
        raise SystemExit(f"Missing saved prompt(s): {missing or PROMPTS}")
    output_dir = args.output_dir or ROOT / "reproduced" / args.provider
    if args.dry_run:
        for path in prompts:
            print(f"{path.relative_to(ROOT)} -> {output_dir / (path.name[:-11] + '-raw.txt')}")
        return

    endpoint, key_name = PROVIDERS[args.provider]
    api_key = os.environ.get(key_name)
    if not api_key:
        raise SystemExit(f"Set {key_name} in your environment before making API requests")
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in prompts:
        prompt = path.read_text(encoding="utf-8")
        name = path.name.removesuffix("-prompt.txt")
        payload = {"model": args.model, "messages": [{"role": "user", "content": prompt}], "stream": False}
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=180) as response:
                result = json.load(response)
        except HTTPError as exc:
            detail = exc.read(500).decode("utf-8", errors="replace").replace(api_key, "[REDACTED]")
            raise SystemExit(f"{args.provider} returned HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise SystemExit(f"Could not reach {args.provider}: {exc.reason}") from exc
        try:
            content = result["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("empty or non-text response")
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise SystemExit(f"{args.provider} returned no usable text for {name}: {exc}") from exc
        (output_dir / f"{name}-raw.txt").write_text(content.rstrip() + "\n", encoding="utf-8")
        metadata = {
            "provider": args.provider,
            "requested_model": args.model,
            "returned_model": result.get("model"),
            "response_id": result.get("id"),
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "prompt_file": str(path.relative_to(ROOT)),
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "usage": result.get("usage"),
        }
        (output_dir / f"{name}-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        print(f"Saved {name} candidate and metadata in {output_dir}")


if __name__ == "__main__":
    main()
